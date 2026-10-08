"""
The figures of this article, each a factory function returning an
:class:`aastex.Figure`.
"""

from ._bunch import bunch, num_emission_lines
from ._grating_multilayer_schematic import grating_multilayer_schematic
from ._layout import layout
from ._schematic_moses import schematic_moses
from ._vignetting import vignetting

__all__ = [
    "bunch",
    "grating_multilayer_schematic",
    "layout",
    "num_emission_lines",
    "schematic_moses",
    "vignetting",
]
