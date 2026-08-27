import aastex

import esis_instrument_paper


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
