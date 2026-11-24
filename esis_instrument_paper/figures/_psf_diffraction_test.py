import aastex
import matplotlib

matplotlib.use("agg")

import esis_instrument_paper


def test_psf_diffraction() -> None:
    """The prose refers to this figure by its label."""
    result = esis_instrument_paper.figures.psf_diffraction()
    assert isinstance(result, aastex.Figure)
    assert "fig:psfDiffraction}" in result.dumps()
