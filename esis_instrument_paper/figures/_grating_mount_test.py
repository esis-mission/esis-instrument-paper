import aastex
import matplotlib

matplotlib.use("agg")

import esis_instrument_paper


def test_grating_mount() -> None:
    """The prose refers to this figure by its label."""
    result = esis_instrument_paper.figures.grating_mount()
    assert isinstance(result, aastex.Figure)
    assert "fig:gratingMount}" in result.dumps()
