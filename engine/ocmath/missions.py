"""Mission-level bookkeeping: walk a route leg by leg, track mass and cost.

For judges: "A route is just a list of stops and travel times. We add up the
fuel for every hop, and the fuel we have to carry for later hops makes earlier
hops heavier -- the rocket equation keeps everyone honest."
"""
from dataclasses import dataclass, field
import numpy as np

from .constants import DAY
from .legs import leg_cost, DriftBounds
from .transfers import mass_before_burn


@dataclass
class Route:
    order: list                # population indices, in visiting order
    depart_jd: list            # departure epoch from each stop (len N-1)
    transfer_days: list        # transfer time of each leg (len N-1)
    leg_dv: list = field(default_factory=list)   # km/s
    leg_detail: list = field(default_factory=list)


def evaluate_route(pop, route, prop, mass_guess, bounds=DriftBounds(), dv_rendezvous=0.0, iterations=2):
    """Compute each leg's dv along a fixed route.  Electric spiral times depend on
    mass, so we iterate with the mass profile from the previous pass."""
    masses = [mass_guess] * len(route.transfer_days)
    for _ in range(iterations):
        route.leg_dv, route.leg_detail = [], []
        for k, (A, B) in enumerate(zip(route.order[:-1], route.order[1:])):
            jd = route.depart_jd[k]
            T = route.transfer_days[k] * DAY
            r = leg_cost(prop, pop.a[A], pop.i[A], pop.raan_at(jd, A), pop.a[[B]], pop.i[[B]],
                         pop.raan_at(jd, [B]), T, masses[k], bounds, dv_rendezvous)
            route.leg_dv.append(float(r["dv"][0]))
            route.leg_detail.append({key: float(v[0]) for key, v in r.items()})
        if prop.kind != "electric":
            break
    return route


def launch_mass(leg_dv_kms, isp, m_dry, m_kit, n_objects):
    """Initial (launch) mass for a mission that drops one kit per object.

    Walk backwards from the end: after the last kit is dropped the truck is
    'dry' (no fuel left).  Each earlier leg needs the mass after it times
    exp(dv/ve); each earlier stop adds back the kit that was dropped there.
    """
    m = m_dry + m_kit            # arriving at the last object, last kit still aboard
    for dv in reversed(leg_dv_kms):
        m = mass_before_burn(m, dv, isp)   # before the burn of this leg
        m += m_kit                          # the kit dropped at the departure object
    return float(m)


def launch_mass_kits(leg_dv_kms, isp, m_dry, kit_masses, dv_final=0.0):
    """Launch mass with a DIFFERENT kit mass for each object (kit_masses in visiting order).

    dv_final: optional dv the truck keeps in reserve after the last stop
    (e.g. to dispose of itself).  Returns (m0, propellant_kg, mass at the start of each leg).
    """
    m = mass_before_burn(m_dry, dv_final, isp) + kit_masses[-1]
    for dv, kit in zip(reversed(leg_dv_kms), reversed(kit_masses[:-1])):
        m = mass_before_burn(m, dv, isp) + kit
    m0 = float(m)
    masses, cur = [], m0
    for dv, kit in zip(leg_dv_kms, kit_masses[:-1]):
        cur -= kit
        masses.append(cur)
        cur = cur / mass_before_burn(1.0, dv, isp)
    propellant = m0 - m_dry - sum(kit_masses)
    return m0, float(propellant), masses


def mass_profile(leg_dv_kms, isp, m_dry, m_kit, n_objects):
    """Mass at the start of each leg (after dropping the kit at the departure object)."""
    m0 = launch_mass(leg_dv_kms, isp, m_dry, m_kit, n_objects)
    masses, m = [], m0
    for dv in leg_dv_kms:
        m -= m_kit
        masses.append(m)
        m = m / mass_before_burn(1.0, dv, isp)
    return m0, masses


def gtoc9_mission_cost(m0, m_dry=2000.0, base=55.0, alpha=2.0e-6):
    """GTOC9 cost model: C = c + alpha (m0 - m_dry)^2  [MEUR]."""
    return base + alpha * (m0 - m_dry) ** 2
