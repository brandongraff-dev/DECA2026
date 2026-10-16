"""Layer 1: turning public catalogue data into orbital elements.

For judges: "Every tracked object has a public 'address' (a TLE) published by the
US Space Force and mirrored by CelesTrak. We decode each address into six numbers
that say how big, how round, how tilted and how twisted its orbit is."

Two sources are supported:
  * GTOC9 `debris.csv` (the 2017 competition benchmark, osculating elements).
  * CelesTrak TLE files (2026 snapshot), decoded with the official SGP4 library,
    joined with CelesTrak's SATCAT (object type / status / radar size) and
    Jonathan McDowell's GCAT (mass).
"""
from dataclasses import dataclass, field
import csv
import math
import numpy as np

from .constants import MU, R_E, DAY, TWO_PI
from .j2 import raan_rate

MJD2000_JD = 2451544.5


@dataclass
class Population:
    """A set of objects with (mean) orbital elements at their own epochs."""
    ids: list
    names: list
    epoch_jd: np.ndarray   # epoch of the elements [Julian date]
    a: np.ndarray          # semi-major axis [km]
    e: np.ndarray
    i: np.ndarray          # inclination [rad]
    raan: np.ndarray       # right ascension of ascending node at epoch [rad]
    argp: np.ndarray
    M: np.ndarray
    meta: dict = field(default_factory=dict)   # extra per-object columns (lists)

    def __len__(self):
        return len(self.ids)

    def raan_at(self, jd, idx=None):
        """RAAN of objects at Julian date jd, propagated with secular J2."""
        sl = slice(None) if idx is None else idx
        dt = (np.asarray(jd) - self.epoch_jd[sl]) * DAY
        return np.mod(self.raan[sl] + raan_rate(self.a[sl], self.i[sl], self.e[sl]) * dt, TWO_PI)

    @property
    def alt_km(self):
        return self.a - R_E

    def subset(self, mask_or_idx):
        idx = np.arange(len(self))[mask_or_idx] if np.asarray(mask_or_idx).dtype == bool else np.asarray(mask_or_idx)
        pick = lambda lst: [lst[k] for k in idx]
        return Population(pick(self.ids), pick(self.names), self.epoch_jd[idx], self.a[idx], self.e[idx],
                          self.i[idx], self.raan[idx], self.argp[idx], self.M[idx],
                          {k: pick(v) for k, v in self.meta.items()})


def load_gtoc9(path):
    """Read GTOC9 debris.csv (epochs in MJD2000, SI units) into a Population."""
    rows = []
    with open(path) as f:
        next(f)
        for line in f:
            p = [x.strip() for x in line.split(",")]
            if len(p) >= 8:
                rows.append(p)
    arr = np.array([[float(x) for x in r[1:8]] for r in rows])
    return Population(
        ids=[int(r[0]) for r in rows], names=[f"GTOC9-{int(r[0]):03d}" for r in rows],
        epoch_jd=arr[:, 0] + MJD2000_JD, a=arr[:, 1] / 1000.0, e=arr[:, 2], i=arr[:, 3],
        raan=arr[:, 4], argp=arr[:, 5], M=arr[:, 6])


def read_tle_file(path):
    """Yield (name, line1, line2) from a 3-line TLE file."""
    with open(path) as f:
        lines = [l.rstrip("\n") for l in f if l.strip()]
    for k in range(0, len(lines) - 2, 3):
        if lines[k + 1].startswith("1 ") and lines[k + 2].startswith("2 "):
            yield lines[k].strip(), lines[k + 1], lines[k + 2]


def load_tles(paths):
    """Decode TLE files with SGP4; duplicates (same NORAD id) keep the newest epoch."""
    from sgp4.api import Satrec
    best = {}
    for path in paths:
        for name, l1, l2 in read_tle_file(path):
            s = Satrec.twoline2rv(l1, l2)
            jd = s.jdsatepoch + s.jdsatepochF
            if s.satnum not in best or jd > best[s.satnum][0]:
                best[s.satnum] = (jd, name, s, l1, l2)
    ids, names, ep, a, e, i, W, w, M, l1s, l2s = ([] for _ in range(11))
    for satnum, (jd, name, s, l1, l2) in sorted(best.items()):
        n = s.no_kozai / 60.0  # rad/s (TLE mean motion)
        ids.append(satnum); names.append(name); ep.append(jd)
        a.append((MU / n ** 2) ** (1 / 3)); e.append(s.ecco); i.append(s.inclo)
        W.append(s.nodeo); w.append(s.argpo); M.append(s.mo); l1s.append(l1); l2s.append(l2)
    return Population(ids, names, np.array(ep), np.array(a), np.array(e), np.array(i),
                      np.array(W), np.array(w), np.array(M), {"tle1": l1s, "tle2": l2s})


def load_satcat(path):
    """CelesTrak SATCAT CSV -> dict NORAD id -> row dict."""
    out = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            try:
                out[int(row["NORAD_CAT_ID"])] = row
            except (KeyError, ValueError):
                pass
    return out


def load_gcat_mass(path):
    """McDowell GCAT satcat.tsv -> dict NORAD id -> mass [kg] (best available column)."""
    out = {}
    with open(path) as f:
        header = None
        for line in f:
            if line.startswith("#JCAT"):
                header = line[1:].rstrip("\n").split("\t")
                continue
            if line.startswith("#") or header is None:
                continue
            p = line.rstrip("\n").split("\t")
            row = dict(zip(header, (x.strip() for x in p)))
            try:
                satnum = int(row["Satcat"])
            except (KeyError, ValueError):
                continue
            mass = None
            for col in ("TotMass", "Mass", "DryMass"):
                try:
                    v = float(row.get(col, ""))
                    if v > 0:
                        mass = v
                        break
                except ValueError:
                    pass
            out[satnum] = {"mass": mass, "gcat_type": row.get("Type", ""), "gcat_name": row.get("Name", ""),
                           "owner": row.get("Owner", ""), "status": row.get("Status", "")}
    return out


def attach_metadata(pop, satcat, gcat):
    """Add object type, status, owner, radar size and mass columns to a Population."""
    cols = {k: [] for k in ("object_type", "ops_status", "owner", "rcs_m2", "mass_kg", "launch_date")}
    for sid in pop.ids:
        sc = satcat.get(sid, {})
        gc = gcat.get(sid, {})
        cols["object_type"].append(sc.get("OBJECT_TYPE", "UNK"))
        cols["ops_status"].append(sc.get("OPS_STATUS_CODE", ""))
        cols["owner"].append(sc.get("OWNER", ""))
        try:
            cols["rcs_m2"].append(float(sc.get("RCS", "") or "nan"))
        except ValueError:
            cols["rcs_m2"].append(math.nan)
        cols["mass_kg"].append(gc.get("mass") if gc.get("mass") is not None else math.nan)
        cols["launch_date"].append(sc.get("LAUNCH_DATE", ""))
    pop.meta.update(cols)
    return pop
