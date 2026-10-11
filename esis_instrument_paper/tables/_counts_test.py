import pylatex

import esis_instrument_paper


def test_counts() -> None:
    """
    The text and the requirements table refer to this table by its label,
    and its rows give the signal of each line, the noise, and the ratio of a
    single exposure and of the stack.
    """
    result = esis_instrument_paper.tables.counts()
    assert isinstance(result, pylatex.Table)
    result = result.dumps()
    assert "table:counts}" in result
    for name in [r"\OV", r"\MgXdim", "Total", "Shot noise", "Read noise"]:
        assert name in result
    assert result.count(r"\SNRShort") == 2
    assert r"\NumExpInStack" in result
