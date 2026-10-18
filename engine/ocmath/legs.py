"""Layer 5: the wait-vs-burn trade-off for ONE leg (object A -> object B).

For judges: "Instead of muscling our orbit around to meet the next piece of junk,
we move to a slightly different 'parking lane' where Earth twists our orbit at a
different speed, wait until our plane lines up with the target's, then hop over.
The longer we're willing to wait, the less fuel we burn."

Model (a "drift-orbit" leg, the same family of model used by GTOC9 teams and by
Di Carlo et al. 2017, here written in a vectorised form):

  1. Leave A's orbit (a_A, i_A) for a drift orbit (a_d, i_d).  Cost dv1.
  2. Coast on the drift orbit for exactly as long as it takes (tau, solved in
     closed form) for its plane to catch up with the target's plane.
  3. Go from the drift orbit to B's orbit (fixing any inclination difference and
     any leftover plane mismatch), then ride along with B until the leg ends.

We search a grid of (a_d, i_d) and keep the cheapest.  Chemical engines change
orbit instantly (impulsive); electric engines spiral slowly, so their transfer
times are subtracted from the coast and the plane drift during the spirals is
accounted for with the average of the start/end rates.

Simplifications (stated in the paper): circular orbits; secular J2 only (no drag,
no higher harmonics); along-track phasing and final proximity operations are
represented by a fixed dv allowance (`dv_rendezvous`), not simulated.
"""
from dataclasses import dataclass
import numpy as np

from .constants import R_E, DAY, DEG, TWO_PI
from .j2 import raan_rate
from .transfers import (impulsive_combined_dv, edelbaum_dv, plane_angle,
                        low_thrust_burn_time, propellant_for_dv)


@dataclass
class Propulsion:
    """What engine the truck carries."""
    kind: str                 # "chemical" or "electric"
    isp: float                # specific impulse [s]
    thrust_N: float = 0.0     # only used for electric
    name: str = ""

    @property
    def thrust_kN(self):
        return self.thrust_N / 1000.0


CHEMICAL_GTOC9 = Propulsion("chemical", isp=340.0, name="Chemical (GTOC9 rules, Isp 340 s)")


@dataclass
class DriftBounds:
    """Where the truck is allowed to park while it drifts."""
    alt_min_km: float = 300.0
    alt_max_km: float = 1400.0
    di_max_deg: float = 2.0   # how far the drift orbit may tilt beyond the A..B inclination range
    n_a: int = 33             # grid resolution in altitude
    n_i: int = 13             # grid resolution in inclination


def _grid(a_A, i_A, a_B, i_B, bounds):
    """Build the (a_d, i_d) candidate grid, shape (nB, n_a*n_i + 2).

    The two extra columns are the 'no-drift' choices: stay in A's orbit, or move
    to B's orbit immediately and ride along with it.
    """
    nB = a_B.shape[0]
    a_lin = R_E + np.linspace(bounds.alt_min_km, bounds.alt_max_km, bounds.n_a)
    di = bounds.di_max_deg * DEG
    i_lo = np.minimum(i_A, i_B) - di
    i_hi = np.maximum(i_A, i_B) + di
    f = np.linspace(0.0, 1.0, bounds.n_i)
    i_grid = i_lo[:, None] + (i_hi - i_lo)[:, None] * f[None, :]          # (nB, n_i)
    a_d = np.broadcast_to(a_lin[None, :, None], (nB, bounds.n_a, bounds.n_i)).reshape(nB, -1)
    i_d = np.broadcast_to(i_grid[:, None, :], (nB, bounds.n_a, bounds.n_i)).reshape(nB, -1)
    a_d = np.concatenate([a_d, np.full((nB, 1), a_A), a_B[:, None]], axis=1)
    i_d = np.concatenate([i_d, np.full((nB, 1), i_A), i_B[:, None]], axis=1)
    return a_d, i_d


def leg_cost(prop, a_A, i_A, raan_A, a_B, i_B, raan_B, T, mass,
             bounds=DriftBounds(), dv_rendezvous=0.0):
    """Cheapest drift-orbit transfer from A to each candidate B in time T.

    Parameters (angles rad, distances km, T seconds, mass kg):
      a_A, i_A, raan_A : chaser's starting orbit (scalars; raan_A may be per-row), raan at departure
      a_B, i_B, raan_B : arrays of candidate targets, raan_B at departure time
      T                : transfer time (scalar, or one value per candidate B)
      mass             : truck mass at departure (for electric spiral times)

    Returns dict of arrays (length nB): dv [km/s], a_d, i_d, t_spiral [s],
    feasible (bool).
    """
    a_B = np.atleast_1d(np.asarray(a_B, float))
    i_B = np.atleast_1d(np.asarray(i_B, float))
    raan_B = np.atleast_1d(np.asarray(raan_B, float))
    T = np.broadcast_to(np.asarray(T, float), a_B.shape)[:, None]
    raan_A = np.broadcast_to(np.asarray(raan_A, float), a_B.shape)[:, None]   # may differ per row
    a_d, i_d = _grid(a_A, i_A, a_B, i_B, bounds)

    w_A = raan_rate(a_A, i_A)
    w_d = raan_rate(a_d, i_d)
    w_B = raan_rate(a_B, i_B)[:, None]
    gap0 = raan_B[:, None] - raan_A                           # target plane minus ours, at departure
    theta1 = np.abs(i_A - i_d)                               # departure: inclination tweak only

    def drift_time(t1, t2):
        """Closed-form drift duration tau that closes the RAAN gap exactly.

        Timeline: spiral out (t1) -> drift on (a_d, i_d) for tau -> spiral in (t2)
        -> ride along in B's orbit for the rest of T.  The gap left at the end is
            G(tau) = C + tau * (w_B - w_d),
            C = gap0 + t1 (w_B - (w_A + w_d)/2) + t2 (w_B - w_d)/2
        and we pick the smallest tau >= 0 with G = 0 (mod 360 deg).  If that tau
        does not fit in the time available, drift as long as possible and pay
        for the leftover angle with a plane change.
        """
        avail = np.maximum(T - t1 - t2, 0.0)
        C = gap0 + t1 * (w_B - 0.5 * (w_A + w_d)) + t2 * 0.5 * (w_B - w_d)
        rel = w_B - w_d
        with np.errstate(divide="ignore", invalid="ignore"):
            tau = np.where(rel > 0, np.mod(-C, TWO_PI) / rel, np.mod(C, TWO_PI) / -rel)
        tau = np.where(np.isfinite(tau), tau, np.inf)
        fits = tau <= avail
        tau_used = np.where(fits, tau, avail)
        resid = np.mod(C + tau_used * rel + np.pi, TWO_PI) - np.pi    # wrapped to [-pi, pi]
        resid0 = np.mod(C + np.pi, TWO_PI) - np.pi                   # option: don't drift at all
        better0 = ~fits & (np.abs(resid0) < np.abs(resid))
        tau_used = np.where(better0, 0.0, tau_used)
        resid = np.where(better0, resid0, resid)
        return tau_used, resid

    if prop.kind == "chemical":
        dv1 = impulsive_combined_dv(a_A, a_d, theta1)
        zero = np.zeros_like(dv1)
        tau, resid = drift_time(zero, zero)
        # arrival burn: altitude change + inclination change + any leftover RAAN angle
        theta2 = plane_angle(i_d, np.zeros_like(resid), i_B[:, None], resid)
        dv2 = impulsive_combined_dv(a_d, a_B[:, None], theta2)
        t_spiral = zero
        t1 = t2 = zero
        feasible = np.ones_like(dv1, dtype=bool)
    elif prop.kind == "electric":
        dv1 = edelbaum_dv(a_A, a_d, theta1)
        t1 = low_thrust_burn_time(mass, dv1, prop.thrust_kN, prop.isp)
        m1 = mass - propellant_for_dv(mass, dv1, prop.isp)
        t2 = np.zeros_like(dv1)
        for _ in range(3):  # fixed-point: t2 depends on dv2 which depends on t2
            tau, resid = drift_time(t1, t2)
            theta2 = plane_angle(i_d, np.zeros_like(resid), i_B[:, None], resid)
            dv2 = edelbaum_dv(a_d, a_B[:, None], theta2)
            t2 = low_thrust_burn_time(m1, dv2, prop.thrust_kN, prop.isp)
        t_spiral = t1 + t2
        feasible = t_spiral <= T
    else:
        raise ValueError(prop.kind)

    dv = dv1 + dv2 + dv_rendezvous
    dv_masked = np.where(feasible, dv, np.inf)
    k = np.argmin(dv_masked, axis=1)
    rows = np.arange(a_B.shape[0])
    return {
        "dv": dv_masked[rows, k],
        "a_d": a_d[rows, k],
        "i_d": i_d[rows, k],
        "t_spiral": t_spiral[rows, k],
        "t_drift": np.broadcast_to(tau, dv.shape)[rows, k],
        "t1": np.broadcast_to(t1, dv.shape)[rows, k],          # spiral-out duration [s]
        "t2": np.broadcast_to(t2, dv.shape)[rows, k],          # spiral-in duration [s]
        "dv1": np.broadcast_to(dv1, dv.shape)[rows, k],
        "dv2": np.broadcast_to(dv2, dv.shape)[rows, k],
        "feasible": feasible[rows, k],
        "dv_direct": (dv1 + dv2)[rows, -1] + dv_rendezvous,  # 'go to B now and ride along'
    }


def leg_cost_throttled(prop, a_A, i_A, raan_A, a_B, i_B, raan_B, T, mass,
                       bounds=DriftBounds(), dv_rendezvous=0.0, factors=tuple(np.linspace(1.0, 2.2, 25)),
                       plan_mass=None):
    """leg_cost, letting an electric truck throttle down.

    Spiral timing shifts where the drift starts, so a leg can close neatly at
    one thrust level and miss at another.  A real electric thruster can run
    below full power, so a light truck can always fly a heavier truck's slower
    schedule: running at 1/f of full thrust is the same, for timing, as being f
    times heavier.  We try a range of throttle settings (and the planner's own
    mass, at which every planned leg is known to work) and keep the cheapest.
    """
    if prop.kind != "electric":
        return leg_cost(prop, a_A, i_A, raan_A, a_B, i_B, raan_B, T, mass, bounds, dv_rendezvous)
    best = None
    factors = list(factors)
    if plan_mass is not None and plan_mass > mass:
        factors.append(plan_mass / mass)        # the mass the planner proved this leg at
    for f in factors:
        r = leg_cost(prop, a_A, i_A, raan_A, a_B, i_B, raan_B, T, mass * f, bounds, dv_rendezvous)
        r["throttle"] = np.full(r["dv"].shape, 1.0 / f)
        if best is None:
            best = r
            continue
        better = r["dv"] < best["dv"]
        for k in best:
            best[k] = np.where(better, r[k], best[k])
    return best


def dv_vs_time_curve(prop, a_A, i_A, raan_A, a_B, i_B, raan_B, times, mass, bounds=DriftBounds()):
    """The wait-vs-burn curve for one leg: cheapest dv for each allowed transfer time."""
    out = []
    for T in times:
        r = leg_cost(prop, a_A, i_A, raan_A, np.array([a_B]), np.array([i_B]),
                     np.array([raan_B]), T, mass, bounds)
        out.append(r["dv"][0])
    return np.array(out)
