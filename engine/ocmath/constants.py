"""Physical constants used everywhere in the Orbital Curbside engine.

Units: kilometres, seconds, kilograms, radians (unless a name says otherwise).
"""
import math

MU = 398600.4418          # Earth's gravitational parameter [km^3/s^2]
R_E = 6378.137            # Earth's equatorial radius [km]
J2 = 1.08262668e-3        # Earth's oblateness coefficient (same value GTOC9 uses)
G0 = 9.80665e-3           # standard gravity [km/s^2]  (9.80665 m/s^2)

DAY = 86400.0             # [s]
YEAR = 365.25 * DAY       # [s]
DEG = math.pi / 180.0     # multiply degrees by DEG to get radians
TWO_PI = 2.0 * math.pi

# Earth's orbit around the Sun advances 360 deg per tropical year; a sun-synchronous
# orbit's node must precess at this same rate.
SSO_RATE = TWO_PI / (365.2421897 * DAY)   # [rad/s]  ~ 0.9856 deg/day
