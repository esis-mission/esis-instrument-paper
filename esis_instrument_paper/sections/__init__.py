"""
The sections of this article, each a factory function returning an
:class:`aastex.Section`.
"""

from ._s1_introduction import introduction
from ._s2_concept import concept
from ._s3_science_objectives import science_objectives

__all__ = [
    "concept",
    "introduction",
    "science_objectives",
]
