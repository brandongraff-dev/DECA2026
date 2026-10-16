"""BENCHMARK 1: does our simple drift-leg model predict JPL's real leg costs?

For each of the 113 legs of JPL's winning GTOC9 solution we feed our model the
SAME start object, end object, departure epoch and transfer time JPL used, and
compare our cheapest dv against the dv JPL actually flew (Table 3 of their paper).

Our model is deliberately simple (circular orbits, secular J2, no phasing), so
we expect it to be in the right ballpark, not identical.  This tells us how much
to trust it -- and in which direction it errs.
"""
import json
from pathlib import Path
import numpy as np

from ocmath.catalog import load_gtoc9, MJD2000_JD
from ocmath.legs import CHEMICAL_GTOC9, DriftBounds
from ocmath.missions import Route, evaluate_route, launch_mass, gtoc9_mission_cost

ROOT = Path(__file__).resolve().parents[2]
pop = load_gtoc9(ROOT / "data/gtoc9/debris.csv")
sol = json.loads((ROOT / "data/gtoc9/jpl_solution.json").read_text())
# GTOC9 rule: pericentre >= 6600 km  -> altitude >= ~222 km.  JPL notes useful drift
# orbits were ~600-900 km; we let the model search 300-1400 km.
bounds = DriftBounds(alt_min_km=300, alt_max_km=1400, di_max_deg=2.0, n_a=45, n_i=17)

rows = []
summary = []
for ms in sol["missions"]:
    idx = [pop.ids.index(d) for d in ms["debris"]]
    route = Route(order=idx, depart_jd=[t + MJD2000_JD for t in ms["departure_mjd2000"][:-1]],
                  transfer_days=ms["transfer_days"])
    evaluate_route(pop, route, CHEMICAL_GTOC9, mass_guess=4000, bounds=bounds)
    ours = np.array(route.leg_dv) * 1000
    jpl = np.array(ms["leg_dv_ms"])
    direct = np.array([d["dv_direct"] for d in route.leg_detail]) * 1000
    for k in range(len(jpl)):
        rows.append((ms["mission"], k + 1, ms["debris"][k], ms["debris"][k + 1], ms["transfer_days"][k],
                     jpl[k], ours[k], direct[k]))
    m0_jpl_check = launch_mass(jpl / 1000, 340.0, 2000.0, 30.0, ms["n_objects"])
    m0_ours = launch_mass(ours / 1000, 340.0, 2000.0, 30.0, ms["n_objects"])
    summary.append({"mission": ms["mission"], "n": ms["n_objects"],
                    "jpl_sum_dv": jpl.sum(), "our_sum_dv": ours.sum(),
                    "jpl_m0_table": ms["launch_mass_kg"], "jpl_m0_rebuilt": m0_jpl_check, "our_m0": m0_ours})

arr = np.array([r[5:] for r in rows])
jpl, ours, direct = arr[:, 0], arr[:, 1], arr[:, 2]
ratio = ours / jpl
print(f"legs: {len(rows)}")
print(f"JPL total dv   : {jpl.sum():9.0f} m/s")
print(f"Our model      : {ours.sum():9.0f} m/s  ({(ours.sum()/jpl.sum()-1)*100:+.1f}%)")
print(f"'Direct' (no drift, go now): {direct.sum():9.0f} m/s  ({direct.sum()/jpl.sum():.1f}x JPL)")
print(f"per-leg ratio ours/JPL: median {np.median(ratio):.2f}, IQR {np.percentile(ratio,25):.2f}-{np.percentile(ratio,75):.2f}")
print(f"correlation (Pearson r) ours vs JPL: {np.corrcoef(ours, jpl)[0,1]:.2f}")
print(f"legs within +/-25%: {np.mean(np.abs(ratio-1) <= 0.25)*100:.0f}%")
print()
print("mission  n   JPL dv   our dv   JPL m0(table)  JPL m0(rebuilt)  our m0")
for s in summary:
    print(f"{s['mission']:>5} {s['n']:>3} {s['jpl_sum_dv']:8.0f} {s['our_sum_dv']:8.0f} {s['jpl_m0_table']:12.1f} {s['jpl_m0_rebuilt']:14.1f} {s['our_m0']:9.1f}")
tot_jpl = sum(gtoc9_mission_cost(s["jpl_m0_table"]) for s in summary)
tot_our = sum(gtoc9_mission_cost(s["our_m0"]) for s in summary)
print(f"\nGTOC9 cost at 55 MEUR base: JPL masses -> {tot_jpl:.1f} MEUR, our-model masses -> {tot_our:.1f} MEUR")

out = ROOT / "results/benchmark_jpl_legs.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps({"bounds": bounds.__dict__, "legs": [
    dict(zip(["mission", "leg", "from", "to", "transfer_days", "jpl_dv_ms", "our_dv_ms", "direct_dv_ms"],
             [int(r[0]), int(r[1]), int(r[2]), int(r[3]), float(r[4]), float(r[5]), float(r[6]), float(r[7])]))
    for r in rows], "missions": summary}, indent=1, default=float))
