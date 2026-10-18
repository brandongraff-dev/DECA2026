"""Layer 8 runs: time-vs-cost Pareto frontier, stops-per-truck scaling, sensitivity.

Outputs results/pareto_economics.json, consumed by make_figures.py.
"""
import glob
import json
import time
from multiprocessing import Pool
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
START_JD = 2462137.5   # 2029-01-01
CLUSTERS = {"B1_SL8_83deg": "SL-8 (Kosmos-3M stage) 83 deg cluster",
            "A1_Iridium_legacy": "Dead first-generation Iridium",
            "B0_SSO_partner": "Rocket bodies, sun-synchronous band"}
PARTNERS = {"US", "IND", "FR", "JPN", "SKOR", "ESA"}   # same B0 filter as launch_options_2026
LTAN_H = 10.5     # rideshare local time of ascending node used for the sweep [ASSUMPTION; matters little]
LAMBDAS = [0.05, 0.25, 0.75, 2.0, 5.0, 12.0]     # price of time, m/s per day
N_SWEEP = [3, 5, 10, 15, 20]

_POP = None


def _setup():
    global _POP
    from ocmath.j2 import set_rate_model
    from ocmath.catalog import load_tles, load_satcat, load_gcat_mass, attach_metadata
    set_rate_model("sgp4")
    D = ROOT / "data/celestrak_2026-10-16"
    _POP = load_tles([f for f in sorted(glob.glob(str(D / "*.tle"))) if "dead_sso" not in f])
    attach_metadata(_POP, load_satcat(D / "satcat.csv"), load_gcat_mass(ROOT / "data/gcat/satcat.tsv"))


def _job(args):
    cluster_key, engine, lam, n = args
    from ocmath.truck import TruckDesign, ELECTRIC, CHEMICAL, plan_mission
    from ocmath.economics import default_params, base_values, mission_cost
    clusters = json.loads((ROOT / "results/clusters_2026.json").read_text())
    c = next(c for c in clusters if c["name"] == CLUSTERS[cluster_key])
    id2 = {s: k for k, s in enumerate(_POP.ids)}
    pool = _pool(cluster_key, c, id2)
    truck = TruckDesign(prop=ELECTRIC if engine == "electric" else CHEMICAL)
    t = time.time()
    r = plan_mission(_POP, pool, n, START_JD, truck, lam_ms_per_day=lam, beam_width=40, per_parent=10, sa_iters=800)
    if r is None or not r["feasible"]:
        return {"cluster": cluster_key, "engine": engine, "lam": lam, "n": n, "feasible": False}
    from ocmath.launch import RIDESHARE_SSO, evaluate_with_launch
    v = base_values(default_params())
    no_launch = mission_cost({**r, "kits_kg": sum(r["kit_masses_kg"])}, engine, n, v)
    from ocmath.economics import price_of_time
    lam_ins = price_of_time(truck.prop, r["launch_mass_kg"], v)        # the climb is priced at the real cost of time
    e = evaluate_with_launch(_POP, truck, r, RIDESHARE_SSO, lam_ins, ltan_h=LTAN_H)   # rideshare + climb to stop 1
    if not e["feasible"]:
        return {"cluster": cluster_key, "engine": engine, "lam": lam, "n": n, "feasible": False, "why": "launch leg"}
    cost = mission_cost(e, engine, n, v)
    return {"cluster": cluster_key, "engine": engine, "lam": lam, "n": n, "feasible": True,
            "duration_days": e["duration_days"], "route_days": r["duration_days"],
            "insertion_days": e["insertion"]["T_days"], "insertion_dv_ms": e["insertion"]["dv"] * 1000.0,
            "launch_mass_kg": e["launch_mass_kg"], "launch_mass_no_launch_leg_kg": r["launch_mass_kg"],
            "propellant_kg": e["propellant_kg"], "dv_kms": e["total_dv_kms"], "kits_kg": sum(r["kit_masses_kg"]),
            "cost_total_musd": cost["total"], "cost_per_removal_musd": cost["per_removal"],
            "cost_per_removal_no_launch_leg_musd": no_launch["per_removal"],
            "price_per_removal_musd": cost["price_per_removal"], "breakdown": cost["breakdown"],
            "order_norad": [_POP.ids[o] for o in r["order"]], "secs": time.time() - t}


def _pool(cluster_key, c, id2):
    pool = [id2[i] for i in c["norad_ids"] if i in id2]
    if cluster_key == "B0_SSO_partner":
        pool = [k for k in pool if _POP.meta["owner"][k] in PARTNERS
                and 300.0 <= float(_POP.meta["mass_kg"][k] or 0) <= 2500.0 and _POP.alt_km[k] >= 650.0]
    return pool


def single_object_mission(engine, cluster_key="B1_SL8_83deg"):
    """One truck, one object (the status-quo business model), same cost model, same way to orbit."""
    from ocmath.truck import TruckDesign, ELECTRIC, CHEMICAL, object_kits
    from ocmath.missions import launch_mass_kits
    from ocmath.economics import default_params, base_values, mission_cost, price_of_time
    from ocmath.launch import RIDESHARE_SSO, evaluate_with_launch
    clusters = json.loads((ROOT / "results/clusters_2026.json").read_text())
    c = next(c for c in clusters if c["name"] == CLUSTERS[cluster_key])
    id2 = {s: k for k, s in enumerate(_POP.ids)}
    k = _pool(cluster_key, c, id2)[0]
    truck = TruckDesign(prop=ELECTRIC if engine == "electric" else CHEMICAL)
    kit = object_kits(_POP, [k])
    m0, prop, _ = launch_mass_kits([], truck.prop.isp, truck.dry_mass_kg, kit, truck.dv_reserve_kms + truck.dv_rendezvous_kms)
    v = base_values(default_params())
    route = {"order": [k], "legs": [], "kit_masses_kg": kit, "start_jd": START_JD, "launch_mass_kg": m0,
             "propellant_kg": prop, "duration_days": 120.0}  # [ASSUMPTION] 4-month mission at the object
    lam = price_of_time(truck.prop, m0, v)
    e = evaluate_with_launch(_POP, truck, route, RIDESHARE_SSO, lam, ltan_h=LTAN_H)
    cost = mission_cost(e, engine, 1, v)
    return {"engine": engine, "cluster": cluster_key, "n": 1, "launch_mass_kg": e["launch_mass_kg"],
            "duration_days": e["duration_days"], "insertion_days": e["insertion"]["T_days"],
            "cost_per_removal_musd": cost["per_removal"],
            "price_per_removal_musd": cost["price_per_removal"], "breakdown": cost["breakdown"]}


if __name__ == "__main__":
    jobs = [(c, e, lam, 10) for c in CLUSTERS for e in ("electric", "chemical") for lam in LAMBDAS]
    jobs += [(c, e, 0.5, n) for c in ("B1_SL8_83deg", "B0_SSO_partner") for e in ("electric", "chemical") for n in N_SWEEP]
    t0 = time.time()
    with Pool(4, initializer=_setup) as p:
        results = []
        for r in p.imap_unordered(_job, jobs):
            results.append(r)
            if r["feasible"]:
                print(f"{r['cluster']:<20}{r['engine']:<9} lam {r['lam']:>5} n {r['n']:>2}: {r['duration_days']:6.0f} d  "
                      f"{r['launch_mass_kg']:6.0f} kg  ${r['cost_per_removal_musd']:6.2f}M/removal  ({r['secs']:.0f}s)", flush=True)
            else:
                print("infeasible", r, flush=True)
    _setup()
    singles = [single_object_mission(e, c) for c in ("B1_SL8_83deg", "B0_SSO_partner") for e in ("electric", "chemical")]
    for s in singles:
        print(f"single-object {s['cluster']} {s['engine']}: ${s['cost_per_removal_musd']:.1f}M per removal")
    (ROOT / "results/pareto_economics.json").write_text(json.dumps({"runs": results, "single_object": singles},
                                                                    indent=1, default=float))
    print(f"done in {(time.time()-t0)/60:.1f} min")
