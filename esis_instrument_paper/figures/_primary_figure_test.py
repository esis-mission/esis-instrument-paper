import aastex
import matplotlib

matplotlib.use("agg")

import esis_instrument_paper


def test_primary_figure() -> None:
    """This figure carries its label."""
    result = esis_instrument_paper.figures.primary_figure()
    assert isinstance(result, aastex.Figure)
    assert "fig:primaryFigure}" in result.dumps()
