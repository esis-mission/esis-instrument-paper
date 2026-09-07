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
    result.append(r"""
\ESIS\ is a multi-projection slitless spectrograph that obtains line intensities, Doppler shifts, and
widths in a single snapshot over a 2D \FOV.
Starting from the notional instrument described in Section~\ref{sec:TheESISConcept}, \ESIS\ has been designed to ensure
all of the science requirements set forth in Table~\ref{table:scireq} are met.
The final design parameters are summarized in Table~\ref{table:prescription}.

A schematic diagram of a single \ESIS\ channel is presented in Figure~\ref{fig:schematic}a, while the mechanical
features of the primary mirror and gratings are detailed in Figures~\ref{fig:schematic}b and
\ref{fig:schematic}c, respectively.""")

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

    subsection_vignetting = aastex.Subsection("Vignetting")
    subsection_vignetting.append(r"""
The original design of \ESIS\ had no vignetting thanks to a stop placed at the primary mirror that was designed to
perfectly fill the grating with the same amount of light for each point in the \FOV.
This is the \ESIS\ design that was used for the optimization procedure of the grating parameters described in
Section~\ref{subsec:OptimizationandTolerancing}, for example.
All other results described in the paper use the fully-open system.
Before flight, we decided to remove the primary aperture stop to increase the sensitivity of the instrument at the
expense of introducing vignetting to the \ESIS\ \FOV.
This was acceptable since the vignetting was found to be a simple linear field as shown in Figure~\ref{fig:vignetting},
and could be removed in the post-processing phase.""")
    subsection_vignetting.append(esis_instrument_paper.figures.vignetting())
    result.append(subsection_vignetting)

    return result
