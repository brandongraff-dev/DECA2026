"""Layer 9: getting the truck to its first stop.

For judges: "A rocket doesn't drop you off wherever you like. The cheap ride
(a shared 'rideshare' launch) only goes to one kind of orbit, sun-synchronous,
tilted about 97.6 degrees. If the first piece of junk is tilted 83 degrees, the
truck has to fix that tilt itself, and Earth's bulge can't help: it turns
orbits around the pole, it doesn't change their tilt. So we price three ways
in: a rideshare plus the truck's own engine, or a whole rocket of our own."

Model:
  * Rideshare: drop-off in a circular sun-synchronous orbit (alt ~550 km).  Its
    node is set by the launch's local time of ascending node (LTAN), which we
    don't control, so we test all 24 hours and report the median and the range.
    The truck then flies an ordinary drift-orbit leg (legs.leg_cost) from the
    drop-off orbit to its first target, choosing how long to take by the same
    economic price of time the route planner uses.
  * Dedicated launch: the rocket puts the truck straight into the first
    target's orbit (dv = 0) for a fixed price.
"""
from dataclasses import dataclass
import numpy as np

from .constants import R_E, DAY, DEG, TWO_PI
from .j2 import sso_inclination
from .legs import leg_cost_throttled as leg_cost
from .missions import launch_mass_kits


@dataclass
class LaunchOption:
    key: str
    name: str
    kind: str                       # "rideshare" or "dedicated"
    alt_km: float = 550.0           # rideshare drop-off altitude
    usd_per_kg: float = 0.0         # rideshare price
    port_max_kg: float = np.inf     # rideshare: above this needs a custom quote
    price_musd: float = 0.0         # dedicated price
    capacity_kg: float = np.inf     # dedicated: to LEO
    source: str = ""


# SOURCED (research/economics_inputs.md, s.1): SpaceX rideshare API $7,500/kg (2027 price; the
# truck would fly ~2028, so we hold the newest published price [ASSUMPTION]); max 831 kg per port.
# Transporter drop-offs are ~500-600 km SSO (Orbit Codex / KeepTrack, Oct 2026); we use 550 km.
RIDESHARE_SSO = LaunchOption("rideshare", "Rideshare to sun-synchronous orbit + truck's own engine", "rideshare",
                             alt_km=550.0, usd_per_kg=7500.0, port_max_kg=831.0,
                             source="SpaceX rideshare price API (16 Oct 2026); custom quote above 831 kg")
# SOURCED: Rocket Lab CFO: Neutron average selling price $50-55M; 13,000 kg to LEO; first flight slipped
# to 2027 (Light Reading, 16 Oct 2026).  Midpoint used.
NEUTRON = LaunchOption("neutron", "Dedicated Rocket Lab Neutron", "dedicated", price_musd=52.5,
                       capacity_kg=13000.0, source="Rocket Lab investor statements; Light Reading 16 Oct 2026")
# SOURCED: Falcon 9 standard price $74M (Spaceflight Now, 24 Feb 2026, citing SpaceX).
FALCON9 = LaunchOption("falcon9", "Dedicated SpaceX Falcon 9", "dedicated", price_musd=74.0,
                       capacity_kg=17000.0, source="Spaceflight Now, 24 Feb 2026")
OPTIONS = [RIDESHARE_SSO, NEUTRON, FALCON9]


def sun_right_ascension(jd):
    """Low-precision right ascension of the Sun [rad] (Astronomical Almanac, ~0.01 deg)."""
    n = np.asarray(jd, float) - 2451545.0
    L = (280.460 + 0.9856474 * n) * DEG
    g = (357.528 + 0.9856003 * n) * DEG
    lam = L + (1.915 * np.sin(g) + 0.020 * np.sin(2 * g)) * DEG
    eps = (23.439 - 4.0e-7 * n) * DEG
    return np.mod(np.arctan2(np.cos(eps) * np.sin(lam), np.cos(lam)), TWO_PI)


def sso_raan(jd, ltan_h):
    """Node of a sun-synchronous orbit whose ascending node crosses at local time ltan_h."""
    return np.mod(sun_right_ascension(jd) + (ltan_h - 12.0) * 15.0 * DEG, TWO_PI)


def insertion_leg(pop, truck, first, arrive_jd, launch, mass, lam_ms_per_day, ltan_h,
                  T_days=np.arange(10.0, 901.0, 5.0)):
    """Cheapest (dv + lam*T) way from the launch drop-off to object `first`, arriving at arrive_jd."""
    if launch.kind == "dedicated":
        return {"dv": 0.0, "T_days": 0.0, "launch_jd": float(arrive_jd), "t_spiral_days": 0.0,
                "a_d": float(pop.a[first]), "i_d": float(pop.i[first]), "feasible": True, "ltan_h": None}
    a0 = R_E + launch.alt_km
    i0 = sso_inclination(a0)
    T = np.asarray(T_days, float)
    jd0 = arrive_jd - T                                         # launch date for each option
    n = len(T)
    r = leg_cost(truck.prop, a0, i0, sso_raan(jd0, ltan_h),
                 np.full(n, pop.a[first]), np.full(n, pop.i[first]),
                 pop.raan_at(jd0, np.full(n, first)), T * DAY, mass, truck.bounds, truck.dv_rendezvous_kms)
    score = r["dv"] * 1000.0 + lam_ms_per_day * T
    k = int(np.argmin(score))
    return {"dv": float(r["dv"][k]), "T_days": float(T[k]), "launch_jd": float(jd0[k]),
            "t_spiral_days": float(r["t_spiral"][k] / DAY), "a_d": float(r["a_d"][k]), "i_d": float(r["i_d"][k]),
            "feasible": bool(np.isfinite(r["dv"][k]) and r["feasible"][k]), "ltan_h": float(ltan_h),
            "drop_alt_km": launch.alt_km, "drop_inc_deg": float(i0 / DEG)}


def evaluate_with_launch(pop, truck, route, launch, lam_ms_per_day, ltan_h=10.5, iterations=4):
    """Re-price a planned route (truck.evaluate output) including the way to orbit.

    The insertion leg is flown with every kit and all propellant aboard, so the
    truck is heavier for the whole route; we re-cost every leg with the new
    masses (electric spirals get slower) and iterate to a consistent launch mass.
    """
    legs = [dict(l) for l in route["legs"]]
    kits = list(route["kit_masses_kg"])
    first = route["order"][0]
    arrive = route["start_jd"]                         # arrival at the first stop
    m0 = route["launch_mass_kg"]
    masses = [m0] * len(legs)
    ins = None
    for _ in range(iterations):
        ins = insertion_leg(pop, truck, first, arrive, launch, m0, lam_ms_per_day, ltan_h)
        for k, l in enumerate(legs):
            A, B = l["from"], l["to"]
            r = leg_cost(truck.prop, pop.a[A], pop.i[A], pop.raan_at(l["depart_jd"], A),
                         pop.a[[B]], pop.i[[B]], pop.raan_at(l["depart_jd"], [B]),
                         l["T_days"] * DAY, masses[k], truck.bounds, truck.dv_rendezvous_kms,
                         plan_mass=route.get("plan_mass_kg"))
            l.update(dv=float(r["dv"][0]), feasible=bool(r["feasible"][0]))
        m0, prop_kg, ms = launch_mass_kits([ins["dv"]] + [l["dv"] for l in legs], truck.prop.isp,
                                           truck.dry_mass_kg, [0.0] + kits, truck.dv_reserve_kms)
        masses = ms[1:]
        if not np.isfinite(m0):
            break
    feasible = bool(ins["feasible"] and all(l["feasible"] for l in legs) and np.isfinite(m0))
    if launch.kind == "rideshare":
        launch_musd = None              # priced per kg by the economics layer (so it is stress-tested)
        note = "custom rideshare quote needed (above 831 kg per port)" if m0 > launch.port_max_kg else ""
    else:
        launch_musd = float(launch.price_musd)
        note = "" if m0 <= launch.capacity_kg else "over rocket capacity"
        feasible &= m0 <= launch.capacity_kg
    return {**route, "legs": legs, "launch": launch.key, "launch_name": launch.name,
            "insertion": ins, "launch_mass_kg": float(m0), "propellant_kg": float(prop_kg),
            "kits_kg": float(sum(kits)), "total_dv_kms": float(ins["dv"] + sum(l["dv"] for l in legs)),
            "launch_jd": ins["launch_jd"], "duration_days": float(route["duration_days"] + ins["T_days"]),
            "launch_fixed_musd": launch_musd, "launch_note": note, "feasible": feasible}
