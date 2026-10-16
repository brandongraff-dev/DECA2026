"""Layer 2: J2 nodal precession -- Earth's bulge as a conveyor belt.

For judges: "Earth is fatter at the equator. That extra mass slowly twists every
orbit around Earth like a lazy Susan, and HOW FAST it twists depends on altitude
and tilt. We use that difference as free transportation."

All functions accept numpy arrays (vectorised) as well as plain floats.
"""
import numpy as np
from .constants import MU, R_E, J2, DAY, DEG, SSO_RATE


def mean_motion(a):
    """Orbital angular rate n = sqrt(mu / a^3)  [rad/s]."""
    return np.sqrt(MU / np.asarray(a, dtype=float) ** 3)


_RATE_MODEL = {"name": "j2", "interp": None}


def set_rate_model(name="j2"):
    """Choose how node drift is computed everywhere in the engine.

    "j2"   : first-order J2 formula (exactly what GTOC9's rules use).
    "sgp4" : J2 formula + a correction table built from SGP4's own secular rates
             (adds second-order J2^2 and J4 terms, WGS-72 constants).  Use this for
             real catalogue (TLE) work: over 1,000+ days the 0.1-0.2% difference
             grows to ~1 degree of plane error.
    """
    if name == "sgp4" and _RATE_MODEL["interp"] is None:
        from sgp4.api import Satrec, WGS72
        alts = np.arange(150.0, 2101.0, 10.0)
        incs = np.arange(0.0, 180.01, 0.5)
        delta = np.zeros((len(alts), len(incs)))
        for ia, h in enumerate(alts):
            a = R_E + h
            n_rad_min = np.sqrt(MU / a ** 3) * 60.0
            for ii, inc in enumerate(incs):
                s = Satrec()
                s.sgp4init(WGS72, "i", 1, 26000.0, 0.0, 0.0, 0.0, 0.0001, 0.0, inc * DEG, 0.0, n_rad_min, 0.0)
                delta[ia, ii] = s.nodedot / 60.0 - _raan_rate_j2(a, inc * DEG, 0.0001)
        _RATE_MODEL["interp"] = (alts[0], alts[1] - alts[0], incs[0], incs[1] - incs[0], delta)
    _RATE_MODEL["name"] = name


def _raan_rate_j2(a, i, e=0.0):
    a = np.asarray(a, dtype=float)
    p = a * (1.0 - np.asarray(e, dtype=float) ** 2)
    return -1.5 * mean_motion(a) * J2 * (R_E / p) ** 2 * np.cos(i)


def raan_rate(a, i, e=0.0):
    """Secular drift of the ascending node, dRAAN/dt  [rad/s].

        dRAAN/dt = -(3/2) * n * J2 * (R_E / p)^2 * cos(i),   p = a (1 - e^2)

    Negative for prograde orbits (i < 90 deg): the plane twists westward.
    Positive for retrograde orbits (i > 90 deg), e.g. sun-synchronous orbits.
    With set_rate_model("sgp4") a small higher-order correction is added.
    """
    base = _raan_rate_j2(a, i, e)
    if _RATE_MODEL["name"] == "sgp4":
        h0, dh, i0, di, tab = _RATE_MODEL["interp"]
        x = (np.asarray(a, float) - R_E - h0) / dh                 # fast bilinear lookup
        y = (np.degrees(np.asarray(i, float)) - i0) / di
        x = np.clip(x, 0, tab.shape[0] - 1.000001)
        y = np.clip(y, 0, tab.shape[1] - 1.000001)
        ix, iy = x.astype(int), y.astype(int)
        fx, fy = x - ix, y - iy
        corr = (tab[ix, iy] * (1 - fx) * (1 - fy) + tab[ix + 1, iy] * fx * (1 - fy)
                + tab[ix, iy + 1] * (1 - fx) * fy + tab[ix + 1, iy + 1] * fx * fy)
        base = base + corr
    return base


def argp_rate(a, i, e=0.0):
    """Secular J2 drift of the argument of perigee  [rad/s] (used for SGP4 checks)."""
    a = np.asarray(a, dtype=float)
    p = a * (1.0 - np.asarray(e, dtype=float) ** 2)
    return 0.75 * mean_motion(a) * J2 * (R_E / p) ** 2 * (5.0 * np.cos(i) ** 2 - 1.0)


def raan_rate_deg_per_day(alt_km, inc_deg):
    """Convenience: drift rate in deg/day for a circular orbit at altitude alt_km."""
    return raan_rate(R_E + np.asarray(alt_km, float), np.asarray(inc_deg, float) * DEG) / DEG * DAY


def raan_rate_partials(a, i):
    """Sensitivity of the drift rate to altitude and inclination (circular orbit).

    d(RAANdot)/da = -3.5 * RAANdot / a        (higher orbit -> slower twist)
    d(RAANdot)/di = -RAANdot * tan(i)          (tilt changes the twist, too)
    """
    w = raan_rate(a, i)
    return -3.5 * w / a, -w * np.tan(i)


def sso_inclination(a):
    """Inclination [rad] that makes a circular orbit at radius a sun-synchronous."""
    cos_i = SSO_RATE / (-1.5 * mean_motion(a) * J2 * (R_E / a) ** 2)
    return np.arccos(np.clip(cos_i, -1.0, 1.0))


def gap_closing_time(d_raan, rate_1, rate_2):
    """Layer 5 in one line: time to close a RAAN gap by drifting at a different rate.

        dt = dRAAN / |RAANdot_1 - RAANdot_2|
    """
    rel = np.abs(np.asarray(rate_1) - np.asarray(rate_2))
    with np.errstate(divide="ignore"):
        return np.abs(d_raan) / rel
