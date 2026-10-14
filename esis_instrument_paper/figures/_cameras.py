import pathlib

import aastex

__all__ = [
    "cameras",
]

_path = pathlib.Path(__file__).parent / "static/cameras.png"
"""
A photograph of the camera assembly, with the serial number of each camera
and the cold block labeled, the one the old draft showed in this figure.

It is the image inside the PDF the old draft converted the photograph to,
extracted as it is.
"""


def cameras() -> aastex.Figure:
    """
    A photograph of the ESIS camera assembly as MSFC built it.

    The photograph is included as it is, at its full resolution, rather than
    drawn into a matplotlib figure, since its labels are part of the image.
    """
    result = aastex.Figure("fig:cameras", position="!htb")
    result.add_image(_path, width=aastex.NoEscape(r"\columnwidth"))
    result.add_caption(aastex.NoEscape(r"""
\ESIS\ camera assembly as built by \MSFC.
Thin film filters and filter tubes are not installed in this image."""))
    return result
