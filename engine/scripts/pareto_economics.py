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
            "A1_Iridium_legacy": "Dead first-generation Iridium"}
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
    pool = [id2[i] for i in c["norad_ids"] if i in id2]
    truck = TruckDesign(prop=ELECTRIC if engine == "electric" else CHEMICAL)
    t = time.time()
    r = plan_mission(_POP, pool, n, START_JD, truck, lam_ms_per_day=lam, beam_width=40, per_parent=10, sa_iters=800)
    if r is None or not r["feasible"]:
        return {"cluster": cluster_key, "engine": engine, "lam": lam, "n": n, "feasible": False}
    cost = mission_cost(r, engine, n, base_values(default_params()))
    return {"cluster": cluster_key, "engine": engine, "lam": lam, "n": n, "feasible": True,
            "duration_days": r["duration_days"], "launch_mass_kg": r["launch_mass_kg"],
            "propellant_kg": r["propellant_kg"], "dv_kms": r["total_dv_kms"], "kits_kg": sum(r["kit_masses_kg"]),
            "cost_total_musd": cost["total"], "cost_per_removal_musd": cost["per_removal"],
            "price_per_removal_musd": cost["price_per_removal"], "breakdown": cost["breakdown"],
            "order_norad": [_POP.ids[o] for o in r["order"]], "secs": time.time() - t}


def single_object_mission(engine):
    """One truck, one object (the status-quo business model), same cost model."""
    from ocmath.truck import TruckDesign, ELECTRIC, CHEMICAL, object_kits
    from ocmath.missions import launch_mass_kits
    from ocmath.economics import default_params, base_values, mission_cost
    clusters = json.loads((ROOT / "results/clusters_2026.json").read_text())
    c = next(c for c in clusters if c["name"] == CLUSTERS["B1_SL8_83deg"])
    id2 = {s: k for k, s in enumerate(_POP.ids)}
    k = id2[c["norad_ids"][0]]
    truck = TruckDesign(prop=ELECTRIC if engine == "electric" else CHEMICAL)
    kit = object_kits(_POP, [k])
    m0, prop, _ = launch_mass_kits([], truck.prop.isp, truck.dry_mass_kg, kit, truck.dv_reserve_kms + truck.dv_rendezvous_kms)
    route = {"launch_mass_kg": m0, "propellant_kg": prop, "duration_days": 120.0}  # [ASSUMPTION] 4-month mission
    cost = mission_cost(route, engine, 1, base_values(default_params()))
    return {"engine": engine, "n": 1, "launch_mass_kg": m0, "cost_per_removal_musd": cost["per_removal"],
            "price_per_removal_musd": cost["price_per_removal"], "breakdown": cost["breakdown"]}


if __name__ == "__main__":
    jobs = [(c, e, lam, 10) for c in CLUSTERS for e in ("electric", "chemical") for lam in LAMBDAS]
    jobs += [("B1_SL8_83deg", e, 0.5, n) for e in ("electric", "chemical") for n in N_SWEEP if n != 10]
    jobs += [("B1_SL8_83deg", e, 0.5, 10) for e in ("electric", "chemical")]
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
    singles = [single_object_mission(e) for e in ("electric", "chemical")]
    for s in singles:
        print(f"single-object {s['engine']}: ${s['cost_per_removal_musd']:.1f}M per removal")
    (ROOT / "results/pareto_economics.json").write_text(json.dumps({"runs": results, "single_object": singles},
                                                                    indent=1, default=float))
    print(f"done in {(time.time()-t0)/60:.1f} min")
