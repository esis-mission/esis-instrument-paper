"""
Create the figures and compile the LaTeX files for this article.
"""

from . import figures, sections, tables
from ._acronyms import acronyms
from ._authors import authors
from ._document import document, pdf
from ._variables import variables

__all__ = [
    "acronyms",
    "authors",
    "document",
    "figures",
    "pdf",
    "sections",
    "tables",
    "variables",
]
