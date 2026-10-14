"""The figure and finish of the optics, as specified and as measured."""

import astropy.units as u
import esis
import named_arrays as na
import optika
import pylatex

__all__ = [
    "surface_error",
]

_unit_slope = u.urad
"""The unit of the slope errors."""

_unit_roughness = u.nm
"""The unit of the roughness and the microroughness."""


def _value(value: u.Quantity | na.AbstractScalar, unit: u.UnitBase) -> str:
    """
    A specification or a measurement, to a tenth of the unit of its row.

    The gratings were measured one at a time, so their measurements are one
    per channel, and the table gives the mean of the four, as the old draft
    did.
    """
    mean = na.as_named_array(value).mean().ndarray
    return f"{mean.to_value(unit):.1f}"


def _length(name: str, value: u.Quantity) -> str:
    """A length which says how a value was measured, in its own unit."""
    return rf"\quad {name} = {value.value:.1f}\,{value.unit:latex_inline}"


def _periods(parameters: optika.metrology.RoughnessParameters) -> str:
    """The range of periods a roughness is measured over."""
    period_min = parameters.period_min
    period_max = parameters.period_max.to(period_min.unit)
    return (
        rf"\quad Periods = {period_min.value:.2f}--{period_max.value:.1f}"
        rf"\,{period_min.unit:latex_inline}"
    )


def _rows(
    specified: esis.optics.abc.AbstractPrimaryMirror | esis.optics.abc.AbstractGrating,
    measured: esis.optics.abc.AbstractPrimaryMirror | esis.optics.abc.AbstractGrating,
) -> list[tuple[str, str, str]]:
    """
    The rows of one optic: each RMS value as specified and as measured,
    followed by the lengths it is measured over.

    The integration length and the sample length are the names the old draft
    gave the step and the kernel of the slope error.
    """
    sag = specified.sag
    slope = sag.parameters_slope_error
    unit_slope = f"{_unit_slope:latex_inline}"
    unit_roughness = f"{_unit_roughness:latex_inline}"
    return [
        (
            f"RMS slope error ({unit_slope})",
            _value(specified.slope_error, _unit_slope),
            _value(measured.slope_error, _unit_slope),
        ),
        (_length("Integration length", slope.step_size), "", ""),
        (_length("Sample length", slope.kernel_size), "", ""),
        (
            f"RMS roughness ({unit_roughness})",
            _value(specified.roughness, _unit_roughness),
            _value(measured.roughness, _unit_roughness),
        ),
        (_periods(sag.parameters_roughness), "", ""),
        (
            f"RMS microroughness ({unit_roughness})",
            _value(specified.microroughness, _unit_roughness),
            _value(measured.microroughness, _unit_roughness),
        ),
        (_periods(sag.parameters_microroughness), "", ""),
    ]


def surface_error() -> pylatex.Table:
    """
    The figure and the finish of the primary mirror and of the gratings, as
    specified and as measured.

    The specifications are those of the design, and the measurements those of
    the instrument as built.
    """
    design = esis.flights.f1.optics.design(num_distribution=0)
    as_built = esis.flights.f1.optics.as_built(num_distribution=0)

    optics = {
        "Primary": (design.primary_mirror, as_built.primary_mirror),
        "Grating": (design.grating, as_built.grating),
    }

    result = pylatex.Table(position="!htb")
    result._star_latex_name = True

    result.add_caption(pylatex.NoEscape(r"""
Figure and surface roughness requirements compared to metrology for the \ESIS\ optics.
Slope error (both the numerical estimates and the measurements) is worked out with integration length and sample length
defined per ISO 10110."""))

    with (
        result.create(pylatex.Center()) as centering,
        centering.create(pylatex.Tabular(table_spec="llrr")) as tabular,
    ):
        tabular.escape = False
        tabular.add_row(["Element", "Parameter", "Requirement", "Measured"])
        for name, (specified, measured) in optics.items():
            tabular.add_hline()
            for index, row in enumerate(_rows(specified, measured)):
                tabular.add_row([name if index == 0 else "", *row])
        tabular.add_hline()

    result.append(pylatex.Label("table:error"))

    return result
