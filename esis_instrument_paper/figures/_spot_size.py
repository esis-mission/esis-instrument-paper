"""The RMS size of the spots across the field of view, at each of the brightest lines."""

import aastex
import astropy.units as u
import esis
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np
import utu

import esis_instrument_paper

__all__ = [
    "num_lines",
    "spot_size",
]

num_lines = 3
"""The number of the brightest lines in the passband to show."""

num_field = 15
"""The number of field positions along each axis of the field of view."""

num_pupil = 15
"""The number of positions along each axis of the pupil, for each spot."""

_seed = 0
"""
The seed of the stratified random grid of positions on the pupil, so that the
figure is the same every time it is made.
"""

_height = 2.5
"""The height of the figure in inches, as in the old draft."""

_dpi = 300
"""The resolution of the maps, which are drawn as images."""


def spot_size() -> aastex.FigureStar:
    """
    The RMS radius of the spot at each position in the field of view of a
    single channel, at each of the brightest lines in the passband.

    The lines are the brightest of the ones the passband figure labels, in
    order of wavelength. A spot which misses the detector, as part of the
    image of the field stop at He I does, is left blank.
    """
    optics = esis.flights.f1.optics.design_single(num_distribution=0)
    system = optics.system
    sensor = system.sensor

    # the same arguments as the passband figure, which reads the lines from
    # the same cache
    lines = esis_instrument_paper.lines(
        wavelength_min=optics.wavelength_min.to(u.AA).ndarray,
        wavelength_max=optics.wavelength_max.to(u.AA).ndarray,
    )
    brightest = lines[{"line": slice(num_lines)}]
    wavelength = brightest.inputs.components["wavelength"]
    names = utu.spectrum.spectroscopic(
        ion=brightest.inputs.components["ion"],
        latex=True,
    )
    order = np.argsort(na.as_named_array(wavelength).ndarray.value)

    # the spots are traced at the centers of a grid of cells, and drawn on
    # their vertices
    axis_field = ("field_x", "field_y")
    centers = na.Cartesian2dVectorLinearSpace(
        start=-1,
        stop=1,
        axis=na.Cartesian2dVectorArray(*axis_field),
        num=num_field,
        centers=True,
    )
    vertices = na.Cartesian2dVectorLinearSpace(
        start=-1,
        stop=1,
        axis=na.Cartesian2dVectorArray(*axis_field),
        num=num_field + 1,
    )
    pupil = na.Cartesian2dVectorStratifiedRandomSpace(
        start=-1,
        stop=1,
        axis=na.Cartesian2dVectorArray("pupil_x", "pupil_y"),
        num=num_pupil,
        seed=_seed,
    )

    radius = system.spot_size_rms(
        wavelength=wavelength,
        field=centers,
        pupil=pupil,
    )
    radius = (radius / sensor.width_pixel * u.pix).to(u.pix)

    # The normalized field spans the box which bounds the field of view, so
    # the vertices of the cells are that box, divided evenly.
    field_min = system.field_min
    field_max = system.field_max
    angle = field_min + (field_max - field_min) * (vertices + 1) / 2
    angle = angle.to(u.arcmin)
    shape = na.shape(angle)
    x = angle.x.broadcast_to(shape).ndarray_aligned(axis_field).value
    y = angle.y.broadcast_to(shape).ndarray_aligned(axis_field).value

    values = na.value(radius)
    vmin = np.nanmin(values.ndarray)
    vmax = np.nanmax(values.ndarray)

    fig, axs = plt.subplots(
        ncols=num_lines,
        figsize=(aastex.text_width_inches, _height),
        sharex=True,
        sharey=True,
        constrained_layout=True,
    )

    for ax, index in zip(axs, order):
        i = {"line": int(index)}
        c = values[i].broadcast_to(na.shape(centers)).ndarray_aligned(axis_field)
        mesh = ax.pcolormesh(
            x,
            y,
            c,
            vmin=vmin,
            vmax=vmax,
            cmap="viridis",
            rasterized=True,
        )
        w = na.as_named_array(wavelength[i]).ndarray.to_value(u.AA)
        ax.set_title(rf"{names[i].ndarray} {w:.2f}\,\AA")
        ax.set_aspect("equal")
        ax.set_xlabel(f"field $x$ ({u.arcmin:latex_inline})")
    axs[0].set_ylabel(f"field $y$ ({u.arcmin:latex_inline})")

    fig.colorbar(mesh, ax=axs, label=f"RMS spot radius ({u.pix:latex_inline})")

    # The maps are drawn as images, since a viewer draws a seam between the
    # cells of a map drawn as vectors.
    result = aastex.FigureStar("fig:spotSize", position="!htb")
    result.add_fig(fig, width=aastex.NoEscape(r"\textwidth"), dpi=_dpi)
    result.add_caption(aastex.NoEscape(rf"""
2D histogram of RMS spot sizes for the {num_lines} brightest wavelengths in the \ESIS\ passband.
Each wavelength has ${num_field} \times {num_field}$ field points across the \FOV, and each field point
has a stratified random grid containing ${num_pupil} \times {num_pupil}$ pupil positions.
The \HeI\ line appears cropped since it is cut off by the edge of the detector."""))

    return result
