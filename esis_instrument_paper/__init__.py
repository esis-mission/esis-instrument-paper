"""
Create the figures and compile the LaTeX files for this article.
"""

from . import figures, sections, tables
from ._abstract import abstract
from ._acronyms import acronyms
from ._authors import authors
from ._document import document, pdf
from ._preamble import preamble
from ._spectrum import lines
from ._variables import variables

__all__ = [
    "abstract",
    "acronyms",
    "authors",
    "document",
    "figures",
    "lines",
    "pdf",
    "preamble",
    "sections",
    "tables",
    "variables",
]
