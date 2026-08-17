# esis-instrument-paper

[![tests](https://github.com/esis-mission/esis-instrument-paper/actions/workflows/tests.yml/badge.svg)](https://github.com/esis-mission/esis-instrument-paper/actions/workflows/tests.yml)
[![Black](https://github.com/esis-mission/esis-instrument-paper/actions/workflows/black.yml/badge.svg)](https://github.com/esis-mission/esis-instrument-paper/actions/workflows/black.yml)
[![Ruff](https://github.com/esis-mission/esis-instrument-paper/actions/workflows/ruff.yml/badge.svg)](https://github.com/esis-mission/esis-instrument-paper/actions/workflows/ruff.yml)
[![Documentation Status](https://readthedocs.org/projects/esis-instrument-paper/badge/?version=latest)](https://esis-instrument-paper.readthedocs.io/en/latest/?badge=latest)

An AAS journal article describing the EUV Snapshot Imaging Spectrograph (ESIS),
a sounding rocket instrument that captures snapshot spectral images of the
solar transition region and corona.

This is a *reproducible* article: the `esis_instrument_paper` Python package
programmatically generates the complete LaTeX document (text, figures, tables,
and numeric values) from the [`esis`](https://github.com/esis-mission/esis)
instrument model. Calling `esis_instrument_paper.pdf()` produces the final PDF.

Here is a link to the [pdf version](https://esis-instrument-paper.readthedocs.io/_/downloads/en/latest/pdf/)
of the article.

## Building the article

Requires a LaTeX installation (TeX Live: `texlive-publishers texlive-science cm-super`).

```bash
pip install -e .[test]
pytest                        # test_pdf compiles the article
python -c "import esis_instrument_paper; esis_instrument_paper.pdf()"
```
