import aastex
import matplotlib

matplotlib.use("agg")

import esis_instrument_paper


def test_contribution_function() -> None:
    """This figure carries its label."""
    result = esis_instrument_paper.figures.contribution_function()
    assert isinstance(result, aastex.Figure)
    assert "fig:contributionFunction}" in result.dumps()
