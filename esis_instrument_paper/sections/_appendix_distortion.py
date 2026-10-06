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
\item \emph{Defocus.} The channels are measured against channel 1 in every exposure, and the one axial
displacement of the primary that reproduces their shifts through the model is solved per exposure and smoothed
by a line through the flight.
\item \emph{Pointing.} The pitch and yaw of every exposure are polished on the mean merit of the four channels,
with the roll held and the windows placed by the smoothed drift and the primary defocused by that exposure's
value.
\item \emph{Co-registration.} The channels are measured against channel 1 once more with everything above
applied, and what is left is removed as an offset of each channel's own pointing, a quadratic in time that
vanishes at the reference exposure and in the mean over the channels.
\item \emph{Acceptance.} The model is scored on exposures the fit never saw, and in every exposure the
coalignment metric is measured: the length of the median tile shift of each channel against channel 1 at each
line, its component along the channel's dispersion in pixels and in \si{\kilo\meter\per\second}, the scatter of
the tiles about it, and the decomposition of the tiles into the linear distortion modes with a test of whether
what remains is noise (Figure~\ref{fig:coalignmentTiles}).
\end{enumerate}
A second run from a different random seed reproduces the correlations to 0.01 and the coalignment to
\SI{0.02}{pixels}; the parameters differ along the null directions of the problem, with the mapping unchanged
to about a pixel at the edge of the field.

\paragraph{The motion that is not explained}
With the pointing, the drift and the defocus applied, each channel's image still translates against the others'
by up to \coalignmentBeforeMax\ between the ends of the flight, rigid, the same at both lines and smooth in time.
Two measurements on the Level-1 exposures alone bound what it can be.
Tracking the interior of each window and its edges separately against the reference exposure, on the detector,
the image does not move with the edges, so it is not a motion of a grating or a camera, which would carry
both; no defocus, astigmatism, coma or trefoil of the primary reproduces its pattern over the channels; and an
error of plate scale or roll would have to be eight percent or five degrees.
But the window edges, which the fit takes for a rigid outline, are not one.
The \HeIion\ window has no left edge on any detector, where the image runs off the sensor, and two channels lack an
edge in the other direction, so several windows are placed along an axis by a single edge.
The edges differ in sharpness from \SI{0.7}{} to over \SI{4}{pixels}, several sharpen or soften by a pixel
during the flight, their profiles are skewed, and the two lines, which share one field stop and one grating,
disagree on the motion of the same side by up to \SI{0.3}{pixels} over half the flight.
The placement of a window from its edges is therefore uncertain by about the size of the motion, and the data
do not say whether the image moved inside a fixed window or the apparent edges moved over a fixed image.
A point spread that is skewed and changes through the flight would do it, since image structure follows the
centroid of the blur and an edge its median; that is a hypothesis.
The co-registration removes the motion empirically, and the committed tables label it as such.

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
The capture takes one to two hours per channel on one GPU, the later stages two to three hours more, and the
chain is about six hours of wall time on a cluster; the stages from the co-registration on run on a
workstation with \SI{128}{\giga\byte} of memory.""")
    result.append(esis_instrument_paper.figures.coalignment_tiles())
    return result
