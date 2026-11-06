import aastex

__all__ = [
    "conclusions",
]


def conclusions() -> aastex.Section:
    """
    The section which closes the article.

    Ported from the old draft, which wrote most of it before the launch. Its
    numbers are taken from the model, as the old draft's notes asked, and the
    verbs which described the flight before it happened are in the past tense.
    The old draft's comparison with MUSE is gone, since the introduction now
    gives MUSE a raster about as short as the cadence of ESIS, and its outlook
    now cites :cite:t:`Parker2022` for the first results and names the second
    flight.
    """
    result = aastex.Section("Conclusions and Outlook")
    result.append(r"""
\ESIS\ is a next generation slitless spectrograph, designed to obtain co-temporal spectral and spatial images of the solar
transition region and corona.
In this paper, we present details of the scientific objectives, instrument, image and spectral resolution, data
acquisition, and flight profile.

Operating at a \detectorExposureLength\ cadence, \ESIS\ acquired spectra over its full \FOV\
$\sim$\numExposuresObserving\ times during its sounding rocket flight.

\ESIS\ follows on the proven \MOSES\ design, incorporating several design changes to improve the utility of the instrument.
The symmetrical arrangement of \CCDs\ and diffraction gratings results in a compact instrument while increasing the number
of dispersed images and dispersion planes.
This aids the inversion process, while also allowing access to higher order spectral line profile moments.
Individual gratings improve resolution by controlling aberration in each channel.
The addition of a field stop eliminates spectral contamination and provides an easily recognizable edge for data
inversion.
The \ESIS\ design also demonstrates that all this can be accomplished in a volume small enough to serve as a prototype for
a future orbital instrument.

For the first flight, \numChannelsWords\ of the six available \ESIS\ channels were populated with optics optimized
around the \OVion\ emission line.
The large (\fov), high resolution \FOV\ (\spatialResolutionMax, \spectralResolution) can simultaneously observe the
evolution of small scale \EUV\ flows and large scale \MHD\ waves in high temporal cadence.
\ESIS\ also enables the study of transport of mass and energy in the transition region and corona during the
$\sim$\observingTimeMinutes~minute data collection portion of rocket flight.

\ESIS\ was recovered after a successful first launch on 2019 September 30, with first results from its data reported by
\citet{Parker2022}.
A second flight, \mbox{\ESIS-II}, is planned for 2027, with new optics for the \NeVIIion\ and \SiXIIion\ lines, and
the instrument will be refined further with an eye toward orbital opportunities.
Suborbital flights such as \mbox{\ESIS-II} allow us to expand the instrument to its full complement of six channels and
refine our data analysis methods, but do not provide access to major flares and eruptive events that drive space
weather.
The long term prospect is that an \ESIS-like instrument on an orbital platform could provide high cadence maps of
spectral line profiles in solar flares, allowing unique and comprehensive observations of the dynamics in solar eruptive
events, flare ribbons, and the flare reconnection region.""")
    return result
