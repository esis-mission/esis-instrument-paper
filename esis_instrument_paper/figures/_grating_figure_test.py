import aastex
import matplotlib

matplotlib.use("agg")

import esis_instrument_paper


def test_grating_figure() -> None:
    """This figure carries its label."""
    result = esis_instrument_paper.figures.grating_figure()
    assert isinstance(result, aastex.Figure)
    assert "fig:gratingFigure}" in result.dumps()
