"""
How sensitive the image of a single channel is to where its grating sits,
which the text of the Alignment and Focus subsection quotes.

A grating can go wrong in two ways that matter here: it can sit too near or
too far along the optic axis, which defocuses the image, or it can be tipped
or tilted about its vertex, which moves the image across the detector.
"""

import functools

import astropy.units as u
import esis
import named_arrays as na
import numpy as np

__all__ = [
    "defocus_sensitivity",
    "margin",
    "optics",
    "tilt_test",
    "tilted",
    "tolerance_tilt",
    "wavelength",
]

wavelength = esis.flights.f1.spectrum.O_V.wavelength
"""
The line whose image has to land on the detector.

It is the line the instrument was designed around. Its image comes nearer an
edge of the detector than that of either line of :math:`\\text{Mg\\,X}`, so
the tolerance it sets keeps theirs on the detector as well. The image of
:math:`\\text{He\\,I}` runs off the edge of the detector even as designed, so
the whole of it never lands there.
"""

tilt_test = 0.1 * u.mrad
"""
How far a grating is turned to find how fast its image moves as it turns.

The image moves in proportion to the turn over a range several times this
wide, so the rate this finds holds out to the tolerance it is used to find.
"""


@functools.cache
def optics() -> esis.optics.Instrument:
    """A single channel of the flight instrument, as designed."""
    return esis.flights.f1.optics.design_single(num_distribution=0)


def defocus_sensitivity() -> na.AbstractScalar:
    """
    How much further the image moves along the optic axis than the grating
    that forms it.

    The grating images the field stop onto the detector with a magnification
    :math:`M`, the ratio of their distances from it, and so moves the image
    :math:`M^2` times as far as the field stop moves. Both lie in front of
    the grating, so moving the grating towards them by :math:`\\delta` both
    pushes the image :math:`M^2 \\delta` further away and brings the detector
    :math:`\\delta` nearer, which leaves the image :math:`(M^2 + 1) \\delta`
    from the detector.
    """
    instrument = optics()
    distance_input = instrument.distance_grating_input
    distance_output = instrument.distance_grating_output
    magnification = distance_output / distance_input
    return (magnification**2 + 1).to(u.dimensionless_unscaled)


def tilted(
    instrument: esis.optics.Instrument,
    pitch: u.Quantity = 0 * u.mrad,
    yaw: u.Quantity = 0 * u.mrad,
) -> esis.optics.Instrument:
    """
    A copy of an instrument with its gratings turned further about their
    vertices.

    Built rather than copied, as :meth:`esis.optics.Instrument.moved_grating`
    builds one, so that its rays are traced through the turned gratings
    rather than taken from the cache of the instrument it was made from.

    Parameters
    ----------
    instrument
        The instrument whose gratings are turned.
    pitch
        How much further to turn the gratings about :math:`x`, which tips the
        image across the dispersion.
    yaw
        How much further to turn the gratings about :math:`y`, which tilts the
        image along the dispersion.
    """
    grating = instrument.grating
    return instrument.replace(
        grating=grating.replace(
            pitch=grating.pitch + pitch,
            yaw=grating.yaw + yaw,
        ),
    )


def margin(
    instrument: esis.optics.Instrument,
    wavelength: u.Quantity = wavelength,
) -> tuple[na.Cartesian2dVectorArray, na.Cartesian2dVectorArray]:
    """
    How far the image of the field stop lies from each edge of the active
    area of the sensor.

    The outline of the field stop is traced through the center of the pupil
    alone. The field stop sits at an image of the Sun, so every ray through a
    point on its edge lands at the same point of a detector in focus, and the
    one through the center of the pupil finds it. The outline is traced
    rather than a grid of field positions which fills it, since the field
    positions on the edge of the stop are the ones that set the extent of the
    image, and a grid loses them: a ray which grazes the edge of the stop is
    as likely to be counted as blocked as not.

    The result is a pair: the distances to the edges at the least :math:`x`
    and :math:`y` of the sensor, and those to the edges at the greatest.
    A distance is negative if the image runs off that edge.

    Parameters
    ----------
    instrument
        The instrument whose image is traced.
    wavelength
        The wavelength of the image.
    """
    system = instrument.system

    # The vertices of the outline are along an axis named the same as those
    # of every polygonal aperture they are traced through, which would
    # broadcast against each other. Combining the one axis into another
    # renames it.
    outline = system.field_stop_polygon(wavelength).vertices.xy
    outline = outline.combine_axes(axes=("vertex",), axis_new="outline")

    rays = system.rayfunction(
        wavelength=wavelength,
        field=outline,
        pupil=na.Cartesian2dVectorArray(0, 0),
        normalized_field=False,
        efficiency=False,
    ).outputs

    position = rays.position.xy

    half_width = instrument.camera.sensor.width_active / 2

    lower = na.Cartesian2dVectorArray(
        x=position.x.min() + half_width.x,
        y=position.y.min() + half_width.y,
    )
    upper = na.Cartesian2dVectorArray(
        x=half_width.x - position.x.max(),
        y=half_width.y - position.y.max(),
    )

    return lower, upper


def tolerance_tilt() -> u.Quantity:
    """
    How far a grating can be tipped or tilted before the image of
    :data:`wavelength` runs off the active area of its sensor.

    Tipping the grating moves the image across the dispersion, and tilting it
    moves the image along the dispersion. Each moves the image in proportion
    to the turn, and either may turn either way, so each may turn as far as
    takes the image to the nearer of the two edges it moves towards. The
    tolerance is the least of these, so that it holds whichever way the
    grating turns.
    """
    instrument = optics()
    lower, upper = margin(instrument)
    position = instrument.position_line(wavelength)

    tipped = tilted(instrument, pitch=tilt_test).position_line(wavelength)
    rate_y = np.abs(tipped.y - position.y) / tilt_test

    turned = tilted(instrument, yaw=tilt_test).position_line(wavelength)
    rate_x = np.abs(turned.x - position.x) / tilt_test

    tolerance_y = np.minimum(lower.y, upper.y) / rate_y
    tolerance_x = np.minimum(lower.x, upper.x) / rate_x

    result = np.minimum(tolerance_x, tolerance_y)

    return na.as_named_array(result).ndarray.to(u.mrad)
