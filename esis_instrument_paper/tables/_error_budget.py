"""The imaging error budget, with the tolerance analysis it rests on."""

import astropy.units as u
import pylatex

from esis_instrument_paper import _error_budget

__all__ = [
    "error_budget",
]

_unit = u.um
"""The unit of the blur of each term."""


def _sigma(term: _error_budget.Term) -> str:
    """The blur of a term to a hundredth of :data:`_unit`, if it has one."""
    if term.sigma is None:
        return ""
    return f"{term.sigma.to_value(_unit):.2f}"


def _mtf(value: float) -> str:
    """
    An MTF to three decimals, since most terms leave an MTF close enough to
    one that two would not tell them apart.
    """
    return f"{value:.3f}"


def error_budget() -> pylatex.Table:
    """
    The imaging error budget of a single channel: the blur each tolerance and
    each fixed contribution adds to the image of the \\OV\\ line, and the MTF
    it leaves at the spatial frequency of the resolution requirement.

    See :mod:`esis_instrument_paper._error_budget` for how each term is found.
    """
    result = pylatex.Table(position="!htb")
    result._star_latex_name = True

    result.add_caption(pylatex.NoEscape(r"""
Imaging error budget and tolerance analysis results.
\MTF\ is given at \mtfFrequency."""))

    with (
        result.create(pylatex.Center()) as centering,
        centering.create(pylatex.Tabular(table_spec="llrrr")) as tabular,
    ):
        tabular.escape = False
        tabular.add_row(
            [
                "Element",
                "",
                "Tolerance",
                f"$\\sigma$ ({_unit:latex_inline})",
                r"\MTF",
            ]
        )
        element = None
        for term in _error_budget.terms():
            if term.element != element:
                tabular.add_hline()
            tabular.add_row(
                [
                    term.element if term.element != element else "",
                    term.name,
                    term.tolerance,
                    _sigma(term),
                    _mtf(term.mtf),
                ]
            )
            element = term.element
        tabular.add_hline()
        tabular.add_row(
            [
                r"Total \MTF",
                "",
                "",
                "",
                _mtf(_error_budget.mtf_total()),
            ]
        )

    result.append(pylatex.Label("table:errorBudget"))

    return result
