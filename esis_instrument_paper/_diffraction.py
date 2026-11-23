"""
The image of a point source made by a single channel at O V, with diffraction:
its point-spread function and its modulation transfer function (MTF), as
designed and as built.

Both come from the Huygens point-spread function of
:meth:`optika.systems.SequentialSystem.psf`, which traces a regular grid of
rays through the channel, keeping track of the optical path of each ray, and
propagates the wavefield on the last surface before the detector to the
detector with the Rayleigh-Sommerfeld diffraction integral, then spreads the
image into the diffraction orders of the mesh which supports the filter. The
channel as built carries the measured figures of its primary mirror and
grating in the optical path of its rays.
"""

import functools

import astropy.units as u
import esis
import named_arrays as na
import numpy as np
import optika

from esis_instrument_paper import _error_budget

__all__ = [
    "angle_corner",
    "axis",
    "axis_field",
    "channel",
    "field",
    "fraction_field",
    "frequency_sky",
    "mtf",
    "mtf_requirement",
    "num_image",
    "num_mtf",
    "num_pupil",
    "position_field_stop",
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

fraction_field = 0.9
"""
How far the point off axis is from the center of the field stop to one of its
corners, as a fraction of the way.

The Huygens point-spread function leaves out diffraction by the field stop,
which is accurate away from its edges.
"""

angle_corner = -90 * u.deg
"""
The direction of the corner of the octagonal field stop toward which the
point off axis lies, in the frame of the field stop.

Of the points :data:`fraction_field` of the way out around the field of view,
the MTF of the channel as built at the spatial frequency of the resolution
requirement is lowest toward this corner.
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

The MTF is normalized to the power of the whole beam, so the light which the
mesh of the filter diffracts, and the measured figures of the channel as built
scatter, beyond this grid lowers it.
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
    :func:`field`, on a grid of positions on the detector :data:`width_image`
    wide, centered on the image of each field angle.

    It includes the diffraction by the mesh which supports the filter, which
    adds copies of the image along the wires of the mesh. The intensity is
    per unit area, normalized to the power of the beam, so its integral over
    the grid is the fraction of the light which lands on it.

    Parameters
    ----------
    as_built
        Whether to model the channel as built, with the measured figures of
        its optics, instead of as designed.
    """
    return system(as_built).psf(
        wavelength=wavelength,
        field=field(as_built),
        normalized_field=False,
        width_sensor=width_image,
        num_sensor=num_image,
        num_pupil=num_pupil,
        axis=axis,
    )


@functools.cache
def mtf(as_built: bool, mesh: bool = True) -> na.FunctionArray:
    """
    The MTF of :data:`channel` at each of the field angles :func:`field`,
    from its point-spread function on a grid of positions on the detector
    :data:`width_mtf` wide.

    The inputs are the spatial frequencies on the detector along its two
    axes. The MTF is normalized to the power of the whole beam, so at zero
    frequency it is the fraction of the light which lands on the grid.

    Parameters
    ----------
    as_built
        Whether to model the channel as built, with the measured figures of
        its optics, instead of as designed.
    mesh
        Whether to include the diffraction by the mesh which supports the
        filter.
    """
    psf = system(as_built).psf(
        wavelength=wavelength,
        field=field(as_built),
        normalized_field=False,
        width_sensor=width_mtf,
        num_sensor=num_mtf,
        num_pupil=num_pupil,
        axis=axis,
        mesh=mesh,
    )
    return optika.wavefields.mtf(
        intensity=psf.outputs,
        position=psf.inputs.position,
        axis=axis,
        normalize=False,
    )


def mtf_requirement(as_built: bool, mesh: bool = True) -> na.Cartesian2dVectorArray:
    """
    The MTF of :func:`mtf` at the spatial frequency of the resolution
    requirement on the sky, along (:math:`x`) and across (:math:`y`) the
    dispersion, at each of the field angles :func:`field`.

    Each component is interpolated along a cut through zero frequency along
    the other axis of the detector.

    Parameters
    ----------
    as_built
        Whether to model the channel as built, with the measured figures of
        its optics, instead of as designed.
    mesh
        Whether to include the diffraction by the mesh which supports the
        filter.
    """
    result = mtf(as_built, mesh)
    frequency = frequency_sky(result.inputs)
    # in the units of `frequency_sky`, which counts no cycles
    requirement = _error_budget.frequency().to_value(u.cycle / u.arcsec) / u.arcsec
    components = {}
    for component, a in zip(("x", "y"), axis):
        cut = {b: result.shape[b] // 2 for b in axis if b != a}
        components[component] = na.interp(
            x=requirement,
            xp=getattr(frequency, component)[cut].to(1 / u.arcsec),
            fp=result.outputs[cut],
            axis=a,
        )
    return na.Cartesian2dVectorArray(**components)


def position_field_stop() -> na.Cartesian2dVectorArray:
    """
    The positions on the field stop, in its own frame, of the points whose
    point-spread functions are computed: its center, and the point
    :data:`fraction_field` of the way to its corner :data:`angle_corner`.
    """
    stop = system(as_built=False).surfaces_all[_index_field_stop(as_built=False)]
    radius = stop.aperture.radius
    r = na.ScalarArray(np.array([0, fraction_field]), axes=axis_field) * radius
    return na.Cartesian2dVectorArray(
        x=r * np.cos(angle_corner),
        y=r * np.sin(angle_corner),
    )


def _index_field_stop(as_built: bool) -> int:
    """
    The index of the field stop among all the surfaces of :func:`system`,
    the object included.

    Parameters
    ----------
    as_built
        Whether to use the channel as built instead of as designed.
    """
    surfaces = system(as_built).surfaces_all
    return next(i for i, s in enumerate(surfaces) if s.is_field_stop)


def _position(
    as_built: bool,
    angle: na.AbstractCartesian2dVectorArray,
) -> na.Cartesian2dVectorArray:
    """
    Where the chief ray of each field angle lands on the field stop, in its
    own frame.

    Parameters
    ----------
    as_built
        Whether to use the channel as built instead of as designed.
    angle
        The field angles on the sky.
    """
    index = _index_field_stop(as_built)
    axis_surface = "_surface"
    raytrace = system(as_built).raytrace(
        wavelength=wavelength,
        field=angle,
        pupil=na.Cartesian2dVectorArray(0, 0),
        axis=axis_surface,
        normalized_field=False,
    )
    rays = raytrace.outputs[{axis_surface: index}]
    stop = system(as_built).surfaces_all[index]
    if stop.transformation is not None:
        rays = stop.transformation.inverse(rays)
    return rays.position.xy


@functools.cache
def field(as_built: bool) -> na.Cartesian2dVectorArray:
    """
    The field angles on the sky whose chief rays land on the field stop at
    :func:`position_field_stop`, for the channel as designed or as built.

    The two models do not share a frame on the sky: the design is turned
    about the optic axis so that the channel disperses along :math:`x`, and
    the channel as built is not, so the same angle on the sky lands at
    different places on the field stop. Each angle is found by Newton's
    method, from where nearby angles land.

    Parameters
    ----------
    as_built
        Whether to use the channel as built instead of as designed.
    """
    target = position_field_stop()
    step = 0.01 * u.deg
    zero = 0 * u.deg
    angle = na.Cartesian2dVectorArray(zero, zero)
    for _ in range(3):
        position = _position(as_built, angle)
        dx = _position(as_built, angle + na.Cartesian2dVectorArray(step, zero))
        dy = _position(as_built, angle + na.Cartesian2dVectorArray(zero, step))
        dx = (dx - position) / step
        dy = (dy - position) / step
        residual = target - position
        determinant = dx.x * dy.y - dy.x * dx.y
        angle = angle + na.Cartesian2dVectorArray(
            x=(dy.y * residual.x - dy.x * residual.y) / determinant,
            y=(dx.x * residual.y - dx.y * residual.x) / determinant,
        )
    return na.Cartesian2dVectorArray(
        x=angle.x.to(u.arcmin),
        y=angle.y.to(u.arcmin),
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
