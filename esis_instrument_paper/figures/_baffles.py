import pathlib

import aastex

__all__ = [
    "baffles",
]

_path = pathlib.Path(__file__).parent / "static/baffles.png"
"""
A rendering of the solid model of the optical bench with its six baffles, the
one the old draft showed in this figure.

The fully transparent rows above and below the bench are trimmed off, which
leaves every other pixel as it was.
"""


def baffles() -> aastex.FigureStar:
    """
    A rendering of the solid model of the ESIS baffles, showing their cutouts
    and where they sit on the optical bench.

    The rendering is included as it is, at its full resolution, rather than
    drawn into a matplotlib figure, since nothing is drawn over it.
    """
    result = aastex.FigureStar("fig:baffles", position="!htb")
    result.add_image(_path, width=aastex.NoEscape(r"\textwidth"))
    result.add_caption(aastex.NoEscape(r"""
Model view of \ESIS\ baffle placement and cutouts."""))
    return result
