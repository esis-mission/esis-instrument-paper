import pylatex

import esis_instrument_paper
from esis_instrument_paper import _error_budget


def test_error_budget() -> None:
    """
    The text refers to this table by its label, and it spans both columns,
    with a row for every term of the budget and one for the total MTF.
    """
    result = esis_instrument_paper.tables.error_budget()
    assert isinstance(result, pylatex.Table)
    result = result.dumps()
    assert r"\begin{table*}" in result
    assert "table:errorBudget}" in result
    for term in _error_budget.terms():
        assert term.name in result
    assert result.count(r"\\") == len(_error_budget.terms()) + 2
    assert f"{_error_budget.mtf_total():.3f}" in result
