"""
The figures of this article, each a factory function returning an
:class:`aastex.Figure`.
"""

from ._bunch import bunch
from ._layout import layout
from ._schematic_moses import schematic_moses

__all__ = [
    "bunch",
    "layout",
    "schematic_moses",
]
