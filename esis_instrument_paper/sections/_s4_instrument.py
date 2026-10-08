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

    subsection_coatings = aastex.Subsection("Coatings and Filters")
    subsection_coatings.append(r"""
The diffraction gratings are coated with a multilayer optimized for a center wavelength of \OV,
developed by a collaboration between Reflective X-Ray Optics LLC and \LBNL.
In Fig.~\ref{fig:gratingEfficiencyVsAngle}, characterization of a single, randomly selected multilayer coated grating at \LBNL\ shows
that the grating reflectivity is constant over the instrument \FOV\ in the $m=1$ order while the $m=0$ order is almost
completely suppressed.
Figure~\ref{fig:gratingMultilayerSchematic} shows a schematic of the coating that achieves peak reflectivity and selectivity in the
$m=0$ order using \gratingCoatingNumLayersWords\ layer pairs of \SiC\ and \Mg.
The \Al\ layers are deposited adjacent to each \Mg\ layer to mitigate corrosion.

The maximum reflectance for the coating alone in the nominal instrument passband is $\sim$\gratingWitnessEfficiency\ in
the upper panel of Figure~\ref{fig:componentEfficiencyVsWavelength}, measured from witness samples coated at the same time as the diffraction gratings.
Combined with the predicted groove efficiency from \S\,\ref{subsec:Optics} and, given the relatively shallow groove profile
and near normal incidence angle, the total reflectivity in first order is $\sim$\gratingEfficiency\ at \OV.
This is confirmed by the first order efficiency measured from a single \ESIS\ grating in the lower panel of
Figure~\ref{fig:componentEfficiencyVsWavelength}.

Unlike \EUV\ imagers (\eg, \TRACE~\citep{Handy99}, \AIA~\citep{Lemen12}, and the \HiC~\citep{Kobayashi2014})
the \ESIS\ passband is defined by a combination of the field stop and grating (\S\,\ref{subsec:Optics},
Fig.~\ref{fig:projections}) rather than multilayer coatings.
The coating selectivity is therefore not critical in this respect, allowing the multilayer to be manipulated to
suppress out-of-band bright, nearby emission lines.
The lower panel of Figure~\ref{fig:componentEfficiencyVsWavelength} shows the peak reflectance of the grating multilayer is shifted slightly towards longer
wavelengths to attenuate the \HeI\ emission line, reducing the likelihood of detector saturation.
A similar issue arises with the bright \HeII\ line.
Through careful design of the grating multilayer, the reflectivity at this wavelength is $\sim$\gratingHeIIRejectionRatio\ of that
at \OV\ (lower panel of Figure~\ref{fig:componentEfficiencyVsWavelength}).
In combination with the primary mirror coating (described below) the rejection ratio at \HeIIwavelength\ is
$\sim$\totalHeIIRejection.  Thus, \HeII\ emission is completely attenuated at the \CCD.

The flight and spare primary mirrors were coated with the same \AlShort/\SiCShort/\MgShort\ multilayer.
Corrosion of this multilayer rendered both mirrors unusable.
The failed coating was stripped from primary mirror SN001.
The mirror was then re-coated with a \primaryCoatingBaseThickness\ thick layer of \Cr\ to improve adhesion followed by a
\primaryCoatingThickness\ thick layer of \SiC.
The reflectance of this coating deposited on a \Si\ wafer witness sample appears in
Fig.~\ref{fig:componentEfficiencyVsWavelength}.
The spare primary mirror (SN002) retains the corroded \AlShort/\SiCShort/\MgShort\ multilayer.

The \Si\ \CCDs\ are sensitive to visible light as well as \EUV.
Visible solar radiation is much stronger than \EUV, and visible stray light can survive multiple scatterings while
retaining enough intensity to contaminate the \EUV\ images.
Lux\'el \citep{Powell90} \Al\ filters \filterThickness\ thick were
used to shield each \CCD\ from visible light.
The \Al\ film is supported by a \filterMeshPitch\ line per inch (lpi) \Ni\ mesh, with \filterMeshRatio\ transmission.
The theoretical filter transmission curve, modeled from CXRO data \citep{Henke93}, is displayed in
Fig.~\ref{fig:componentEfficiencyVsWavelength}.
We conservatively estimate filter oxidation at the time of launch as a \filterOxideThickness\ thick layer of Al$_2$O$_3$.

An \Al\ filter is positioned in front of the focal plane of each \CCD\ by a filter tube, creating a light-tight box with a
labyrinthine evacuation vent (e.g., Fig.~\ref{F-cameras}).
The placement of the filter relative to the \CCD\ is optimized so that the filter mesh shadow is not visible.
By modeling the filter mesh shadow, we find that a position far from the \CCD\ (\filterToDetectorDistance) and mesh grid
clocking of \filterClocking\ to the detector array reduces the shadow amplitude well below photon statistics.
The \MOSES\ instrument utilizes a similar design;
no detectable signature of the filter mesh is found in data and inversion residuals from the 2006 \MOSES\ flight.

To prevent oxidation, and to minimize the risk of tears, pinholes, and breakage from handling, the filters were
stored in a nitrogen purged environment until after payload vibration testing.""")
    result.append(subsection_coatings)

    return result
