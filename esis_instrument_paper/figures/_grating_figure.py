"""Our measurement of the figure of each grating which flew."""

import aastex
import astropy.units as u
import esis
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np

__all__ = [
    "grating_figure",
]

_height = 2.8
"""The height of the figure in inches."""

_unit_position = u.mm
"""The unit the positions are drawn in."""

_unit_height = u.nm
"""The unit the heights of the surface are drawn in."""

_percentile = 99
"""
How far either side of zero the colors run, as a percentile of the size of
the heights of all four gratings.

The largest heights are a few pixels at the edges of the maps, two or three
times the rest, which would leave the maps themselves pale. The pixels beyond
this percentile are drawn in the darkest color.
"""


def grating_figure() -> aastex.Figure:
    """
    Our measurement of the figure of each grating which flew, over its clear
    aperture.

    The maps are the ones the instrument as built carries in the sags of its
    gratings, the same ones their slope errors in
    :func:`esis_instrument_paper.tables.surface_error` are worked out from.
    Each is drawn in the panel of the channel its grating flew in, and as it
    was measured, since which way each grating faced the interferometer about
    its :math:`x` axis is not known.
    """
    as_built = esis.flights.f1.optics.as_built(num_distribution=0)
    grating = as_built.grating
    axis = as_built.axis_channel
    aperture = grating.surface.aperture

    figure = grating.sag.figure_error
    position = figure.inputs
    height = figure.outputs.to(_unit_height)
    limit = np.nanpercentile(np.abs(height.ndarray.value), _percentile)

    fig, axs = plt.subplots(
        nrows=2,
        ncols=2,
        sharex=True,
        sharey=True,
        figsize=(aastex.column_width_inches, _height),
        constrained_layout=True,
    )

    channels = na.as_named_array(as_built.camera.channel)
    for ax, index in zip(axs.flat, np.argsort(channels.ndarray)):
        mesh = na.plt.pcolormesh(
            position.x.to(_unit_position).value,
            position.y.to(_unit_position).value,
            C=height[{axis: index}].value,
            ax=ax,
            cmap="RdBu_r",
            vmin=-limit,
            vmax=limit,
            rasterized=True,
        )
        aperture.plot(
            ax=ax,
            components=("x", "y"),
            unit=_unit_position,
            color="black",
            linewidth=0.6,
        )
        ax.set_aspect("equal")
        ax.set_title(f"Channel {channels[{axis: index}].ndarray}", fontsize="small")

    for ax in axs[1]:
        ax.set_xlabel(f"$x$ ({_unit_position:latex_inline})")
    for ax in axs[:, 0]:
        ax.set_ylabel(f"$y$ ({_unit_position:latex_inline})")
    fig.colorbar(
        mesh.ndarray.item(),
        ax=axs,
        extend="both",
        label=f"surface height ({_unit_height:latex_inline})",
    )

    result = aastex.Figure("fig:gratingFigure", position="!htb")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
Surface height of the four flight gratings over their clear apertures (black outlines), measured with an interferometer
at their centers of curvature at Montana State University.
Each map is the mean of three measurements, with the grating aligned again before each, after the reference measurement
of the interferometer, smoothed, has been subtracted from them.
Piston, tilt, and power have been removed.
A narrow border at the edge of each clear aperture, where the ruled area meets the border of the blank, is not shown.
The slope errors of the gratings in Table~\ref{table:error} are computed from these maps.
Which way each grating faced the interferometer about its $x$ axis is not known, so the maps are shown as they were
measured."""))

    return result
