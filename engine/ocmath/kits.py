"""Deorbit kits: the 'garbage bag' the truck leaves on each object.

For judges: "The truck doesn't haul junk home. At each stop it bolts a small
rocket 'tag' onto the dead object. The tag fires and drops that object into the
atmosphere, where it burns up. The truck keeps driving."

Sizing:
  1. dv to lower perigee from a circular orbit at r_a to a target perigee r_p
     (one burn at apogee):  dv = v_c - v_apo(ellipse r_a x r_p)
  2. Tsiolkovsky with the kit's own motor gives the propellant mass.
  3. Kit inert mass = fixed hardware + tankage fraction of propellant.

Perigee choices (assumptions, documented in the paper):
  * 'uncontrolled' -> perigee 250 km: object re-enters within months (well inside
    the 5-year rule) but at an unpredictable place.  Only acceptable if the
    object's casualty risk is below 1 in 10,000 (US standard practice).
  * 'controlled'   -> perigee 50 km: re-entry over the ocean on the next pass,
    required for large objects (e.g. 9-tonne SL-16 stages) whose surviving
    fragments would exceed the casualty-risk limit.
"""
from dataclasses import dataclass
import numpy as np

from .constants import MU, R_E, G0


@dataclass
class KitDesign:
    isp: float = 285.0             # [ASSUMPTION] small solid / green-monoprop motor class
    fixed_inert_kg: float = 12.0   # [ASSUMPTION] avionics, attach mechanism, structure
    tank_fraction: float = 0.15    # [ASSUMPTION] inert mass per kg propellant
    perigee_uncontrolled_km: float = 250.0
    perigee_controlled_km: float = 50.0


def perigee_lowering_dv(alt_km, perigee_km):
    """dv [km/s] to drop the perigee of a circular orbit at alt_km to perigee_km."""
    ra = R_E + np.asarray(alt_km, float)
    rp = R_E + perigee_km
    v_c = np.sqrt(MU / ra)
    v_apo = np.sqrt(MU * (2 / ra - 2 / (ra + rp)))
    return v_c - v_apo


def kit_mass(obj_mass_kg, alt_km, controlled=False, design=KitDesign()):
    """Total kit mass [kg] needed to deorbit an object of obj_mass_kg at alt_km."""
    rp = design.perigee_controlled_km if controlled else design.perigee_uncontrolled_km
    dv = perigee_lowering_dv(alt_km, rp)
    ve = design.isp * G0
    # solve m_prop with the kit's own inert mass riding along (closed form):
    #   (m_obj + m_inert + m_prop) / (m_obj + m_inert) = exp(dv/ve)
    #   m_inert = fixed + f * m_prop
    r = np.exp(dv / ve)
    m_prop = (r - 1) * (obj_mass_kg + design.fixed_inert_kg) / (1 - (r - 1) * design.tank_fraction)
    return design.fixed_inert_kg + design.tank_fraction * m_prop + m_prop, dv
