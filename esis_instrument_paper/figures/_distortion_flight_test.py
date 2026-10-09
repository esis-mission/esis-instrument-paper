import aastex
import matplotlib

matplotlib.use("agg")

import esis_instrument_paper


def test_distortion_flight():
    result = esis_instrument_paper.figures.distortion_flight()
    assert isinstance(result, aastex.Figure)


def test_distortion_flight_label():
    """The prose refers to this figure, so the label has to keep its name."""
    result = esis_instrument_paper.figures.distortion_flight()
    assert "fig:distortionFlight" in result.dumps()


def test_coalignment_tiles():
    result = esis_instrument_paper.figures.coalignment_tiles()
    assert isinstance(result, aastex.FigureStar)
    assert "fig:coalignmentTiles" in result.dumps()
