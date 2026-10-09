import aastex

import esis_instrument_paper

__all__ = [
    "distortion_fit",
]


def distortion_fit() -> aastex.Section:
    r"""
    The appendix describing how the distortion of the flight instrument was fit.

    The procedure, the merit, the acceptance metric, the motion the fit
    cannot explain and what the window edges turned out to be, and the cost
    of reproducing it.  The numbers are macros read from the committed
    tables; the full account is the report in the ``esis`` documentation.
    """
    result = aastex.Section("The Distortion Fit")
    result.append(r"""
The distortion of each channel is fit to the flight data as the placement of the optics in the as-built model,
rather than as a polynomial over the detector, so that the result has physical units, carries the wavelength
dependence the model knows, and can be checked against what was measured on the ground.
The fit is reproducible from the \texttt{esis} package, whose documentation carries the full report, every
table it commits, and the scripts that regenerate them.

\paragraph{What one exposure determines}
A single exposure of one channel determines eight combinations of that channel's parameters: a singular-value
decomposition of the Jacobian of the sky-to-detector mapping with respect to the parameters has eight singular
values above \SI{40}{pixels} of image motion per half-width of the parameter bounds, then a cliff.
Nine terms span them: the yaw and pitch of the grating, the ruling spacing, the pitch and yaw of the pointing,
and the sensor's distance along the beam and its three angles.
The pointing and the grating angles are degenerate in the image of the sky, which only the field stop breaks:
its octagonal image, the window of each line on the detector, does not follow the pointing.

\paragraph{Merit}
Every candidate model is linearized at the three brightest lines of the passband, \HeIion, \MgXion\ and \OVion, into
a polynomial mapping from the sky to the detector and a vignetting function, and the \AIA\ images of the same
field at the time of the exposure, 304~\AA\ for \HeIion\ and \OVion\ and 193~\AA\ for \MgXion,
are resampled through it onto the detector.
The merit is the correlation of that model image with the exposure, which is indifferent to the photometric
calibration and to the smooth gradients vignetting and effective area leave between the channels.
One evaluation takes about a second.

\paragraph{Stages}
\begin{enumerate}
\item \emph{Capture.} Each channel is fit alone against the exposure at the middle of the flight, a seeded
differential evolution over the nine terms followed by a restarted Nelder--Mead polish.
\item \emph{Edges.} An error-function step is fit where each window's predicted outline crosses the rows and
columns of every exposure bright enough to show it; the median over the flight places the windows and the
departure from it in each exposure is the drift of the windows.
\item \emph{Outline.} Each channel's windows are placed on the median edges through the grating angles and the
sensor roll, which move the windows without moving the sky inside them, and the sky terms are re-polished.
\item \emph{Shared.} The pointing is set to one value for the four channels, and each channel's grating and
sensor placement is polished again with it fixed.
\item \emph{Internal alignment.} Each channel's exposure is read onto a common sky grid through its own mapping
at \HeIion\ and \OVion, inside the window that line illuminates, and cross-correlated tile by tile against channel 1;
the parameters are moved so that the mappings reproduce the measured shifts.
Two lines separate a geometric error, the same shift in both, from a dispersion error.
\item \emph{Focus.} The channels are measured against channel 1 in every exposure.
Each channel views the Sun through its own sector of the primary, so a defocus moves its image along its own
dispersion while the windows stay put; the focus of every sector is solved from the shifts through the model,
four unknowns from six measured components, and smoothed by a quadratic through the flight.
The mean over the sectors is the defocus of the primary as a whole.
\item \emph{Pointing.} The pitch and yaw of every exposure are polished on the mean merit of the four channels,
with the roll held and the windows placed by the smoothed drift and the primary defocused by that exposure's
value.
\item \emph{Acceptance.} The model is scored on exposures the fit never saw, and in every exposure the
coalignment metric is measured: the length of the median tile shift of each channel against channel 1 at each
line, its component along the channel's dispersion in pixels and in \si{\kilo\meter\per\second}, the scatter of
the tiles about it, and the decomposition of the tiles into the linear distortion modes with a test of whether
what remains is noise (Figure~\ref{fig:coalignmentTiles}).
\end{enumerate}
The same chain run on a host without a GPU reproduces the committed tables, the correlations to seven figures
and the coalignment to \SI{0.01}{pixels}. A second run from a different random seed, on the chain before the
focus of each sector was added, reproduced the correlations to 0.01 and the coalignment to \SI{0.02}{pixels};
the parameters differ along the null directions of the problem, with the mapping unchanged to about a pixel at
the edge of the field.

\paragraph{The focus of each sector}
With the pointing, the drift and one defocus of the whole primary applied, each channel's image still
translated against the others' by up to \coalignmentBeforeMax\ between the ends of the flight, rigid, the same
at both lines and smooth in time.
Tracking the interior of each window and its edges separately against the reference exposure, on the detector,
the image did not move with the edges, so it was not a motion of a grating or a camera, which carry both; nor a
decenter of the field stop or of the primary, which move every window, or every image, by one vector; and an
error of plate scale or roll would have to be eight percent or five degrees.
A focus that differs from sector to sector moves each channel's image along its own dispersion by its own
amount, three parameters per exposure against six measured components, and it fits: it leaves the floor of the
measurement, where the figure modes tried first, astigmatism, coma and trefoil, which force the sectors into a
fixed relation, left three times that.
Each sector's focus is smooth in time to the precision of a single exposure, a few microns.
Nothing after the field stop can do this, and neither can any rigid motion of the mirror or the stop, so if it is
real it is the figure of the primary changing unevenly with temperature, about \SI{100}{\nano\meter} of sag
between sectors over the flight, the same scale as the common drift of the focus.
But the window edges, which the measurement takes for a rigid outline, are not one.
The \HeIion\ window has no left edge on any detector, where the image runs off the sensor, and two channels lack an
edge in the other direction, so several windows are placed along an axis by a single edge.
The edges differ in sharpness from \SI{0.7}{} to over \SI{4}{pixels}, several sharpen or soften by a pixel
during the flight, their profiles are skewed, and the two lines, which share one field stop and one grating,
disagree on the motion of the same side by up to \SI{0.3}{pixels} over half the flight.
The focus of a sector is measured along the channel's dispersion, and the window's position along the
dispersion comes from the two edges perpendicular to it, which are the edges that behaved worst; the crossing of
a skewed step moves when its width changes, by a fraction of the change, and that would appear here as a focus
of the sector.
The disagreement between the lines puts that at up to half the effect.
The data therefore support two readings, the mirror bending or the along-dispersion fiducials drifting, and do
not decide between them; the model carries the first, the simpler physical account, and the tables record the
sectors' histories so that a thermal model of the mirror, or the next flight's temperature sensors, can judge
it.

\paragraph{Lessons}
The field stop's edge was the calibration source, and its weak point: a field stop imaged whole, with margin on
every side of every window, with edges verified sharp on the ground and a deliberate fiducial in each side, would
have decided the question above and would fix the rotation and the scale of every window as well as its
position.
An undispersed channel sharing the field stop would anchor the sky absolutely to a few hundredths of a pixel,
where the \AIA\ proxy anchors it to half a pixel, and would separate a common Doppler shift from a change of
focus outright.
The primary's focus drifted by \defocusRange\ and the field stop by a few microns, and each moved the images by
tenths of a pixel; an athermal metering structure between them, or a way to measure both in flight, is worth
more to the registration of the channels than any improvement of the detectors.

\paragraph{Cost}
The capture takes one to two hours per channel on one GPU, the later stages four hours more, and the chain
is about six hours of wall time on a cluster; the same chain on the host without a GPU takes about as long,
and the stages from the focus on fit a workstation with \SI{128}{\giga\byte} of memory.""")
    result.append(esis_instrument_paper.figures.coalignment_tiles())
    return result
