import aastex

__all__ = [
    "abstract",
]


def abstract() -> aastex.Abstract:
    """
    The abstract of this article.

    Ported from the old draft, with its numbers from the model. The sentence
    on the cadence is the one Amy suggested in the old draft's notes, the
    sentence on reconstructing the line profiles is in the present tense, and
    the sentence which promised a paper on the flight data, since published
    before this one, is gone.

    The name of the instrument is written out, rather than given by the macro
    of its acronym. AASTeX insets the abstract by setting its left margin when
    its paragraph starts, and a macro which starts the paragraph inside a
    group resets the margin when the group ends, so the abstract would run the
    full width of the page.

    The acronyms are reset after the abstract, so that any it uses are spelled
    out again in the introduction.
    """
    result = aastex.Abstract()
    result.append(r"""
The EUV Snapshot Imaging Spectrograph (ESIS) is a next generation rocket borne instrument designed to investigate
magnetic reconnection and energy transport in the solar atmosphere by observing emission lines formed in the
chromosphere (\HeI), the transition region (\OV), and corona (\MgX).
The instrument is a pseudo Gregorian telescope with an octagonal field stop at prime focus.
This field stop is re-imaged using an array of \numChannelsWords\ spherical diffraction gratings with differing
dispersion angles oriented in \SI{45}{\degree} increments, with each diffraction grating projecting the spectrum onto a
unique detector.
The instrument is designed to be capable of obtaining co-temporal spatial (\plateScaleMean) and spectral (\dispersion)
images at high cadence ($\geq$\detectorExposureLengthMin).
Combining the co-temporal exposures from all the detectors enables us to reconstruct line profile information at high
spatial and spectral resolution over a large (\fov) field of view.
The instrument was launched on 2019 September 30.
\acresetall""")
    return result
