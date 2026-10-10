import aastex
import astropy.units as u
import numpy as np

import esis_instrument_paper
from esis_instrument_paper import _grids


def test_variables():
    result = esis_instrument_paper.variables()
    assert result
    assert all(isinstance(v, aastex.Variable) for v in result)


def test_variables_unique():
    """A name defined twice would silently take whichever value came last."""
    names = [v.name for v in esis_instrument_paper.variables()]
    assert len(names) == len(set(names))


def test_num_channels_words():
    """
    The prose says the gratings are clocked into this many dispersion planes.

    It has to describe the four channels which flew rather than the six
    positions of `design_full`, and it is spelled out because the sentence
    reads it as a word.
    """
    variables = {v.name: v for v in esis_instrument_paper.variables()}
    assert variables["numChannelsWords"].value == "four"


def test_distortion_wavelength() -> None:
    """
    The caption of the distortion table says the model measures wavelength
    from the mean of the three lines it was fit at.
    """
    variables = {v.name: v for v in esis_instrument_paper.variables()}
    expected = _grids.wavelength().ndarray.mean().to(u.AA)
    assert np.isclose(
        variables["distortionWavelength"].value, expected, atol=0.005 * u.AA
    )
