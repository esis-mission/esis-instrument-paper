import aastex

import esis_instrument_paper

__all__ = [
    "science_objectives",
]


def science_objectives() -> aastex.Section:
    result = aastex.Section("Science Objectives")
    result.append(r"""
Early flights of \MOSES\ demonstrated a working concept of simultaneous \EUV\ imaging and spectroscopy.
This concept adds a unique capability to the science that we can obtain from the \EUV\ solar atmosphere.
\ESIS\ as designed improves upon the \MOSES\ concept, as discussed in the previous section, and therefore improves our ability
to accomplish our scientific objectives.
In this section, we set forth the specific scientific objectives of the \ESIS\ mission.
It is from these objectives that we derived the quantitative science requirements (\S\,\ref{subsec:ScienceRequirements})
that drove the \ESIS\ design.

The \ESIS\ mission was designed to achieve the following two overarching science goals: \begin{inparaenum}[(1)]
\item observe magnetic reconnection in the \TR\label{item-goal1}, and \item map the transfer of energy through the \TR\
with emphasis on \MHD\ waves\label{item-goal2}. \end{inparaenum}
These objectives have significant overlap with the missions of \IRIS~\citep{IRIS14}, the \EIS~\citep{Culhane07}
aboard Hinode, the \EUNIS~\citep{Brosius07,Brosius14}, and a long history of \FUV\ and \EUV\ slit spectrographs.
The \ESIS\ instrument, however, can obtain both spatial and spectral information co-temporally.
This will allow us to resolve complicated morphologies of compact \TR\ reconnection events (as was done with
\MOSES~\citep{Fox11,Rust17,Courrier18}) and observe signatures of \MHD\ waves over a large portion of the solar disk.
Therefore, in support of goal~\ref{item-goal1}, we will use \ESIS\ to map flows as a function of time and
space in multiple \TR\ reconnection events.
To achieve goal~\ref{item-goal2}, we will cross-correlate the evolution at multiple temperatures in the \TR\ to map the
vertical transport of energy over a wide \FOV.""")

    subsection_reconnection = aastex.Subsection("Magnetic Reconnection Events")
    subsection_reconnection.append(r"""
Magnetic reconnection describes the re-arrangement of the magnetic topology wherein magnetic energy
is converted to kinetic energy resulting in the acceleration of plasma particles.
Reconnection is implicated in many dynamic, high energy solar events.
Solar flares are a well studied example (\eg\,\citet{Priest02} and the references therein), however we have little hope
of pointing in the right place at the right time to observe a significant flare event in a rocket flight lasting only
five minutes.
Instead, we will search for signatures of magnetic reconnection in \TR\ spectral lines.
%label to track table 1 references
\phantomsection
\label{t1_2}
A particular signature of reconnection in the \TR\ is the explosive energy release by ubiquitous, small scale events.
These \EEs\ are characterized as spatially compact ($\approx$\SI{1.5}{\mega\meter} length~\citep{Dere94}) line
broadenings on the order of \SI{100}{\kilo\meter\per\second}~\citep{Dere91}.
They are observed across a range of \TR\ emission lines that span temperatures of \SI{20000}{}--\SI{250000}{\kelvin}
(C\,\textsc{ii}--O\,\textsc{v})~\citep{1994Moses}.
The typical lifetime of an \EE\ is 60-\SI{90}{\second}~\citep{1994Moses,Dere94,Dere91}.
Due to their location near quiet sun magnetic network elements, and the presence of supersonic flows near the Alfv\`en
speed, \citet{Dere91} first suggested that \EEs\ may result from the model of fast Petschek~\citep{Petschek64}
reconnection.

The spectral line profile of \EEs\ may indicate the type of reconnection that is occurring in the \TR\
(\eg\,\citet{Rust17}).
For example, the Petschek model of reconnection predicts a `bi-directional jet' line profile with highly Doppler
shifted wings, but little emission from the line core~\citep{Innes99}.
\citet{Innes15} developed a reconnection model resulting from a plasmoid instability~\citep{Bhattacharjee09}.
In contrast to the bi-directional jet, this modeled line profile has bright core emission and broad wings.
Both types of profile are seen in slit spectrograph data (\eg, \citet{Innes97,Innes15}, and the references therein),
however \MOSES\ observed \EEs\ with more complicated morphologies than either of these two models
suggest~\citep{Fox10,Rust17}.
It is unclear whether the differing observations are a function of wavelength and temperature, a result of a limited
number of observations, or because the morphology of the event is difficult to ascertain from slit spectrograph data.

%label to track table 1 references
\phantomsection
\label{t1_01}
\ESIS\ will observe magnetic reconnection in the context of \EEs, by extending the technique pioneered by \MOSES\ to
additional \TR\ lines.
Explosive events are well suited to sounding rocket observations;
a significant portion of their temporal evolution can be captured in $>$\SI{150}{\second} (\eg\,the analysis by
\citet{Rust17}) and they are sufficiently common to provide a statistically meaningful sample in a 5-minute rocket
flight (\eg,~\citet{Dere89,Dere91}).
In similarity with \MOSES, we seek a \TR\ line for \ESIS\ that is bright and well enough isolated from neighboring
emission lines so as to be easily distinguished.""")
    result.append(subsection_reconnection)

    subsection_energy = aastex.Subsection("Energy Transfer")
    subsection_energy.append(
        r"""
Tracking the mass and energy flow through the solar atmosphere is a long-standing goal in solar physics.
Bulk mass flow is evidenced by Doppler shifts or skewness in spectral lines.
However, the observed non-thermal broadening of \TR\ spectral lines may result from a variety of physical processes,
including \MHD\ waves~\citep{DePontieu15, DePontieu07}, high-speed evaporative up-flows (\eg\,nanoflares,
\citet{Patsourakos06}), turbulence, and other sources (\eg\,\citet{Mariska1992}).
This is a broad topic which \ESIS\ can address in many ways.
Here we will focus on a single application;
\ESIS\ will search for sources of Alfv\'en waves in the solar atmosphere by observing Doppler shifts and line broadening
as the spectroscopic signature of these waves.
The spectroscopic signature Alfv\'en waves will be most obvious near the limb of the solar disk, since the motion of the
ions are transverse with respect to the propagation direction.
Pointing near the limb may make it more difficult to observe distinct \EEs, described in Section~\ref{subsec:MagneticReconnectionEvents},
since the average width of \TR\ lines often increases near the limb of the Sun \citep{Ayres2021}, thus decreasing the
\SNR\ of single events.

Alfv\'en waves in coronal holes are observed to carry an energy flux of
\SI{7e5}{erg\per\centi\square\meter\per\second}, enough to energize the fast solar wind \citep{Hahn2012,Hahn2013}.
The source and frequency spectrum of these waves is unknown.
Here, we hypothesize that \MHD\ waves are similarly ubiquitous in quiet Sun and active regions, and play an important
role in the energization of the quiescent corona.

%label to track table 1 references
\phantomsection
\label{t1_1}
The magnitude of non-thermal broadening of optically thin spectral lines is a direct measure of the wave
amplitude~\citep{Banerjee09,Hahn2012,Hahn2013}.
We may estimate a lower limit on the non-thermal velocity to be observed as follows.
We assume that the magnetic field is constant for small changes in scale height in the \TR\ and that line of sight
effects are negligible for observations sufficiently far from disk center.
Since the solar wind is not accelerated to an appreciable fraction of the Alfv\'en wave velocity at altitudes below
$R \leq 1.15R_\odot$~\citep{Cranmer05}, the wave amplitude, $v_{nt}$, depends only weakly on electron density, $n_e$, so
that $v_{nt} \propto n_e^{-1/4}$~\citep{Hahn2013,Moran01}.
Assuming pressure balance between the low corona and transition zone, we may infer non-thermal velocities in the \TR\ by
scaling according to the temperature drop, $v_{nt} \propto T^{1/4}$.
The measured non-thermal velocity of \SI{24}{\kilo\meter\per\second} for Si\,\textsc{viii}~\citep{Doyle98}
(\SI{0.8}{\mega\kelvin}~\citep{Moran03}) near the limb should, neglecting damping, correspond to velocities of at least
\SI{18}{\kilo\meter\per\second} in the O\,\textsc{v} (\SI{0.25}{\mega\kelvin}) line.
This is larger than the thermal width of \SI{11}{\kilo\meter\per\second}.

More recently, ~\citet{Srivastava17} observed torsional Alfv\'en waves with amplitude
$\sim$\SI{20}{\kilo\meter\per\second} and period $\sim$\SI{30}{\second} in the chromosphere.
Modeling shows that these torsional waves can transfer a significant amount of energy to the corona~\citep{Kudoh99}.
The torsional motion will be observed as Doppler shifts when viewed from the side.
The oscillation period is long enough to be well resolved but short enough to see $\sim$\SI{10}{} cycles in a single
rocket flight.
An \ESIS-like instrument is therefore well suited to observations of torsional Alfv\'en wave propagation over multiple
heights in the \TR.

By mapping Doppler velocities over a wide field of view in the \TR, \ESIS\ can address questions about both the origin
of waves and whether they are able to propagate upward into the corona.
Independent of the two propagation modes discussed above, there is a range of possible sources for Alfv\'en
(and other \MHD) waves in the solar atmosphere.
Three potential scenarios are: \begin{inparaenum}[(1)] \item Waves originate in the chromosphere or below and propagate
through the \TR\ at a spatially uniform intensity; \label{wave-1}
\item Intense sources are localized in the \TR, but fill only a fraction of the surface\label{wave-2}; and \item Weak
sources are localized in the \TR, but cover the surface densely enough to appear like the first case\label{wave-3}.
\end{inparaenum}
The resulting non-thermal widths for localized sources will be significantly higher than the
$\sim$\SI{20}{\kilo\meter\per\second} mean derived above.
The concentration of non-thermal energy observed by \ESIS\ will serve as an indicator of source density.
Comparison of Doppler maps captured at different temperatures by \ESIS\ will indicate whether a uniform source density originates in the
chromosphere or below (scenario~\ref{wave-1}) or is associated with spatially distributed \TR\ phenomena
(scenario~\ref{wave-3}) such as explosive events, or macrospicules.
Comparison with a wider selection of ground and space based imagery will allow us to determine whether intense,
localized sources (scenario~\ref{wave-2}) are associated with converging or emerging magnetic bipoles, type \textsc{ii}
spicules, spicule bushes, or other sources beneath the \TR.
For these comparisons, we need only to localize, rather than resolve, wave sources.
A spatial resolution of $\sim$\SI{2}{\mega\meter} will be sufficient to localize sources associated with magnetic flux
tubes that are rooted in photospheric inter-granular network lanes (\eg\,\citet{Berger95ApJ})."""
    )
    result.append(subsection_energy)

    subsection_requirements = aastex.Subsection("Science Requirements")
    subsection_requirements.append(r"""
\ESIS\ will investigate two science targets:
reconnection in explosive events and the transport of mass and energy through the transition region.
The latter may take many forms, from \MHD\ waves of various modes to \EUV\ jets or macro-spicules.
To fulfill these goals, \ESIS\ will obtain simultaneous intensity, Doppler shift and line width images of the \OV\ line
in the solar transition region (\SI{.25}{\mega\kelvin}) at rapid cadence.
The bright, optically thin \OVion\ emission line is well isolated except for the two coronal \MgXion\ lines.
These coronal lines can be viewed as contamination or as a bonus;
we expect that with the \numChannelsWords\ \ESIS\ projections it will be possible to separate the \OVion\ emission from
that of \MgXion.
From the important temporal, spatial, and velocity scales referenced Sections~\ref{subsec:MagneticReconnectionEvents}
and \ref{subsec:EnergyTransfer} we define the instrument requirements in Table~\ref{table:scireq} that are needed to
meet our science goals.""")
    subsection_requirements.append(esis_instrument_paper.figures.bunch())
    subsection_requirements.append(esis_instrument_paper.tables.requirements())
    result.append(subsection_requirements)

    return result
