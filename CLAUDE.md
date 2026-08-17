# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`esis-instrument-paper` is a **reproducible scientific article**, not a conventional
software library. The `esis_instrument_paper` Python package programmatically generates
a complete AAS-journal LaTeX article (text, figures, tables, and numeric values)
describing the EUV Snapshot Imaging Spectrograph (ESIS) sounding rocket instrument.
Calling `esis_instrument_paper.pdf()` produces the final `esis-instrument.pdf`.

This is one package within the larger Kankelborg-Group workspace (see the parent
`../CLAUDE.md`). It depends on the group's stack — `named-arrays`
(`import named_arrays as na`), `optika`, `esis`, and `aastex` — plus `pylatex` and
`astropy.units`. Use `named_arrays` rather than `numpy` for array work in new code.

## Provenance: porting from ESIS-old

This article is being ported, subsection by subsection, from an older draft at
`../ESIS-old/esis/science/papers/instrument/`, which was built on the deprecated
`kgpy` package and the old ESIS model. Rules for the port:

- **Never import from `kgpy` or `ESIS-old`** — they are read-only reference material.
- **Recompute every number** from the modern `esis` flight model rather than trusting
  values in the old draft; discrepancies between old and new are findings to surface.
- **Push reusable functionality down the stack**: if a figure or quantity needs a
  capability the modern `esis`/`optika` packages lack, add it there (with tests) rather
  than writing bespoke code in this repo. This repo should contain only prose, `aastex`
  document assembly, and thin glue that calls library functions.

## Commands

Run from this package directory:

```bash
pip install -e .[test]          # install for development
pytest                          # run tests; test_pdf compiles the LaTeX → PDF
pytest esis_instrument_paper/_document_test.py::test_pdf   # build the PDF specifically
black esis_instrument_paper     # format (CI enforces --check)
ruff check                      # lint (CI enforces)
```

Building the PDF requires a **LaTeX installation** (TeX Live: `texlive-publishers
texlive-science cm-super`) and matplotlib's usetex support, since `_document.py` sets
`text.usetex = True`.

## Architecture

The whole article is assembled in `_document.py`: `document()` builds an
`aastex.Document`, appending acronyms, variables, title, authors, then each section,
and finally the bibliography (`sources.bib`). `pdf()` renders it. Everything else
exists to feed this function.

Structure mirrors the parts of a journal article, each a subpackage of public factory
functions re-exported in its `__init__.py`:

- **`sections/`** — each module returns an `aastex.Section`. Prose lives here as raw
  LaTeX strings (with `\cite`, `\ref`, equations) and embeds figures/tables by calling
  the corresponding factory.
- **`figures/`** — each module builds a matplotlib figure and wraps it in an
  `aastex.Figure`/`FigureStar` with a caption.
- **`tables/`** — factories returning `aastex.Table` objects.
- **`_variables.py`** — defines `aastex.Variable` LaTeX macros for every numeric value
  cited in the prose, computed from the instrument model. **This is how numbers stay in
  sync between the model and the text** — reference `\variableName` in section strings
  rather than hardcoding a number.
- **`_acronyms.py`** — `aastex.Acronym` definitions; prose uses `\ACRONYM` macros.

The instrument model itself lives in the `esis` package (`esis.flights.f1` for the
2019 flight this article describes) — this repo defines no physics of its own.

## Conventions

- Every module declares an explicit `__all__` and exposes functionality through small
  factory functions, re-exported up the package via `__init__.py`. To add a new
  figure/table/section: create `_name.py`, then add it to the subpackage `__init__.py`.
- Modules import the top-level package as `import esis_instrument_paper` and reach back
  into it (`esis_instrument_paper.figures.x()`) rather than deep relative imports —
  access happens at call time, not import time, so the apparent circularity is fine.
- Generated LaTeX/PDF output and caches are gitignored — never commit build artifacts.
- Stage explicit files with `git add`; never `git add` whole directories.
