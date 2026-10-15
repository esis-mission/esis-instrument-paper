"""
The figures of this article, each a factory function returning an
:class:`aastex.Figure`.
"""

from ._baffles import baffles
from ._bunch import bunch, num_emission_lines
from ._cameras import cameras
from ._component_efficiency_vs_wavelength import component_efficiency_vs_wavelength
from ._distortion import distortion, distortion_residual
from ._field_stop_projections import field_stop_projections
from ._focus_curve import focus_curve
from ._grating_efficiency_vs_angle import grating_efficiency_vs_angle
from ._grating_efficiency_vs_position import grating_efficiency_vs_position
from ._grating_mount import grating_mount
from ._grating_multilayer_schematic import grating_multilayer_schematic
from ._layout import layout
from ._schematic import schematic
from ._schematic_moses import schematic_moses
from ._spot_diagrams import spot_diagrams
from ._spot_size import num_lines, spot_size
from ._vignetting import vignetting

__all__ = [
    "baffles",
    "bunch",
    "cameras",
    "component_efficiency_vs_wavelength",
    "distortion",
    "distortion_residual",
    "field_stop_projections",
    "focus_curve",
    "grating_efficiency_vs_angle",
    "grating_efficiency_vs_position",
    "grating_mount",
    "grating_multilayer_schematic",
    "layout",
    "num_emission_lines",
    "num_lines",
    "schematic",
    "schematic_moses",
    "spot_diagrams",
    "spot_size",
    "vignetting",
]
