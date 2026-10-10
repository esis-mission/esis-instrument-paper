"""
The signal a single channel collects in a pixel, which the count-rate table
and the text of the Sensitivity and Cadence subsection both read.

The radiances are measured rather than modeled, as the old draft took them:
the averages of :cite:t:`Vernazza1978` over the quiet Sun, coronal holes and
active regions, and a weak active region observed by the Coronal Diagnostic
Spectrometer. Everything else is the model of the instrument that flew.
"""

import functools
import math

import astropy.units as u
import esis
import named_arrays as na
import numpy as np

from esis_instrument_paper import _distortion_model, _grids

__all__ = [
    "axis_context",
    "axis_line",
    "context_active_region",
    "context_coronal_hole",
    "contexts",
    "counts",
    "counts_image",
    "index",
    "lines",
    "noise_read",
    "num_stack",
    "num_stack_counts",
    "num_stack_required",
    "optics",
    "snr",
    "solid_angle_pixel",
]

axis_line = "line"
"""The name of the logical axis along :data:`lines`."""

axis_context = "context"
"""The name of the logical axis along :data:`contexts`."""

lines = (
    esis.flights.f1.spectrum.O_V,
    esis.flights.f1.spectrum.Mg_X_625,
)
"""
The lines whose signal is counted, as modules of :mod:`esis.flights.f1.spectrum`.

The weaker line of the :math:`\\text{Mg\\,X}` doublet lies close enough to
:math:`\\text{O\\,V}` that its image lands about 130 pixels from the image of
:math:`\\text{O\\,V}` on a field about 900 pixels across, so most pixels see
both lines, and the signal in a pixel is their sum.
"""

contexts = (
    "radiance",
    "radiance_coronal_hole",
    "radiance_active_region",
    "radiance_active_region_cds",
)
"""
The radiance of each line in each column of the count-rate table, named by
the attribute of each of :data:`lines` which holds it: the quiet Sun, a coronal
hole and an active region of :cite:t:`Vernazza1978`, and the weak active region
observed by the Coronal Diagnostic Spectrometer.
"""

context_coronal_hole = "radiance_coronal_hole"
"""The context the signal-to-noise requirement is set in."""

context_active_region = "radiance_active_region"
"""
The context the text quotes the time to collect a good image in, the active
region of :cite:t:`Vernazza1978`, as the old draft did.
"""

counts_image = 300
"""
The signal of a good image, in photons in a pixel.

The old draft's rule of thumb rather than a property of the instrument: the
text says that a good image needs about this many.
"""

_num_field = 21
"""
The number of field cells along each axis the effective area is averaged
over, the same as the distortion and vignetting figures.
"""

_num_pupil = 21
"""The number of pupil cells along each axis the effective area is summed over."""

_seed = 42
"""
The seed of the draws which place a sample inside each field and pupil cell.

The effective area is averaged over the whole field, so the draw changes it
by well under a percent, but it has to be seeded for the article to be the
same every time it is built.
"""


@functools.cache
def optics() -> esis.optics.Instrument:
    """
    The instrument that flew, with its measured coatings, gratings and
    cameras.

    Remembered, since solving for the focus and alignment of its gratings
    takes several seconds, and the table and the text both need it.
    """
    return esis.flights.f1.optics.as_built(num_distribution=0)


def _wavelength() -> na.AbstractScalar:
    """The rest wavelength of each of :data:`lines`."""
    return na.stack([line.wavelength for line in lines], axis=axis_line)


def _radiance() -> na.AbstractScalar:
    """The radiance of each of :data:`lines` in each of :data:`contexts`."""
    return na.stack(
        arrays=[
            na.stack(
                arrays=[getattr(line, context) for context in contexts],
                axis=axis_context,
            )
            for line in lines
        ],
        axis=axis_line,
    )


def _area_effective() -> na.AbstractScalar:
    """
    The effective area at each of :data:`lines`, averaged over the field of
    view and over the channels, since the table is for a typical channel.

    It includes the vignetting of the instrument that flew, which has no
    stop at the primary mirror, since it is averaged over the whole field of
    view rather than taken at its center.
    """
    instrument = optics()
    wavelength = _wavelength()
    model = instrument.system.area_effective(
        wavelength=wavelength,
        field=_grids.vertices("field", _num_field),
        pupil=_grids.vertices("pupil", _num_pupil),
        seed_field=_seed,
        seed_pupil=_seed,
    )
    return model(wavelength).mean(instrument.axis_channel)


def solid_angle_pixel() -> na.AbstractScalar:
    """
    The solid angle a pixel subtends on the sky.

    The reciprocal of the determinant of the linear terms of the distortion
    model, :math:`\\mathbf{C}_x` and :math:`\\mathbf{C}_y` in the distortion
    table, which is the solid angle at the center of the field of view and at
    the mean wavelength of the lines the model was fit at. Across the field
    of view and between these two lines it changes by less than a percent.
    """
    coefficients = _distortion_model.model().fit.coefficients.components
    x = coefficients["position.x"]
    y = coefficients["position.y"]
    determinant = x.x * y.y - x.y * y.x
    return (u.pix**2 / np.abs(determinant)).to(u.sr)


def counts() -> na.AbstractScalar:
    """
    The photons each of :data:`lines` deposits in a pixel in a single
    exposure, in each of :data:`contexts`.

    The effective area includes the absorbance of the sensor, so these are
    the photons absorbed in it.
    """
    energy = _wavelength().to(u.erg, equivalencies=u.spectral()) / u.ph
    result = (
        _radiance()
        * _area_effective()
        * solid_angle_pixel()
        * optics().camera.timedelta_exposure
        / energy
    )
    return result.to(u.ph)


def noise_read() -> u.Quantity | na.AbstractScalar:
    """
    The read noise of the sensor, as the photons of
    :math:`\\text{O\\,V}` which would free as many electrons.
    """
    sensor = optics().camera.sensor
    quantum_yield = sensor.material.quantum_yield_ideal(
        esis.flights.f1.spectrum.O_V.wavelength
    )
    return (sensor.readout_noise / quantum_yield).to(u.ph)


def snr(
    signal: u.Quantity | na.AbstractScalar,
    noise_read: u.Quantity | na.AbstractScalar,
    num: int = 1,
) -> na.AbstractScalar:
    """
    The signal-to-noise ratio of the sum of several exposures.

    The shot noise of the summed signal and the read noise of each exposure
    are added in quadrature.

    Parameters
    ----------
    signal
        The photons in a pixel in a single exposure.
    noise_read
        The read noise of a single exposure, in photons.
    num
        The number of exposures summed.
    """
    total = num * signal
    variance = total * u.ph + num * np.square(noise_read)
    return (total / np.sqrt(variance)).to(u.dimensionless_unscaled)


def num_stack(
    signal: u.Quantity | na.AbstractScalar,
    noise_read: u.Quantity | na.AbstractScalar,
    snr_min: float | u.Quantity,
) -> int:
    """
    The fewest exposures whose sum reaches a signal-to-noise ratio.

    The ratio of the sum of :math:`n` exposures grows as :math:`\\sqrt{n}`,
    so this is the least :math:`n` whose square root reaches the ratio
    sought over the ratio of a single exposure.

    Parameters
    ----------
    signal
        The photons in a pixel in a single exposure.
    noise_read
        The read noise of a single exposure, in photons.
    snr_min
        The signal-to-noise ratio to reach.
    """
    ratio = snr_min / snr(signal, noise_read)
    return math.ceil(float(na.as_named_array(np.square(ratio)).ndarray))


def index(context: str) -> dict[str, int]:
    """
    The index of one of :data:`contexts` along :data:`axis_context`.

    Parameters
    ----------
    context
        One of :data:`contexts`.
    """
    return {axis_context: contexts.index(context)}


def num_stack_required(
    signal: u.Quantity | na.AbstractScalar,
    noise_read: u.Quantity | na.AbstractScalar,
) -> int:
    """
    The fewest exposures whose sum meets the signal-to-noise ratio the
    mission required, in the context it was required in.

    Parameters
    ----------
    signal
        The photons in a pixel in a single exposure, in each of
        :data:`contexts`.
    noise_read
        The read noise of a single exposure, in photons.
    """
    return num_stack(
        signal=signal[index(context_coronal_hole)],
        noise_read=noise_read,
        snr_min=esis.flights.f1.optics.requirements().snr,
    )


def num_stack_counts(
    signal: u.Quantity | na.AbstractScalar,
    counts_min: float,
) -> int:
    """
    The fewest exposures whose sum collects a number of photons.

    Parameters
    ----------
    signal
        The photons in a pixel in a single exposure.
    counts_min
        The photons to collect.
    """
    ratio = counts_min * u.ph / signal
    return math.ceil(float(na.as_named_array(ratio).ndarray.to(u.one)))
