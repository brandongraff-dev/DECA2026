"""Layer 3 + 4: what it costs to move between orbits, and how much fuel that burns.

For judges: "Changing altitude is cheap. Twisting an orbit's plane is brutally
expensive -- about 1.3 km/s for ten degrees, roughly what it takes to fly from
orbit back to the ground. That's why we wait for Earth to twist it for us."

Two engine types are modelled with the SAME formula shape, which makes the
comparison easy to explain:

  chemical (impulsive):  dv = sqrt(v1^2 + v2^2 - 2 v1 v2 cos(theta))
  electric (Edelbaum):   dv = sqrt(v1^2 + v2^2 - 2 v1 v2 cos(pi/2 * theta))

v1, v2 are circular speeds before/after and theta is the angle between the two
orbital planes. With theta = 0 both reduce to |v1 - v2| (a small altitude change).
"""
import numpy as np
from .constants import MU, G0


def circular_speed(a):
    """Speed on a circular orbit of radius a [km/s]."""
    return np.sqrt(MU / np.asarray(a, dtype=float))


def plane_angle(i1, raan1, i2, raan2):
    """Angle between two orbital planes [rad] (spherical law of cosines).

    cos(theta) = cos i1 cos i2 + sin i1 sin i2 cos(RAAN2 - RAAN1)
    This combines an inclination difference and a RAAN difference into one angle.
    """
    c = np.cos(i1) * np.cos(i2) + np.sin(i1) * np.sin(i2) * np.cos(raan2 - raan1)
    return np.arccos(np.clip(c, -1.0, 1.0))


def plane_change_dv(v, theta):
    """Pure plane change at constant speed: dv = 2 v sin(theta/2)."""
    return 2.0 * v * np.sin(np.asarray(theta) / 2.0)


def hohmann_dv(a1, a2):
    """Total two-burn Hohmann transfer dv between circular orbits [km/s]."""
    a1 = np.asarray(a1, float)
    a2 = np.asarray(a2, float)
    dv1 = np.abs(np.sqrt(MU / a1) * (np.sqrt(2 * a2 / (a1 + a2)) - 1))
    dv2 = np.abs(np.sqrt(MU / a2) * (1 - np.sqrt(2 * a1 / (a1 + a2))))
    return dv1 + dv2


def impulsive_combined_dv(a1, a2, theta):
    """Chemical estimate: altitude change + plane change done together.

    Law-of-cosines form; for nearby circular orbits it is within a few percent of
    a Hohmann transfer with the plane change split optimally between its burns.
    """
    v1, v2 = circular_speed(a1), circular_speed(a2)
    return np.sqrt(np.maximum(v1 ** 2 + v2 ** 2 - 2 * v1 * v2 * np.cos(theta), 0.0))


def edelbaum_dv(a1, a2, theta):
    """Low-thrust (electric) dv between circular orbits: Edelbaum (1961).

    Valid for continuous, constant-acceleration thrust with optimal steering
    between circular orbits (the standard first-order model for Hall thrusters).
    """
    v1, v2 = circular_speed(a1), circular_speed(a2)
    return np.sqrt(np.maximum(v1 ** 2 + v2 ** 2 - 2 * v1 * v2 * np.cos(np.pi / 2 * np.asarray(theta)), 0.0))


def propellant_for_dv(m_initial, dv, isp):
    """Layer 4 -- Tsiolkovsky rocket equation: propellant burned for a given dv.

        m_final = m_initial * exp(-dv / (Isp * g0))
    """
    return m_initial * (1.0 - np.exp(-np.asarray(dv) / (isp * G0)))


def mass_before_burn(m_after, dv, isp):
    """Inverse Tsiolkovsky: mass needed before a burn to end at m_after."""
    return m_after * np.exp(np.asarray(dv) / (isp * G0))


def low_thrust_burn_time(m_initial, dv, thrust_kN, isp):
    """Time to deliver dv with constant thrust (mass decreasing as fuel is used) [s].

        t = (m0 * Isp * g0 / F) * (1 - exp(-dv / (Isp * g0)))
    thrust_kN is in kilonewtons to keep units consistent with km/s and kg.
    """
    ve = isp * G0
    return m_initial * ve / thrust_kN * (1.0 - np.exp(-np.asarray(dv) / ve))
