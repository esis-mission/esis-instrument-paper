import types

import astropy.units as u
import esis
import named_arrays as na
import numpy as np
import pytest

from esis_instrument_paper import _alignment, _grids


def _least(
    margin: tuple[na.Cartesian2dVectorArray, na.Cartesian2dVectorArray],
) -> u.Quantity:
    """The least distance from the image to any edge of the sensor."""
    lower, upper = margin
    return min(lower.x, lower.y, upper.x, upper.y)


def _turns(angle: u.Quantity) -> list[tuple[u.Quantity, u.Quantity]]:
    """The four ways to turn a grating by an angle, as its pitch and its yaw."""
    zero = 0 * u.mrad
    return [(angle, zero), (-angle, zero), (zero, angle), (zero, -angle)]


def test_defocus_sensitivity() -> None:
    """
    Moving the detector along the optic axis moves the best focus of the
    grating by that distance over the sensitivity.

    The grating is refocused by the ray trace rather than by the
    magnification, so this checks the formula against the optics it
    describes. The detector moves away from the grating, and the grating
    follows it.
    """
    instrument = _alignment.optics()
    wavelength = _alignment.wavelength
    distance = 1 * u.mm

    sensor = instrument.camera.sensor
    moved = instrument.replace(
        camera=instrument.camera.replace(
            sensor=sensor.replace(
                translation=sensor.translation
                + na.Cartesian3dVectorArray(0, 0, 1) * distance,
            ),
        ),
    )

    focus = instrument.focus_grating(wavelength, min_step_size=0.05 * u.um)
    focus_moved = moved.focus_grating(wavelength, min_step_size=0.05 * u.um)
    shift = focus_moved.grating.translation.z - focus.grating.translation.z

    expected = distance / _alignment.defocus_sensitivity()
    assert np.allclose(shift, expected, rtol=0.01)


def test_tilted() -> None:
    """
    Tipping a grating moves its image across the dispersion, and tilting it
    moves the image along the dispersion.
    """
    instrument = _alignment.optics()
    wavelength = _alignment.wavelength
    position = instrument.position_line(wavelength)

    tipped = _alignment.tilted(instrument, pitch=_alignment.tilt_test)
    shift = tipped.position_line(wavelength) - position
    assert np.allclose(shift.x, 0 * u.mm, atol=1 * u.um)
    assert np.abs(shift.y) > 0.1 * u.mm

    turned = _alignment.tilted(instrument, yaw=_alignment.tilt_test)
    shift = turned.position_line(wavelength) - position
    assert np.abs(shift.x) > 0.1 * u.mm
    assert np.allclose(shift.y, 0 * u.mm, atol=1 * u.um)


def test_margin_outline() -> None:
    """
    The outline of the field stop reaches as far as the image of any field
    position which passes the stop, and hardly further.

    The field positions are a grid which fills the stop. The ones on its edge
    may or may not be counted as passing it, so the grid falls short of the
    outline by up to a step of the grid.
    """
    instrument = _alignment.optics()
    width_pixel = instrument.camera.sensor.width_pixel

    rays = instrument.system.rayfunction(
        wavelength=_alignment.wavelength,
        field=_grids.vertices("field", 400),
        pupil=na.Cartesian2dVectorArray(0, 0),
        efficiency=False,
    ).outputs
    position = rays.position.xy[rays.unvignetted]
    half_width = instrument.camera.sensor.width_active / 2

    lower, upper = _alignment.margin(instrument)
    for outline, grid in [
        (lower.x, position.x.min() + half_width.x),
        (lower.y, position.y.min() + half_width.y),
        (upper.x, half_width.x - position.x.max()),
        (upper.y, half_width.y - position.y.max()),
    ]:
        assert grid - outline > -1 * u.um
        assert grid - outline < 3 * width_pixel


@pytest.mark.parametrize(
    argnames="line",
    argvalues=[
        esis.flights.f1.spectrum.Mg_X,
        esis.flights.f1.spectrum.Mg_X_625,
    ],
)
def test_margin(line: types.ModuleType) -> None:
    """
    The image of :data:`_alignment.wavelength` fits on the sensor and comes
    nearer an edge than the image of either line of Mg X, and turning a
    grating by the tolerance, whichever way it turns, leaves theirs on the
    sensor.
    """
    instrument = _alignment.optics()
    wavelength = line.wavelength

    least = _least(_alignment.margin(instrument))
    least_line = _least(_alignment.margin(instrument, wavelength))
    assert least > 0 * u.mm
    assert least < least_line

    for pitch, yaw in _turns(_alignment.tolerance_tilt()):
        turned = _alignment.tilted(instrument, pitch=pitch, yaw=yaw)
        assert _least(_alignment.margin(turned, wavelength)) > 0 * u.mm


def test_tolerance_tilt() -> None:
    """
    Turning a grating by the tolerance, whichever way it turns, takes the
    image no further than the edge of the sensor, and one of those ways
    takes it to the edge.

    The tolerance assumes the image moves in proportion to the turn, so the
    edge is reached to within a fraction of a pixel rather than exactly.
    """
    instrument = _alignment.optics()
    width_pixel = instrument.camera.sensor.width_pixel

    least = []
    for pitch, yaw in _turns(_alignment.tolerance_tilt()):
        turned = _alignment.tilted(instrument, pitch=pitch, yaw=yaw)
        least.append(_least(_alignment.margin(turned)))

    assert min(least) > -width_pixel / 2
    assert min(least) < width_pixel / 2
