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
    # The old draft placed this figure in the Optics subsection, which is not
    # ported yet, so it goes beside the paragraph which first cites it.
    result.append(esis_instrument_paper.figures.schematic())

    subsection_pointing = aastex.Subsection("Pointing System")
    subsection_pointing.append(r"""
The imaging target was selected prior to launch, the morning of the day of flight.
During flight, pointing was maintained by the \SPARCS~\citep{Lockheed69}.
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

    subsection_distortion = aastex.Subsection("Distortion")
    subsection_distortion.append(
        r"""
Imaging from the prime focus to the detector introduces distortion.
Since the \numChannelsWords\ \ESIS\ channels are arranged in four different orientations, the distortion complicates the
comparison of the channels, and we must correct for it.
The distortion is due to two factors: first, the tilt of the detector as needed to maintain good focus over the
\FOV~\citep{Poletto04}; second, the anamorphic magnification of the grating (see \citet{Schweizer1979})."""
    )
    subsection_distortion.append(r"""
\begin{equation}
\begin{split}
\left(x', y'\right) &= \C + \C_x x + \C_y y + \C_\lambda \lambda \\
&+ \C_{xx} x^2 + \C_{xy} x y + \C_{x \lambda} x \lambda \\
&+ \C_{yy} y^2 + \C_{y \lambda} y \lambda + \C_{\lambda \lambda} \lambda^2
\end{split}
\label{eq:distortion}
\end{equation}""")
    subsection_distortion.append(esis_instrument_paper.tables.distortion())
    subsection_distortion.append(esis_instrument_paper.figures.distortion())
    subsection_distortion.append(esis_instrument_paper.figures.distortion_residual())
    result.append(subsection_distortion)

    subsection_coatings = aastex.Subsection("Coatings and Filters")
    subsection_coatings.append(r"""
The diffraction gratings are coated with a multilayer optimized for a center wavelength of \OV,
developed by a collaboration between Reflective X-ray Optics LLC and \LBNL.
In Figure~\ref{fig:gratingEfficiencyVsAngle}, characterization of a single, randomly selected multilayer coated grating at \LBNL\ shows
that the grating reflectivity is constant over the instrument \FOV\ in the $m=1$ order while the $m=0$ order is almost
completely suppressed.
Figure~\ref{fig:gratingMultilayerSchematic} shows a schematic of the coating that achieves peak reflectivity and selectivity in the
$m=0$ order using \gratingCoatingNumLayersWords\ layer pairs of \SiC\ and \Mg.
The \Al\ layers are deposited adjacent to each \Mg\ layer to mitigate corrosion.

The maximum reflectance for the coating alone in the nominal instrument passband is $\sim$\gratingWitnessEfficiency\ in
the upper panel of Figure~\ref{fig:componentEfficiencyVsWavelength}, measured from witness samples coated at the same time as the diffraction gratings.
Combined with the predicted groove efficiency from Section~\ref{subsec:Optics} and, given the relatively shallow groove profile
and near normal incidence angle, the total reflectivity in first order is $\sim$\gratingEfficiency\ at \OV.
This is confirmed by the first order efficiency measured from a single \ESIS\ grating in the lower panel of
Figure~\ref{fig:componentEfficiencyVsWavelength}.

Unlike \EUV\ imagers (\eg, \TRACE~\citep{Handy99}, \AIA~\citep{Lemen12}, and the \HiC~\citep{Kobayashi2014})
the \ESIS\ passband is defined by a combination of the field stop and grating (Section~\ref{subsec:Optics},
Figure~\ref{fig:projections}) rather than multilayer coatings.
The coating selectivity is therefore not critical in this respect, allowing the multilayer to be manipulated to
suppress out-of-band bright, nearby emission lines.
The lower panel of Figure~\ref{fig:componentEfficiencyVsWavelength} shows the peak reflectance of the grating multilayer is shifted slightly towards longer
wavelengths to attenuate the \HeI\ emission line, reducing the likelihood of detector saturation.
A similar issue arises with the bright \HeII\ line.
Through careful design of the grating multilayer, the reflectivity at this wavelength is $\sim$\gratingHeIIRejectionRatio\ of that
at \OV\ (upper panel of Figure~\ref{fig:componentEfficiencyVsWavelength}).
In combination with the primary mirror coating (described below) the rejection ratio at \HeIIwavelength\ is
$\sim$\totalHeIIRejection.  Thus, \HeII\ emission is completely attenuated at the \CCD.

The flight and spare primary mirrors were coated with the same \AlShort/\SiCShort/\MgShort\ multilayer.
Corrosion of this multilayer rendered both mirrors unusable.
The failed coating was stripped from primary mirror SN001.
The mirror was then re-coated with a \primaryCoatingBaseThickness\ thick layer of \Cr\ to improve adhesion followed by a
\primaryCoatingThickness\ thick layer of \SiC.
The reflectance of this coating deposited on a \Si\ wafer witness sample appears in
Figure~\ref{fig:componentEfficiencyVsWavelength}.
The spare primary mirror (SN002) retains the corroded \AlShort/\SiCShort/\MgShort\ multilayer.

The \Si\ \CCDs\ are sensitive to visible light as well as \EUV.
Visible solar radiation is much stronger than \EUV, and visible stray light can survive multiple scatterings while
retaining enough intensity to contaminate the \EUV\ images.
Lux\'el~\citep{Powell90} \Al\ filters \filterThickness\ thick were
used to shield each \CCD\ from visible light.
The \Al\ film is supported by a \filterMeshPitch\ line per inch (lpi) \Ni\ mesh, with \filterMeshRatio\ transmission.
The theoretical filter transmission curve, modeled from CXRO data~\citep{Henke93}, is displayed in
Figure~\ref{fig:componentEfficiencyVsWavelength}.
We conservatively estimate filter oxidation at the time of launch as a \filterOxideThickness\ thick layer of Al$_2$O$_3$.

An \Al\ filter is positioned in front of the focal plane of each \CCD\ by a filter tube, creating a light-tight box with a
labyrinthine evacuation vent (\eg, Figure~\ref{F-cameras}).
The placement of the filter relative to the \CCD\ is optimized so that the filter mesh shadow is not visible.
By modeling the filter mesh shadow, we find that a position far from the \CCD\ (\filterToDetectorDistance) and mesh grid
clocking of \filterClocking\ to the detector array reduces the shadow amplitude well below photon statistics.
The \MOSES\ instrument utilizes a similar design;
no detectable signature of the filter mesh is found in data and inversion residuals from the 2006 \MOSES\ flight.

To prevent oxidation, and to minimize the risk of tears, pinholes, and breakage from handling, the filters were
stored in a nitrogen purged environment until after payload vibration testing.""")
    subsection_coatings.append(
        esis_instrument_paper.figures.grating_efficiency_vs_angle()
    )
    subsection_coatings.append(
        esis_instrument_paper.figures.grating_multilayer_schematic()
    )
    subsection_coatings.append(
        esis_instrument_paper.figures.component_efficiency_vs_wavelength()
    )
    subsection_coatings.append(
        esis_instrument_paper.figures.grating_efficiency_vs_position()
    )
    result.append(subsection_coatings)

    subsection_sensitivity = aastex.Subsection("Sensitivity and Cadence")
    subsection_sensitivity.append(r"""
Count rates for \ESIS\ are estimated using the expected component throughput from
Section~\ref{subsec:CoatingsandFilters} and the \CCD\ \QE\ listed in Table~\ref{table:prescription}.
Line intensities are derived from \VR\ and the \SOHO/\CDS~\citep{Harrison95} data, and are given in a variety of
solar contexts: \QS, \CHs, and \ARs.
The \SI{100}{\percent} duty cycle of \ESIS\ (Section~\ref{subsec:Cameras}) gives us the flexibility to use the shortest
exposures that are scientifically useful.
So long as the shot noise dominates over read noise (which is true even for our coronal hole estimates at
\detectorExposureLength\ exposure length), we can stack exposures without a significant \SNR\ penalty.
Table~\ref{table:counts} shows that \ESIS\ is effectively shot noise limited with a \detectorExposureLength\ exposure.
The signal requirement in Table~\ref{table:scireq} is met by stacking exposures.
Good quality images ($\sim$\goodImageCounts\ counts) in active regions can be obtained by stacking
\activeRegionStackLength\ worth of exposures.
This cadence is sufficient to observe explosive events, but will not resolve torsional Alfv\'en waves described in
Section~\ref{sec:ScienceObjectives}.
However, by stacking multiple \detectorExposureLength\ exposures, sufficient \SNR\ \emph{and} temporal resolution of
torsional Alfv\'en wave oscillations can be obtained.""")
    subsection_sensitivity.append(esis_instrument_paper.tables.counts())
    result.append(subsection_sensitivity)

    subsection_alignment = aastex.Subsection("Alignment and Focus")
    subsection_alignment.append(r"""
In the conceptual phase of \ESIS, the decision was made to perform focus and alignment in visible light with a
\HeNe\ source.
Certain difficulties are introduced by this choice, however, the benefits outweigh the operational complexity and
equipment that would be required for focus in \EUV.
Moreover, a sounding rocket instrument requires robust, adjustment-free mounts to survive the launch environment.
Such a design is not amenable to iterative adjustment in vacuum.  The choice of alignment wavelength is arbitrary for
most components;
\CCD\ response and multilayer coating reflectivity is sufficient across a wide band of visible wavelengths.
The exceptions are the thin film filters (which were not installed until just before launch and have no effect on
telescope alignment and focus) and the diffraction gratings.
Visible light gratings were manufactured specifically for alignment and focus.
These gratings are identical to the \EUV\ flight version, but with a ruling pattern scaled to a
\SI{632.8}{\nano\meter} wavelength.""")
    subsection_alignment.append(esis_instrument_paper.figures.grating_mount())
    subsection_alignment.append(r"""
After alignment and focus had been obtained with the \HeNe\ source, the instrument was prepared for flight by
replacing the visible gratings by the \EUV\ flight versions.
Each grating (\EUV\ and alignment) is individually mounted to a backing plate using a bipod system similar to that of
the primary mirror.
The array of gratings on their backing plates are in turn mounted to a single part which we call the `tuffet.'
The backing plate is attached to the tuffet by bolts through spherical washers.
With this mounting scheme, the gratings can be individually aligned in tip/tilt.
The tuffet is attached to the secondary mirror mount structure (Figure~\ref{fig:gratingMount}).
This enables the entire grating array to be replaced simply by removing/installing the tuffet, such as when switching
between alignment and \EUV\ gratings.

Properly positioning the gratings was expected to be the most difficult aspect of final telescope assembly.
Table~\ref{table:errorBudget} shows that the telescope is very sensitive to defocus.
The depth of field is an order of magnitude smaller in \EUV\ than in visible light.
Moreover, the sensitivity to defocus at the gratings is $M^2+1=\gratingDefocusSensitivity$ times greater than at the
detectors, where $M=\armRatio$ is the ratio of the grating exit arm to the grating entrance arm.
Another sensitive aspect of the telescope is grating tip/tilt.
A tolerance of $\sim\pm$\gratingTiltTolerance\ is needed to ensure that the entire image lands on the active area of
the \CCD.

%Once the visible gratings are aligned and focused, the challenge is to transfer this alignment to the UV gratings.
%\citet{Johnson18} describes a procedure and the apparatus constructed to accurately transfer the position of an
%alignment grating radius to an \EUV\ flight grating.
%This device, displayed in Fig.~\ref{F-alt}, consists of an array of three miniature confocal microscopes that record the
%position of the alignment grating radius.
%The alignment grating is replaced by an \EUV\ grating, which is then measured into position by the same apparatus.
%This device (and procedure) is capable of obtaining position measurements of the diffraction gratings to a repeatability
%of $\approx$\SI{14}{\micro\meter} in the three confocal channels.
%This alignment transfer apparatus will ensure that the \EUV\ flight gratings are positioned to within the tolerances
%described in Table~\ref{table:tol}.

Once the visible gratings were aligned and focused, the challenge was to transfer this alignment to the \EUV\ flight
gratings.
We performed this transfer using a 4D Phasecam 6000 interferometer.
We aligned the interferometer to each visible grating such that the tip, tilt, and defocus aberrations were zero.
Then, placing the corresponding flight grating in the visible grating's place, we shimmed the mounting screws of the
flight grating to match the tip, tilt, and defocus of the alignment grating.
Since the mounting interface for the tuffet is extremely repeatable by design we were able to swap tuffets and compare
their alignment and focus to ensure everything was transferred correctly.

When transferring the focus and alignment two key details were considered.
First, there is nothing about the tuffet that constrains the grating roll.
Therefore, we needed to ensure each flight grating had the same roll as each visible grating.
This was accomplished by using a \HeNe\ laser diverged through a cylindrical optic that illuminated each grating with a
line perpendicular \jake{better make sure I know which direction is implied here} to the grating blaze direction.
The line of light was reflected back onto a ruled target that could be compared between gratings.
Since our alignment gratings were ruled to image light of approximately an order of magnitude longer wavelength the
laser and cylindrical optic were placed at the position of Littrow for the 10th order image in the visible grating,
and the 1st order for the \EUV\ gratings.
Second, during testing we measured slight differences in radius of curvature between each grating.
Therefore each flight grating was prescribed a specific amount of defocus to account for the difference in radius of
curvature between each optic when transferring alignment and focus.""")
    result.append(subsection_alignment)

    subsection_baffles = aastex.Subsection("Apertures and Baffles")
    # A figure across both columns goes at the top of a page after the one it
    # is defined on, so it is defined here rather than after the paragraph
    # that cites it, which would put it after the end of the subsection.
    subsection_baffles.append(esis_instrument_paper.figures.baffles())
    subsection_baffles.append(r"""
\jake{Needs a big rework}
Each channel of \ESIS\ was designed with two apertures: one at the surface of the grating and a stop in front of the
primary mirror.
The purpose of the aperture at the grating is to mask the out-of-figure margins at the edges of these optics.
This provides a well defined edge to the clear aperture of each grating while also keeping unwanted rays from being
reflected from the grating margins and back onto the \CCDs.
The dimensions of the grating aperture match those of the grating clear aperture shown in Figure~\ref{fig:schematic}c.

The stop at the primary mirror was designed to be the stop of each channel.
Its area was maximized under the constraint that no rays be vignetted anywhere else in the system.
The gratings and their clear apertures were the most significant areas of concern for potential vignetting, so the
shape of the stop was largely influenced by the shape of the grating clear aperture.
The inner extent of the stop was defined by the occultation of the primary by the shadow cast from the gratings and
their mounts.
This presented an intricate geometry problem, as the occultation is a function of the incoming field angle, the
radial extent of the grating mount, and the distance of the mount to the primary mirror along the optical axis.
Hence, the inner extent of the stop was solved for iteratively with the optimization described in
Section~\ref{subsec:OptimizationandTolerancing}, which affected the placement of the gratings relative to the primary
mirror.

After final optimization, the stop geometry was analyzed with the optical model to check for vignetting at the
grating.
A footprint diagram was generated at the grating from multiple grids of rays.
The incidence angle of each grid of rays corresponded to the extremes of the \FOV\ defined by the positions of the
eight points of the octagonal field stop.
The footprint diagram showed that, with the stop completely filled, no ray landed outside of the grating clear
aperture, and no ray was intercepted by the central obscuration.

This non-vignetting stop left considerable surface area of the primary mirror unused, which could only be put to use
by relaxing the vignetting constraint.
Before flight, the stop was removed to increase the sensitivity of the instrument at the expense of vignetting
(Section~\ref{subsec:Vignetting}), which made the grating aperture the stop of each channel.
The footprint of the beam of each channel on the primary mirror in Figure~\ref{fig:schematic}b is that of the
instrument as flown, without the stop.

The \ESIS\ baffles are designed to block direct light paths between the front aperture plate and the \CCDs\ for any
ray $<$\SI{1.4}{\degree} from the optical axis.
This angle is purposefully larger than the angular diameter of the sun ($\sim$\SI{0.5}{\degree}) so that any direct
paths are excluded from bright sources in the solar corona.
All baffles are bead-blasted, anodized \Al\ sheet metal oriented perpendicular to the optical axis.
The size and shape of the cutouts were determined using a combination of the ray trace from
Section~\ref{subsec:OptimizationandTolerancing} and 3D modeling.
Between the primary mirror and the gratings, each cutout is the footprint of the rays of that trace where they cross
the baffle.
Between the gratings and the \CCDs, the light path is defined as the volume that connects each vertex of the grating
clear aperture to every vertex of the image of the octagonal field stop on the \CCD.
This is a conservative definition that ensures no rays within the \FOV\ are excluded, and therefore unintentionally
vignetted by the baffles.
The cutouts there are the projection of this volume onto the baffle.
A conservative \SI{1}{\milli\meter} margin is added to each cutout to prevent unintentional vignetting.
A model of the six baffles, showing their cutouts and positions on the optical bench, is displayed in
Figure~\ref{fig:baffles}.""")
    result.append(subsection_baffles)

    subsection_cameras = aastex.Subsection("Cameras")
    subsection_cameras.append(esis_instrument_paper.figures.cameras())
    subsection_cameras.append(r"""
The \ESIS\ \CCD\ cameras were designed and constructed by \MSFC\ and were the latest in a
series of camera systems developed specifically for use on solar space flight instruments.
The \ESIS\ camera heritage includes those flown on both the \CLASP~\citep{Kano12,Kobayashi12} and
\HiC~\citep{Kobayashi2014}.

The \ESIS\ detectors are \detectorName\ astro-process \CCDs\ from \detectorManufacturer.
For each camera, the \CCD\ is operated in a split frame transfer mode with each of the four ports read out by a
\detectorAnalogToDigitalBits-bit A/D converter.
The central $\detectorPixelsX \times \detectorPixelsY$ pixels of the $2k\times2k$ device are used for imaging, while
the outer two regions are used for storage.
\DetectorNumOverscanColumnsWords\ overscan columns on either side of the imaging area and
\detectorNumMaskedRowsWords\ extra rows in each storage region were intended to monitor read noise and dark current.
When the camera receives the trigger signal, it transfers the image from the imaging region to the storage regions and
starts image readout.
The digitized data are sent to the \DACS\ through a SpaceWire interface immediately, one line at a time.
The frame transfer takes \detectorFrameTransferTime, and readout takes \detectorReadoutTime.
The cadence is adjustable from \detectorExposureLengthMin\ to \detectorExposureLengthMax\ in increments of
\detectorExposureLengthIncrement, to satisfy the requirement listed in Table~\ref{table:scireq}.
Because the imaging region is continuously illuminated, the action of frame transfer (transferring the image from the
imaging region to the storage regions) also starts the next exposure without delay.
Thus the exposure time is controlled by the time period between triggers.
Camera~\detectorTriggerChannel\ (Figure~\ref{fig:cameras}) generates the sync trigger, which is fed back into
Camera~\detectorTriggerChannel's trigger input and provides independently buffered triggers to the remaining three
cameras.
The trigger signals are synchronized to better than $\pm$\detectorSynchronizationError.
Shutterless operation allows \ESIS\ to observe with a \SI{100}{\percent} duty cycle.
The cadence is limited only by the \detectorReadoutTime\ readout time.

\MSFC\ custom designed the camera board, enclosure, and mounting structure for \ESIS\ to fit the unique packaging
requirements of this experiment (Figure~\ref{fig:cameras}).
The front part of the camera is a metal block which equalizes the temperature across the \CCD\ while fastening it in
place.
The carriers of all cameras are connected to a central two-piece copper (\SI{3}{\kilo\gram}) and aluminum
(\SI{1}{\kilo\gram}) thermal reservoir (cold block) by flexible copper cold straps.
The flexible cold straps allow individual cameras to be translated parallel to the optical axis (by means of shims) up
to $\sim$\SI{13}{\milli\meter} to adjust focus in each channel prior to launch.
The centrally located cold block was cooled by \LN\ flow from outside the payload until just before launch.
The \LN\ flow was controlled automatically by a \GSE\ computer so that all cameras were maintained above survival
temperature but below the target temperature of \detectorTemperatureTarget\ to ensure a negligible dark current level.

The gain, read noise, and dark current of the four cameras were measured at \MSFC\ using an ${}^{55}$Fe radioactive
source.
Cameras are labeled \channelNames\ with associated serial numbers \detectorSerialNumbers\ respectively in
Figure~\ref{fig:cameras}.
Gain ranges from \detectorGainMin\ to \detectorGainMax\ in each quadrant of all four cameras.
Table~\ref{table:cameras} lists gain, read noise, and dark current by quadrant for each camera.

The \QE\ of the \ESIS\ \CCDs\ was not measured before flight.
This paper models it with the measurements of a back-illuminated e2v CCD97 by \citet{Moody2017} and
\citet{Heymes2020}, which give a \QE\ of \detectorQuantumEfficiencyHeI\ at \HeI\ and \detectorQuantumEfficiencyOV\ at
\OV.""")
    subsection_cameras.append(esis_instrument_paper.tables.cameras())
    result.append(subsection_cameras)

    return result
