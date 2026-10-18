"""How does the truck get to its first stop, and what does that do to the price?

For every route (and a new one, B0: partner-nation rocket stages in the
sun-synchronous band, where rideshares already go) we price three ways in:
  1. rideshare to sun-synchronous orbit + the truck's own engine (all 24 LTANs;
     median reported, range kept),
  2. a dedicated Rocket Lab Neutron,
  3. a dedicated Falcon 9.

Writes results/launch_options_2026.json.
Run: python -m scripts.launch_options_2026   (~5 min)
"""
import glob
import json
import time
from pathlib import Path
import numpy as np

from ocmath.catalog import load_tles, load_satcat, load_gcat_mass, attach_metadata
from ocmath.constants import DEG
from ocmath.j2 import set_rate_model
from ocmath.truck import TruckDesign, ELECTRIC, CHEMICAL, plan_mission, object_kits
from ocmath.launch import OPTIONS, evaluate_with_launch
from ocmath.economics import (price_of_time, default_params, base_values, mission_cost, monte_carlo,
                              reusable_campaign)

ROOT = Path(__file__).resolve().parents[2]
set_rate_model("sgp4")
D = ROOT / "data/celestrak_2026-10-16"
pop = load_tles([f for f in sorted(glob.glob(str(D / "*.tle"))) if "dead_sso" not in f])
attach_metadata(pop, load_satcat(D / "satcat.csv"), load_gcat_mass(ROOT / "data/gcat/satcat.tsv"))
clusters = json.loads((ROOT / "results/clusters_2026.json").read_text())
id2idx = {sid: k for k, sid in enumerate(pop.ids)}
START_JD = 2462137.5            # arrival at the first stop: 2029-01-01, as in truck_routes_2026
PARAMS = default_params()
V = base_values(PARAMS)

# B0: rocket stages in the SSO band owned by the US, India, France (ESA/Arianespace), Japan or
# South Korea, 300-2,500 kg (heavy enough to matter, light enough for a ~150 kg kit), above 650 km.  Owner
# consent is still required; these owners are partners of the agencies that buy removal today.
PARTNERS = {"US", "IND", "FR", "JPN", "SKOR", "ESA"}
sso = next(c for c in clusters if c["name"] == "Rocket bodies, sun-synchronous band")
b0_pool = [id2idx[i] for i in sso["norad_ids"] if i in id2idx
           and pop.meta["owner"][id2idx[i]] in PARTNERS
           and 300.0 <= float(pop.meta["mass_kg"][id2idx[i]] or 0) <= 2500.0
           and pop.alt_km[id2idx[i]] >= 650.0]       # below ~650 km drag brings stages down on its own, and
                                                     # drag (not in our planner) makes their planes hard to predict

routes = json.loads((ROOT / "results/truck_routes_2026.json").read_text())
out = {"b0_pool": [{"norad": pop.ids[k], "name": pop.names[k], "owner": pop.meta["owner"][k],
                    "mass_kg": pop.meta["mass_kg"][k], "alt_km": float(pop.alt_km[k]),
                    "inc_deg": float(pop.i[k] / DEG)} for k in b0_pool],
       "routes": {}, "options": {}}
print(f"B0 pool: {len(b0_pool)} partner-nation SSO rocket stages")

for label, prop in (("electric", ELECTRIC), ("chemical", CHEMICAL)):
    truck = TruckDesign(prop=prop)
    t = time.time()
    kits = sorted(object_kits(pop, b0_pool))[:10]
    lam = price_of_time(prop, truck.dry_mass_kg + sum(kits) + 100.0, V)
    r = None
    for _ in range(4):
        r = plan_mission(pop, b0_pool, 10, START_JD, truck, lam_ms_per_day=lam)
        if r is not None and r["feasible"]:
            break
        lam /= 2.0
    r["lam_ms_per_day"] = lam
    r["targets"] = [{"norad": pop.ids[o], "name": pop.names[o], "owner": pop.meta["owner"][o],
                     "alt_km": float(pop.alt_km[o]), "inc_deg": float(pop.i[o] / DEG),
                     "mass_kg": pop.meta["mass_kg"][o]} for o in r["order"]]
    routes[f"B0_SSO_partner/{label}"] = r
    print(f"B0 {label}: {r['duration_days']:.0f} d, {r['total_dv_kms']*1000:.0f} m/s, "
          f"{r['launch_mass_kg']:.0f} kg, feasible={r['feasible']} ({time.time()-t:.0f}s)")
out["routes"] = {k: v for k, v in routes.items() if k.startswith("B0_")}


def price(e, prop_kind):
    c = mission_cost(e, prop_kind, len(e["order"]), V)
    return {"cost_per_removal_musd": c["per_removal"], "price_per_removal_musd": c["price_per_removal"],
            "breakdown": c["breakdown"], "total_musd": c["total"]}


for key in ["B0_SSO_partner", "B1_SL8_83deg", "A1_Iridium_legacy"]:
    for label, prop in (("electric", ELECTRIC), ("chemical", CHEMICAL)):
        r = routes.get(f"{key}/{label}")
        if r is None or not r.get("feasible"):
            continue
        truck = TruckDesign(prop=prop)
        lam = price_of_time(prop, r["launch_mass_kg"], V)      # economic price of time for the climb
        no_launch = price({**r, "kits_kg": sum(r["kit_masses_kg"])}, label)
        rows = {"no_launch_leg": {**no_launch, "duration_days": r["duration_days"],
                                  "launch_mass_kg": r["launch_mass_kg"]}}
        for L in OPTIONS:
            if L.kind == "rideshare":
                evs = [evaluate_with_launch(pop, truck, r, L, lam, ltan_h=h) for h in np.arange(0.0, 24.0, 1.0)]
                evs = [e for e in evs if e["feasible"]]
                if not evs:
                    rows[L.key] = {"feasible": False}
                    continue
                costs = [price(e, label)["cost_per_removal_musd"] for e in evs]
                e = evs[int(np.argsort(costs)[len(costs) // 2])]           # median-LTAN case
                spread = (float(min(costs)), float(max(costs)))
            else:
                e = evaluate_with_launch(pop, truck, r, L, lam)
                spread = None
            p = price(e, label)
            ins = e["insertion"]
            rows[L.key] = {
                **p, "feasible": e["feasible"], "launch_name": L.name, "source": L.source,
                "launch_mass_kg": e["launch_mass_kg"], "propellant_kg": e["propellant_kg"],
                "duration_days": e["duration_days"], "insertion_dv_ms": ins["dv"] * 1000.0,
                "insertion_days": ins["T_days"], "launch_jd": e["launch_jd"], "ltan_h": ins["ltan_h"],
                "cost_range_over_ltan_musd": spread, "note": e["launch_note"],
                "launch_fixed_musd": e["launch_fixed_musd"],
                "_eval": e,
            }
        best = min((k for k in rows if k != "no_launch_leg" and rows[k].get("feasible")),
                   key=lambda k: rows[k]["cost_per_removal_musd"])
        rows["best"] = best
        out["options"][f"{key}/{label}"] = rows
        line = "  ".join(f"{k}: ${rows[k]['cost_per_removal_musd']:.1f}M/{rows[k]['duration_days']:.0f}d"
                         for k in rows if isinstance(rows[k], dict) and rows[k].get("cost_per_removal_musd"))
        print(f"{key}/{label:<9} {line}  -> best {best}")

# headline: Monte Carlo + reuse for each electric route with its best launch
for key in ["B0_SSO_partner", "B1_SL8_83deg", "A1_Iridium_legacy"]:
    rows = out["options"].get(f"{key}/electric")
    if not rows:
        continue
    e = rows[rows["best"]]["_eval"]
    rows["monte_carlo_best"] = monte_carlo(e, "electric", len(e["order"]), PARAMS)
    if key == "B0_SSO_partner" and rows["best"] == "rideshare":
        # Kit pods ride later rideshares straight to SSO, where this truck already works, so the
        # reuse model applies as-is.  The insertion leg is flown once: add its extra launch mass
        # (propellant), the insurance on it, and its days of operations.
        r0 = routes[f"{key}/electric"]
        camp = reusable_campaign({**r0, "kits_kg": sum(r0["kit_masses_kg"])}, "electric", 10, 10, V)
        dm = e["launch_mass_kg"] - r0["launch_mass_kg"]
        ins_days = e["insertion"]["T_days"]
        extra = dm * V["launch_usd_per_kg"] / 1e6 * (1 + V["insurance_frac"]) + V["ops_musd_per_year"] * ins_days / 365.25
        camp["total"] += extra
        camp["per_removal"] = camp["total"] / camp["removals"]
        camp["years"] += ins_days / 365.25
        camp["first_launch_kg"] += dm
        rows["reuse_10_routes"] = camp

for rows in out["options"].values():
    for v in rows.values():
        if isinstance(v, dict):
            v.pop("_eval", None)
(ROOT / "results/launch_options_2026.json").write_text(json.dumps(out, indent=1, default=float))
routes_path = ROOT / "results/truck_routes_2026.json"
routes_path.write_text(json.dumps(routes, indent=1, default=float))
print("wrote results/launch_options_2026.json and added B0 to truck_routes_2026.json")
