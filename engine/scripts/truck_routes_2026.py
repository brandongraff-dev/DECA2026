"""Plan Orbital Curbside missions on the REAL 2026 catalogue.

For each target cluster we plan a 10-stop mission with the electric truck and
with an otherwise identical chemical truck, starting 1 Jan 2029 (a plausible
first-flight date; ELSA-M and ADRAS-J2 are 2027-28).
"""
import glob
import json
import time
from pathlib import Path
import numpy as np

from ocmath.catalog import load_tles, load_satcat, load_gcat_mass, attach_metadata
from ocmath.constants import DEG
from ocmath.truck import TruckDesign, ELECTRIC, CHEMICAL, plan_mission

ROOT = Path(__file__).resolve().parents[2]
from ocmath.j2 import set_rate_model
set_rate_model("sgp4")   # real-catalogue mode: SGP4-consistent drift rates
D = ROOT / "data/celestrak_2026-10-16"
pop = load_tles([f for f in sorted(glob.glob(str(D / "*.tle"))) if "dead_sso" not in f])
attach_metadata(pop, load_satcat(D / "satcat.csv"), load_gcat_mass(ROOT / "data/gcat/satcat.tsv"))
clusters = json.loads((ROOT / "results/clusters_2026.json").read_text())
id2idx = {sid: k for k, sid in enumerate(pop.ids)}

START_JD = 2462137.5   # 2029-01-01 00:00 UTC
TARGETS = {
    "B1_SL8_83deg": "SL-8 (Kosmos-3M stage) 83 deg cluster",
    "B2_SL8_74deg_750km": "SL-8 74 deg / ~750 km cluster",
    "A1_Iridium_legacy": "Dead first-generation Iridium",
}

results = {}
for key, cname in TARGETS.items():
    c = next(c for c in clusters if c["name"] == cname)
    pool = [id2idx[i] for i in c["norad_ids"] if i in id2idx]
    for label, prop in (("electric", ELECTRIC), ("chemical", CHEMICAL)):
        truck = TruckDesign(prop=prop)
        t = time.time()
        r = plan_mission(pop, pool, 10, START_JD, truck, lam_ms_per_day=0.5)
        r["secs"] = time.time() - t
        r["targets"] = [{"norad": pop.ids[o], "name": pop.names[o], "alt_km": float(pop.alt_km[o]),
                         "inc_deg": float(pop.i[o] / DEG), "mass_kg": pop.meta["mass_kg"][o]} for o in r["order"]]
        results[f"{key}/{label}"] = r
        print(f"{key:<22} {label:<9} pool {len(pool):>3}  dv {r['total_dv_kms']*1000:6.0f} m/s  "
              f"launch {r['launch_mass_kg']:7.0f} kg  propellant {r['propellant_kg']:6.0f} kg  "
              f"kits {sum(r['kit_masses_kg']):6.0f} kg  {r['duration_days']:5.0f} d  feasible={r['feasible']}  ({r['secs']:.0f}s)")

(ROOT / "results/truck_routes_2026.json").write_text(json.dumps(results, indent=1, default=float))
