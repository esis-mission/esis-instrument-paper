"""The RMS size of the spot at the center of the field, through focus."""

import dataclasses

import aastex
import astropy.units as u
import esis
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np
import utu

import esis_instrument_paper

__all__ = [
    "focus_curve",
]

num_pupil = 11
"""The number of positions along each axis of the pupil, as in the old draft."""

num_defocus = 51
"""The number of positions of the detector, as in the old draft."""

_range_defocus = 5 * u.mm
"""How far the detector is moved either way along its axis, as in the old draft."""

_height = 2.5
"""The height of the figure in inches, as in the old draft."""


def focus_curve() -> aastex.Figure:
    """
    The RMS radius of the spot at the center of the field of view of a single
    channel, as its detector is moved along its own axis, at each of the
    brightest lines in the passband.

    The lines are those of :func:`esis_instrument_paper.figures.spot_size`.
    The detector is moved from where the design puts it, and every position
    is traced at once, along an axis of its own.
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
    num_lines = esis_instrument_paper.figures.num_lines
    brightest = lines[{"line": slice(num_lines)}]
    wavelength = brightest.inputs.components["wavelength"]
    names = utu.spectrum.spectroscopic(
        ion=brightest.inputs.components["ion"],
        latex=True,
    )
    order = np.argsort(na.as_named_array(wavelength).ndarray.value)

    defocus = na.linspace(
        start=-_range_defocus,
        stop=_range_defocus,
        axis="defocus",
        num=num_defocus,
    )
    moved = dataclasses.replace(
        system,
        sensor=dataclasses.replace(
            sensor,
            transformation=na.transformations.compose(
                sensor.transformation,
                na.transformations.Cartesian3dTranslation(z=defocus),
            ),
        ),
    )
    pupil = na.Cartesian2dVectorLinearSpace(
        start=-1,
        stop=1,
        axis=na.Cartesian2dVectorArray("pupil_x", "pupil_y"),
        num=num_pupil,
    )
    radius = moved.radius_spot(
        wavelength=wavelength,
        field=na.Cartesian2dVectorArray(0, 0),
        pupil=pupil,
    )
    radius = (radius / sensor.width_pixel * u.pix).to(u.pix)

    fig, ax = plt.subplots(
        figsize=(aastex.column_width_inches, _height),
        constrained_layout=True,
    )

    for index in order:
        i = {"line": int(index)}
        w = na.as_named_array(wavelength[i]).ndarray.to_value(u.AA)
        ax.plot(
            defocus.ndarray.to_value(u.mm),
            na.value(radius[i]).ndarray_aligned(("defocus",)),
            label=rf"{names[i].ndarray} {w:.2f}\,\AA",
        )

    ax.set_xlabel(f"detector translation ({u.mm:latex_inline})")
    ax.set_ylabel(f"RMS spot radius ({u.pix:latex_inline})")
    ax.legend(bbox_to_anchor=(0.5, -0.3), loc="upper center", ncol=2)

    result = aastex.Figure("fig:focusCurve", position="!htb")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(rf"""
Focus curve for the field angle at the middle of the \ESIS\ \FOV\ for the {num_lines} brightest wavelengths
in the passband."""))

    return result
