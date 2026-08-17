import aastex

__all__ = [
    "introduction",
]


def introduction() -> aastex.Section:
    result = aastex.Section("Introduction")
    result.append(r"""
The light emitted by the solar \TR\ and corona varies significantly as a function
of position, wavelength, and time.
When viewed from Earth, the spectral radiance from the Sun can be written as: $I(x, y, \lambda, t)$,
where $x$ and $y$ are the helioprojective Cartesian coordinates \citep{Thompson2006},
$\lambda$ is wavelength, and $t$ is time.
The ideal solar imaging spectrograph would capture $I(x, y, \lambda, t)$ with high resolution in $x$, $y$, $\lambda$,
and $t$ \textit{and} over a wide \FOV, wavelength range, and time period.
Of course, the temporal dimension is privileged, so we often reduce the problem to capturing a 3D spatial/spectral
cube at a particular time $t_0$: $I(x, y, \lambda, t_0)$.
Since we use 2D detectors, this means that we must find a way to flatten the 3D cube into two dimensions
without losing information.

One obvious way to accomplish this is to multiplex one of the three remaining dimensions in time.
Narrowband, tunable filters,
such as the GREGOR Fabry--P{\'e}rot Interferometer \citep{Puschmann12},
multiplex the wavelength dimension in time,
and can change the selected wavelength in \SI{100}{\milli\second} or less \citep{vanNoort2022},
but the technology does not exist to use this technique for wavelengths shorter than
$\sim$\SI{150}{\nano\meter}~\citep{2000WuelserFP}.
The nearest \EUV\ equivalent is a multilayer-coated imager such as \TRACE~\citep{Handy99} or
\AIA~\citep{Lemen12}, which abandons the wavelength dimension entirely and integrates over a passband
holding many emission lines.
Two such passbands can be compared to infer a Doppler shift \citep{Sakao99}, but weaker lines within them
bound the velocity resolution near $\sim$\SI{1000}{\kilo\meter\per\second} \citep{Kobayashi00},
coarser than the flows that characterize \TR\ dynamics.

A spatial dimension can be multiplexed instead.
An entrance slit admits a single column of the scene, so the detector records $\lambda$ against $y$ without
ambiguity, and $x$ is recovered by stepping the slit across the target.
\IRIS~\citep{IRIS14} and \SPICE\ aboard Solar Orbiter \citep{Spice2020} work this way, and the spectra they
return are the most faithful of any technique discussed here.
What is sacrificed is simultaneity: neighboring columns of the reconstructed cube are separated in time by the
raster, and structure that evolves faster than the raster completes is smeared along $x$.
\MUSE\ \citep{DePontieu2020,DePontieu2022,Cheung2022} narrows this gap considerably by ruling 37 slits across
the field and separating their overlapping spectra afterward, which shortens the raster of an active region
to as little as \SI{12}{\second}.

A third strategy divides the detector rather than the exposure.
An integral field spectrograph slices the field of view and reformats those slices so that each is dispersed
onto its own region of the detector, so the entire cube arrives in one exposure, at the cost of trading field
of view against wavelength range.
The microlensed hyperspectral imager of \citet{vanNoort2022} demonstrates the technique at visible wavelengths,
and the recently flown \SNIFS~\citep{Herde2024} demonstrates it in the \FUV.
Extending it to the \EUV\ remains out of reach of available optics.

The last strategy is to allow the flattening to be ambiguous and to undo it afterward.
A spectrograph with no entrance slit disperses the whole field at once, so every emission line forms an image
of the Sun and those images superimpose on the detector.
The resulting frame, an \textit{overlappogram}, encodes $x$ and $\lambda$ along a single axis, and the two
cannot be separated within one exposure.
Overlappograms are as old as spaceborne solar spectroscopy, having been recorded by the \Acposs{NRL} S082A
spectroheliograph \citep{Tousey73,Tousey77}, which yielded both a census of \EUV\ transitions
\citep{Feldman85} and, much later, flare line ratios \citep{Keenan06};
the technique is in use today at soft X-ray wavelengths by \MaGIXS~\citep{Savage2023}.
What has changed since S082A is that the ambiguity has become tractable.
Reconstructing the cube from superimposed images is a tomographic problem \citep{Kak88}, in which each
diffraction order views the cube from a different angle and the number of independent views limits how much
of the line profile can be recovered \citep{Descour97}.
\Acp{CTIS} \citep{okamoto1991,Bulygin91,Descour95} carry this to its extreme, projecting as many as 25 orders
onto a single detector, with computational cost rising accordingly \citep{Hagen08,Hagen2013}.
Fewer views can suffice when the scene is sparse: \citet{DeForest04} synthesized a magnetogram from a single
exposure using only two dispersed orders.
Inversion methods for overlapping spectral images have advanced considerably since
\citep{Winebarger2019,Davila2019,Kamaci2026}.

\MOSES~\citep{Fox10,Fox11} brought this strategy to the solar \EUV.
A single concave grating forms three images at once, the undispersed $m=0$ order and the $m=\pm1$ orders, on
three detectors, while a multilayer coating narrows the passband to a few emission lines so that the cube to
be recovered is sparse enough to invert.
Two flights showed that the concept works.
\citet{Fox10} measured the Doppler shift and width of explosive event line profiles in the \TR;
\citet{Rust2019} resolved bimodal profiles in quiet Sun events;
\citet{Courrier18} recovered Doppler maps using local correlation tracking;
and \citet{Parker2022moses} separated the contributions of individual spectral lines.
The same flights exposed where the design binds.
Only three views are available, one of which is undispersed and therefore contributes no spectral
information, which caps the number of degrees of freedom that an inversion can recover;
and because the dispersed orders lie in a plane, they fill the cylindrical volume of a sounding rocket
payload poorly.

\jake{might just need to go through the whole paper then write this paragraph}
The \ESIS\ was designed to relax both constraints.
An array of gratings arranged about the optical axis re-images the prime focus of a single primary mirror,
each dispersing at a different angle, so that every detector records a dispersed view and the views are
distributed around the payload rather than confined to a plane.
\ESIS\ flew for the first time on 2019 September 30, and first results from that flight are reported by
\citet{Parker2022}.
An earlier form of the design was described by \citet{Courrier2020};
the instrument that flew differs from it, most consequentially in the removal of the primary mask, which
admits vignetting into the system.
This paper describes the instrument as it was built and flown.
In Section~\ref{sec:TheESISConcept} we explain how experience with \MOSES\ shaped the design of \ESIS.
Section~\ref{sec:ScienceObjectives} states the scientific objectives and the requirements they impose.
Section~\ref{sec:TheESISInstrument} describes the instrument itself, and
Section~\ref{sec:MissionProfile} the mission profile.""")
    return result
