import aastex
import matplotlib

matplotlib.use("agg")

import esis_instrument_paper


def test_mtf() -> None:
    """The prose refers to this figure by its label."""
    result = esis_instrument_paper.figures.mtf()
    assert isinstance(result, aastex.Figure)
    assert "fig:mtf}" in result.dumps()
