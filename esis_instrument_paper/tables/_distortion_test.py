import re

import pylatex

import esis_instrument_paper


def test_distortion() -> None:
    """The caption of the distortion figure refers to this table by its label."""
    result = esis_instrument_paper.tables.distortion()
    assert isinstance(result, pylatex.Table)
    assert "table:distortion}" in result.dumps()


def test_distortion_order() -> None:
    """
    The table lists every coefficient of the quadratic model once, in the
    order the text's equation writes them.
    """
    result = esis_instrument_paper.tables.distortion().dumps()
    symbols = re.findall(r"\$(\\C(?:_\{[^}]*\})?)\$", result)
    assert symbols == [
        r"\C",
        r"\C_{x}",
        r"\C_{y}",
        r"\C_{\lambda}",
        r"\C_{xx}",
        r"\C_{xy}",
        r"\C_{x\lambda}",
        r"\C_{yy}",
        r"\C_{y\lambda}",
        r"\C_{\lambda\lambda}",
    ]
