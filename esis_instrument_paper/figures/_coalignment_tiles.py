import aastex
import esis
import matplotlib.pyplot as plt

__all__ = [
    "coalignment_tiles",
]

_frames = (0, 15)
"""The exposures drawn: the first of the flight, and the one the fit was made against."""

_figsize = (6.4, 8.6)
"""Two columns wide, four rows of three panels."""


def coalignment_tiles() -> aastex.FigureStar:
    r"""
    The tile shifts of every channel against channel 1 over the field.

    Drawn by :func:`esis.flights.f1.optics.plot_coalignment_tiles` from the
    committed acceptance tables, at the first exposure of the flight and at
    the reference exposure, at both aligned lines.
    """
    with plt.rc_context({"axes.unicode_minus": False}):
        fig, axes = plt.subplots(
            nrows=2 * len(_frames),
            ncols=3,
            figsize=_figsize,
            constrained_layout=True,
            squeeze=False,
        )
        esis.flights.f1.optics.plot_coalignment_tiles(axes=axes, frames=_frames)

    result = aastex.FigureStar("fig:coalignmentTiles", position="!ht")
    result.append(aastex.NoEscape(r"\centering"))
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
The coalignment of the channels over the field, after the fit.
Each panel shows one channel's sky against channel 1's at one exposure and one line: the
field is divided into tiles, each tile of the two channels is cross-correlated, and the
shift that best registers them is drawn as an arrow at the tile's place in the field, with a
half-pixel arrow for scale.
The title of each panel decomposes the arrows into a translation, a magnification and a
rotation of the field, and gives what remains once those are removed, which is
uncorrelated from tile to tile and is the floor of the measurement.
The first exposure of the flight is on top and the reference exposure, against which the
fit was made, below."""))
    return result
