import aastex
import matplotlib

matplotlib.use("agg")

import esis_instrument_paper


def test_focus_curve() -> None:
    """This figure carries its label."""
    result = esis_instrument_paper.figures.focus_curve()
    assert isinstance(result, aastex.Figure)
    assert "fig:focusCurve}" in result.dumps()
