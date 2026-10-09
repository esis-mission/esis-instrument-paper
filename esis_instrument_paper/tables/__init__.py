"""
The tables of this article, each a factory function returning an
:class:`aastex.Table`.
"""

from ._distortion_fit import distortion_fit
from ._requirements import requirements

__all__ = [
    "distortion_fit",
    "requirements",
]
