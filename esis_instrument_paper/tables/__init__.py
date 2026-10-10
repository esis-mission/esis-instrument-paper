"""
The tables of this article, each a factory function returning an
:class:`aastex.Table`.
"""

from ._counts import counts
from ._distortion import distortion
from ._requirements import requirements

__all__ = [
    "counts",
    "distortion",
    "requirements",
]
