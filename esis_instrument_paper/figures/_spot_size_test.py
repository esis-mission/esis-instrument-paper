import aastex
import matplotlib

matplotlib.use("agg")

import esis_instrument_paper


def test_spot_size() -> None:
    """This figure spans both columns, and carries its label."""
    result = esis_instrument_paper.figures.spot_size()
    assert isinstance(result, aastex.FigureStar)
    assert "fig:spotSize}" in result.dumps()
