import pathlib

import aastex
import matplotlib.pyplot as plt

__all__ = [
    "grating_mount",
]

_path = pathlib.Path(__file__).parent / "static/secondary_mount.png"
"""
A rendering of the solid model of the secondary mount, the one the old draft
drew this figure from.
"""

_labels = (
    ("Tuffet", (1000, 550), (250, 250)),
    ("Backplate", (1010, 760), (150, 770)),
    ("Bipod", (1130, 550), (1460, 120)),
    ("Grating", (1340, 650), (1740, 700)),
)
"""
Each label, the point of the rendering it marks, and where it is written,
both in pixels of the rendering, as the old draft placed them.
"""


def grating_mount() -> aastex.Figure:
    """
    A rendering of the solid model of the secondary mount, which holds the
    gratings, with its parts labeled.
    """
    fig, ax = plt.subplots(
        figsize=(aastex.column_width_inches, 3),
        constrained_layout=True,
    )

    ax.imshow(plt.imread(_path))
    ax.set_axis_off()

    for text, xy, xytext in _labels:
        ax.annotate(
            text=text,
            xy=xy,
            xytext=xytext,
            arrowprops={
                "arrowstyle": "->",
                "linewidth": 0.75,
                "relpos": (0.5, 0.5),
            },
            ha="center",
        )

    result = aastex.Figure("fig:gratingMount", position="!htb")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
A solid model of the \ESIS\ secondary mount.
Each trapezoidal grating is supported and attached to its backplate by three bonded, titanium bipods.
All mounted gratings sit on the ``tuffet'' and are mounted with three spherical washers.
This allows independent tip/tilt adjustment of each grating, and for all of them to be removed/reinstalled
without compromising alignment and focus."""))

    return result
