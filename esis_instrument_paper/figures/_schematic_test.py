import aastex
import matplotlib

matplotlib.use("agg")

import esis_instrument_paper


def test_schematic() -> None:
    """The prose and the captions refer to this figure by its label."""
    result = esis_instrument_paper.figures.schematic()
    assert isinstance(result, aastex.FigureStar)
    assert "fig:schematic}" in result.dumps()
