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


def test_pdf_bibliography(capsys):
    """
    The bibliography is only formatted if the compiler runs BibTeX, which it
    silently skips without `latexmk`, leaving every citation unresolved.
    """
    with capsys.disabled():
        pdf = esis_instrument_paper.pdf()

    bbl = pdf.with_suffix(".bbl")

    assert bbl.exists()
    assert "bibitem" in bbl.read_text(encoding="utf-8", errors="replace")
