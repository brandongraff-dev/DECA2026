"""Fill paper_template.html with numbers from results/*.json and render the PDF.

    python paper/build_paper.py
Every number in the paper comes from the analysis outputs, so the paper, the deck
and the simulation cannot disagree.  Unfilled placeholders abort the build.
"""
import json
import math
import re
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
J = lambda name: json.loads((RES / name).read_text())

AUTHOR, SCHOOL, DATE = "Brandon Graff", "[__School__]", "October 2026"

bench = J("benchmark_jpl_legs.json")
m10 = J("benchmark_mission10.json")
routes = J("truck_routes_2026.json")
val = J("validation_sgp4.json")
econ = J("economics_summary.json")
pareto = J("pareto_economics.json")
clusters = J("clusters_2026.json")
launch = J("launch_options_2026.json")

f0 = lambda x: f"{x:,.0f}"
f1 = lambda x: f"{x:,.1f}"
f2 = lambda x: f"{x:,.2f}"

legs = bench["legs"]
jpl = np.array([l["jpl_dv_ms"] for l in legs]); ours = np.array([l["our_dv_ms"] for l in legs])
direct = np.array([l["direct_dv_ms"] for l in legs])
b1 = routes["B1_SL8_83deg/electric"]; b1c = routes["B1_SL8_83deg/chemical"]
v = {}
v["AUTHOR"], v["SCHOOL"], v["DATE"] = AUTHOR, SCHOOL, DATE
v["BENCH_PCT"] = f1(abs(ours.sum() / jpl.sum() - 1) * 100)
v["BENCH_SIGNED"] = f"{(ours.sum() / jpl.sum() - 1) * 100:+.1f}"
v["BENCH_R"] = f2(np.corrcoef(ours, jpl)[0, 1])
v["BENCH_OURS"] = f1(ours.sum() / 1000); v["BENCH_JPL"] = f1(jpl.sum() / 1000)
v["BENCH_WITHIN"] = f0(np.mean(np.abs(ours / jpl - 1) <= 0.25) * 100)
v["BENCH_DIRECT"] = f1(direct.sum() / jpl.sum())
v["B1_N"] = str(len(b1["order"]))
v["B1_DAYS"] = f0(b1["duration_days"]); v["B1_MONTHS"] = f0(b1["duration_days"] / 30.44)
v["B1_DV"] = f0(b1["total_dv_kms"] * 1000); v["B1_PROP"] = f0(b1["propellant_kg"])
v["B1_KITS"] = f0(sum(b1["kit_masses_kg"]))
v["MASS_SAVING"] = f0((1 - b1["launch_mass_kg"] / b1c["launch_mass_kg"]) * 100)
v["LAM_E"] = f0(b1.get("lam_ms_per_day", float("nan"))); v["LAM_C"] = f1(b1c.get("lam_ms_per_day", float("nan")))
# headline = the first route (B0), priced with its rideshare launch and climb
b0 = routes["B0_SSO_partner/electric"]
lo_b0 = launch["options"]["B0_SSO_partner/electric"]; best_b0 = lo_b0[lo_b0["best"]]
lo_b1 = launch["options"]["B1_SL8_83deg/electric"]; best_b1 = lo_b1[lo_b1["best"]]
lo_a1 = launch["options"]["A1_Iridium_legacy/electric"]; best_a1 = lo_a1[lo_a1["best"]]
v["B0_N"] = str(len(b0["order"])); v["B0_POOL"] = str(len(launch["b0_pool"]))
v["B0_DAYS"] = f0(b0["duration_days"]); v["B0_TOTAL_DAYS"] = f0(best_b0["duration_days"])
v["B0_MONTHS"] = f0(best_b0["duration_days"] / 30.44)
v["B0_DV"] = f0(b0["total_dv_kms"] * 1000); v["B0_KITS"] = f0(sum(b0["kit_masses_kg"]))
v["B0_PROP"] = f0(best_b0["propellant_kg"]); v["B0_LAUNCH_KG"] = f0(best_b0["launch_mass_kg"])
v["B0_CLIMB_DAYS"] = f0(best_b0["insertion_days"]); v["B0_CLIMB_DV"] = f0(best_b0["insertion_dv_ms"])
v["HEAD_CPR"] = f1(econ["base_cost_per_removal_musd"]); v["HEAD_PRICE"] = f1(econ["base_price_per_removal_musd"])
v["HEAD_TOTAL"] = f0(econ["base_cost_per_removal_musd"] * len(b0["order"]))
v["B1_CPR_NOLAUNCH"] = f1(lo_b1["no_launch_leg"]["cost_per_removal_musd"])
v["B1_CPR"] = f1(best_b1["cost_per_removal_musd"]); v["B1_TOTAL_DAYS"] = f0(best_b1["duration_days"])
v["B1_CLIMB_DAYS"] = f0(best_b1["insertion_days"]); v["B1_CLIMB_DV"] = f0(best_b1["insertion_dv_ms"])
v["B1_LAUNCH_KG"] = f0(best_b1["launch_mass_kg"])
v["A1_CPR"] = f1(best_a1["cost_per_removal_musd"])
v["NEUTRON_B1"] = f1(lo_b1["neutron"]["cost_per_removal_musd"]); v["F9_B1"] = f1(lo_b1["falcon9"]["cost_per_removal_musd"])
lo_b1c = launch["options"]["B1_SL8_83deg/chemical"]
v["B1C_LAUNCH_KG"] = f0(lo_b1c["rideshare"]["launch_mass_kg"]); v["B1C_CPR"] = f1(lo_b1c["rideshare"]["cost_per_removal_musd"])
single = next(s for s in econ["single_object_model"] if s["engine"] == "electric" and s.get("cluster") == "B0_SSO_partner")
v["SINGLE_CPR"] = f0(single["cost_per_removal_musd"])
v["MC_P10"] = f1(econ["monte_carlo_cost_per_removal"]["p10"]); v["MC_P90"] = f1(econ["monte_carlo_cost_per_removal"]["p90"])
re_e, re_c = econ["reuse"]["electric"], econ["reuse"]["chemical"]
nr = re_e["routes_at_limit"]                         # electric truck stops at its thrusters' rated life
v["REUSE_ROUTES"] = str(nr); v["REUSE_OBJECTS"] = str(10 * nr)
v["REUSE_CPR"] = f1(re_e["campaign_at_limit"]["per_removal"])
v["REUSE_CPR_CHEM"] = f1(re_c["per_removal_by_routes"][nr - 1])
v["REUSE_YEARS"] = f0(re_e["campaign_at_limit"]["years"])
v["THRUSTER_LIMIT"] = f1(re_e["thruster_route_limit"])
v["REUSE_ELEC_PROP"] = f"{round(re_e['campaign_at_limit']['propellant_total_kg'], -1):,.0f}"
tor = {r["param"]: r for r in econ["tornado"]}
v["TOR_HW_LO"] = f1(tor["truck_hw_musd"]["low"]); v["TOR_HW_HI"] = f1(tor["truck_hw_musd"]["high"])
for n in (3, 5, 15, 20):
    r = next(r for r in pareto["runs"] if r.get("feasible") and r["cluster"] == "B0_SSO_partner"
             and r["engine"] == "electric" and r["n"] == n and r["lam"] == 0.5)
    v[f"N{n}"] = f1(r["cost_per_removal_musd"])
vb1 = [x["target_plane_err_deg"] for x in val["B1_SL8_83deg/electric"] if "target_plane_err_deg" in x]
v["VAL_B1"] = f2(np.median(vb1))
vb1c = [x["correction_dv_ms"] for x in val["B1_SL8_83deg/chemical"] if "correction_dv_ms" in x]
v["VAL_B1_DV"] = f1(np.median(vb1c))
vb0 = [x["target_plane_err_deg"] for x in val["B0_SSO_partner/electric"] if "target_plane_err_deg" in x]
v["VAL_B0"] = f2(np.median(vb0)); v["VAL_B0_MAX"] = f1(np.max(vb0))
vb0c = [x["correction_dv_ms"] for x in val["B0_SSO_partner/chemical"] if "correction_dv_ms" in x]
v["VAL_B0_DV"] = f1(np.median(vb0c)); v["VAL_B0_DV_MAX"] = f0(np.max(vb0c))

# ---------------------------------------------------------------- tables
def table(head, rows, cap, num_cols=()):
    th = "".join(f'<th class="{"n" if k in num_cols else ""}">{h}</th>' for k, h in enumerate(head))
    tr = "".join("<tr>" + "".join(f'<td class="{"n" if k in num_cols else ""}">{c}</td>' for k, c in enumerate(r)) + "</tr>"
                 for r in rows)
    return f"<table><tr>{th}</tr>{tr}</table><p class=\"cap\">{cap}</p>"

keep = ["SL-16 (Zenit-2 upper stage) cluster", "SL-8 (Kosmos-3M stage) 83 deg cluster", "SL-8 74 deg / ~750 km cluster",
        "SL-8 74 deg / ~1500 km cluster", "Dead first-generation Iridium", "Rocket bodies, sun-synchronous band"]
crow = []
for c in clusters:
    if c["name"] in keep:
        dr = c["drift_rate_deg_day"]
        crow.append([c["name"], f0(c["count"]), f0(c["median_mass_kg"] or 0), f1(c["total_mass_t"]),
                     f"{dr[0]:+.2f} to {dr[1]:+.2f}", f0(c["raan_spread_deg"]) + "°"])
v["CLUSTER_TABLE"] = table(["Cluster (16 Oct 2026)", "Objects", "Median kg", "Total t", "Drift °/day", "Planes span"],
                           crow, "<b>Table 1.</b> Candidate clusters. Drift rates from the SGP4-consistent model.", (1, 2, 3, 4, 5))

mrow = []
for r in m10:
    mrow.append([r["method"], f0(r["dv_ms"]), f1(r["m0"])])
v["M10_TABLE"] = table(["GTOC9 Mission 10 (10 objects; all scored by our model)", "Total Δv, m/s", "Launch mass, kg"], mrow,
                       f"<b>Table 2.</b> Optimisers on GTOC9 Mission 10. JPL's actual flown launch mass: "
                       f"{m10[0].get('m0_jpl_actual', 0):,.1f} kg.", (1, 2))

rrow = []
names = {"B0_SSO_partner": "Partner-nation stages, sun-sync (first route)",
         "B1_SL8_83deg": "SL-8 stages, 83°, ~960 km (Product B)", "B2_SL8_74deg_750km": "SL-8 stages, 74°, ~750 km",
         "A1_Iridium_legacy": "Dead Iridium, 86° (Product A)"}
for k, r in routes.items():
    c, eng = k.split("/")
    if not r["feasible"] or not math.isfinite(r["total_dv_kms"]):
        rrow.append([names[c], eng, "not feasible at the economic price of time", "–", f0(sum(r["kit_masses_kg"])), "–", "–"])
        continue
    rrow.append([names[c], eng, f0(r["total_dv_kms"] * 1000), f0(r["propellant_kg"]), f0(sum(r["kit_masses_kg"])),
                 f0(r["launch_mass_kg"]), f0(r["duration_days"])])
order = ["B0_SSO_partner", "B1_SL8_83deg", "B2_SL8_74deg_750km", "A1_Iridium_legacy"]
rrow.sort(key=lambda row: next(k for k, c in enumerate(order) if names[c] == row[0]))
v["ROUTES_TABLE"] = table(["10-stop route, first stop 1 Jan 2029", "Engine", "Δv m/s", "Propellant kg", "Kits kg",
                           "Launch kg", "Days"], rrow,
                          "<b>Table 3.</b> Optimised missions on the real 2026 catalogue (simulated plans), each planned with the "
                          "price of time derived from the cost model. These are the routes themselves, from the first stop; "
                          "Table 5 adds the launch and the climb to the first stop.", (2, 3, 4, 5, 6))

lrow = []
for key in ("B0_SSO_partner", "B1_SL8_83deg", "A1_Iridium_legacy"):
    o = launch["options"][f"{key}/electric"]
    cell = lambda lk: (f"<b>{f1(o[lk]['cost_per_removal_musd'])}</b>" if lk == o["best"] else f1(o[lk]["cost_per_removal_musd"]))
    rs = o["rideshare"]
    lrow.append([names[key], f1(o["no_launch_leg"]["cost_per_removal_musd"]),
                 f"{cell('rideshare')} ({f0(rs['insertion_days'])} d, {f0(rs['insertion_dv_ms'])} m/s climb; {f0(rs['launch_mass_kg'])} kg)",
                 cell("neutron"), cell("falcon9")])
v["LAUNCH_TABLE"] = table(["Electric truck, 10 stops ($M per removal)", "Launch not counted", "Rideshare + own climb",
                           "Dedicated Neutron", "Dedicated Falcon 9"], lrow,
                          "<b>Table 5.</b> Getting to the first stop. Rideshare: SpaceX Transporter-class drop-off at 550 km, "
                          "97.6°, $7,500/kg, median over all 24 launch times of day. Dedicated: Neutron $52.5M, Falcon 9 $74M, "
                          "straight into the first target's orbit. Bold: cheapest.", (1, 3, 4))

vrow = []
for k, rows in val.items():
    te = [x["target_plane_err_deg"] for x in rows if "target_plane_err_deg" in x]
    cv = [x["correction_dv_ms"] for x in rows if "correction_dv_ms" in x]
    c, eng = k.split("/")
    vrow.append([names[c], eng, f"{np.median(te):.2f} / {np.max(te):.2f}",
                 f"{np.median(cv):.1f} / {np.max(cv):.1f}" if cv else "–"])
v["VAL_TABLE"] = table(["Route", "Engine", "Plane error at meeting, ° (median / max)", "Drift-leg correction, m/s (median / max)"],
                       vrow, "<b>Table 4.</b> Planned rendezvous re-checked with SGP4; drift legs integrated with J₂–J₄ "
                       "(chemical legs, which use instantaneous burns).", (2, 3))

# ---------------------------------------------------------------- render
html = (ROOT / "paper/paper_template.html").read_text()
for key, val_ in v.items():
    html = html.replace("{{" + key + "}}", val_)
left = re.findall(r"\{\{[A-Z0-9_]+\}\}", html)
assert not left, f"unfilled placeholders: {left}"
out_html = ROOT / "paper/OrbitalCurbside_paper.html"
out_html.write_text(html)
(ROOT / "paper/paper_numbers.json").write_text(json.dumps({k: x for k, x in v.items() if "TABLE" not in k}, indent=1))

from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
    pg = b.new_page(); pg.goto(out_html.as_uri()); pg.wait_for_timeout(1500)
    pg.pdf(path=str(ROOT / "paper/OrbitalCurbside_paper.pdf"), format="Letter", print_background=True,
           display_header_footer=True, header_template="<span></span>",
           footer_template='<div style="font-size:8px;width:100%;text-align:center;color:#888">'
                           'Orbital Curbside · <span class="pageNumber"></span></div>',
           margin={"top": "0.7in", "bottom": "0.75in", "left": "0.75in", "right": "0.75in"})
    b.close()
print("paper built:", {k: v[k] for k in ("B1_DAYS", "B1_CPR", "SINGLE_CPR", "REUSE_CPR", "BENCH_PCT", "VAL_B1")})
