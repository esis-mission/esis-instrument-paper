"""
The image of a point source made by a single channel at O V, with diffraction:
its point-spread function and its modulation transfer function (MTF), as
designed and as built.

Both come from the Huygens point-spread function of
:meth:`optika.systems.SequentialSystem.psf`, which traces a regular grid of
rays through the channel, keeping track of the optical path of each ray, and
propagates the wavefield on the last surface before the detector to the
detector with the Rayleigh-Sommerfeld diffraction integral. The channel as
built carries the measured figures of its primary mirror and grating in the
optical path of its rays.
"""

import functools

import astropy.units as u
import esis
import named_arrays as na
import numpy as np
import optika

__all__ = [
    "axis",
    "axis_field",
    "channel",
    "field",
    "frequency_sky",
    "mtf",
    "num_image",
    "num_mtf",
    "num_pupil",
    "psf",
    "system",
    "wavelength",
    "width_image",
    "width_mtf",
]

wavelength = esis.flights.f1.spectrum.O_V.wavelength
"""The wavelength of the line the instrument was designed around."""

channel = 1
"""
The channel whose optics as built are modeled, the same channel that
:func:`esis.flights.f1.optics.design_single` models as designed.
"""

axis_field = "field_psf"
"""The logical axis of the field angles of the point-spread functions."""

field = na.Cartesian2dVectorArray(
    x=na.ScalarArray(np.array([0, 0]), axes=axis_field),
    y=na.ScalarArray(np.array([0, 0.9]), axes=axis_field),
)
"""
The field angles of the point-spread functions, in normalized coordinates:
the center of the field of view, and a point off axis, nine tenths of the way
from the center to the edge of the field of view, perpendicular to the
dispersion.
"""

axis = ("psf_x", "psf_y")
"""The two logical axes of the grid of positions on the detector."""

num_pupil = 151
"""
The number of rays along each axis of the grid of rays across the beam.

The grid of rays aliases the image at several hundred microns from it, far
outside either grid of positions on the detector.
"""

width_image = 80 * u.um
"""
The width of the grid of positions on which the image is drawn.

The grid is centered on where the rays land, and the measured figures move
the image of the channel as built about half a pixel from there.
"""

num_image = 161
"""The number of positions along each axis of the grid the image is drawn on."""

width_mtf = 600 * u.um
"""
The width of the grid of positions from which the MTF is computed.

The MTF is computed from the light which lands on this grid. The measured
figures scatter some of the light of the channel as built beyond it, which
the MTF leaves out.
"""

num_mtf = 301
"""
The number of positions along each axis of the grid the MTF is computed from,
which samples the MTF out past its cutoff.
"""


@functools.cache
def system(as_built: bool) -> optika.systems.SequentialSystem:
    """
    The optical system of :data:`channel`, as designed or as built.

    Parameters
    ----------
    as_built
        Whether to model the channel as built, with the measured figures of
        its optics, instead of as designed.
    """
    if not as_built:
        return esis.flights.f1.optics.design_single(num_distribution=0).system
    instrument = esis.flights.f1.optics.as_built(num_distribution=0)
    channels = na.as_named_array(instrument.camera.channel).ndarray
    index = list(channels).index(channel)
    return instrument[{instrument.axis_channel: index}].system


@functools.cache
def psf(as_built: bool) -> na.FunctionArray:
    """
    The point-spread function of :data:`channel` at each of the field angles
    :data:`field`, on a grid of positions on the detector :data:`width_image`
    wide, centered on the image of each field angle.

    The intensity sums to one over the grid.

    Parameters
    ----------
    as_built
        Whether to model the channel as built, with the measured figures of
        its optics, instead of as designed.
    """
    return system(as_built).psf(
        wavelength=wavelength,
        field=field,
        width_sensor=width_image,
        num_sensor=num_image,
        num_pupil=num_pupil,
        axis=axis,
    )


@functools.cache
def mtf(as_built: bool) -> na.FunctionArray:
    """
    The MTF of :data:`channel` at each of the field angles :data:`field`,
    from its point-spread function on a grid of positions on the detector
    :data:`width_mtf` wide.

    The inputs are the spatial frequencies on the detector along its two
    axes.

    Parameters
    ----------
    as_built
        Whether to model the channel as built, with the measured figures of
        its optics, instead of as designed.
    """
    psf = system(as_built).psf(
        wavelength=wavelength,
        field=field,
        width_sensor=width_mtf,
        num_sensor=num_mtf,
        num_pupil=num_pupil,
        axis=axis,
    )
    return optika.wavefields.mtf(
        intensity=psf.outputs,
        position=psf.inputs.position,
        axis=axis,
    )


def frequency_sky(
    frequency: na.AbstractCartesian2dVectorArray,
) -> na.Cartesian2dVectorArray:
    """
    Turn spatial frequencies on the detector into spatial frequencies on the
    sky, with the plate scale of the channel as designed along each axis of
    the detector.

    Parameters
    ----------
    frequency
        The spatial frequencies on the detector along each of its axes.
    """
    instrument = esis.flights.f1.optics.design_single(num_distribution=0)
    plate_scale = instrument.system.plate_scale(wavelength)
    width_pixel = instrument.camera.sensor.width_pixel / u.pix
    scale = plate_scale / width_pixel
    return na.Cartesian2dVectorArray(
        x=(frequency.x / scale.x).to(1 / u.arcsec),
        y=(frequency.y / scale.y).to(1 / u.arcsec),
    )
