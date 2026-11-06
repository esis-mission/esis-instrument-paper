import pylatex

import esis_instrument_paper


def test_cameras() -> None:
    """
    The text refers to this table by its label, and it has a row for each
    quadrant of each camera, named by its serial number.
    """
    result = esis_instrument_paper.tables.cameras()
    assert isinstance(result, pylatex.Table)
    result = result.dumps()
    assert "table:cameras}" in result
    for name in ["Gain", "Read noise", "Dark current"]:
        assert name in result
    for serial in ["SN6", "SN7", "SN9", "SN10"]:
        assert f"({serial})" in result
