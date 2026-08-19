import aastex

import esis_instrument_paper


def test_schematic_moses():
    result = esis_instrument_paper.figures.schematic_moses()
    assert isinstance(result, aastex.Figure)


def test_schematic_moses_label():
    """The prose refers to this figure, so the label has to keep its name."""
    result = esis_instrument_paper.figures.schematic_moses()
    assert "fig:mosesSchematic" in result.dumps()
