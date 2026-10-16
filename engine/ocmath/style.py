"""Orbital Curbside chart style (matplotlib), validated with the dataviz palette checker.

Two themes share one set of roles:
  * "deck"  -- deep-space navy surface for slides and the simulation
  * "paper" -- near-white surface for the research paper

Categorical slots (validated adjacent-pair CVD-safe in both modes):
  1  TRUCK   brand orange  -- always "our truck / Orbital Curbside"
  2  OTHER   blue          -- single-object missions, competitors, chemical
  3  THIRD   aqua
Context data (e.g. active satellites) is drawn in a recessive neutral, never a slot.
"""
import matplotlib as mpl
import matplotlib.pyplot as plt

THEMES = {
    "deck": {
        "surface": "#0b1020", "text": "#eef0f6", "text2": "#aab1c4", "muted": "#5d6680",
        "grid": "#222a40", "truck": "#e8620c", "other": "#3987e5", "third": "#199e70",
        # ordinal blue ramp (dark-mode safe end first)
        "ramp": ["#184f95", "#256abf", "#3987e5", "#6da7ec", "#9ec5f4"],
    },
    "paper": {
        "surface": "#fcfcfb", "text": "#0b0b0b", "text2": "#52514e", "muted": "#b9b8b2",
        "grid": "#e7e6e1", "truck": "#e8620c", "other": "#2a78d6", "third": "#1baf7a",
        "ramp": ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#0d366b"],
    },
}


def use(theme="paper"):
    t = THEMES[theme]
    mpl.rcParams.update({
        "figure.facecolor": t["surface"], "axes.facecolor": t["surface"], "savefig.facecolor": t["surface"],
        "axes.edgecolor": t["muted"], "axes.labelcolor": t["text2"], "axes.titlecolor": t["text"],
        "xtick.color": t["text2"], "ytick.color": t["text2"], "text.color": t["text"],
        "axes.grid": True, "grid.color": t["grid"], "grid.linewidth": 0.6,
        "axes.spines.top": False, "axes.spines.right": False,
        "font.family": "DejaVu Sans", "font.size": 10.5, "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.titlelocation": "left", "legend.frameon": False, "lines.linewidth": 2.0,
        "figure.dpi": 110, "savefig.dpi": 200, "savefig.bbox": "tight",
    })
    return t


def save(fig, path_stem):
    """Save PNG (slides/paper) and SVG (crisp scaling)."""
    fig.savefig(f"{path_stem}.png")
    fig.savefig(f"{path_stem}.svg")
    plt.close(fig)
