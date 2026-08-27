import aastex
import esis
import matplotlib
import numpy as np
import pytest

matplotlib.use("agg")

import matplotlib.pyplot as plt

import esis_instrument_paper
from esis_instrument_paper.figures import _layout


def test_layout():
    result = esis_instrument_paper.figures.layout()
    assert isinstance(result, aastex.FigureStar)


def test_layout_label():
    """The prose refers to this figure, so the label has to keep its name."""
    result = esis_instrument_paper.figures.layout()
    assert "fig:layout" in result.dumps()


def test_channels_populated():
    """
    Four of the six available channel positions flew.

    The figure draws the other two dotted and the caption says so, so this is
    read from the two models rather than written down. It also pins the claim
    in the caption that four channels were populated.
    """
    grid = _layout._grid()
    full = esis.flights.f1.optics.design_full(grid=grid, num_distribution=0)
    flown = esis.flights.f1.optics.design(grid=grid, num_distribution=0)

    result = _layout._channels_populated(full, flown)

    assert result.sum() == 4
    assert result.size == 6
    # the unpopulated positions are the two ends of the arc
    assert np.array_equal(result, [False, True, True, True, True, False])


@pytest.fixture(autouse=True)
def _close_figures():
    """Building the figure leaves it open, and it is a large one."""
    yield
    plt.close("all")
