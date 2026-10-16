"""All figures for the paper (light) and the deck (navy).  Run after the analyses.

    python -m scripts.make_figures            # everything available
Outputs: figures/paper/*.png|svg and figures/deck/*.png|svg
"""
import glob
import json
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from ocmath import style
from ocmath.j2 import set_rate_model, raan_rate_deg_per_day, raan_rate
from ocmath.catalog import load_tles, load_satcat, load_gcat_mass, attach_metadata
from ocmath.constants import DEG, DAY, R_E
from ocmath.legs import leg_cost
from ocmath.truck import TruckDesign, ELECTRIC, CHEMICAL

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "results"
set_rate_model("sgp4")
D = ROOT / "data/celestrak_2026-10-16"
POP = load_tles([f for f in sorted(glob.glob(str(D / "*.tle"))) if "dead_sso" not in f])
attach_metadata(POP, load_satcat(D / "satcat.csv"), load_gcat_mass(ROOT / "data/gcat/satcat.tsv"))
ID2 = {s: k for k, s in enumerate(POP.ids)}


def out(theme, name):
    d = ROOT / "figures" / theme
    d.mkdir(parents=True, exist_ok=True)
    return d / name


# ------------------------------------------------------------------ 1. the problem
def fig_population(theme):
    t = style.use(theme)
    alt, inc = POP.alt_km, POP.i / DEG
    typ = np.array(POP.meta["object_type"])
    stat = np.array(POP.meta["ops_status"])
    leo = (alt > 200) & (alt < 2000) & (POP.e < 0.05)
    active = (typ == "PAY") & np.isin(stat, ["+", "P", "B", "S", "X"])
    frag = typ == "DEB"
    derelict = ((typ == "PAY") & ~active) | (typ == "R/B")
    fig, ax = plt.subplots(figsize=(9, 5.2))
    ax.scatter(inc[leo & active], alt[leo & active], s=2, color=t["muted"], alpha=0.35, linewidths=0,
               label=f"Working satellites ({(leo & active).sum():,})")
    ax.scatter(inc[leo & frag], alt[leo & frag], s=4, color=t["other"], alpha=0.7, linewidths=0,
               label=f"Collision fragments in these sets ({(leo & frag).sum():,})")
    ax.scatter(inc[leo & derelict], alt[leo & derelict], s=10, color=t["truck"], alpha=0.9, linewidths=0,
               label=f"Dead satellites + rocket stages ({(leo & derelict).sum():,}): our targets")
    for x, y, txt, off in [(71, 845, "SL-16 cluster\n(9-tonne stages)", (-95, 70)),
                           (83, 965, "SL-8 cluster\n142 stages", (-20, 95)),
                           (86.4, 770, "Dead Iridium", (25, -70)),
                           (98.5, 1150, "Sun-synchronous\nband", (10, 60))]:
        ax.annotate(txt, (x, y), xytext=off, textcoords="offset points", fontsize=8.5, color=t["text"],
                    arrowprops=dict(arrowstyle="-", color=t["text2"], lw=0.7))
    ax.set_xlabel("Inclination (tilt of the orbit), degrees")
    ax.set_ylabel("Altitude, km")
    ax.set_xlim(0, 110)
    ax.set_ylim(250, 2000)
    ax.set_title("Low Earth orbit, 16 Oct 2026: the junk lives in tight clusters")
    ax.legend(loc="upper left", markerscale=3, fontsize=8.5)
    fig.text(0.01, -0.02, "Data: CelesTrak GP + SATCAT (16 Oct 2026); only the groups downloaded are shown "
             "(active, 4 debris clouds, all rocket bodies, operator lists).", fontsize=7.5, color=t["text2"])
    style.save(fig, out(theme, "01_population").with_suffix(""))


# ------------------------------------------------------------------ 2. conveyor belt speeds
def fig_drift_rates(theme):
    t = style.use(theme)
    h = np.linspace(400, 1500, 200)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    incs = [(50, "50°"), (71, "71° (SL-16)"), (83, "83° (SL-8)"), (86.4, "86.4° (Iridium)"), (98, "98° (sun-sync)")]
    for (inc, lab), col in zip(incs, t["ramp"]):
        r = raan_rate_deg_per_day(h, inc)
        ax.plot(h, r, color=col)
        ax.text(h[-1] + 15, r[-1], lab, color=t["text"], fontsize=8.5, va="center")
    ax.axhline(0, color=t["muted"], lw=0.8)
    ax.set_xlim(400, 1750)
    ax.set_xlabel("Altitude, km")
    ax.set_ylabel("Plane drift, degrees per day")
    ax.set_title("Earth's bulge twists every orbit; how fast depends on height and tilt")
    fig.text(0.01, -0.03, "dRAAN/dt = -(3/2) n J2 (R_E/p)^2 cos i  (+ SGP4 higher-order correction).  "
             "Negative = plane drifts westward.", fontsize=7.5, color=t["text2"])
    style.save(fig, out(theme, "02_drift_rates").with_suffix(""))


# ------------------------------------------------------------------ 3. wait vs burn on one real leg
def fig_wait_vs_burn(theme):
    t = style.use(theme)
    clusters = json.loads((RES / "clusters_2026.json").read_text())
    c = next(c for c in clusters if c["name"].startswith("SL-8 (Kosmos-3M stage) 83"))
    idx = [ID2[i] for i in c["norad_ids"]]
    jd = 2462137.5
    raans = np.array([POP.raan_at(jd, k) for k in idx])
    A = idx[0]
    gaps = np.mod(raans - raans[0] + np.pi, 2 * np.pi) - np.pi
    B = idx[int(np.argmin(np.abs(np.abs(gaps) - 20 * DEG)))]   # a neighbour ~20 deg away in plane
    gap_deg = float(np.degrees(np.mod(POP.raan_at(jd, B) - POP.raan_at(jd, A) + np.pi, 2 * np.pi) - np.pi))
    days = np.array([5, 10, 20, 30, 45, 60, 90, 120, 150, 180, 240, 300, 365])
    fig, ax = plt.subplots(figsize=(8, 4.8))
    M0 = 2000.0   # a 2-tonne truck
    from ocmath.transfers import propellant_for_dv
    for prop, col, lab in ((CHEMICAL, t["other"], "Chemical truck"), (ELECTRIC, t["truck"], "Electric truck (ours)")):
        tr = TruckDesign(prop=prop)
        kg = []
        for d in days:
            r = leg_cost(prop, POP.a[A], POP.i[A], POP.raan_at(jd, A), POP.a[[B]], POP.i[[B]],
                         POP.raan_at(jd, [B]), d * DAY, M0, tr.bounds, 0.0)
            kg.append(propellant_for_dv(M0, r["dv"][0], prop.isp) if np.isfinite(r["dv"][0]) else np.nan)
        kg = np.array(kg)
        ok = np.isfinite(kg)
        ax.plot(days[ok], kg[ok], color=col, marker="o", ms=4)
        ax.text(days[ok][-1] + 6, kg[ok][-1], lab, color=t["text"], fontsize=9, va="center")
        if prop.kind == "electric":
            ax.annotate("electric needs\n>= 90 days per hop", (days[ok][0], kg[ok][0]), xytext=(-10, 40),
                        textcoords="offset points", fontsize=8, color=t["text2"], ha="right",
                        arrowprops=dict(arrowstyle="-", color=t["text2"], lw=0.7))
    v = np.sqrt(398600.4418 / POP.a[A])
    brute_dv = 2 * v * np.sin(abs(gap_deg) * DEG / 2)
    brute = propellant_for_dv(M0, brute_dv, CHEMICAL.isp)
    ax.axhline(brute, color=t["muted"], lw=1.2, ls="--")
    ax.text(8, brute * 1.08, f"Brute-force plane change now (chemical): {brute:,.0f} kg of {M0:,.0f} kg truck",
            color=t["text2"], fontsize=8.5)
    ax.set_yscale("log")
    ax.set_xlabel("Days the truck is allowed to take")
    ax.set_ylabel("Propellant burned, kg (2-tonne truck), log scale")
    ax.set_title(f"Trade time for fuel: hopping between two SL-8 stages {abs(gap_deg):.0f}° apart")
    ax.set_xlim(0, 420)
    fig.text(0.01, -0.03, f"Real objects: NORAD {POP.ids[A]} -> {POP.ids[B]}, departing 1 Jan 2029. Electric uses more "
             "delta-v (slow spirals) but ~5x less propellant (Isp 1710 s vs 320 s).", fontsize=7.5, color=t["text2"])
    style.save(fig, out(theme, "03_wait_vs_burn").with_suffix(""))


# ------------------------------------------------------------------ 4. benchmark vs JPL
def fig_benchmark(theme):
    t = style.use(theme)
    b = json.loads((RES / "benchmark_jpl_legs.json").read_text())
    jpl = np.array([l["jpl_dv_ms"] for l in b["legs"]])
    ours = np.array([l["our_dv_ms"] for l in b["legs"]])
    fig, ax = plt.subplots(figsize=(5.6, 5.2))
    m = max(jpl.max(), ours.max()) * 1.05
    ax.plot([0, m], [0, m], color=t["muted"], lw=1)
    ax.scatter(jpl, ours, s=22, color=t["truck"], alpha=0.85, edgecolor=t["surface"], linewidth=0.6)
    r = np.corrcoef(jpl, ours)[0, 1]
    ax.text(0.04, 0.95, f"113 legs   r = {r:.2f}\nTotal: ours {ours.sum()/1000:.1f} km/s vs JPL {jpl.sum()/1000:.1f} km/s",
            transform=ax.transAxes, va="top", fontsize=9, color=t["text"])
    ax.set_xlabel("JPL's flown leg cost (GTOC9 winner), m/s")
    ax.set_ylabel("Our model's leg cost, m/s")
    ax.set_title("Our physics vs the 2017 world champions")
    ax.set_xlim(0, m)
    ax.set_ylim(0, m)
    style.save(fig, out(theme, "04_benchmark_jpl").with_suffix(""))


# ------------------------------------------------------------------ 5. the subway map
def fig_route_map(theme, key="B1_SL8_83deg/electric"):
    t = style.use(theme)
    routes = json.loads((RES / "truck_routes_2026.json").read_text())
    r = routes[key]
    order = r["order"]
    jd0 = r["start_jd"]
    days = np.linspace(0, r["duration_days"], 400)
    ref = POP.raan_at(jd0, order[0])
    rate0 = raan_rate(POP.a[order[0]], POP.i[order[0]])
    fig, ax = plt.subplots(figsize=(9, 5.2))
    # plot every object's plane RELATIVE to the first target's plane (a 'conveyor belt' frame)
    rel = lambda k, d: np.degrees(np.mod(POP.raan_at(jd0 + d, k) - (ref + rate0 * d * DAY) + np.pi, 2 * np.pi) - np.pi)
    for k in order:
        y = rel(k, days)
        y = np.where(np.abs(np.diff(y, prepend=y[0])) > 180, np.nan, y)
        ax.plot(days, y, color=t["muted"], lw=1.0)
    # truck path: at each stop it sits on the target's plane
    xs, ys = [], []
    jd = jd0
    stops = [(r["start_jd"], order[0])] + [(l["depart_jd"] + l["T_days"], l["to"]) for l in r["legs"]]
    for j, (jd_arr, k) in enumerate(stops):
        d_arr = jd_arr - jd0
        d_dep = d_arr + 10.0
        xs += [d_arr, d_dep]
        ys += [float(rel(k, np.array([d_arr]))[0]), float(rel(k, np.array([d_dep]))[0])]
        ax.scatter([d_arr], [ys[-2]], s=36, color=t["truck"], zorder=5, edgecolor=t["surface"], linewidth=1)
        ax.annotate(str(j + 1), (d_arr, ys[-2]), xytext=(0, 9), textcoords="offset points",
                    color=t["text"], fontsize=8.5, ha="center", fontweight="bold")
    ax.plot(xs, ys, color=t["truck"], lw=2.2, zorder=4)
    ax.set_xlabel("Mission day")
    ax.set_ylabel("Plane position relative to stop 1, degrees")
    ax.set_title("The truck rides the conveyor belt: 10 SL-8 stages, one electric truck")
    fig.text(0.01, -0.03, "Grey: each target's orbital plane drifting under J2. Orange: the truck's plane, hopping from "
             "target to target. Real 2026 TLEs, launch 1 Jan 2029.", fontsize=7.5, color=t["text2"])
    style.save(fig, out(theme, "05_route_map").with_suffix(""))


if __name__ == "__main__":
    which = sys.argv[1:] or ["population", "drift", "wait", "bench", "route", "econ"]
    for theme in ("paper", "deck"):
        if "population" in which: fig_population(theme)
        if "drift" in which: fig_drift_rates(theme)
        if "wait" in which: fig_wait_vs_burn(theme)
        if "bench" in which: fig_benchmark(theme)
        if "route" in which: fig_route_map(theme)
        if "econ" in which and (RES / "pareto_economics.json").exists():
            from scripts.make_econ_figures import make_all
            make_all(theme)
    print("figures written")
