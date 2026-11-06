import pathlib

import aastex
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("agg")

import esis_instrument_paper
from esis_instrument_paper.figures import _grating_mount


def test_grating_mount() -> None:
    """The prose refers to this figure by its label."""
    result = esis_instrument_paper.figures.grating_mount()
    assert isinstance(result, aastex.Figure)
    assert "fig:gratingMount}" in result.dumps()


def test_grating_mount_resolution(tmp_path: pathlib.Path) -> None:
    """
    The PDF embeds every pixel of the rendering, rather than resampling it to
    the resolution of the figure.
    """
    (image,) = esis_instrument_paper.figures.grating_mount().images
    height, width, _ = plt.imread(_grating_mount._path).shape
    result = image.write(tmp_path).read_bytes()
    assert f"/Width {width} /Height {height}".encode() in result
