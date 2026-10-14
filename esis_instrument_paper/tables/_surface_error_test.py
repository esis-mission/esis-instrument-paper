import pylatex

import esis_instrument_paper


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
