import aastex

import esis_instrument_paper


def test_acknowledgments() -> None:
    """
    The acknowledgments are the AASTeX environment, with the acknowledgment
    CHIANTI asks for and the address of the code that builds the article.
    """
    result = esis_instrument_paper.acknowledgments()
    assert isinstance(result, aastex.Acknowledgments)
    result = result.dumps()
    assert "CHIANTI is a collaborative project" in result
    assert r"\url{https://github.com/esis-mission/esis-instrument-paper}" in result
