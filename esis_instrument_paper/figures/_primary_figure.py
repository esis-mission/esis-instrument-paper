"""Our measurement of the figure of the primary mirror which flew."""

import aastex
import astropy.units as u
import esis
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np

__all__ = [
    "primary_figure",
]

_height = 2.6
"""The height of the figure in inches."""

_unit_position = u.mm
"""The unit the positions are drawn in."""

_unit_height = u.nm
"""The unit the heights of the surface are drawn in."""


def primary_figure() -> aastex.Figure:
    """
    Our measurement of the figure of the primary mirror which flew, over its
    clear aperture.

    The map is the one the instrument as built carries in the sag of its
    primary mirror, the same one its slope error in
    :func:`esis_instrument_paper.tables.surface_error` is worked out from.
    It is drawn as it was stored, since which way the mirror was turned about
    its axis in flight is not known.
    The colors run as far either side of zero as the largest height inside
    the clear aperture.
    """
    as_built = esis.flights.f1.optics.as_built(num_distribution=0)
    primary = as_built.primary_mirror
    aperture = primary.surface.aperture

    figure = primary.sag.figure_error
    position = figure.inputs
    inside = aperture(na.Cartesian3dVectorArray(position.x, position.y, 0 * u.mm))
    height = np.where(inside, figure.outputs, np.nan).to(_unit_height)
    limit = np.nanmax(np.abs(height)).ndarray.value

    fig, ax = plt.subplots(
        figsize=(aastex.column_width_inches, _height),
        constrained_layout=True,
    )

    mesh = na.plt.pcolormesh(
        position.x.to(_unit_position).value,
        position.y.to(_unit_position).value,
        C=height.value,
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
    ax.set_xlabel(f"$x$ ({_unit_position:latex_inline})")
    ax.set_ylabel(f"$y$ ({_unit_position:latex_inline})")
    fig.colorbar(
        mesh.ndarray.item(),
        ax=ax,
        label=f"surface height ({_unit_height:latex_inline})",
    )

    result = aastex.Figure("fig:primaryFigure", position="!htb")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
Surface height of the flight primary mirror over its clear aperture (black outline), measured with an interferometer
at its center of curvature at Montana State University.
The map is the mean of two measurements, with the mirror turned half a turn about its axis between them.
Piston, tilt, power, and the spherical aberration of a paraboloid seen from its center of curvature have been removed.
The disk at the center, behind the central obscuration, was not measured.
The slope error of the primary mirror in Table~\ref{table:error} is computed from this map.
Which way the mirror was turned about its axis in flight is not known, so the map is shown as it was
measured."""))

    return result
