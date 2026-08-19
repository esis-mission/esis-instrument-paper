import aastex
import matplotlib.patches
import matplotlib.pyplot as plt
import numpy as np

__all__ = [
    "schematic_moses",
]

_color_grating = "#378c8e"
"""The colour of the grating."""

_color_undispersed = "#82318c"
"""The colour of the light which is not dispersed, the :math:`m=0` order."""

_color_long = "#c33017"
"""The colour marking the longer wavelength of the two."""

_color_short = "#003acc"
"""The colour marking the shorter wavelength of the two."""

_color_both = "#e95ffa"
"""The colour of the two wavelengths superimposed, as they are at :math:`m=0`."""


def schematic_moses() -> aastex.Figure:
    """
    A diagram of how the three orders of MOSES fall onto its three detectors.

    Two features, ``A`` at the longer wavelength and ``B`` at the shorter, are
    superimposed in the undispersed order and pull apart in opposite directions
    in the two dispersed orders.
    """
    # every length is a fraction of the width of the figure, with the origin on
    # the optical axis
    x_grating = 0.065
    x_detector = 0.855
    x_face = 0.838
    x_entrance = 1

    # half the height of the illuminated part of the grating, which is where
    # the two edge rays of every beam leave from
    aperture = 0.08

    # how far the dispersed detectors sit off the axis, and how far the two
    # wavelengths land apart on them
    separation = 0.229
    dispersion = 0.025

    height_detector = 0.135
    width_detector = 0.040

    # the outboard detectors are canted to face the grating, which is drawn by
    # lifting the far edge of the tile
    cant = 0.02

    height = 0.6033
    fig = plt.figure(
        figsize=(aastex.column_width_inches, height * aastex.column_width_inches),
    )
    # the diagram is its own frame, so the axes fills the figure exactly and
    # every coordinate above is a fraction of the width of the figure
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_axis_off()
    ax.set_aspect("equal")
    ax.set_xlim(0, 1)
    ax.set_ylim(-height / 2, height / 2)

    # the grating, rendered as a ruled ellipse to suggest the grooves
    grating = matplotlib.patches.Ellipse(
        xy=(x_grating - 0.026, 0),
        width=0.078,
        height=0.216,
        facecolor=_color_grating,
        edgecolor="none",
        zorder=1,
    )
    ax.add_patch(grating)
    for y in np.linspace(-0.108, 0.108, num=61):
        groove = ax.plot(
            [x_grating - 0.07, x_grating + 0.03],
            [y, y],
            color="white",
            linewidth=0.3,
            zorder=2,
        )
        groove[0].set_clip_path(grating)

    # the light entering the instrument, which is undispersed until it reaches
    # the grating
    for sign in (1, -1):
        ax.plot(
            [x_grating, x_entrance],
            [sign * aperture, sign * aperture],
            color=_color_undispersed,
            linewidth=1.3,
            zorder=0,
        )
        # the head sits in from the edge, where there is room for it
        ax.annotate(
            "",
            xy=(0.86, sign * aperture),
            xytext=(0.95, sign * aperture),
            arrowprops={
                "arrowstyle": "->",
                "color": _color_undispersed,
                "linewidth": 1,
                "mutation_scale": 16,
                "shrinkA": 0,
                "shrinkB": 0,
            },
            zorder=0,
        )

    # each order is a beam converging from the two edges of the grating onto
    # one point of one detector
    orders = [
        (0, _color_undispersed),
        (separation, _color_long),
        (separation - dispersion, _color_short),
        (-separation, _color_long),
        (-separation + dispersion, _color_short),
    ]
    for y, color in orders:
        for sign in (1, -1):
            ax.plot(
                [x_grating, x_face],
                [sign * aperture, y],
                color=color,
                linewidth=1.3,
                zorder=0,
            )

    # the detectors, each a tile with vertical edges, the far one raised on the
    # orders which are canted
    for y, sign in ((separation, 1), (0, 0), (-separation, -1)):
        near = y - sign * cant / 2
        far = y + sign * cant / 2
        ax.add_patch(
            matplotlib.patches.Polygon(
                [
                    (x_detector - width_detector / 2, near + height_detector / 2),
                    (x_detector + width_detector / 2, far + height_detector / 2),
                    (x_detector + width_detector / 2, far - height_detector / 2),
                    (x_detector - width_detector / 2, near - height_detector / 2),
                ],
                facecolor="black",
                zorder=2,
            )
        )

    # the two features, superimposed at m=0 and pulled apart either side of it
    letters = [
        (separation, "A", _color_long),
        (separation - dispersion, "B", _color_short),
        (0.006, "A", _color_both),
        (-0.006, "B", _color_both),
        (-separation, "A", _color_long),
        (-separation + dispersion, "B", _color_short),
    ]
    for y, letter, color in letters:
        # written as maths so that the letters come out bold whether or not the
        # document is rendering text through LaTeX, which ignores `fontweight`
        ax.text(
            x=x_detector,
            y=y,
            s=rf"$\mathbf{{{letter}}}$",
            color=color,
            fontsize=15.5,
            ha="center",
            va="center",
            zorder=3,
        )

    result = aastex.Figure("fig:mosesSchematic", position="!ht")
    result.append(aastex.NoEscape(r"\centering"))
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
Schematic diagram of the \MOSES\ instrument.
Incident light from the right forms an undispersed image on the central $m=0$ \CCD.
Dispersed images are formed on the outboard $m=\pm1$ \CCDs.
The imaging of longer and shorter wavelengths is indicated by the use of red and
blue letters respectively."""))

    return result
