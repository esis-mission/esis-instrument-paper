import aastex
import matplotlib
import matplotlib.colors
import matplotlib.patches
import matplotlib.pyplot as plt
import numpy as np
import pytest

import esis_instrument_paper
from esis_instrument_paper.figures import _schematic_moses

_colors_light = {
    _schematic_moses._color_undispersed,
    _schematic_moses._color_long,
    _schematic_moses._color_short,
}
"""The colours the light is drawn in, which is how a beam is told from a groove."""


def test_schematic_moses():
    result = esis_instrument_paper.figures.schematic_moses()
    assert isinstance(result, aastex.Figure)


def test_schematic_moses_label():
    """The prose refers to this figure, so the label has to keep its name."""
    result = esis_instrument_paper.figures.schematic_moses()
    assert "fig:mosesSchematic" in result.dumps()


def _beams(axes) -> list:
    """Every line drawn in one of the colours of the light."""
    return [
        line
        for line in axes.lines
        if matplotlib.colors.to_hex(line.get_color()) in _colors_light
    ]


@pytest.fixture
def axes() -> matplotlib.axes.Axes:
    matplotlib.use("agg")
    esis_instrument_paper.figures.schematic_moses()
    result = plt.gcf().axes[0]
    yield result
    plt.close("all")


def test_beam_clears_the_undispersed_detector(axes: matplotlib.axes.Axes):
    """
    The light entering the instrument has to miss the detectors on its way in.

    It runs at the height of the edge of the grating, so that height has to
    thread the gap between the undispersed detector and the dispersed ones.
    Merely missing them is not enough: a beam which passes a hair above the
    undispersed detector reads as clipping it, so this asks for a quarter of
    the gap as clearance at either end.
    """
    tiles = [p for p in axes.patches if isinstance(p, matplotlib.patches.Polygon)]
    undispersed = min(tiles, key=lambda p: abs(p.get_xy()[:, 1].mean()))
    dispersed = max(tiles, key=lambda p: p.get_xy()[:, 1].mean())

    lower = undispersed.get_xy()[:, 1].max()
    upper = dispersed.get_xy()[:, 1].min()
    margin = (upper - lower) / 4

    incoming = [
        line
        for line in _beams(axes)
        if np.ptp(line.get_ydata()) == 0
        if np.ptp(line.get_xdata()) > 0.5
    ]
    assert incoming

    for line in incoming:
        y = abs(line.get_ydata()[0])
        assert lower + margin < y < upper - margin


def test_beam_leaves_the_grating(axes: matplotlib.axes.Axes):
    """
    The beams have to start on the face of the grating rather than off it.

    Widening the beam without growing the grating would leave the light
    apparently reflecting off empty space.
    """
    faces = [p for p in axes.patches if isinstance(p, matplotlib.patches.Ellipse)]
    face = max(faces, key=lambda p: p.get_center()[0])
    x_face, y_face = face.get_center()
    a = face.get_width() / 2
    b = face.get_height() / 2

    for line in _beams(axes):
        x, y = line.get_xdata(), line.get_ydata()
        # the end of the beam which sits on the grating
        i = int(np.argmin(x))
        assert ((x[i] - x_face) / a) ** 2 + ((y[i] - y_face) / b) ** 2 <= 1
