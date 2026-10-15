"""The spots the design makes at O V, across its field of view."""

import aastex
import astropy.units as u
import esis
import matplotlib.colors
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np

__all__ = [
    "spot_diagrams",
]

num_field = 4
"""The number of field angles along each axis of the field of view."""

num_pupil = 201
"""The number of positions along each axis of the pupil, for each spot."""

_margin = 0.99
"""
How far out the outermost field angles are, as a fraction of the way from
the center of the field of view to the edge of the box which bounds it.

The flat edges of the octagonal field stop are the edges of that box, and a
field angle exactly on one lands exactly on the edge of the field stop, where
rounding decides whether it passes. Just inside, the spot is that of the edge
of the field of view.
"""

_seed = 0
"""
The seed of the stratified random grid of positions on the pupil, so that the
figure is the same every time it is made.
"""

_num_bins = 100
"""The number of bins along each axis of the pixel which frames each spot."""

_height = 2.6
"""The height of the figure in inches, as in the old draft."""

_dpi = 300
"""The resolution of the histograms, which are drawn as images."""


def spot_diagrams() -> aastex.Figure:
    """
    The spot which each of a grid of field angles makes on the detector of a
    single channel at O V, framed by a box one pixel across.

    Each spot is a histogram of where the rays through a stratified random
    grid of positions on the pupil land, about the centroid of the spot. The
    field angles at the corners of the grid are outside the octagonal field
    stop, so they make no spot, and are left blank.
    """
    optics = esis.flights.f1.optics.design_single(num_distribution=0)
    system = optics.system
    sensor = system.sensor
    wavelength = esis.flights.f1.spectrum.O_V.wavelength

    axis_field = ("field_x", "field_y")
    axis_pupil = ("pupil_x", "pupil_y")
    field = na.Cartesian2dVectorLinearSpace(
        start=-_margin,
        stop=_margin,
        axis=na.Cartesian2dVectorArray(*axis_field),
        num=num_field,
    )
    pupil = na.Cartesian2dVectorStratifiedRandomSpace(
        start=-1,
        stop=1,
        axis=na.Cartesian2dVectorArray(*axis_pupil),
        num=num_pupil,
        seed=_seed,
    )
    rayfunction = system.rayfunction(
        wavelength=wavelength,
        field=field,
        pupil=pupil,
        efficiency=False,
    )
    rays = rayfunction.outputs
    angle = rayfunction.inputs.field.to(u.arcmin)

    # where each ray lands, in pixels, from the centroid of its spot
    position = sensor.pixels(rays.position.xy)
    where = rays.unvignetted
    count = where.sum(axis_pupil)
    centroid = position.sum(axis_pupil, where=where) / np.maximum(count, 1)
    offset = (position - centroid).to(u.pix)

    edges = np.linspace(-0.5, 0.5, _num_bins + 1)
    histograms = {}
    for ix in range(num_field):
        for iy in range(num_field):
            index = {axis_field[0]: ix, axis_field[1]: iy}
            shape = na.broadcast_shapes(
                na.shape(offset[index]),
                na.shape(where[index]),
            )
            lit = where[index].broadcast_to(shape).ndarray
            if not lit.any():
                continue
            x = offset.x[index].broadcast_to(shape).ndarray.value[lit]
            y = offset.y[index].broadcast_to(shape).ndarray.value[lit]
            histograms[ix, iy], _, _ = np.histogram2d(x, y, bins=(edges, edges))

    peak = max(h.max() for h in histograms.values())
    norm = matplotlib.colors.PowerNorm(gamma=1 / 3, vmin=0, vmax=peak)

    fig, axs = plt.subplots(
        nrows=num_field,
        ncols=num_field,
        figsize=(aastex.column_width_inches, _height),
        squeeze=False,
        constrained_layout=True,
    )

    mappable = None
    for row in range(num_field):
        for ix in range(num_field):
            # the top row is the top of the field of view
            iy = num_field - 1 - row
            ax = axs[row, ix]
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_aspect("equal")
            if row == 0:
                angle_x = angle.x[{axis_field[0]: ix, axis_field[1]: iy}]
                ax.set_title(f"${na.value(angle_x).ndarray:.1f}'$")
            if ix == num_field - 1:
                angle_y = angle.y[{axis_field[0]: ix, axis_field[1]: iy}]
                ax.text(
                    x=1.1,
                    y=0.5,
                    s=f"${na.value(angle_y).ndarray:.1f}'$",
                    transform=ax.transAxes,
                    va="center",
                )
            if (ix, iy) not in histograms:
                for spine in ax.spines.values():
                    spine.set_visible(False)
                continue
            mappable = ax.pcolormesh(
                edges,
                edges,
                histograms[ix, iy].T,
                cmap="gray_r",
                norm=norm,
                rasterized=True,
            )

    fig.colorbar(mappable, ax=axs)

    result = aastex.Figure("fig:psf", position="!htb")
    # the histograms are drawn as images, which are much smaller than
    # their thousands of cells drawn one at a time
    result.add_fig(fig, width=None, dpi=_dpi)
    result.add_caption(aastex.NoEscape(rf"""
Raytraced spot diagrams for \OV\ with ${num_field} \times {num_field}$ field angles across the \FOV.
The box around each spot represents a single pixel on the detector.
Each spot was traced using a stratified random grid across the pupil with ${num_pupil} \times {num_pupil}$
positions per spot."""))

    return result
