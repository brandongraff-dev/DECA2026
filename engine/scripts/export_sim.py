"""Export the optimised routes + the 2026 debris field for the 3D simulation.

Writes sim/data/:
  background.json  compact mean elements for every loaded LEO object (fast analytic animation)
  mission_<key>.json  targets (TLEs for satellite.js SGP4), truck segments, live counters, comparison

Truck path model in the sim (matches the planner, schematic in phasing):
  STAY      truck sits next to target k (SGP4 position of the target)
  SPIRAL    altitude/inclination change A -> drift orbit (electric: slow spiral)
  DRIFT     coast on the drift orbit; its plane twists at a different rate (the 'conveyor belt')
  SPIRAL    drift orbit -> target B's orbit
  RIDE      ride along in B's plane, closing the along-track gap, until the rendezvous
"""
import glob
import json
from pathlib import Path
import numpy as np
from sgp4.api import Satrec

from ocmath.j2 import set_rate_model, raan_rate
from ocmath.catalog import load_tles, load_satcat, load_gcat_mass, attach_metadata
from ocmath.constants import DEG, DAY, R_E, MU
from ocmath.legs import leg_cost
from ocmath.truck import TruckDesign, ELECTRIC, CHEMICAL
from ocmath.missions import launch_mass_kits
from ocmath.transfers import propellant_for_dv
from ocmath.economics import default_params, base_values, mission_cost, REAL_WORLD_ANCHORS

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "sim/data"
OUT.mkdir(parents=True, exist_ok=True)
set_rate_model("sgp4")
D = ROOT / "data/celestrak_2026-10-16"
POP = load_tles([f for f in sorted(glob.glob(str(D / "*.tle"))) if "dead_sso" not in f])
attach_metadata(POP, load_satcat(D / "satcat.csv"), load_gcat_mass(ROOT / "data/gcat/satcat.tsv"))
JD_UNIX0 = 2440587.5


def unix_ms(jd):
    return float((jd - JD_UNIX0) * 86400000.0)


def arg_lat(k, jd):
    """Argument of latitude of object k at jd from SGP4 (for phase continuity)."""
    s = Satrec.twoline2rv(POP.meta["tle1"][k], POP.meta["tle2"][k])
    _, r, v = s.sgp4(np.floor(jd), jd - np.floor(jd))
    r, v = np.array(r), np.array(v)
    h = np.cross(r, v)
    nvec = np.cross([0, 0, 1.0], h)
    u = np.arccos(np.clip(np.dot(nvec, r) / np.linalg.norm(nvec) / np.linalg.norm(r), -1, 1))
    return float(u if r[2] >= 0 else 2 * np.pi - u)


# ------------------------------------------------------------------ background field
typ = np.array(POP.meta["object_type"])
stat = np.array(POP.meta["ops_status"])
active = (typ == "PAY") & np.isin(stat, ["+", "P", "B", "S", "X"])
code = np.where(active, 0, np.where(typ == "DEB", 1, np.where(typ == "R/B", 2, 3)))  # 3 = dead payload / unknown
leo = (POP.alt_km > 150) & (POP.alt_km < 2100) & (POP.e < 0.1)
bg = {"fields": ["a_km", "e", "i_rad", "raan_rad", "argp_rad", "M_rad", "epoch_jd", "type"],
      "type_codes": {"0": "working satellite", "1": "fragment", "2": "rocket body", "3": "dead satellite"},
      "source": "CelesTrak GP data downloaded 16 Oct 2026 (active, debris groups, rocket bodies, operator lists)",
      "rows": [[round(float(POP.a[k]), 3), round(float(POP.e[k]), 6), round(float(POP.i[k]), 6),
                round(float(POP.raan[k]), 6), round(float(POP.argp[k]), 6), round(float(POP.M[k]), 6),
                round(float(POP.epoch_jd[k]), 6), int(code[k])] for k in np.nonzero(leo)[0]]}
(OUT / "background.json").write_text(json.dumps(bg, separators=(",", ":")))
print("background objects:", len(bg["rows"]))


# ------------------------------------------------------------------ one mission
def export_mission(key, route, prop, title, product):
    truck = TruckDesign(prop=prop)
    order = route["order"]
    kits = route["kit_masses_kg"]
    m0, prop_kg, masses = launch_mass_kits([l["dv"] for l in route["legs"]], prop.isp, truck.dry_mass_kg,
                                           kits, truck.dv_reserve_kms)
    econ = mission_cost(route, prop.kind, len(order), base_values(default_params()))
    segs, stops = [], []
    jd_arr = route["start_jd"]
    mass = m0
    cum_dv = cum_prop = 0.0
    for j, k in enumerate(order):
        jd_dep = jd_arr + truck.stay_days
        mass -= kits[j]
        stops.append({"stop": j + 1, "norad": POP.ids[k], "name": POP.names[k], "arrive_ms": unix_ms(jd_arr),
                      "depart_ms": unix_ms(jd_dep), "kit_kg": round(kits[j], 1),
                      "mass_kg": POP.meta["mass_kg"][k], "alt_km": round(float(POP.alt_km[k]), 1),
                      "inc_deg": round(float(POP.i[k] / DEG), 3),
                      "cum_dv_ms": round(cum_dv * 1000, 1), "cum_prop_kg": round(cum_prop, 1)})
        segs.append({"kind": "STAY", "t0": unix_ms(jd_arr), "t1": unix_ms(jd_dep), "target": POP.ids[k]})
        if j == len(order) - 1:
            break
        l = route["legs"][j]
        A, B = k, order[j + 1]
        r = leg_cost(prop, POP.a[A], POP.i[A], POP.raan_at(l["depart_jd"], A), POP.a[[B]], POP.i[[B]],
                     POP.raan_at(l["depart_jd"], [B]), l["T_days"] * DAY, masses[j], truck.bounds,
                     truck.dv_rendezvous_kms)
        g = {q: float(v[0]) for q, v in r.items()}
        t = l["depart_jd"]
        raan = float(POP.raan_at(t, A))
        u = arg_lat(A, t)
        phases = [("SPIRAL", g["t1"] / DAY, POP.a[A], g["a_d"], POP.i[A], g["i_d"]),
                  ("DRIFT", g["t_drift"] / DAY, g["a_d"], g["a_d"], g["i_d"], g["i_d"]),
                  ("SPIRAL", g["t2"] / DAY, g["a_d"], POP.a[B], g["i_d"], POP.i[B])]
        for kind, dur, a0, a1, i0, i1 in phases:
            if dur <= 1e-6:
                continue
            w = 0.5 * (raan_rate(a0, i0) + raan_rate(a1, i1))
            n = 0.5 * (np.sqrt(MU / a0 ** 3) + np.sqrt(MU / a1 ** 3))
            segs.append({"kind": kind, "t0": unix_ms(t), "t1": unix_ms(t + dur), "a0": a0, "a1": a1, "i0": i0, "i1": i1,
                         "raan0": raan, "raan_rate": float(w), "u0": u, "n": float(n)})
            raan += float(w) * dur * DAY
            u = float(np.mod(u + n * dur * DAY, 2 * np.pi))
            t += dur
        jd_next = l["depart_jd"] + l["T_days"]
        segs.append({"kind": "RIDE", "t0": unix_ms(t), "t1": unix_ms(jd_next), "target": POP.ids[B],
                     "a": float(POP.a[B]), "i": float(POP.i[B]), "raan0": raan, "u0": u,
                     "raan_rate": float(raan_rate(POP.a[B], POP.i[B])), "n": float(np.sqrt(MU / POP.a[B] ** 3))})
        cum_dv += l["dv"]
        cum_prop += propellant_for_dv(masses[j], l["dv"], prop.isp)
        jd_arr = jd_next
    singles = mission_cost({"launch_mass_kg": truck.dry_mass_kg + float(np.mean(kits)) + 60.0, "propellant_kg": 60.0,
                            "duration_days": 120.0}, prop.kind, 1, base_values(default_params()))
    mission = {
        "key": key, "title": title, "product": product,
        "truck": {"engine": prop.name, "isp_s": prop.isp, "thrust_N": prop.thrust_N, "dry_mass_kg": truck.dry_mass_kg,
                  "launch_mass_kg": round(m0, 1), "propellant_kg": round(prop_kg, 1), "kits_kg": round(sum(kits), 1)},
        "start_ms": unix_ms(route["start_jd"]), "end_ms": unix_ms(route["end_jd"]),
        "duration_days": round(route["duration_days"], 1), "total_dv_ms": round(route["total_dv_kms"] * 1000, 1),
        "targets": [{"norad": POP.ids[k], "name": POP.names[k], "tle1": POP.meta["tle1"][k], "tle2": POP.meta["tle2"][k]}
                    for k in order],
        "stops": stops, "segments": segs,
        "economics": {"total_musd": round(econ["total"], 2), "per_removal_musd": round(econ["per_removal"], 2),
                      "price_per_removal_musd": round(econ["price_per_removal"], 2),
                      "breakdown_musd": {k: round(v, 2) for k, v in econ["breakdown"].items()},
                      "single_object_per_removal_musd": round(singles["per_removal"], 2),
                      "anchors": [{"name": a["name"], "per_object_musd": round(a["musd"] / a["objects"], 1)}
                                  for a in REAL_WORLD_ANCHORS],
                      "note": "Base-case assumptions; see research/economics_inputs.md and the paper's assumption table."},
    }
    (OUT / f"mission_{key}.json").write_text(json.dumps(mission, indent=1, default=float))
    print(f"{key}: {len(order)} stops, {len(segs)} segments, {route['duration_days']:.0f} d, "
          f"${econ['per_removal']:.1f}M per removal (single-object same model ${singles['per_removal']:.1f}M)")
    return mission


routes = json.loads((ROOT / "results/truck_routes_2026.json").read_text())
export_mission("B1", routes["B1_SL8_83deg/electric"], ELECTRIC, "10 Soviet-era SL-8 rocket stages, one electric truck",
               "Product B: agency rocket-body cleanup")
export_mission("A1", routes["A1_Iridium_legacy/electric"], ELECTRIC, "10 dead first-generation Iridium satellites",
               "Product A: operator constellation sweep")
