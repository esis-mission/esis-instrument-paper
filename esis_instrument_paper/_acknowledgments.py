import aastex

__all__ = [
    "acknowledgments",
]


def acknowledgments() -> aastex.Acknowledgments:
    """
    The acknowledgments of this article.

    The grant numbers are left for the authors to fill in. The sentence on
    CHIANTI is the acknowledgment CHIANTI asks of the articles which use it,
    as the passband figure does.
    """
    result = aastex.Acknowledgments()
    result.append(r"""
\roy{Grant numbers for the \ESIS\ instrument and its flight.}
We thank the NASA Sounding Rocket Operations Contract team and White Sands Missile Range for the launch and recovery of
\ESIS.
CHIANTI is a collaborative project involving George Mason University, the University of Michigan (USA), University of
Cambridge (UK) and NASA Goddard Space Flight Center (USA).
This article is an executable paper: its plots, its tables, and the properties of the instrument quoted in its text are
computed from the \texttt{esis} model of the instrument each time the article is built, and the code that builds it is
available at \url{https://github.com/esis-mission/esis-instrument-paper}.""")
    return result
