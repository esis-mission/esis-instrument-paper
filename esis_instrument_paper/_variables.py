import aastex
import astropy.units as u

__all__ = [
    "variables",
]


def variables() -> list[aastex.Variable]:
    """
    A list of LaTeX variables for every numeric quantity cited in the prose.

    Reference these macros in section strings instead of hardcoding numbers so
    that the text stays in sync with the instrument model.
    """
    return [
        aastex.Variable(
            name="mosesDispersionDoppler",
            value=29 * u.km / u.s / u.pix,
        ),
        aastex.Variable(
            name="skinDiameter",
            value=round((22 * u.imperial.inch).to_value(u.m), 1) * u.m,
        ),
    ]
