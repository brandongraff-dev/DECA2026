"""Layer 8: economics -- turning kilograms and days into dollars per removal.

For judges: "A mission's cost is the truck, the kits, the launch, the fuel and
the people flying it. Divide by how many objects it removes and you get the
price tag per removal. One truck that removes ten objects spreads its big fixed
costs ten ways; a one-object mission eats them all alone."

Every parameter carries (low, base, high) values and a source string.  Values
marked [ASSUMPTION] are not published anywhere we could find; they are the first
things to test in customer/expert interviews and are stress-tested below.
All money in US$ millions.
"""
from dataclasses import dataclass, field, replace
import numpy as np


@dataclass
class Param:
    low: float
    base: float
    high: float
    source: str


def default_params():
    return {
        # --- hardware ------------------------------------------------------------------
        "truck_hw_musd": Param(50.0, 80.0, 115.0,
            "Low: NASA OTPS (2023) estimate ~$50M to design+build Astroscale ELSA-M. High: NASA OTPS Table 34, "
            "$115.16M hardware for a 1,000 kg ADR servicer (Orbit Fab study). Base: [ASSUMPTION] midpoint-ish."),
        "kit_musd": Param(0.5, 1.5, 3.0,
            "[ASSUMPTION] Unit cost of one deorbit kit (small solid motor + attach mechanism + avionics). "
            "No public price found. VALIDATE in interviews."),
        # --- launch & propellant --------------------------------------------------------
        "launch_usd_per_kg": Param(7000.0, 7500.0, 15000.0,
            "SpaceX rideshare price API: $7,000/kg (2026), $7,500/kg (2027). High: NASA OTPS assumption $15,000/kg. "
            "Note: >831 kg per port needs a custom quote."),
        "xenon_usd_per_kg": Param(2780.0, 2780.0, 12000.0,
            "Expert Market Research Q1-2026 average $2,780/kg; SETS (2024) quotes up to $12,000/kg."),
        "chem_prop_usd_per_kg": Param(200.0, 500.0, 1000.0, "[ASSUMPTION] storable bipropellant, small vs other costs."),
        # --- operations ----------------------------------------------------------------
        "ops_musd_per_year": Param(3.0, 5.0, 10.0,
            "[ASSUMPTION] mission operations team + ground stations + tracking data per year."),
        "insurance_frac": Param(0.05, 0.08, 0.12,
            "[ASSUMPTION] launch + in-orbit insurance as a fraction of (hardware + launch)."),
        # --- engineering margin ---------------------------------------------------------
        "dv_margin_frac": Param(0.10, 0.10, 0.25,
            "Our model is ~2% optimistic vs JPL GTOC9 and SGP4 checks show correction burns; 10% dv margin base."),
        "profit_margin": Param(0.15, 0.20, 0.30, "[ASSUMPTION] target gross margin on price."),
    }


def base_values(params):
    return {k: p.base for k, p in params.items()}


def mission_cost(route, prop_kind, n_removed, v, isp=None):
    """Cost breakdown [US$M] of one truck mission.

    route: dict from ocmath.truck.evaluate (launch_mass_kg, propellant_kg, duration_days)
    v    : dict of parameter values (e.g. base_values(default_params()))
    """
    # fuel margin: re-scale propellant (and launch mass) for extra dv
    prop = route["propellant_kg"] * (1.0 + v["dv_margin_frac"])
    m0 = route["launch_mass_kg"] + (prop - route["propellant_kg"])
    years = route["duration_days"] / 365.25
    prop_price = v["xenon_usd_per_kg"] if prop_kind == "electric" else v["chem_prop_usd_per_kg"]
    c = {
        "truck_hardware": v["truck_hw_musd"],
        "kits": v["kit_musd"] * n_removed,
        "launch": m0 * v["launch_usd_per_kg"] / 1e6,
        "propellant": prop * prop_price / 1e6,
        "operations": v["ops_musd_per_year"] * years,
    }
    c["insurance"] = v["insurance_frac"] * (c["truck_hardware"] + c["launch"])
    total = sum(c.values())
    return {"breakdown": c, "total": total, "per_removal": total / n_removed,
            "price_per_removal": total / n_removed / (1.0 - v["profit_margin"]), "launch_mass_kg": m0,
            "years": years}


def tornado(route, prop_kind, n_removed, params):
    """Swing in cost per removal when each parameter goes low -> high (others at base)."""
    base = base_values(params)
    ref = mission_cost(route, prop_kind, n_removed, base)["per_removal"]
    rows = []
    for k, p in params.items():
        if k == "profit_margin":
            continue
        lo = mission_cost(route, prop_kind, n_removed, {**base, k: p.low})["per_removal"]
        hi = mission_cost(route, prop_kind, n_removed, {**base, k: p.high})["per_removal"]
        rows.append({"param": k, "low": lo, "high": hi, "swing": abs(hi - lo)})
    return ref, sorted(rows, key=lambda r: -r["swing"])


def monte_carlo(route, prop_kind, n_removed, params, n=20000, seed=0):
    """Sample every parameter from a triangular(low, base, high) distribution."""
    rng = np.random.default_rng(seed)
    out = np.empty(n)
    for j in range(n):
        v = {k: (rng.triangular(p.low, p.base, p.high) if p.high > p.low else p.base) for k, p in params.items()}
        out[j] = mission_cost(route, prop_kind, n_removed, v)["per_removal"]
    return {"p10": float(np.percentile(out, 10)), "p50": float(np.percentile(out, 50)),
            "p90": float(np.percentile(out, 90)), "mean": float(out.mean())}


# ----------------------------------------------------------------------------- anchors
# Real single-object removal contracts (public values).  These are what customers
# pay TODAY for one object at a time.  Sources: research/economics_inputs.md, s.6.
REAL_WORLD_ANCHORS = [
    {"name": "ESA ClearSpace-1", "musd": 86 * 1.08, "objects": 1, "note": "EUR 86M ESA contract (2020); converted at ~1.08 USD/EUR [ASSUMPTION fx]"},
    {"name": "JAXA/Astroscale ADRAS-J2", "musd": 82.0, "objects": 1, "note": "JPY ~13.2B incl. tax (~$82M per Payload Space)"},
    {"name": "UK ADR / ClearSpace (2026)", "musd": 80.0, "objects": 2, "note": "~GBP 61M (~$80M) for two satellites, 15 Oct 2026"},
    {"name": "NASA est. ELSA-M class mission", "musd": 60.0, "objects": 1, "note": "NASA OTPS 2023: ~$50M build + ~$10M launch"},
]


# ------------------------------------------------------------------ reusable truck
def reusable_campaign(route, prop_kind, n_per_route, n_routes, v, pod_dry_kg=150.0, pod_musd=4.0):
    """A long-lived truck that flies `n_routes` routes like `route`, restocked with kit pods.

    Electric: the truck launches once with all the xenon it will ever need (propellant is
    tiny per route), so only KIT PODS are launched afterwards.
    Chemical: each route also needs its propellant delivered (pod carries kits + propellant).
    pod_dry_kg / pod_musd: [ASSUMPTION] a simple carrier the truck docks with to collect kits.
    """
    prop_route = route["propellant_kg"] * (1.0 + v["dv_margin_frac"])
    kits_route = route["kits_kg"]
    years = route["duration_days"] * n_routes / 365.25
    dry = route["launch_mass_kg"] - route["propellant_kg"] - kits_route
    if prop_kind == "electric":
        first_launch_kg = dry + kits_route + prop_route * n_routes
        pod_kg = kits_route + pod_dry_kg
        prop_cost = prop_route * n_routes * v["xenon_usd_per_kg"] / 1e6
    else:
        first_launch_kg = dry + kits_route + prop_route
        pod_kg = kits_route + prop_route + pod_dry_kg
        prop_cost = prop_route * n_routes * v["chem_prop_usd_per_kg"] / 1e6
    n_pods = n_routes - 1
    c = {
        "truck_hardware": v["truck_hw_musd"],
        "kits": v["kit_musd"] * n_per_route * n_routes,
        "launch": (first_launch_kg + n_pods * pod_kg) * v["launch_usd_per_kg"] / 1e6,
        "pods": n_pods * pod_musd,
        "propellant": prop_cost,
        "operations": v["ops_musd_per_year"] * years,
    }
    c["insurance"] = v["insurance_frac"] * (c["truck_hardware"] + c["launch"] + c["pods"])
    total = sum(c.values())
    n = n_per_route * n_routes
    return {"breakdown": c, "total": total, "per_removal": total / n, "removals": n, "years": years,
            "first_launch_kg": first_launch_kg, "pod_kg": pod_kg, "propellant_total_kg": prop_route * n_routes}


def thruster_routes_limit(route, isp, total_impulse_MNs=13.0):
    """How many routes the thrusters' rated total impulse allows (2x BHT-1500: >6.5 MN*s each)."""
    from .constants import G0
    impulse_per_route = route["propellant_kg"] * isp * G0 * 1000.0   # N*s
    return total_impulse_MNs * 1e6 / impulse_per_route


def price_of_time(prop, truck_mass_kg, v):
    """Economic exchange rate between mission days and delta-v [m/s per day].

    One extra day costs the operations team v['ops_musd_per_year']/365.
    One extra m/s costs the propellant for it plus launching that propellant:
        dm = m * dv / (Isp g0)   ->  $ = dm * (propellant price + launch price per kg)
    lambda = (cost of a day) / (cost of one m/s).  The route planner uses it so
    'faster vs cheaper' is decided by money, not by an arbitrary setting.
    """
    from .constants import G0
    day_usd = v["ops_musd_per_year"] * 1e6 / 365.25
    prop_price = v["xenon_usd_per_kg"] if prop.kind == "electric" else v["chem_prop_usd_per_kg"]
    kg_per_ms = truck_mass_kg * 0.001 / (prop.isp * G0)          # 1 m/s = 0.001 km/s
    usd_per_ms = kg_per_ms * (prop_price + v["launch_usd_per_kg"])
    return day_usd / usd_per_ms
