import pylatex
import pytest

import esis_instrument_paper
from esis_instrument_paper.tables import _surface_error


def test_surface_error() -> None:
    """
    The text refers to this table by its label, and it spans both columns,
    with the slope error, roughness, and microroughness of the primary mirror
    and of the gratings, each as required and as measured.
    """
    result = esis_instrument_paper.tables.surface_error()
    assert isinstance(result, pylatex.Table)
    result = result.dumps()
    assert r"\begin{table*}" in result
    assert "table:error}" in result
    for element in ["Primary", "Grating"]:
        assert element in result
    for parameter in ["RMS slope error", "RMS roughness", "RMS microroughness"]:
        assert result.count(parameter) == 2
    for header in ["Requirement", "Measured"]:
        assert header in result


@pytest.mark.parametrize(
    argnames="value,expected",
    argvalues=[
        (0.436, "0.44"),
        (0.024, "0.024"),
        (0.02, "0.020"),
        (4, "4.0"),
        (70, "70"),
    ],
)
def test_format(value: float, expected: str) -> None:
    """
    Every number in the table has two significant figures: a measurement
    or the shortest of the periods is not rounded to one, and the zeros of a
    round number are kept, without a decimal point left trailing.
    """
    assert _surface_error._format(value) == expected
