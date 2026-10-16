"""Extract JPL's winning GTOC9 solution (Petropoulos et al., Acta Futura 11, 2018,
Tables 1 and 3: the FINAL SUBMITTED solution) from the paper's text into JSON.

Input : data/gtoc9/jpl_gtoc9.txt  (pdftotext -layout of the Zenodo PDF)
Output: data/gtoc9/jpl_solution.json
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
txt = (ROOT / "data/gtoc9/jpl_gtoc9.txt").read_text().splitlines()


def block_after(title, start=0):
    for k in range(start, len(txt)):
        if title in txt[k]:
            return k
    raise ValueError(title)


# --- Table 1: mission overview -------------------------------------------------
k1 = block_after("TABLE 1. Campaign Overview of Final Submitted Solution")
missions = []
k2 = block_after("TABLE 2.", k1)
for line in txt[k1 + 1:k2]:
    m = re.match(r"\s+(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+([\d,]+)", line)
    if m:
        missions.append({
            "mission": int(m.group(1)), "start_mjd2000": float(m.group(2)), "end_mjd2000": float(m.group(3)),
            "launch_mass_kg": float(m.group(4)), "n_objects": int(m.group(5)),
            "debris": [int(x) for x in m.group(6).split(",")],
        })
assert len(missions) == 10, len(missions)

# --- Table 3: per-leg characteristics -------------------------------------------
k3 = block_after("TABLE 3. Mission Characteristics of Final Submitted Solution")
k4 = block_after("TABLE 4.", k3)
section = None
rows = {"rdv": {}, "tof": {}, "dv": {}}
for line in txt[k3:k4]:
    if "Rendezvous Duration" in line:
        section = "rdv"; continue
    if "Transfer Duration" in line:
        section = "tof"; continue
    if "m/s" in line and "Mission" in line:
        section = "dv"; continue
    m = re.match(r"\s+(\d+)\s+([\d.,]+)\s*$", line)
    if section and m:
        rows[section][int(m.group(1))] = [float(x) for x in m.group(2).split(",")]

for ms in missions:
    k = ms["mission"]
    ms["rendezvous_days"] = rows["rdv"][k]
    ms["transfer_days"] = rows["tof"][k]
    ms["leg_dv_ms"] = rows["dv"][k]
    assert len(ms["transfer_days"]) == ms["n_objects"] - 1 == len(ms["leg_dv_ms"]), k
    # reconstruct arrival / departure epochs of every debris visit
    t = ms["start_mjd2000"]
    arrivals, departures = [], []
    for j in range(ms["n_objects"]):
        arrivals.append(t)
        t += ms["rendezvous_days"][j]
        departures.append(t)
        if j < ms["n_objects"] - 1:
            t += ms["transfer_days"][j]
    ms["arrival_mjd2000"] = arrivals
    ms["departure_mjd2000"] = departures

out = {"source": "Petropoulos et al., 'GTOC9: Results from the Jet Propulsion Laboratory (team JPL)', "
                 "Acta Futura 11 (2018) 25-35, doi:10.5281/zenodo.1139152, Tables 1 and 3 (final submitted solution)",
       "total_cost_MEUR_reported": 731.28, "missions": missions}
(ROOT / "data/gtoc9/jpl_solution.json").write_text(json.dumps(out, indent=1))
print("missions:", len(missions), "legs:", sum(m["n_objects"] - 1 for m in missions),
      "objects:", sum(m["n_objects"] for m in missions))
for ms in missions:
    print(ms["mission"], ms["n_objects"], "end check:", round(ms["departure_mjd2000"][-1], 2), "vs", ms["end_mjd2000"])
