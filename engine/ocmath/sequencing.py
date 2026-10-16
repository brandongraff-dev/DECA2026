"""Layer 6: choosing WHICH objects and in WHAT ORDER (a moving-target salesman).

For judges: "With 10 stops there are 3.6 million possible orders; with 20 stops
there are 2.4 billion billion -- and every option changes as the orbits drift.
No computer can try them all, so we use four smart search strategies borrowed
from nature and logistics, and let them compete."

All four methods share one cost oracle (`LegOracle`), so they are compared on
exactly the same physics:

  * Beam search        -- grow many partial routes in parallel, keep the best W.
  * Simulated annealing -- shuffle a route, sometimes accept worse ones early so
                           we don't get stuck (like slowly cooling metal).
  * Genetic algorithm  -- breed good routes together, mutate, keep the fittest.
  * Ant colony         -- virtual ants lay "pheromone" on good hops; future ants
                           follow strong trails.

Route timing is decoded greedily: at each hop we choose the transfer time T from
a menu that minimises  dv + lambda * T.  lambda (km/s per day) is the "price of
time"; sweeping it traces the time-vs-fuel Pareto frontier (Layer 8).
"""
from dataclasses import dataclass
import math
import numpy as np

from .constants import DAY
from .legs import leg_cost, DriftBounds


def search_space_size(n_pick, n_pool=None):
    """Number of possible visiting orders: N!  (or M!/(M-N)! when picking N of M)."""
    if n_pool is None:
        return math.factorial(n_pick)
    return math.perm(n_pool, n_pick)


@dataclass
class LegOracle:
    pop: object
    prop: object
    bounds: DriftBounds
    t_options_days: tuple            # menu of transfer times
    stay_days: float                 # time spent at each object (capture + kit install)
    mass: float                      # representative truck mass (electric spiral times)
    lam: float = 0.0                 # price of time [km/s per day]
    dv_rendezvous: float = 0.0
    calls: int = 0

    def hops(self, A, depart_jd, Bs, Ts_days):
        """Core vectorised call: dv for rows (depart_jd[k], Bs[k], Ts_days[k]) leaving object A."""
        Bs = np.asarray(Bs)
        depart_jd = np.broadcast_to(np.asarray(depart_jd, float), Bs.shape)
        r = leg_cost(self.prop, self.pop.a[A], self.pop.i[A], self.pop.raan_at(depart_jd, np.full(Bs.shape, A)),
                     self.pop.a[Bs], self.pop.i[Bs], self.pop.raan_at(depart_jd, Bs),
                     np.asarray(Ts_days, float) * DAY, self.mass, self.bounds, self.dv_rendezvous)
        self.calls += 1
        return r["dv"]

    def hop_matrix(self, A, depart_jd, candidates):
        """dv for every (candidate B, time option) pair: arrays (nB, nT) of dv and T [days]."""
        cand = np.asarray(candidates)
        nT = len(self.t_options_days)
        Bs = np.repeat(cand, nT)
        Ts = np.tile(np.asarray(self.t_options_days, float), len(cand))
        dv = self.hops(A, depart_jd, Bs, Ts)
        return dv.reshape(len(cand), nT), Ts.reshape(len(cand), nT)

    def best_hops(self, A, depart_jd, candidates):
        """For each candidate B: the best (dv, T) from the time menu."""
        dv, T = self.hop_matrix(A, depart_jd, candidates)
        score = dv + self.lam * T
        k = np.argmin(score, axis=1)
        rows = np.arange(dv.shape[0])
        return dv[rows, k], T[rows, k], score[rows, k]

    def optimal_timing(self, order, start_jd, step_days=0.5, max_states=120, max_days=None):
        """Dynamic programming over arrival times for a FIXED order.

        Unlike the greedy decoder, this can accept a slightly pricier hop now if
        it sets up much cheaper hops later.  Arrival times are bucketed to
        `step_days`; to stay fast we keep the `max_states` best partial
        schedules at each stop (a beam over time).  Minimises
        sum(dv) + lam * duration.
        """
        Topt = np.asarray(self.t_options_days, float)
        nT = len(Topt)
        # each state: elapsed days at arrival, score, dv sum, back-pointer
        el = np.array([0.0]); sc = np.array([0.0]); dvs = np.array([0.0])
        history = []
        for A, B in zip(order[:-1], order[1:]):
            depart = start_jd + el + self.stay_days                     # (nS,)
            dep_rows = np.repeat(depart, nT)
            T_rows = np.tile(Topt, len(el))
            dv = self.hops(A, dep_rows, np.full(dep_rows.shape, B), T_rows)
            el2 = np.round((np.repeat(el, nT) + self.stay_days + T_rows) / step_days) * step_days
            sc2 = np.repeat(sc, nT) + dv + self.lam * (self.stay_days + T_rows)
            dv2 = np.repeat(dvs, nT) + dv
            parent = np.repeat(np.arange(len(el)), nT)
            ok = np.isfinite(sc2)
            if max_days is not None:
                ok &= el2 <= max_days
            idx = np.nonzero(ok)[0]
            idx = idx[np.argsort(sc2[idx])]
            _, first = np.unique(el2[idx], return_index=True)          # best per time bucket
            idx = idx[np.sort(first)][:max_states] if len(first) else idx[:0]
            idx = idx[np.argsort(sc2[idx])][:max_states]
            if len(idx) == 0:
                return np.inf, np.inf, []
            history.append({"A": int(A), "B": int(B), "depart": dep_rows[idx], "T": T_rows[idx],
                            "dv": dv[idx], "parent": parent[idx]})
            el, sc, dvs = el2[idx], sc2[idx], dv2[idx]
        k = int(np.argmin(sc))
        best_sc, best_dv = float(sc[k]), float(dvs[k])
        legs = []
        for h in reversed(history):                                     # walk back-pointers
            legs.append({"from": h["A"], "to": h["B"], "depart_jd": float(h["depart"][k]),
                         "T_days": float(h["T"][k]), "dv": float(h["dv"][k])})
            k = int(h["parent"][k])
        return best_sc, best_dv, legs[::-1]

    def decode(self, order, start_jd, timing="greedy"):
        """Score a fixed order. timing='greedy' (fast) or 'dp' (optimal_timing)."""
        if timing == "dp":
            return self.optimal_timing(order, start_jd)
        jd = start_jd
        legs, total_dv, score = [], 0.0, 0.0
        for A, B in zip(order[:-1], order[1:]):
            depart = jd + self.stay_days
            dv, T, sc = self.best_hops(A, depart, [B])
            legs.append({"from": int(A), "to": int(B), "depart_jd": depart, "T_days": float(T[0]), "dv": float(dv[0])})
            total_dv += dv[0]
            score += sc[0] + self.lam * self.stay_days
            jd = depart + T[0]
        return float(score), float(total_dv), legs


# --------------------------------------------------------------------------- beam
def beam_search(oracle, pool, n_stops, start_jd, width=64, per_parent=8, starts=None, max_days=None,
                time_bucket=2.0, t_per_b=2):
    """Grow routes of n_stops objects chosen from `pool`.

    starts: candidate first objects (default: all of pool).
    max_days: optional cap on mission duration (arrival at last object).
    """
    pool = list(pool)
    starts = pool if starts is None else list(starts)
    beam = [{"order": [s], "jd": start_jd, "score": 0.0, "dv": 0.0} for s in starts]
    for _ in range(n_stops - 1):
        children = []
        for st in beam:
            cand = [b for b in pool if b not in st["order"]]
            if not cand:
                continue
            depart = st["jd"] + oracle.stay_days
            dv, T = oracle.hop_matrix(st["order"][-1], depart, cand)
            sc = dv + oracle.lam * T
            # diversity: for each candidate keep its best `t_per_b` timings, then
            # keep the best `per_parent` (candidate, timing) pairs overall
            tk = np.argsort(sc, axis=1)[:, :t_per_b]
            pairs = [(sc[b, t], b, t) for b in range(sc.shape[0]) for t in tk[b]]
            pairs.sort(key=lambda x: x[0])
            for _, b, t in pairs[:per_parent]:
                if not np.isfinite(sc[b, t]):
                    continue
                arrive = depart + T[b, t]
                if max_days is not None and arrive - start_jd > max_days:
                    continue
                children.append({"order": st["order"] + [cand[b]], "jd": arrive,
                                 "score": st["score"] + sc[b, t] + oracle.lam * oracle.stay_days,
                                 "dv": st["dv"] + dv[b, t]})
        # de-duplicate: same visited set + same current object + similar time -> keep best
        best = {}
        for c in children:
            key = (frozenset(c["order"]), c["order"][-1], round((c["jd"] - start_jd) / time_bucket))
            if key not in best or c["score"] < best[key]["score"]:
                best[key] = c
        beam = sorted(best.values(), key=lambda c: c["score"])[:width]
        if not beam:
            return None
    return beam[0]


# ---------------------------------------------------------------- annealing
def simulated_annealing(oracle, objects, start_jd, iters=3000, t0=0.05, t1=0.0005, seed=0, init=None,
                        timing="greedy", pool=None):
    """Optimise the order of a set of objects (first object may also move).

    If `pool` is given, a fourth move type swaps a stop for an unused object from
    the pool -- so the method chooses WHICH objects as well as their order.
    """
    rng = np.random.default_rng(seed)
    cur = list(init) if init is not None else list(rng.permutation(objects))
    spare = [p for p in pool if p not in cur] if pool is not None else []
    cur_s, _, _ = oracle.decode(cur, start_jd, timing)
    best, best_s = cur[:], cur_s
    for it in range(iters):
        temp = t0 * (t1 / t0) ** (it / max(iters - 1, 1))
        new = cur[:]
        i, j = sorted(rng.choice(len(new), 2, replace=False))
        move = rng.integers(4 if spare else 3)
        if move == 3:                                   # swap in an unused object
            k = rng.integers(len(spare))
            new[i], cand_out = spare[k], new[i]
        elif move == 0:
            new[i], new[j] = new[j], new[i]                 # swap two stops
        elif move == 1:
            new[i:j + 1] = new[i:j + 1][::-1]               # reverse a segment (2-opt)
        else:
            x = new.pop(i); new.insert(j, x)                 # move one stop
        s, _, _ = oracle.decode(new, start_jd, timing)
        if s < cur_s or rng.random() < math.exp(-(s - cur_s) / temp):
            if move == 3:
                spare[k] = cand_out
            cur, cur_s = new, s
            if s < best_s:
                best, best_s = new[:], s
    return best, best_s


# ------------------------------------------------------------------- genetic
def _order_crossover(p1, p2, rng):
    n = len(p1)
    i, j = sorted(rng.choice(n, 2, replace=False))
    child = [None] * n
    child[i:j + 1] = p1[i:j + 1]
    fill = [g for g in p2 if g not in child[i:j + 1]]
    k = 0
    for pos in range(n):
        if child[pos] is None:
            child[pos] = fill[k]; k += 1
    return child


def genetic_algorithm(oracle, objects, start_jd, pop_size=40, generations=60, p_mut=0.3, seed=0, seeds=(),
                      timing="greedy"):
    rng = np.random.default_rng(seed)
    popl = [list(s) for s in seeds] + [list(rng.permutation(objects)) for _ in range(pop_size - len(seeds))]
    fit = [oracle.decode(ind, start_jd, timing)[0] for ind in popl]
    for _ in range(generations):
        new = [popl[int(np.argmin(fit))][:]]                       # elitism
        while len(new) < pop_size:
            a, b = (min(rng.choice(pop_size, 3, replace=False), key=lambda q: fit[q]) for _ in range(2))
            child = _order_crossover(popl[a], popl[b], rng)
            if rng.random() < p_mut:
                i, j = sorted(rng.choice(len(child), 2, replace=False))
                child[i:j + 1] = child[i:j + 1][::-1]
            new.append(child)
        popl = new
        fit = [oracle.decode(ind, start_jd, timing)[0] for ind in popl]
    k = int(np.argmin(fit))
    return popl[k], fit[k]


# ----------------------------------------------------------------------- ants
def ant_colony(oracle, objects, start_jd, ants=20, iterations=30, alpha=1.0, beta=3.0, rho=0.2, seed=0):
    rng = np.random.default_rng(seed)
    objs = list(objects)
    n = len(objs)
    pos = {o: k for k, o in enumerate(objs)}
    tau = np.ones((n + 1, n))              # row n = "start" pheromone
    best, best_s = None, np.inf
    for _ in range(iterations):
        tours = []
        for _ in range(ants):
            first = objs[rng.choice(n, p=tau[n] / tau[n].sum())]
            order, jd, score = [first], start_jd, 0.0
            while len(order) < n:
                cand = [o for o in objs if o not in order]
                depart = jd + oracle.stay_days
                dv, T, sc = oracle.best_hops(order[-1], depart, cand)
                eta = 1.0 / (sc + 1e-3)
                w = tau[pos[order[-1]], [pos[c] for c in cand]] ** alpha * eta ** beta
                k = rng.choice(len(cand), p=w / w.sum())
                order.append(cand[k]); score += sc[k]; jd = depart + T[k]
            tours.append((order, score))
            if score < best_s:
                best, best_s = order, score
        tau *= (1 - rho)
        for order, score in sorted(tours, key=lambda t: t[1])[:5]:
            tau[n, pos[order[0]]] += 1.0 / score
            for a, b in zip(order[:-1], order[1:]):
                tau[pos[a], pos[b]] += 1.0 / score
    return best, best_s
