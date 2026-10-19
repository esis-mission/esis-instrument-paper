import aastex
import matplotlib

matplotlib.use("agg")

import esis_instrument_paper


def test_spot_diagrams() -> None:
    """The prose refers to this figure by its label."""
    result = esis_instrument_paper.figures.spot_diagrams()
    assert isinstance(result, aastex.Figure)
    assert "fig:psf}" in result.dumps()
