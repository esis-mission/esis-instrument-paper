import pylatex

import esis_instrument_paper


def test_distortion_fit():
    result = esis_instrument_paper.tables.distortion_fit()
    assert isinstance(result, pylatex.Table)
    dumped = result.dumps()
    assert "table:distortionFit" in dumped
    # one row per stage, one column per channel, and the held-out row is a
    # correlation between zero and one
    assert "Held out" in dumped
    assert "Channel 3" in dumped
