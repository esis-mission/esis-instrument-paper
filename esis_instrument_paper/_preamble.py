import aastex
import pylatex

__all__ = [
    "preamble",
]


def preamble() -> list[pylatex.base_classes.LatexObject]:
    """
    Custom LaTeX commands used throughout the article.
    """
    return [
        pylatex.NoEscape(r"""
\makeatletter
\newcommand{\acposs}[1]{%
 \expandafter\ifx\csname AC@#1\endcsname\AC@used
   \acs{#1}'s%
 \else
   \aclu{#1}'s (\acs{#1}'s)%
 \fi
}
\newcommand{\Acposs}[1]{%
 \expandafter\ifx\csname AC@#1\endcsname\AC@used
   \acs{#1}'s%
 \else
   \Aclu{#1}'s (\acs{#1}'s)%
 \fi
}
\makeatother"""),
        pylatex.NoEscape(r"\newcommand{\ie}{i.e.}"),
        pylatex.NoEscape(r"\newcommand{\eg}{e.g.}"),
        pylatex.NoEscape(r"\newcommand{\amy}[1]{{{\color{red} #1}}}"),
        pylatex.NoEscape(r"\newcommand{\jake}[1]{{{\color{purple} #1}}}"),
        pylatex.NoEscape(r"\newcommand{\roy}[1]{{{\color{blue} #1}}}"),
        aastex.Command(
            "DeclareSIUnit",
            [pylatex.NoEscape(r"\angstrom"), pylatex.NoEscape(r"\AA")],
        ),
    ]
