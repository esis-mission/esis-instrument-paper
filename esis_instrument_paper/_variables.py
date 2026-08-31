import aastex
import astropy.units as u
import esis
import num2words
import pylatex

import esis_instrument_paper

__all__ = [
    "variables",
]


def _pending(name: str) -> aastex.Variable:
    """
    A quantity the model cannot supply yet, marked where it is cited.

    Every number in this article is computed from the instrument model, and
    these are the ones the model has no answer for. They are written into the
    text as ``??`` rather than guessed at or left out, so that a draft shows
    plainly what is still owed and no placeholder can be mistaken for a
    measurement.
    """
    return aastex.Variable(name=name, value=aastex.NoEscape(r"\textbf{??}"))


def variables() -> list[aastex.Variable]:
    """
    A list of LaTeX variables for every numeric quantity cited in the prose.

    Reference these macros in section strings instead of hardcoding numbers so
    that the text stays in sync with the instrument model.

    A few of these are still literals, since the model does not carry the
    quantity they describe: two which belong to MOSES or to the payload
    rather than to the instrument, and the spectroscopic name of each
    emission line, whose wavelength the model does carry.
    """
    design = esis.flights.f1.optics.design()

    # `design` is the flight instrument, whose four channels were populated
    # from the six positions of `design_full`.
    num_channels = design.camera.channel.shape[design.axis_channel]

    # the performance the mission required of the instrument, as opposed to
    # the performance the instrument achieved
    requirements = esis.flights.f1.optics.requirements()

    # One channel of the flight instrument. The field of view and the
    # dispersion belong to a channel rather than to the set of them, and the
    # nominal model is used rather than a Monte Carlo population, so that
    # neither carries an axis of its own.
    channel = esis.flights.f1.optics.design_single(num_distribution=0)

    # The traced outline of the field, which for an octagonal field stop is
    # wider corner to corner than edge to edge by a factor of
    # 1 / cos(22.5 degrees). This group means edge to edge when it says field
    # of view, which is twice the least distance from the centre of the field
    # to its outline.
    boundary = channel.system.field_boundary
    fov = 2 * boundary.length.min(channel.system.axis_stops)

    # The observing time is taken from the flight timeline, as the span over
    # which the rate gyros held the payload pointed. The 30 exposures of the
    # Level 1 data sit inside it, beginning 12 seconds after it opens and
    # ending as it closes.
    timeline = esis.flights.f1.nsroc.timeline()
    length_observation = (
        timeline.timedelta_sparcs_rlg_disable - timeline.timedelta_sparcs_rlg_enable
    )

    return [
        # TODO: this describes MOSES rather than ESIS, so it is not something
        # the ESIS model can supply.
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
        aastex.Variable(
            name="numChannelsWords",
            value=aastex.NoEscape(num2words.num2words(num_channels)),
        ),
        # the same word capitalised, for a sentence which opens with it
        aastex.Variable(
            name="NumChannelsWords",
            value=aastex.NoEscape(num2words.num2words(num_channels).capitalize()),
        ),
        aastex.Variable(
            name="OVwavelength",
            value=esis.flights.f1.spectrum.O_V.wavelength,
        ),
        # The model carries the wavelength of each line but not its name, so
        # the spectroscopic notation is written here.
        aastex.Variable(
            name="OVion",
            value=aastex.NoEscape(r"O\,\textsc{v}"),
        ),
        aastex.Variable(
            name="MgXion",
            value=aastex.NoEscape(r"Mg\,\textsc{x}"),
        ),
        aastex.Variable(
            name="OV",
            value=aastex.NoEscape(r"\OVion~\OVwavelength"),
        ),
        aastex.Variable(
            name="spatialResolutionRequirement",
            value=requirements.resolution_spatial,
        ),
        aastex.Variable(
            name="angularResolutionRequirement",
            value=requirements.resolution_angular.round(1),
        ),
        aastex.Variable(
            name="spectralResolutionRequirement",
            value=requirements.resolution_spectral,
        ),
        aastex.Variable(
            name="fovRequirement",
            value=requirements.fov,
        ),
        aastex.Variable(
            # a plain number rather than the dimensionless quantity it is in
            # the model, which would otherwise be set with an empty unit
            name="snrRequirement",
            value=float(requirements.snr),
        ),
        aastex.Variable(
            name="cadenceRequirement",
            value=requirements.cadence,
        ),
        aastex.Variable(
            name="observingTimeRequirement",
            value=requirements.length_observation,
        ),
        aastex.Variable(
            name="detectorExposureLength",
            value=design.camera.timedelta_exposure,
        ),
        aastex.Variable(
            name="HeIion",
            value=aastex.NoEscape(r"He\,\textsc{i}"),
        ),
        aastex.Variable(
            name="fov",
            value=fov.ndarray.to(u.arcmin).round(1),
        ),
        aastex.Variable(
            # The dispersion varies by about a percent across the passband,
            # and its Doppler equivalent by ten times that, so it is quoted
            # at the line the instrument was designed around rather than
            # averaged over the passband.
            name="dispersionDoppler",
            value=channel.dispersion_doppler(
                wavelength=esis.flights.f1.spectrum.O_V.wavelength,
            ).ndarray.round(1),
            # astropy orders the bases of a composite unit itself, which puts
            # the pixels before the seconds; this is the order it is read in,
            # and the order the requirement beside it is written in
            unit=(u.km, u.s**-1, u.pix**-1),
        ),
        aastex.Variable(
            name="observingTime",
            value=length_observation.round(1),
        ),
        aastex.Variable(
            # How many exposures to stack is chosen rather than derived: it
            # buys signal at the cost of the cadence the torsional waves need,
            # and the old draft settled on twelve. It is written here because
            # the count rates are computed from it, not the other way about.
            name="NumExpInStack",
            value=12,
        ),
        aastex.Variable(
            # the number of emission lines drawn in the bunch figure
            name="numEmissionLines",
            value=aastex.NoEscape(
                num2words.num2words(esis_instrument_paper.figures.num_emission_lines)
            ),
        ),
        aastex.Variable(
            # the pressure the quiet sun spectrum is computed at
            name="chiantiPressure",
            value=esis_instrument_paper._spectrum.pressure,
        ),
        aastex.Variable(
            # The files the spectrum was computed from, named rather than
            # described, so that the article says which of the several
            # abundance tables and several differential emission measures
            # CHIANTI carries were the ones read.
            name="chiantiAbundances",
            # `Command` escapes its argument, which these names need: an
            # underscore outside of mathematics is a subscript and does not
            # compile, and every one of these file names has several.
            value=aastex.NoEscape(
                pylatex.Command(
                    "texttt",
                    esis_instrument_paper._spectrum.abundance,
                ).dumps()
            ),
        ),
        aastex.Variable(
            name="chiantiDEM",
            value=aastex.NoEscape(
                pylatex.Command(
                    "texttt",
                    esis_instrument_paper._spectrum.dem,
                ).dumps()
            ),
        ),
        aastex.Variable(
            # Read from the database rather than written down, since which
            # version is installed is what the numbers were computed from,
            # and the two would otherwise drift apart silently. The lines in
            # the passband move by a few percent between versions.
            name="chiantiVersion",
            value=aastex.NoEscape(esis_instrument_paper._spectrum.version()),
        ),
        # Quantities the model cannot supply yet. Each is a capability of the
        # instrument rather than a requirement of the mission, and each waits
        # on analysis which has not been ported: the spatial resolution on the
        # error budget, and the stacked signal-to-noise ratio on the count
        # rates.
        _pending("spatialResolutionTotal"),
        _pending("StackedCoronalHoleSNR"),
    ]
