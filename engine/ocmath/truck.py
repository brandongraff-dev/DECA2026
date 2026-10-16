"""The Orbital Curbside truck: design parameters + 'plan a mission' in one call.

Every number here is either SOURCED (see research/economics_inputs.md) or an
explicit [ASSUMPTION] that the economics layer stress-tests.
"""
from dataclasses import dataclass, field, asdict
import numpy as np

from .constants import DAY, R_E, DEG
from .legs import Propulsion, DriftBounds, leg_cost
from .kits import kit_mass, KitDesign
from .missions import launch_mass_kits
from .sequencing import LegOracle, beam_search, simulated_annealing

# SOURCED: Busek BHT-1500: 101 mN, 1710 s, 1.5 kW each (busek.com/bht1500); two units.
ELECTRIC = Propulsion("electric", isp=1710.0, thrust_N=0.202, name="Electric: 2x BHT-1500-class Hall thrusters")
# [ASSUMPTION] storable bipropellant, typical Isp ~320 s, for the chemical comparison truck.
CHEMICAL = Propulsion("chemical", isp=320.0, name="Chemical: bipropellant (Isp 320 s)")


@dataclass
class TruckDesign:
    prop: Propulsion = field(default_factory=lambda: ELECTRIC)
    dry_mass_kg: float = 600.0            # [ASSUMPTION] bus + capture arm + thrusters + power
    stay_days: float = 10.0               # [ASSUMPTION] approach, inspect, attach kit, back away
    dv_rendezvous_kms: float = 0.020      # [ASSUMPTION] phasing + proximity ops allowance per stop
    dv_reserve_kms: float = 0.150         # [ASSUMPTION] truck disposes of itself at the end
    t_options_days: tuple = (10, 15, 20, 30, 45, 60, 90, 120, 150, 180)
    bounds: DriftBounds = field(default_factory=lambda: DriftBounds(alt_min_km=600, alt_max_km=1500,
                                                                    di_max_deg=3.0, n_a=31, n_i=13))
    kit: KitDesign = field(default_factory=KitDesign)


def object_kits(pop, idx, controlled_above_kg=5000.0, design=KitDesign()):
    """Kit mass for each object (controlled re-entry kit for very heavy objects)."""
    masses = np.array(pop.meta.get("mass_kg", [np.nan] * len(pop)), float)[idx]
    alts = pop.alt_km[idx]
    out = []
    for m, h in zip(masses, alts):
        m = 1000.0 if not np.isfinite(m) else m       # [ASSUMPTION] unknown mass -> 1 t
        k, _ = kit_mass(m, h, controlled=m > controlled_above_kg, design=design)
        out.append(float(k))
    return out


def evaluate(pop, truck, order, legs_timing, kit_masses, iterations=3):
    """Re-price a planned route with the truck's real, changing mass."""
    legs = [dict(l) for l in legs_timing]
    m0, prop_kg, masses = None, None, [truck.dry_mass_kg + sum(kit_masses)] * len(legs)
    for _ in range(iterations):
        for k, l in enumerate(legs):
            A, B = l["from"], l["to"]
            r = leg_cost(truck.prop, pop.a[A], pop.i[A], pop.raan_at(l["depart_jd"], A),
                         pop.a[[B]], pop.i[[B]], pop.raan_at(l["depart_jd"], [B]),
                         l["T_days"] * DAY, masses[k], truck.bounds, truck.dv_rendezvous_kms)
            l.update(dv=float(r["dv"][0]), a_d=float(r["a_d"][0]), i_d=float(r["i_d"][0]),
                     t_spiral_days=float(r["t_spiral"][0] / DAY), feasible=bool(r["feasible"][0]))
        m0, prop_kg, masses = launch_mass_kits([l["dv"] for l in legs], truck.prop.isp, truck.dry_mass_kg,
                                               kit_masses, truck.dv_reserve_kms)
        if truck.prop.kind != "electric":
            break
    start = legs[0]["depart_jd"] - truck.stay_days
    end = legs[-1]["depart_jd"] + legs[-1]["T_days"] + truck.stay_days
    return {
        "order": [int(o) for o in order], "legs": legs, "kit_masses_kg": kit_masses,
        "total_dv_kms": float(sum(l["dv"] for l in legs)), "launch_mass_kg": m0, "propellant_kg": prop_kg,
        "start_jd": float(start), "end_jd": float(end), "duration_days": float(end - start),
        "feasible": all(l["feasible"] for l in legs) and np.isfinite(m0),
    }


def plan_mission(pop, pool, n_stops, start_jd, truck, lam_ms_per_day=0.5, beam_width=60, per_parent=12,
                 sa_iters=1500, seed=0, max_days=None):
    """Choose + order n_stops objects from pool, time every leg, return the priced route."""
    kits_all = dict(zip(pool, object_kits(pop, pool, design=truck.kit)))
    # Plan with the HEAVIEST the truck will be (all kits aboard + a propellant guess):
    # spirals only get faster as it lightens, so every planned leg stays feasible.
    rep_mass = truck.dry_mass_kg + sum(sorted(kits_all.values())[-n_stops:]) + 300.0
    oracle = LegOracle(pop, truck.prop, truck.bounds, truck.t_options_days, truck.stay_days,
                       mass=rep_mass, lam=lam_ms_per_day / 1000.0, dv_rendezvous=truck.dv_rendezvous_kms)
    b = beam_search(oracle, pool, n_stops, start_jd, width=beam_width, per_parent=per_parent,
                    max_days=max_days, t_per_b=2)
    if b is None:
        return None
    order, _ = simulated_annealing(oracle, b["order"], start_jd, iters=sa_iters, seed=seed,
                                   init=b["order"], pool=pool)
    sc_dp, _, legs = oracle.optimal_timing(order, start_jd, step_days=1.0, max_days=max_days)
    sc_beam, _, legs_beam = oracle.optimal_timing(b["order"], start_jd, step_days=1.0, max_days=max_days)
    if sc_beam < sc_dp:
        order, legs = b["order"], legs_beam
    if not legs:
        return None
    return evaluate(pop, truck, order, legs, [kits_all[o] for o in order])
