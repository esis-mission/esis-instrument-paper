import pathlib

import aastex
import matplotlib.pyplot as plt

import esis_instrument_paper

__all__ = [
    "document",
    "pdf",
]


def document(linenumbers: bool = True) -> aastex.Document:
    """
    An :mod:`aastex` representation of the article.

    Parameters
    ----------
    linenumbers
        Whether to number the lines, as the journal requires for review.
    """

    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.size"] = 9
    plt.rcParams["lines.linewidth"] = 1

    doc = aastex.Document(
        document_options=[
            "twocolumn",
        ],
        lmodern=False,
        textcomp=False,
        linenumbers=linenumbers,
    )

    doc.packages.append(aastex.Package("amsmath"))
    doc.packages.append(aastex.Package("hyperref"))
    doc.packages.append(aastex.Package("siunitx"))
    doc.packages.append(aastex.Package("paralist"))

    doc.preamble += esis_instrument_paper.preamble()
    doc.preamble += esis_instrument_paper.acronyms()

    doc.variables += esis_instrument_paper.variables()

    doc.append(aastex.Title("The EUV Snapshot Imaging Spectrograph"))

    doc += esis_instrument_paper.authors()

    doc.append(esis_instrument_paper.abstract())

    doc.append(esis_instrument_paper.sections.introduction())
    doc.append(esis_instrument_paper.sections.concept())
    doc.append(esis_instrument_paper.sections.science_objectives())
    doc.append(esis_instrument_paper.sections.instrument())
    doc.append(esis_instrument_paper.sections.mission_profile())
    doc.append(esis_instrument_paper.sections.conclusions())

    doc.append(aastex.Bibliography("sources"))

    return doc


def pdf(linenumbers: bool = True) -> pathlib.Path:
    """
    Build a pdf version of :func:`document` and return the path of the document.

    Parameters
    ----------
    linenumbers
        Whether to number the lines, as the journal requires for review.
    """

    doc = document(linenumbers=linenumbers)

    path = pathlib.Path(__file__).parent / "esis-instrument"
    doc.generate_pdf(
        filepath=path,
        clean_tex=False,
    )

    return path.with_suffix(".pdf")
