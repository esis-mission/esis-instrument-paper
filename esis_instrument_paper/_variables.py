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

    Several of these are still literals. The version of ``esis`` on PyPI
    predates the modules they should come from, so they cannot be taken from
    the model until it is released.
    """
    return [
        aastex.Variable(
            name="mosesDispersionDoppler",
            value=29 * u.km / u.s / u.pix,
        ),
        # TODO: the current model does not carry a skin diameter; this is the
        # 22 inch value from the old model.
        aastex.Variable(
            name="skinDiameter",
            value=round((22 * u.imperial.inch).to_value(u.m), 1) * u.m,
        ),
        # TODO: the old draft spelled the number of channels with `num2words`.
        aastex.Variable(
            name="numChannelsWords",
            value=aastex.NoEscape("four"),
        ),
        # TODO: take this from `esis.flights.f1.spectrum.O_V.wavelength`.
        aastex.Variable(
            name="OVwavelength",
            value=629.73 * u.AA,
        ),
    ]
