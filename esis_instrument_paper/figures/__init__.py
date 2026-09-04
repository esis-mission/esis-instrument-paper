"""
The figures of this article, each a factory function returning an
:class:`aastex.Figure`.
"""

from ._bunch import bunch, num_emission_lines
from ._layout import layout
from ._schematic_moses import schematic_moses

__all__ = [
    "bunch",
    "layout",
    "num_emission_lines",
    "schematic_moses",
]
