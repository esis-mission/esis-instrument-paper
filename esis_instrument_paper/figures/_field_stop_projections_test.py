import aastex
import matplotlib

matplotlib.use("agg")

import esis_instrument_paper


def test_field_stop_projections() -> None:
    """The prose and the captions refer to this figure by its label."""
    result = esis_instrument_paper.figures.field_stop_projections()
    assert isinstance(result, aastex.Figure)
    assert "fig:projections}" in result.dumps()
