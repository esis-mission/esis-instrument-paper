import aastex
import esis
import matplotlib.pyplot as plt

__all__ = [
    "distortion_flight",
]

_figsize = (3.4, 7.4)
"""One column wide, tall enough for five panels."""


def distortion_flight() -> aastex.Figure:
    r"""
    The time-dependent terms of the distortion fit, and the coalignment they leave.

    Drawn by :func:`esis.flights.f1.optics.plot_distortion_flight` from the
    committed tables of the fit: the pointing of the payload, the drift of
    the windows, the defocus of the primary, the focus of each sector of the
    primary about it, and the shift of every channel's sky against channel 1
    with one focus for the whole primary and with one per sector.
    """
    # usetex drops the minus sign of a negative tick label unless it is
    # written as a hyphen
    with plt.rc_context({"axes.unicode_minus": False}):
        fig, axes = plt.subplots(
            nrows=5,
            ncols=1,
            figsize=_figsize,
            sharex=True,
            constrained_layout=True,
        )
        esis.flights.f1.optics.plot_distortion_flight(axes=axes)
    for ax, loc, ncol in zip(
        axes,
        ("upper right", "upper center", "lower right", "upper center", "upper center"),
        (2, 4, 1, 2, 3),
    ):
        ax.legend(frameon=False, fontsize=7, ncol=ncol, loc=loc)
        ax.tick_params(labelsize=8)
        ax.yaxis.label.set_size(8)

    result = aastex.Figure("fig:distortionFlight", position="!ht")
    result.append(aastex.NoEscape(r"\centering"))
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
The distortion fit through the flight.
From the top: the pointing of the payload fit to each exposure against the \AIA\ scene;
the drift of each channel's windows measured from the edges of the field stop;
the defocus of the primary mirror at the field stop, the mean over its sectors, measured
from the channels against one another in every exposure and smoothed by a quadratic;
the focus of each channel's sector of the primary about that mean, measured per exposure
(dots) and as applied (lines);
and the shift of each channel's sky against channel 1, dashed with one focus for the whole
primary and solid with one per sector, with the \coalignmentThreshold\ acceptance threshold
dotted."""))
    return result
