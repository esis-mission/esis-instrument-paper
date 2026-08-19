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
    x_entrance = 1

    # The light is drawn over the grating and the detectors it lands on, so
    # that a beam reads as reflecting off the one and converging onto the
    # other, rather than disappearing behind either. Only the letters sit on
    # top of it.
    zorder_grating = 1
    zorder_detector = 2
    zorder_light = 3
    zorder_letter = 4

    # half the height of the illuminated part of the grating, which is where
    # the two edge rays of every beam leave from
    aperture = 0.08

    # how far the dispersed detectors sit off the axis, and how far the two
    # wavelengths land apart on them
    separation = 0.229
    dispersion = 0.042

    # the two wavelengths straddle the centre of each dispersed detector, the
    # longer one always landing further from the axis
    position_long = separation + dispersion / 2
    position_short = separation - dispersion / 2

    height_detector = 0.135
    width_detector = 0.058

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

    # The grating is drawn as a disc with some thickness rather than a flat
    # ellipse: a back face, the cylindrical wall between them, and the ruled
    # front face. Only the wall and the sliver of the back face are ever seen,
    # and they are what give the grating its edge.
    width_grating = 0.0525
    height_grating = 0.215
    x_front_grating = 0.054
    depth_grating = 0.0276

    x_back_grating = x_front_grating - depth_grating

    ax.add_patch(
        matplotlib.patches.Ellipse(
            xy=(x_back_grating, 0),
            width=width_grating,
            height=height_grating,
            facecolor=_color_grating,
            edgecolor="none",
            zorder=zorder_grating,
        )
    )
    ax.add_patch(
        matplotlib.patches.Rectangle(
            xy=(x_back_grating, -height_grating / 2),
            width=depth_grating,
            height=height_grating,
            facecolor=_color_grating,
            edgecolor="none",
            zorder=zorder_grating,
        )
    )

    # the rim of the front face, which is the only thing separating it from the
    # body behind, since the two are the same colour
    face = matplotlib.patches.Ellipse(
        xy=(x_front_grating, 0),
        width=width_grating,
        height=height_grating,
        facecolor=_color_grating,
        edgecolor="white",
        linewidth=0.4,
        zorder=zorder_grating + 0.1,
    )
    ax.add_patch(face)

    for y in np.linspace(-height_grating / 2, height_grating / 2, num=31):
        groove = ax.plot(
            [x_front_grating - width_grating, x_front_grating + width_grating],
            [y, y],
            color="white",
            linewidth=0.3,
            dashes=(2.5, 1.2),
            zorder=zorder_grating + 0.2,
        )
        groove[0].set_clip_path(face)

    # the light entering the instrument, which is undispersed until it reaches
    # the grating
    for sign in (1, -1):
        ax.plot(
            [x_grating, x_entrance],
            [sign * aperture, sign * aperture],
            color=_color_undispersed,
            linewidth=1.3,
            zorder=zorder_light,
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
            zorder=zorder_light,
        )

    # each order is a beam converging from the two edges of the grating onto
    # one point of one detector
    orders = [
        (0, _color_undispersed),
        (position_long, _color_long),
        (position_short, _color_short),
        (-position_long, _color_long),
        (-position_short, _color_short),
    ]
    for y, color in orders:
        for sign in (1, -1):
            ax.plot(
                [x_grating, x_detector],
                [sign * aperture, y],
                color=color,
                linewidth=1.3,
                zorder=zorder_light,
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
                zorder=zorder_detector,
            )
        )

    # the two features, superimposed at m=0 and pulled apart either side of it
    letters = [
        (position_long, "A", _color_long),
        (position_short, "B", _color_short),
        (0.006, "A", _color_both),
        (-0.006, "B", _color_both),
        (-position_long, "A", _color_long),
        (-position_short, "B", _color_short),
    ]
    for y, letter, color in letters:
        # written as maths so that the letters come out bold whether or not the
        # document is rendering text through LaTeX, which ignores `fontweight`
        ax.text(
            x=x_detector,
            y=y,
            s=rf"$\mathbf{{{letter}}}$",
            color=color,
            fontsize=13,
            ha="center",
            va="center",
            zorder=zorder_letter,
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
