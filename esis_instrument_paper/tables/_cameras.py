"""The gain, read noise, and dark current of each quadrant of each camera."""

import functools
import operator

import astropy.units as u
import named_arrays as na
import pylatex

import esis_instrument_paper

__all__ = [
    "cameras",
]

_quadrants = {
    1: (0, 0),
    2: (1, 0),
    3: (1, 1),
    4: (0, 1),
}
"""
The index of the tap which reads out each quadrant, as the vertical and the
horizontal tap, in the layout of :attr:`msfc_ccd.TapData.amplifier`.
"""

_columns = (
    ("Gain", (u.electron, u.DN**-1), 2),
    ("Read noise", (u.electron,), 1),
    ("Dark current", (u.electron, u.s**-1), 3),
)
"""The name of each measured column, its unit, and the decimals it is given to."""


def _unit(unit: tuple[u.UnitBase, ...]) -> str:
    """A unit written as its factors in the given order."""
    factors = [f"{factor:latex_inline}"[1:~0] for factor in unit]
    return "$" + r"\,".join(factors) + "$"


def cameras() -> pylatex.Table:
    """
    The gain, read noise, and dark current measured for each quadrant of each
    camera that flew, by the name and serial number of the camera.
    """
    instrument = esis_instrument_paper._counts.optics()
    camera = instrument.camera
    axis_channel = instrument.axis_channel

    values = (camera.gain, camera.sensor.readout_noise, camera.dark_current)

    result = pylatex.Table(position="!htb")

    result.add_caption(pylatex.NoEscape(r"\ESIS\ camera properties."))

    with (
        result.create(pylatex.Center()) as centering,
        centering.create(pylatex.Tabular(table_spec="lcrrr")) as tabular,
    ):
        tabular.escape = False
        tabular.add_row(["Camera", "Quad.", *[name for name, _, _ in _columns]])
        tabular.add_row(["", "", *[f"({_unit(unit)})" for _, unit, _ in _columns]])
        tabular.add_hline()
        for index in range(camera.channel.shape[axis_channel]):
            i = {axis_channel: index}
            name = na.as_named_array(camera.channel[i]).ndarray
            serial = na.as_named_array(camera.sensor.serial_number[i]).ndarray
            for quadrant, (y, x) in _quadrants.items():
                tap = i | {camera.axis_tap_y: y, camera.axis_tap_x: x}
                row = [f"{name} ({serial})" if quadrant == 1 else "", quadrant]
                for value, (_, unit, decimals) in zip(values, _columns):
                    value = na.as_named_array(value[tap]).ndarray
                    value = value.to_value(functools.reduce(operator.mul, unit))
                    row.append(f"{value:.{decimals}f}")
                tabular.add_row(row)
            tabular.add_hline()

    result.append(pylatex.Label("table:cameras"))

    return result
