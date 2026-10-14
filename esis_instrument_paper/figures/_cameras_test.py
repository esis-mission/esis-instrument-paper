import aastex

import esis_instrument_paper


def test_cameras() -> None:
    """The prose refers to this figure by its label, and it shows the photograph."""
    result = esis_instrument_paper.figures.cameras()
    assert isinstance(result, aastex.Figure)
    latex = result.dumps()
    assert "fig:cameras}" in latex
    assert "cameras.png" in latex
