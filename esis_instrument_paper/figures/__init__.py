"""
The figures of this article, each a factory function returning an
:class:`aastex.Figure`.
"""

from ._bunch import bunch, num_emission_lines
from ._coalignment_tiles import coalignment_tiles
from ._distortion_flight import distortion_flight
from ._layout import layout
from ._schematic_moses import schematic_moses

__all__ = [
    "bunch",
    "coalignment_tiles",
    "distortion_flight",
    "layout",
    "num_emission_lines",
    "schematic_moses",
]
