"""BENCHMARK 2: four optimisers vs JPL on GTOC9 Mission 10 (10 objects).

Same 10 debris pieces, same launch epoch as JPL's Mission 10.  Each optimiser
must find the visiting order and leg timings (GTOC9 rules: 5-day stay at each
object, arrival-to-arrival <= 30 days -> transfer <= 25 days).

Fair comparison: all routes are scored with OUR leg model, including JPL's own
route (re-evaluated with our model), and converted to launch mass (kg) with the
GTOC9 spacecraft (2000 kg dry, 30 kg kits, Isp 340 s).
"""
import json
import time
from pathlib import Path
import numpy as np

from ocmath.catalog import load_gtoc9, MJD2000_JD
from ocmath.legs import CHEMICAL_GTOC9, DriftBounds
from ocmath.missions import launch_mass
from ocmath.sequencing import (LegOracle, beam_search, simulated_annealing, genetic_algorithm,
                               ant_colony, search_space_size)

ROOT = Path(__file__).resolve().parents[2]
pop = load_gtoc9(ROOT / "data/gtoc9/debris.csv")
sol = json.loads((ROOT / "data/gtoc9/jpl_solution.json").read_text())
ms = next(m for m in sol["missions"] if m["mission"] == 10)
objs = [pop.ids.index(d) for d in ms["debris"]]
start = ms["start_mjd2000"] + MJD2000_JD

bounds = DriftBounds(alt_min_km=300, alt_max_km=1400, di_max_deg=2.0, n_a=33, n_i=13)
oracle = LegOracle(pop, CHEMICAL_GTOC9, bounds, t_options_days=tuple(np.arange(1, 25.01, 1.0)),
                   stay_days=5.0, mass=4000.0, lam=0.0)

def report(name, order, secs, dp=True):
    _, dv, legs = oracle.optimal_timing(order, start) if dp else oracle.decode(order, start)
    m0 = launch_mass([l["dv"] for l in legs], 340.0, 2000.0, 30.0, len(order))
    days = legs[-1]["depart_jd"] + legs[-1]["T_days"] - start
    print(f"{name:<24} dv {dv*1000:7.0f} m/s   launch mass {m0:7.1f} kg   duration {days:5.0f} d   ({secs:5.1f} s)")
    return {"method": name, "order": [pop.ids[o] for o in order], "dv_ms": dv * 1000, "m0": m0, "days": days, "secs": secs}

print(f"Mission 10: {len(objs)} objects -> {search_space_size(len(objs)):,} possible orders")
results = []
# JPL's route with JPL's timing, evaluated by our model
from ocmath.missions import Route, evaluate_route
r = Route(objs, [t + MJD2000_JD for t in ms["departure_mjd2000"][:-1]], ms["transfer_days"])
evaluate_route(pop, r, CHEMICAL_GTOC9, 4000, bounds)
m0_jpl_ours = launch_mass(r.leg_dv, 340.0, 2000.0, 30.0, len(objs))
print(f"{'JPL route (our model)':<24} dv {sum(r.leg_dv)*1000:7.0f} m/s   launch mass {m0_jpl_ours:7.1f} kg   (JPL actual flown: {ms['launch_mass_kg']} kg)")
results.append({"method": "JPL route, our model", "dv_ms": sum(r.leg_dv) * 1000, "m0": m0_jpl_ours,
                "m0_jpl_actual": ms["launch_mass_kg"]})

t = time.time(); b = beam_search(oracle, objs, len(objs), start, width=400, per_parent=24, t_per_b=3)
results.append(report("Beam search", b["order"], time.time() - t))
t = time.time(); o, _ = simulated_annealing(oracle, objs, start, iters=2500, seed=1)
results.append(report("Simulated annealing", o, time.time() - t))
t = time.time(); o, _ = genetic_algorithm(oracle, objs, start, pop_size=40, generations=50, seed=1)
results.append(report("Genetic algorithm", o, time.time() - t))
t = time.time(); o, _ = ant_colony(oracle, objs, start, ants=20, iterations=25, seed=1)
results.append(report("Ant colony", o, time.time() - t))
t = time.time(); o, _ = simulated_annealing(oracle, objs, start, iters=1500, seed=2, init=b["order"])
results.append(report("Beam + annealing polish", o, time.time() - t))

t = time.time(); results.append(report("JPL order + our DP timing", objs, time.time() - t))
(ROOT / "results/benchmark_mission10.json").write_text(json.dumps(results, indent=1, default=float))
