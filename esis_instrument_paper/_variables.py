import aastex

__all__ = [
    "variables",
]


def variables() -> list[aastex.Variable]:
    """
    A list of LaTeX variables for every numeric quantity cited in the prose.

    Reference these macros in section strings instead of hardcoding numbers so
    that the text stays in sync with the instrument model.
    """
    return []
