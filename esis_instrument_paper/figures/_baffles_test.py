import aastex

import esis_instrument_paper


def test_baffles() -> None:
    """The prose refers to this figure by its label, and it shows the render."""
    result = esis_instrument_paper.figures.baffles()
    assert isinstance(result, aastex.FigureStar)
    latex = result.dumps()
    assert "fig:baffles}" in latex
    assert "baffles.png" in latex
