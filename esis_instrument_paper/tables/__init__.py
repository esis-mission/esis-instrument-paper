"""
The tables of this article, each a factory function returning an
:class:`aastex.Table`.
"""

from ._cameras import cameras
from ._counts import counts
from ._distortion import distortion
from ._prescription import prescription
from ._requirements import requirements
from ._surface_error import surface_error

__all__ = [
    "cameras",
    "counts",
    "distortion",
    "prescription",
    "requirements",
    "surface_error",
]
