import aastex

import esis_instrument_paper

__all__ = [
    "instrument",
]


def instrument() -> aastex.Section:
    """
    The section describing the instrument as it was built.

    The subsections which describe each part of it are still to be ported,
    and so are the tables and figures the prose here points at.
    """
    result = aastex.Section(aastex.NoEscape(r"The \ESIS\ Instrument"))
    result.append(
        r"""
\ESIS\ is a multi-projection slitless spectrograph that obtains line intensities, Doppler shifts, and
widths in a single snapshot over a 2D \FOV.
Starting from the notional instrument described in Sec.~\ref{sec:TheESISConcept}, \ESIS\ has been designed to ensure all
of the science requirements set forth in Table~\ref{table:scireq} are met.
The final design parameters are summarized in Table~\ref{table:prescription}.

A schematic diagram of a single \ESIS\ channel is presented in Fig.~\ref{fig:schematic}a, while the mechanical features
of the primary mirror and gratings are detailed in Figs.~\ref{fig:schematic}b and \ref{fig:schematic}c, respectively."""
    )

    subsection_pointing = aastex.Subsection("Pointing System")
    subsection_pointing.append(r"""
The imaging target was selected prior to launch, the morning of the day of flight.
During flight, pointing was maintained by the \SPARCS\ \citep{Lockheed69}.
Images from Camera 1 were downlinked and displayed in real time on the \SPARCS\ control system console at intervals of
$\sim$\SI{16}{\second} to verify pointing was maintained during flight.""")
    result.append(subsection_pointing)

    subsection_mechanical = aastex.Subsection("Mechanical")
    subsection_mechanical.append(
        r"""
\ESIS\ and \MOSES\ are mounted on opposite sides of a composite optical table structure originally developed for the
\SPDE~\citep{Bruner95lock}.
The layered carbon fiber structure features a convenient, precisely coplanar array of threaded inserts with precision
counterbores.
The carbon fiber layup is designed to minimize the longitudinal coefficient of thermal expansion.
The optical table is housed in two \skinDiameter\ diameter skin sections, with a total length of \skinLength.
A ball joint and spindle assembly on one end and flexible metal aperture plate on the other hold the optical table in
position inside the skin sections.
The kinematic mounting system isolates the optical table from bending or twisting strain of the skins."""
    )
    result.append(subsection_mechanical)

    subsection_avionics = aastex.Subsection("Avionics")
    subsection_avionics.append(
        r"""
The \ESIS\ \DACS\ is based on the designs used for both \CLASP~\citep{Kano12,Kobayashi12,Narukage2016} and
\HiC~\citep{Kobayashi2014,Rachmeler2019}.
The electronics are a combination of \MOTS\ hardware and custom designed components.
The \DACS\ is a 6-slot, 3U, open VPX PCIe architecture conduction cooled system using an AiTech C873 single board
computer.
The data system also includes a \MOTS\ PCIe switch card, \MSFC\ parallel interface card, and two \MOTS\ Spacewire cards.
A slot for an additional Spacewire card is included to accommodate two more cameras for the next \ESIS\ flight.
The C873 has a \SI{2.4}{\giga\hertz} Intel i7 processor with \SI{16}{\giga\byte} of memory.
The operating temperature range for the data system is \SI{-40}{\celsius}
to \SI{85}{\celsius}.
The operating system for the flight data system is Linux Fedora 23.

The \DACS\ is responsible for several functions;
it controls the \ESIS\ experiment, responds to timers and uplinks, acquires and stores image data from the cameras,
downlinks a subset of images through telemetry, and provides experiment health and status.
The \DACS\ is housed with the rest of the avionics (power supply, analog signal conditioning system) in a
\skinDiameter\ to \SI{0.43}{\meter} transition section outside of the experiment section.
This relaxes the thermal and cleanliness constraints placed on the avionics.
Custom DC/DC converters are used for secondary voltages required by other electronic components.
The use of custom designed converters allowed additional ripple filtering for low noise."""
    )
    result.append(subsection_avionics)

    subsection_distortion = aastex.Subsection("Measured Distortion")
    subsection_distortion.append(
        r"""
Every channel of \ESIS\ forms a dispersed image of the same field, and recovering line intensities,
Doppler shifts and widths from the four images requires knowing where each point of the sky lands on each
detector to a fraction of a pixel, in every exposure.
The as-built model of the optics, assembled from the measured figures of the components and their
nominal placement, correlates with the flight images at only 0.35 to 0.42; the placement of the optics as
flown differs from nominal by enough to move the images by several pixels.
We therefore fit the model to the flight itself, and the fit is described in Appendix~\ref{sec:TheDistortionFit}.
In brief, each channel's grating angles, ruling spacing, pointing and sensor placement were fit against the
exposure at the middle of the flight, using the \AIA\ 304 and 193~\AA\ images of the same field as
a proxy for the scene; the windows the field stop cuts into each image were placed on their measured edges, which
separates the pointing from the gratings; the four channels were registered against one another on the sky at
\HeIion\ and \OVion; and the pointing, the drift of the windows and the focus of the primary mirror were followed
exposure by exposure.
Table~\ref{table:distortionFit} gives the correlation of each channel's model with its exposure after each
stage, and on exposures across the flight that the fit never saw.

Figure~\ref{fig:distortionFlight} shows what moved during the flight.
The pointing drifted by \pointingYawRange\ in yaw and \pointingPitchRange\ in pitch, and the windows drifted by
up to \windowDriftMax, which the model reproduces as a translation of the field stop of a few microns.
With those applied, the channels' skies still slid against one another by \coalignmentBefore\ rms, and by
\coalignmentBeforeMax\ at the first exposure: a translation of each channel's whole image inside its window, the
same at both lines and smooth in time, which nothing after the field stop can produce.
Each channel views the Sun through its own sector of the primary mirror, and a change of focus moves its image
along its own dispersion while the field stop's edges stay put; the motion is reproduced, to the precision of the
measurement, by a focus that differs from sector to sector and drifts through the flight
(Appendix~\ref{sec:TheDistortionFit}).
The focus of the primary as a whole drifted by \defocusRange, and the sectors departed from that mean by up to
\sectorFocusSpread, with the sector of channel 1 moving most; a paraboloid has one focus for every zone, so if
this is real it is the figure of the mirror changing unevenly with temperature, by about \SI{100}{\nano\meter}
of sag between sectors.
The edges the measurement rests on are soft on several sides and the two lines disagree on their motion by up to
half the effect, so the data do not exclude that part of the sector pattern is the apparent position of those
edges drifting; the model carries the simpler reading, one focus per sector, with that caveat.
With it, over the \distortionNumFramesMeasured\ exposures bright enough to measure, the channels agree to
\coalignmentAfterHeI\ rms at \HeIion\ and \coalignmentAfterOV\ at \OVion, and at worst \coalignmentAfterMaxHeI\ and
\coalignmentAfterMaxOV.
What the sector focus leaves, \registrationLeftBySectors\ rms in the registration measurement itself, is also
fit as an empirical offset of each channel's pointing, of up to \channelOffsetMax\ (\channelOffsetMaxPixels), which
halves it to \registrationLeftByOffsets; the model carries these twelve numbers as an option, off by default,
since no mechanism stands behind them (Appendix~\ref{sec:TheDistortionFit}).
Only the component of a misregistration along a channel's dispersion is a velocity error, and a pixel along the
dispersion is \dispersionVelocityHeI\ at \HeIion\ and \dispersionVelocityOV\ at \OVion: projected that way, the
registration of the channels contributes \coalignmentVelocityHeI\ and \coalignmentVelocityOV\ rms to a measured
Doppler shift, and \coalignmentVelocityMaxHeI\ at worst, against quiet-Sun velocities of order
\SI{10}{\kilo\meter\per\second}.
The three dark exposures that close the flight are not constrained by the fit and are extrapolated."""
    )
    subsection_distortion.append(esis_instrument_paper.tables.distortion_fit())
    subsection_distortion.append(esis_instrument_paper.figures.distortion_flight())
    result.append(subsection_distortion)

    return result
