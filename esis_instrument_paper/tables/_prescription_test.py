import pylatex

import esis_instrument_paper


def test_prescription() -> None:
    """
    The text refers to this table by its label, and it spans both columns,
    with a row for each part of a channel.
    """
    result = esis_instrument_paper.tables.prescription()
    assert isinstance(result, pylatex.Table)
    result = result.dumps()
    assert r"\begin{table*}" in result
    assert "table:prescription}" in result
    for component in ["Primary", "Field stop", "Gratings", "Filters", "Detectors"]:
        assert component in result
    for shape in ["Parabolic", "Octagonal", "Spherical", "Trapezoidal", "Circular"]:
        assert shape in result
