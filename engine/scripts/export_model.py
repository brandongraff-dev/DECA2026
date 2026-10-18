"""Write model/data/truck.json: the numbers the 3D truck model is sized from.

Usage: python -m scripts.export_model [ROUTE_KEY] [LAUNCH_KEY]
  default: the flagship route below with its cheapest launch option.
Reads results/truck_routes_2026.json and results/launch_options_2026.json.
"""
import json
import sys
from pathlib import Path
import numpy as np

from ocmath.truck import ELECTRIC

ROOT = Path(__file__).resolve().parents[2]
ROUTE = sys.argv[1] if len(sys.argv) > 1 else "B0_SSO_partner"
routes = json.loads((ROOT / "results/truck_routes_2026.json").read_text())
opts = json.loads((ROOT / "results/launch_options_2026.json").read_text())["options"][f"{ROUTE}/electric"]
LAUNCH = sys.argv[2] if len(sys.argv) > 2 else opts["best"]
r = routes[f"{ROUTE}/electric"]
o = opts[LAUNCH]

# Approximate stage sizes for the 3D model only (public reference values, rounded).
STAGES = {
    "SL-8 R/B": {"name": "SL-8 rocket stage (Kosmos-3M)", "length_m": 6.5, "diameter_m": 2.4},
    "PSLV R/B": {"name": "PSLV fourth stage (India)", "length_m": 3.0, "diameter_m": 2.0},
    "ARIANE 40 R/B": {"name": "Ariane 4 third stage (France)", "length_m": 9.9, "diameter_m": 2.6},
    "ARIANE 40+ R/B": {"name": "Ariane 4 third stage (France)", "length_m": 9.9, "diameter_m": 2.6},
    "DELTA 1 R/B": {"name": "Delta second stage (US)", "length_m": 6.0, "diameter_m": 1.5},
    "THOR AGENA D R/B": {"name": "Agena D upper stage (US, 1960s)", "length_m": 7.1, "diameter_m": 1.5},
    "IRS-P2 R/B": {"name": "PSLV fourth stage (India)", "length_m": 3.0, "diameter_m": 2.0},
    "ARIANE 5 R/B": {"name": "Ariane 5 upper stage (Europe)", "length_m": 4.5, "diameter_m": 5.4},
}
first = r["targets"][0]
st = STAGES.get(first["name"], {"name": first["name"].replace(" R/B", " rocket stage"), "length_m": 5.0, "diameter_m": 2.0})
st = {**st, "mass_kg": float(first["mass_kg"])}

# where the other stops' orbits sit relative to the first (for the faint route rings)
from ocmath.catalog import load_tles  # noqa: E402  (only for RAAN at the start date)
import glob  # noqa: E402
from ocmath.j2 import set_rate_model  # noqa: E402
set_rate_model("sgp4")
pop = load_tles([f for f in sorted(glob.glob(str(ROOT / "data/celestrak_2026-10-16/*.tle"))) if "dead_sso" not in f])
raans = pop.raan_at(r["start_jd"], np.array(r["order"]))
off = [float(np.degrees((x - raans[0] + np.pi) % (2 * np.pi) - np.pi)) for x in raans]

kits = [float(k) for k in r["kit_masses_kg"]]
dry = 600.0
launch_kg = float(o["launch_mass_kg"])
xenon = launch_kg - dry - sum(kits)
ins_dv = float(o.get("insertion_dv_ms", 0.0))
ins_days = float(o.get("insertion_days", 0.0))
ins_xe = float(launch_kg * (1 - np.exp(-ins_dv / (ELECTRIC.isp * 9.80665)))) if ins_dv else 0.0
to_alt = float(first["alt_km"])
to_inc = float(first["inc_deg"])
rideshare = LAUNCH == "rideshare"
LAUNCH_TXT = {
    "rideshare": ("Rideshare to sun-synchronous orbit",
                  "A shared Falcon 9 rideshare from Vandenberg, California drops the truck at about 550 km, "
                  "tilted 97.6° (sun-synchronous). That is the cheap ride; it only goes to this one kind of orbit.",
                  "Shared rideshare launch"),
    "neutron": ("A Rocket Lab Neutron of our own", "A dedicated rocket puts the truck straight into the first stage's orbit.",
                "Dedicated Neutron launch"),
    "falcon9": ("A Falcon 9 of our own", "A dedicated rocket puts the truck straight into the first stage's orbit.",
                "Dedicated Falcon 9 launch"),
}[LAUNCH]
out = {
    "route": {"key": ROUTE, "name": {"B1_SL8_83deg": "SL-8 stages, 83°", "B0_SSO_partner": "Partner-nation stages, sun-sync",
                                     "A1_Iridium_legacy": "Dead Iridium satellites"}.get(ROUTE, ROUTE),
              "stops": len(r["order"]), "days": float(r["duration_days"]),
              "stop_alt_km": [t["alt_km"] for t in r["targets"]], "stop_inc_deg": [t["inc_deg"] for t in r["targets"]],
              "stop_raan_offsets_deg": off},
    "launch": {"key": LAUNCH, "title": LAUNCH_TXT[0], "text": LAUNCH_TXT[1], "short": LAUNCH_TXT[2]},
    "insertion": {"from_alt_km": 550.0 if rideshare else to_alt, "from_inc_deg": 97.6 if rideshare else to_inc,
                  "to_alt_km": to_alt, "to_inc_deg": to_inc, "days": ins_days, "dv_ms": ins_dv, "xenon_kg": ins_xe,
                  "raan_shift_deg": 25.0 if ins_dv > 50 else 5.0},
    "mass": {"dry_kg": dry, "kits_kg": kits, "kits_total_kg": sum(kits), "xenon_kg": xenon, "launch_kg": launch_kg},
    "truck": {"thrusters": "Two Busek BHT-1500-class Hall thrusters: 0.202 N together, Isp 1,710 s, 1.5 kW each",
              "power_kw": 3.5},
    "stage": st,
    "kit": {"perigee_km": 250},
    "cost": {"per_removal_musd": float(o["cost_per_removal_musd"]), "total_days": float(o["duration_days"])},
    "note": ("Concept sized from our model: kit masses from the rocket equation, xenon from the route plus "
             "the climb after launch. Power (≈3.5 kW) and the 600 kg dry mass are assumptions."),
}
dst = ROOT / "model/data/truck.json"
dst.parent.mkdir(parents=True, exist_ok=True)
dst.write_text(json.dumps(out, indent=1))
print(f"wrote {dst.relative_to(ROOT)}: {ROUTE} via {LAUNCH}, launch {launch_kg:.0f} kg, xenon {xenon:.0f} kg, "
      f"kits {sum(kits):.0f} kg, insertion {ins_dv:.0f} m/s / {ins_days:.0f} d")
