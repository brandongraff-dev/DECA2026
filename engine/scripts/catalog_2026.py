"""2026 catalogue snapshot: what is up there, and where the 'truck-friendly' clusters are.

Inputs (downloaded 16 Oct 2026):
  data/celestrak_2026-10-16/*.tle   CelesTrak GP data (active, debris groups, rocket bodies, operators)
  data/celestrak_2026-10-16/satcat.csv  CelesTrak SATCAT (type, status, owner, RCS)
  data/gcat/satcat.tsv              McDowell GCAT (mass)
Outputs:
  results/catalog_2026_summary.json
  results/targets_*.json            candidate pools for Product A and Product B
"""
import glob
import json
from pathlib import Path
import numpy as np

from ocmath.catalog import load_tles, load_satcat, load_gcat_mass, attach_metadata
from ocmath.constants import DEG, R_E
from ocmath.j2 import raan_rate_deg_per_day

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / "data/celestrak_2026-10-16"
pop = load_tles(sorted(glob.glob(str(D / "*.tle"))))
satcat = load_satcat(D / "satcat.csv")
gcat = load_gcat_mass(ROOT / "data/gcat/satcat.tsv")
attach_metadata(pop, satcat, gcat)

alt = pop.alt_km
inc = pop.i / DEG
typ = np.array(pop.meta["object_type"])
status = np.array(pop.meta["ops_status"])
mass = np.array(pop.meta["mass_kg"], float)
leo = (alt > 160) & (alt < 2000) & (pop.e < 0.05)

active = (typ == "PAY") & np.isin(status, ["+", "P", "B", "S", "X"])
dead_pay = (typ == "PAY") & ~active
rb = typ == "R/B"
deb = typ == "DEB"


def stats(mask):
    m = mask & leo
    return {"count": int(m.sum()), "mass_t": float(np.nansum(mass[m]) / 1000), "mass_known": int(np.isfinite(mass[m]).sum())}


summary = {
    "snapshot": "CelesTrak GP, 16 Oct 2026 (subset: active + debris groups + rocket bodies + operator names + dead SSO payloads)",
    "note": "Not the full catalogue: CelesTrak publishes no single 'all objects' GP file; counts are of the files fetched.",
    "objects_loaded": len(pop),
    "leo": {"active_payloads": stats(active), "dead_payloads": stats(dead_pay), "rocket_bodies": stats(rb),
            "fragments": stats(deb)},
}

# ---------------------------------------------------------------- clusters
# A 'truck-friendly' cluster: similar inclination and altitude (cheap hops),
# planes spread around the globe (so J2 drift can bring them to us), heavy.
def cluster(mask, name, inc_lo, inc_hi, alt_lo, alt_hi):
    m = mask & leo & (inc >= inc_lo) & (inc <= inc_hi) & (alt >= alt_lo) & (alt <= alt_hi)
    idx = np.nonzero(m)[0]
    rates = raan_rate_deg_per_day(alt[idx], inc[idx])
    return {"name": name, "count": int(len(idx)), "inc_range": [inc_lo, inc_hi], "alt_range": [alt_lo, alt_hi],
            "median_mass_kg": float(np.nanmedian(mass[idx])) if len(idx) else None,
            "total_mass_t": float(np.nansum(mass[idx]) / 1000),
            "drift_rate_deg_day": [float(rates.min()), float(rates.max())] if len(idx) else None,
            "raan_spread_deg": float(np.ptp(pop.raan[idx] / DEG)) if len(idx) > 1 else 0.0,
            "norad_ids": [int(pop.ids[k]) for k in idx],
            "names": sorted(set(pop.names[k] for k in idx))[:12]}

names = np.array([n.upper() for n in pop.names]).astype(str)
has = lambda token: np.char.find(names, token) >= 0
is_sl16 = rb & has("SL-16")
is_sl8 = rb & has("SL-8")
is_iridium_dead = dead_pay & has("IRIDIUM")
is_globalstar_dead = dead_pay & has("GLOBALSTAR")
is_orbcomm_dead = dead_pay & has("ORBCOMM")

clusters = [
    cluster(is_sl16, "SL-16 (Zenit-2 upper stage) cluster", 70, 72, 780, 900),
    cluster(is_sl8, "SL-8 (Kosmos-3M stage) 83 deg cluster", 82, 84, 900, 1050),
    cluster(is_sl8, "SL-8 74 deg / ~750 km cluster", 73, 75, 700, 820),
    cluster(is_sl8, "SL-8 74 deg / ~1500 km cluster", 73, 75, 1400, 1600),
    cluster(is_iridium_dead, "Dead first-generation Iridium", 85, 88, 500, 900),
    cluster(is_globalstar_dead, "Dead first-generation Globalstar", 50, 54, 600, 1500),
    cluster(is_orbcomm_dead, "Dead Orbcomm", 0, 180, 500, 1000),
    cluster(dead_pay, "Dead payloads, sun-synchronous band", 95, 101, 500, 1000),
    cluster(rb, "Rocket bodies, sun-synchronous band", 95, 101, 500, 1000),
]
summary["clusters"] = [{k: v for k, v in c.items() if k not in ("norad_ids",)} for c in clusters]
out = ROOT / "results"
out.mkdir(exist_ok=True)
(out / "catalog_2026_summary.json").write_text(json.dumps(summary, indent=1))
(out / "clusters_2026.json").write_text(json.dumps(clusters, indent=1))

print(json.dumps(summary["leo"], indent=1))
print(f"\n{'cluster':<42}{'n':>5}{'med kg':>9}{'tot t':>8}{'drift deg/d':>18}{'RAAN spread':>13}")
for c in clusters:
    dr = c["drift_rate_deg_day"]
    print(f"{c['name']:<42}{c['count']:>5}{(c['median_mass_kg'] or 0):>9.0f}{c['total_mass_t']:>8.1f}"
          f"{(f'{dr[0]:+.2f}..{dr[1]:+.2f}' if dr else ''):>18}{c['raan_spread_deg']:>12.0f}°")
