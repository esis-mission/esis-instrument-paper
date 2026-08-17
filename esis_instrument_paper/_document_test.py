import pathlib

import pylatex

import esis_instrument_paper


def test_document():
    doc = esis_instrument_paper.document()
    assert isinstance(doc, pylatex.Document)


def test_pdf(capsys):
    with capsys.disabled():
        pdf = esis_instrument_paper.pdf()
    assert isinstance(pdf, pathlib.Path)
    assert pdf.exists()
