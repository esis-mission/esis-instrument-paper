"""
The sections of this article, each a factory function returning an
:class:`aastex.Section`.
"""

from ._s1_introduction import introduction
from ._s2_concept import concept
from ._s3_science_objectives import science_objectives
from ._s4_instrument import instrument

__all__ = [
    "concept",
    "instrument",
    "introduction",
    "science_objectives",
]
