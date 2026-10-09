import aastex
import matplotlib

matplotlib.use("agg")

import esis_instrument_paper


def test_distortion_fit():
    result = esis_instrument_paper.sections.distortion_fit()
    assert isinstance(result, aastex.Section)
    dumped = result.dumps()
    # the instrument section refers to the appendix by this label
    assert "sec:TheDistortionFit" in dumped
    assert "fig:coalignmentTiles" in dumped


def test_instrument_refers_to_the_appendix():
    """Every macro the measured-distortion prose uses is defined."""
    variables = {v.name for v in esis_instrument_paper.variables()}
    section = esis_instrument_paper.sections.instrument().dumps()
    assert "sec:TheDistortionFit" in section
    for name in (
        "coalignmentBefore",
        "coalignmentAfterHeI",
        "coalignmentVelocityOV",
        "defocusRange",
        "sectorFocusSpread",
        "distortionNumFramesMeasured",
    ):
        assert f"\\{name}" in section
        assert name in variables
