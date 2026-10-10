"""
The distortion model of a single channel, which the distortion figures and
the distortion table all read.

It is fit by :meth:`optika.systems.SequentialSystem.distortion` at the lines
and over the cells of the vignetting figure.
"""

import esis
import optika

from esis_instrument_paper import _grids

__all__ = [
    "degree",
    "degree_linear",
    "model",
    "optics",
]

_num_field = 21
"""
The number of field positions sampled along each axis.

The same as in the vignetting figure, so that the two maps are drawn over the
same cells.
"""

_num_pupil = 21
"""
The number of pupil positions sampled along each axis.

Where a field cell lands on the detector is the mean over its pupil samples,
and that mean hardly depends on how finely the pupil is sampled: four times
as finely moves the largest residual of the quadratic fit by about a
thousandth of a pixel. So the residual is the distortion itself rather than
the quadrature, and the pupil need not be sampled as finely as the vignetting
figure samples it to resolve the area of the pupil.
"""

_seed_pupil = 42
"""
The seed of the random draw which places a sample inside each pupil cell.

The same as in the vignetting figure. The draw has to be seeded for the
article to be the same every time it is built.
"""

_seed_field = None
"""
The seed of the random draw which places a sample inside each field cell.

There is none, as in the vignetting figure, so the field is taken at the
centers of its cells and the residual is drawn as a regular grid.
"""

degree = 2
"""
The degree of the distortion model the text writes out.

The text gives the model as a quadratic in position and wavelength, and the
residual figure is the evidence that a quadratic is enough.
"""

degree_linear = 1
"""The degree of the model the residual figure compares the quadratic with."""


def optics() -> esis.optics.Instrument:
    """A single channel of the flight instrument, as designed."""
    return esis.flights.f1.optics.design_single(num_distribution=0)


def model(
    degree: int = degree,
) -> optika.distortion.PolynomialDistortionModel:
    """
    Fit a polynomial to where the field of a single channel lands on its
    detector, as a function of field position and wavelength.

    Parameters
    ----------
    degree
        The degree of the polynomial, the one the text writes out by default.
    """
    return optics().system.distortion(
        wavelength=_grids.wavelength(),
        field=_grids.vertices("field", _num_field),
        pupil=_grids.vertices("pupil", _num_pupil),
        degree=degree,
        seed_field=_seed_field,
        seed_pupil=_seed_pupil,
    )
