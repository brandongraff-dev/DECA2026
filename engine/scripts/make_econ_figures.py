"""Economics figures (6-9) + the summary numbers used in the paper and deck."""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from ocmath import style
from ocmath.economics import (default_params, base_values, mission_cost, tornado, monte_carlo, REAL_WORLD_ANCHORS,
                              reusable_campaign, thruster_routes_limit)
from ocmath.truck import ELECTRIC, CHEMICAL

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "results"
LABEL = {"B1_SL8_83deg": "SL-8 rocket stages (83°)", "A1_Iridium_legacy": "Product A: dead Iridium satellites",
         "B0_SSO_partner": "First route: partner-nation stages (sun-sync)"}
BASE = "B0_SSO_partner"        # the first route: where a rideshare already goes
LAUNCH_NOTE = "Includes a rideshare launch to sun-synchronous orbit and the truck's own climb to its first stop."
PNAME = {"truck_hw_musd": "Truck hardware cost", "kit_musd": "Deorbit kit unit cost",
         "launch_usd_per_kg": "Launch price per kg", "xenon_usd_per_kg": "Xenon price",
         "chem_prop_usd_per_kg": "Chemical propellant price", "ops_musd_per_year": "Operations cost per year",
         "insurance_frac": "Insurance rate", "dv_margin_frac": "Fuel margin"}


def _out(theme, name):
    d = ROOT / "figures" / theme
    d.mkdir(parents=True, exist_ok=True)
    return str(d / name)


def load():
    return json.loads((RES / "pareto_economics.json").read_text())


def pareto_front(pts):
    """Points not beaten on BOTH duration and cost."""
    pts = sorted(pts, key=lambda p: (p[0], p[1]))
    front, best = [], np.inf
    for p in pts:
        if p[1] < best:
            front.append(p); best = p[1]
    return front


def fig_pareto(theme, data):
    t = style.use(theme)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), sharey=False)
    for ax, ck in zip(axes, [BASE, "B1_SL8_83deg"]):
        for eng, col, lab in (("chemical", t["other"], "Chemical truck"), ("electric", t["truck"], "Electric truck")):
            pts = [(r["duration_days"], r["cost_per_removal_musd"]) for r in data["runs"]
                   if r.get("feasible") and r["cluster"] == ck and r["engine"] == eng and r["n"] == 10]
            if not pts:
                continue
            x, y = zip(*pts)
            ax.scatter(x, y, s=26, color=col, alpha=0.45, linewidths=0)
            f = pareto_front(pts)
            fx, fy = zip(*f)
            ax.plot(fx, fy, color=col, marker="o", ms=5)
            ax.annotate(lab, (fx[-1], fy[-1]), xytext=(6, 0), textcoords="offset points", fontsize=8.5,
                        color=t["text"], va="center")
        ax.set_title(LABEL[ck], fontsize=11)
        ax.set_xlabel("Mission duration, days (10 removals)")
        ax.set_ylabel("Cost per removal, US$ millions")
    fig.suptitle("Fuel is nearly free; time is not. Faster routes are often the cheaper ones", x=0.01, ha="left",
                 fontweight="bold", fontsize=13, color=t["text"])
    fig.text(0.01, -0.03, "Each dot is one optimised 10-stop mission for a different 'price of time'. Lines = Pareto "
             "frontier (no other plan of that engine is both faster and cheaper). Operations cost per year outweighs "
             "the extra propellant of faster routes. Base-case assumptions. " + LAUNCH_NOTE, fontsize=7.5,
             color=t["text2"])
    fig.tight_layout()
    style.save(fig, _out(theme, "06_pareto"))


def fig_scaling(theme, data):
    t = style.use(theme)
    fig, ax = plt.subplots(figsize=(8.6, 5))
    for eng, col, lab in (("chemical", t["other"], "Chemical truck"), ("electric", t["truck"], "Electric truck (ours)")):
        single = next(s for s in data["single_object"] if s["engine"] == eng and s.get("cluster") == BASE)
        pts = sorted([(r["n"], r["cost_per_removal_musd"]) for r in data["runs"]
                      if r.get("feasible") and r["cluster"] == BASE and r["engine"] == eng and r["lam"] == 0.5])
        pts = [(1, single["cost_per_removal_musd"])] + pts
        x, y = zip(*pts)
        ax.plot(x, y, color=col, marker="o", ms=5)
        ax.annotate(f"{lab}: \\${y[-1]:.1f}M", (x[-1], y[-1]), xytext=(6, 0 if eng == "electric" else 10),
                    textcoords="offset points", fontsize=8.5, color=t["text"], va="center")
    for a in REAL_WORLD_ANCHORS:
        per = a["musd"] / a["objects"]
        ax.scatter([1], [per], marker="D", s=30, color=t["muted"], zorder=5)
        ax.annotate(f"{a['name']}  \\${per:.0f}M", (1, per), xytext=(14, 0), textcoords="offset points",
                    fontsize=7.5, color=t["text2"], va="center", zorder=6,
                    bbox=dict(boxstyle="round,pad=0.2", fc=t["surface"], ec="none"))
    ax.set_xlabel("Objects removed by one truck")
    ax.set_ylabel("Cost per removal, US$ millions")
    ax.set_xticks([1, 3, 5, 10, 15, 20])
    ax.set_ylim(0, None)
    ax.set_title("One truck, many stops: the cost per removal collapses")
    fig.text(0.01, -0.03, "Lines: our cost model (base assumptions), first route (partner-nation stages, sun-synchronous "
             "band), real 2026 orbits. " + LAUNCH_NOTE + " Diamonds: public contract values for real single-object "
             "missions (total / objects).", fontsize=7.5, color=t["text2"], wrap=True)
    style.save(fig, _out(theme, "07_scaling"))


def fig_tornado(theme, route):
    t = style.use(theme)
    params = default_params()
    ref, rows = tornado(route, "electric", 10, params)
    rows = [r for r in rows if r["swing"] > 1e-3]
    fig, ax = plt.subplots(figsize=(8.4, 4.6))
    for k, r in enumerate(reversed(rows)):
        lo, hi = r["low"] - ref, r["high"] - ref
        ax.barh(k, lo, color=t["other"], height=0.6)
        ax.barh(k, hi, color=t["truck"], height=0.6)
        ax.text(min(lo, hi) - 0.15, k, PNAME.get(r["param"], r["param"]), ha="right", va="center", fontsize=9,
                color=t["text"])
    ax.axvline(0, color=t["text2"], lw=1)
    ax.set_yticks([])
    ax.set_xlabel(f"Change in cost per removal vs base case (\\${ref:.1f}M), US\\$ millions")
    ax.set_title("What moves the price? (first route, 10 stops, launch included)")
    lo_patch = plt.Rectangle((0, 0), 1, 1, color=t["other"])
    hi_patch = plt.Rectangle((0, 0), 1, 1, color=t["truck"])
    ax.legend([lo_patch, hi_patch], ["Low value of parameter", "High value of parameter"], loc="lower right",
              fontsize=8.5)
    xmin = min(min(r["low"], r["high"]) for r in rows) - ref
    ax.set_xlim(xmin * 1.9, max(max(r["low"], r["high"]) for r in rows) - ref + 0.5)
    style.save(fig, _out(theme, "08_tornado"))
    return ref, rows


def fig_breakdown(theme, data, route_run):
    t = style.use(theme)
    single = next(s for s in data["single_object"] if s["engine"] == "electric" and s.get("cluster") == BASE)
    cats = ["truck_hardware", "kits", "launch", "propellant", "operations", "insurance"]
    names = ["Truck", "Kits", "Launch", "Propellant", "Operations", "Insurance"]
    per_single = [single["breakdown"][c] / 1 for c in cats]
    per_truck = [route_run["breakdown"][c] / 10 for c in cats]
    fig, ax = plt.subplots(figsize=(8.4, 4.4))
    for row, (vals, lab) in enumerate([(per_truck, "Orbital Curbside truck\n(10 stops)"),
                                       (per_single, "One mission per object\n(same model)")]):
        left = 0
        for k, v in enumerate(vals):
            col = t["truck"] if k == 0 else (t["other"] if k == 2 else t["muted"])
            ax.barh(row, v, left=left, color=col, height=0.55, edgecolor=t["surface"], linewidth=2)
            if v > 7.5:
                ax.text(left + v / 2, row, f"{names[k]}\n\\${v:.1f}M", ha="center", va="center", fontsize=8,
                        color="#ffffff" if k in (0, 2) else t["text"])
            left += v
        ax.text(left + 1, row, f"\\${left:.1f}M", va="center", fontsize=10, fontweight="bold", color=t["text"])
    ax.set_yticks([0, 1])
    ax.set_yticklabels(["Orbital Curbside truck\n(10 stops)", "One mission per object\n(same model)"])
    ax.set_xlabel("Cost per removal, US$ millions (base assumptions)")
    ax.set_title("Where the money goes, per object removed")
    ax.text(0.99, -0.2, "Orange = truck hardware, blue = launch, grey = kits, propellant, operations, insurance",
            transform=ax.transAxes, ha="right", fontsize=7.5, color=t["text2"])
    ax.grid(axis="y", visible=False)
    style.save(fig, _out(theme, "09_breakdown"))


def base_route(key=BASE, eng="electric"):
    """A route priced the way it would really fly: rideshare launch + climb + the 10 stops."""
    lo = json.loads((RES / "launch_options_2026.json").read_text())["options"][f"{key}/{eng}"]
    b = lo[lo["best"]]
    r = json.loads((RES / "truck_routes_2026.json").read_text())[f"{key}/{eng}"]
    c = mission_cost(b, eng, len(r["order"]), base_values(default_params()))
    return {"duration_days": b["duration_days"], "launch_mass_kg": b["launch_mass_kg"],
            "propellant_kg": b["propellant_kg"], "kits_kg": sum(r["kit_masses_kg"]), "dv_kms": r["total_dv_kms"],
            "launch_fixed_musd": b.get("launch_fixed_musd"), "insertion_days": b["insertion_days"],
            "insertion_dv_ms": b["insertion_dv_ms"], "route_days": r["duration_days"],
            "cost_total_musd": c["total"], "cost_per_removal_musd": c["per_removal"], "breakdown": c["breakdown"],
            "n": len(r["order"])}


def reuse_curve(key, eng, n_routes, v):
    """Cost per removal after k routes, k = 1..n_routes. The climb after launch is flown once."""
    r0 = json.loads((RES / "truck_routes_2026.json").read_text())[f"{key}/{eng}"]
    r0 = {**r0, "kits_kg": sum(r0["kit_masses_kg"])}
    lo = json.loads((RES / "launch_options_2026.json").read_text())["options"][f"{key}/{eng}"]
    b = lo[lo["best"]]
    dm = b["launch_mass_kg"] - r0["launch_mass_kg"]
    extra = dm * v["launch_usd_per_kg"] / 1e6 * (1 + v["insurance_frac"]) + v["ops_musd_per_year"] * b["insertion_days"] / 365.25
    out = []
    for k in range(1, n_routes + 1):
        c = reusable_campaign(r0, eng, 10, k, v)
        c["total"] += extra
        c["per_removal"] = c["total"] / c["removals"]
        c["years"] += b["insertion_days"] / 365.25
        c["first_launch_kg"] += dm
        out.append(c)
    return r0, out


def fig_reuse(theme, data):
    """One long-lived truck flying many 10-stop routes on the first route, restocked by kit pods.

    Pods ride later rideshares to sun-synchronous orbit, where this truck works, so this only
    applies to the first route. The electric truck is stopped at its thrusters' rated life.
    """
    t = style.use(theme)
    v = base_values(default_params())
    fig, ax = plt.subplots(figsize=(8.6, 4.8))
    out = {}
    for eng, col, lab, prop in (("chemical", t["other"], "Chemical truck (needs propellant resupply)", CHEMICAL),
                                ("electric", t["truck"], "Electric truck (one xenon load)", ELECTRIC)):
        r0, camp = reuse_curve(BASE, eng, 10, v)
        limit = thruster_routes_limit(r0, prop.isp) if eng == "electric" else None
        n_ok = int(np.floor(limit)) if limit else 10
        ks = np.arange(1, n_ok + 1)
        per = [c["per_removal"] for c in camp[:n_ok]]
        ax.plot(ks * 10, per, color=col, marker="o", ms=4)
        ax.annotate(f"{lab}: \\${per[-1]:.1f}M", (ks[-1] * 10, per[-1]), xytext=(6, 10 if eng == "chemical" else -12),
                    textcoords="offset points", fontsize=8.5, color=t["text"], va="center")
        if limit:
            ax.axvline(limit * 10, color=col, ls=":", lw=1)
            ax.annotate("thruster rated life", (limit * 10, ax.get_ylim()[1] * 0.0 + per[0] * 0.9), xytext=(4, 0),
                        textcoords="offset points", fontsize=7.5, color=t["text2"], rotation=90, va="top")
        out[eng] = {"route_days": r0["duration_days"], "per_removal_by_routes": [c["per_removal"] for c in camp],
                    "campaign_10_routes": camp[-1], "campaign_at_limit": camp[n_ok - 1], "routes_at_limit": n_ok,
                    "thruster_route_limit": limit}
    ax.set_xlabel("Objects removed by one truck over its working life")
    ax.set_ylabel("Cost per removal, US$ millions")
    ax.set_ylim(0, None)
    ax.set_xlim(0, 110)
    ax.set_title("Keep the truck, ship new kits: cost per removal keeps falling")
    fig.text(0.01, -0.03, "First route (sun-synchronous band). After route 1, only kit pods are launched, on later "
             "rideshares that already go to this orbit. Pod carrier mass and price: [ASSUMPTIONS]. The electric line stops "
             "where its thrusters reach their rated total impulse.", fontsize=7.5, color=t["text2"], wrap=True)
    style.save(fig, _out(theme, "10_reuse"))
    return out


def make_all(theme):
    data = load()
    base = base_route()
    # make the scaling curve's 10-stop point the simulated route itself
    for r in data["runs"]:
        if r.get("feasible") and r["cluster"] == BASE and r["engine"] == "electric" and r["n"] == 10 and r["lam"] == 0.5:
            r.update(base)
    fig_pareto(theme, data)
    fig_scaling(theme, data)
    reuse = fig_reuse(theme, data)
    ref, rows = fig_tornado(theme, base)
    fig_breakdown(theme, data, base)
    if theme == "paper":
        params = default_params()
        summary = {"base_key": BASE,
                   "base_route": {k: base[k] for k in ("duration_days", "launch_mass_kg", "propellant_kg", "kits_kg",
                                                       "insertion_days", "insertion_dv_ms", "route_days")},
                   "routes_with_launch": {k: base_route(k) for k in (BASE, "B1_SL8_83deg", "A1_Iridium_legacy")},
                   "base_cost_per_removal_musd": ref,
                   "base_price_per_removal_musd": mission_cost(base, "electric", 10, base_values(params))["price_per_removal"],
                   "monte_carlo_cost_per_removal": monte_carlo(base, "electric", 10, params),
                   "single_object_model": data["single_object"],
                   "tornado": rows,
                   "anchors": REAL_WORLD_ANCHORS, "reuse": reuse}
        (RES / "economics_summary.json").write_text(json.dumps(summary, indent=1, default=float))
        print(json.dumps({k: summary[k] for k in ("base_cost_per_removal_musd", "base_price_per_removal_musd",
                                                  "monte_carlo_cost_per_removal")}, indent=1))
        for eng, rr in reuse.items():
            cmp = rr["campaign_at_limit"]
            print(f"reuse {eng}: route {rr['route_days']:.0f} d, {rr['routes_at_limit']} routes -> ${cmp['per_removal']:.2f}M/removal over "
                  f"{cmp['years']:.1f} y; first launch {cmp['first_launch_kg']:.0f} kg, pod {cmp['pod_kg']:.0f} kg, "
                  f"thruster limit {rr['thruster_route_limit']}")
