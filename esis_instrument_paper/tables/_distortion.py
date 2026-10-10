"""The coefficients of the distortion model of a single channel."""

import astropy.units as u
import named_arrays as na
import pylatex

from esis_instrument_paper import _distortion_model

__all__ = [
    "distortion",
]

_unit_field = u.arcsec
"""
The unit of field angle the coefficients are given per, the one the
distortion figures draw the field in.
"""

_unit_wavelength = u.AA
"""The unit of wavelength the coefficients are given per."""

_symbols = {
    "position.x": "x",
    "position.y": "y",
    "wavelength": r"\lambda",
}
"""
The symbol the text's equation gives each input of the model, keyed by the
name the fit gives it, in the order the equation writes the terms of each
degree in.
"""

_units = {
    "position.x": _unit_field,
    "position.y": _unit_field,
    "wavelength": _unit_wavelength,
}
"""The unit each input of the model is given in, keyed as :data:`_symbols`."""


def _factors(name: str) -> list[str]:
    """
    The inputs whose product a term of the fit is.

    The fit names each term by its factors joined by ``*``, and the constant
    term by the empty string, the empty product.

    Parameters
    ----------
    name
        The name the fit gives the term.
    """
    return name.split("*") if name else []


def _order(name: str) -> tuple[int, tuple[int, ...]]:
    """
    Sort the terms the way the text's equation writes them: by degree, and
    within a degree by their factors, :math:`x` before :math:`y` before
    :math:`\\lambda`.

    Parameters
    ----------
    name
        The name the fit gives the term.
    """
    order = list(_symbols)
    factors = _factors(name)
    return len(factors), tuple(sorted(order.index(f) for f in factors))


def _symbol(name: str) -> str:
    """
    The symbol of the coefficient of a term, as the text's equation writes it.

    Parameters
    ----------
    name
        The name the fit gives the term.
    """
    order = list(_symbols)
    factors = sorted(_factors(name), key=order.index)
    subscript = "".join(_symbols[f] for f in factors)
    return rf"$\C_{{{subscript}}}$" if subscript else r"$\C$"


def _unit(name: str) -> u.UnitBase:
    """
    The unit of the coefficient of a term: a pixel on the detector per unit
    of each of its factors.

    Parameters
    ----------
    name
        The name the fit gives the term.
    """
    result = u.pix
    for f in _factors(name):
        result = result / _units[f]
    return result


def _number(value: na.AbstractScalar, unit: u.UnitBase) -> str:
    """
    A coefficient in scientific notation, to two decimals as in the old draft.

    Parameters
    ----------
    value
        The coefficient.
    unit
        The unit to give it in.
    """
    return rf"\num{{{na.as_named_array(value).ndarray.to_value(unit):.2e}}}"


def distortion() -> pylatex.Table:
    """
    The coefficients of the quadratic distortion model of a single channel,
    term by term in the order the text's equation writes them.

    The fit centers its inputs on the mean of its samples, so each coefficient
    is a derivative at the center of the field and at the mean wavelength of
    the three lines. It measures where the field lands in pixels from a
    corner of the detector, so the constant term is where that center lands.
    """
    fit = _distortion_model.model().fit
    coefficients = fit.coefficients.components

    result = pylatex.Table(position="!htb")

    # The old draft never gave this table a caption, and what it should say is
    # the authors' to write. A table is numbered only by its caption, and the
    # caption of the distortion figure cites this table by number, so a marked
    # placeholder stands in for one.
    result.add_caption(pylatex.NoEscape(r"\textbf{??}"))

    with (
        result.create(pylatex.Center()) as centering,
        centering.create(pylatex.Tabular(table_spec="ll|rr")) as tabular,
    ):
        tabular.escape = False
        tabular.append(
            pylatex.NoEscape(r"\multicolumn{2}{l}{Coefficient} & $x'$ & $y'$ \\")
        )
        tabular.add_hline()
        for name in sorted(fit.coefficient_names, key=_order):
            unit = _unit(name)
            coefficient = coefficients[name]
            tabular.add_row(
                [
                    _symbol(name),
                    f"({unit:latex_inline})",
                    _number(coefficient.x, unit),
                    _number(coefficient.y, unit),
                ]
            )

    result.append(pylatex.Label("table:distortion"))

    return result
