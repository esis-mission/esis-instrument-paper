import aastex
import matplotlib

matplotlib.use("agg")

import esis_instrument_paper


def test_distortion() -> None:
    """The prose and the captions refer to this figure by its label."""
    result = esis_instrument_paper.figures.distortion()
    assert isinstance(result, aastex.Figure)
    assert "fig:distortion}" in result.dumps()


def test_distortion_residual() -> None:
    """The prose and the captions refer to this figure by its label."""
    result = esis_instrument_paper.figures.distortion_residual()
    assert isinstance(result, aastex.FigureStar)
    assert "fig:distortionResidual" in result.dumps()
