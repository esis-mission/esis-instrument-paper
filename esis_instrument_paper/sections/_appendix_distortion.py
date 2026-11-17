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
    result.append(
        r"""
The distortion of each channel is fit to the flight data as the placement of the optics in the as-built model,
rather than as a polynomial over the detector, so that the result has physical units, carries the wavelength
dependence the model knows, and can be checked against what was measured on the ground.
The fit is reproducible from the \texttt{esis} package, whose documentation carries the full report, every
table it commits, and the scripts that regenerate them.

\paragraph{What is fit}
The terms fit are chosen by what each does to the image on the detector.
In each channel, the yaw and pitch of the grating translate the spectrum, and with it the window of every line;
the ruling spacing sets the dispersion; the pitch and yaw of the pointing translate the Sun within the windows;
the sensor's distance along the beam sets the plate scale; and its three angles rotate the image and tilt it in
the two keystone senses.
The other placements in the model repeat one of these motions or leave the image unchanged to first order, and
are held at their as-built values: the sensor's position in its own plane moves the image as a grating tilt does,
a displacement of the primary along its axis is undone by the sensor's distance, and a roll of the field stop
moves only the edges of the windows.
Among the nine, the pointing and the grating angles are degenerate in the image of the sky, which only the field
stop breaks: its octagonal image, the window of each line on the detector, does not follow the pointing.

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
\item \emph{Edges.} The sides of every window are measured in every exposure bright enough to show them, as
described under \emph{The window edges} below: their median over the flight places the windows, and their
motion from exposure to exposure is the drift of the windows.
\item \emph{Outline.} Each channel's windows are placed on the median edges through the yaw and pitch of the
grating and the roll of the field stop, which move the windows without moving the sky inside them, and the sky
terms are re-polished.
The field stop is the measured polygon described below, the same in every channel.
\item \emph{Shared.} The pointing is set to one value for the four channels, and each channel's grating and
sensor placement is polished again with it fixed.
The displacement of the primary is held at nominal, since a scan of it does not discriminate on the flight data.
\item \emph{Internal alignment.} Each channel's exposure is read onto a common sky grid through its own mapping
at \HeIion\ and \OVion, inside the window that line illuminates, and cross-correlated tile by tile against channel 1;
the parameters are moved so that the mappings reproduce the measured shifts.
Two lines separate a geometric error, the same shift in both, from a dispersion error.
\item \emph{Focus.} The channels are measured against channel 1 in every exposure, with the windows placed by the
smoothed drift since the reference exposure, at which the reference was fit with no grating offset.
Each channel views the Sun through its own sector of the primary, so a defocus moves its image along its own
dispersion while the windows stay put; the focus of every sector is solved from the shifts through the model,
four unknowns from six measured components, and smoothed by a quadratic through the flight.
The mean over the sectors is the defocus of the primary as a whole.
\item \emph{Pointing.} The pitch and yaw of every exposure are polished on the mean merit of the four channels,
with the roll held, each channel's grating offset by the smoothed drift of its windows since the reference
exposure, and each sector of the primary focused by that exposure's value.
\item \emph{Acceptance.} The model is scored on six exposures across the flight, the reference exposure among
them, with each exposure's own pitch and yaw applied, and in every exposure the coalignment metric is measured: the length of the median tile shift of each channel against channel 1 at each
line, its component along the channel's dispersion in pixels and in \si{\kilo\meter\per\second}, the scatter of
the tiles about it, and the decomposition of the tiles into the linear distortion modes with a test of whether
what remains is noise (Figure~\ref{fig:coalignmentTiles}).
\end{enumerate}
The fit is stochastic: the capture draws its population at random, and every linearization samples the field
and the pupil at random positions inside its cells. One seed sets all of these draws, and every committed table
records the seed it was made with, zero. To see how much the draws matter, the whole chain was run from five
seeds. The registration of the channels against one another, the median tile shift of each channel against
channel 1 at each line and exposure, varies between the runs by \seedScatter\ rms over the first 29 exposures,
small against the registration itself. The scatter grows as the signal falls late in the flight, and reaches
\seedScatterLast\ rms in the last and faintest exposure, which holds \SI{14}{\percent} of the peak signal.
The parameters differ more, along the near-null directions of the problem, with the mapping differing by about \SI{0.4}{pixels} in the median over the field and by up to about a pixel at its edge. In an earlier set of runs, on the code before its last corrections, one of the twenty captures settled in a false
optimum, a correlation of 0.65 where the others reached 0.79 to 0.85, from which the later stages could not
continue; that seed was not repeated and another stands in for it, and all twenty captures of this set reach 0.79
to 0.85. On the cluster's GPUs a seed repeats the fit only to about 0.0005 in correlation, not exactly.

\paragraph{The window edges}
The edges of the windows are the image of the field stop, which sits at the prime focus ahead of the gratings,
so they carry the grating and the sensor but not the pointing, and they are the only part of the image that does.
Each side of a window is fit as one straight edge: across the side, the profile of every row or column it
crosses is modelled as a constant, plus a step, plus a ramp that rises from the step into the window, each
blurred by a Gaussian, with a linear least-squares solve for the three amplitudes of each profile inside a
non-linear fit for the side's position, slope and blur, which all the profiles share; rows whose residual is more
than three times the side's median are left out and the side refit.
A side that runs at forty-five degrees to the rows and columns, a diagonal of the octagon, is first resampled
on a grid one pixel apart along it and across it and then fit the same way, so all eight sides are measured
alike.
The windows are placed by the median of these fits over the exposures of the flight, in which the same edge is
seen against a different solar backdrop each time.
The straight-edge fit places a side well but follows its motion poorly: solar structure crossing a side as the
pointing drifts moves the fitted edge by a few tenths of a pixel from one exposure to the next, and the two
sides of one window, which cannot move apart, do so by 0.25 to 0.35~pixels rms through the flight.
The drift of the windows is therefore taken from a second fit, an error-function step in each row and column on
its own against its own median over the flight, which holds the two sides together to 0.13 to 0.19~pixels;
the drift of a side in an exposure is the median of its rows' departures, and the drift of a window, carried as
a grating offset, is smoothed by a cubic in the exposure index.
The distinction matters: the focus of each sector, below, moves a channel's image along its dispersion, so an
error in the drift is absorbed by the focus rather than seen, and with the straight-edge drift the registration
of the channels was worse by half.
% TODO numbers: deploy9 acceptance O V 0.131 vs 0.078/0.082 px rms -> macros from the committed tables

\paragraph{The shape of the field stop}
The field stop is modelled as a regular octagon, but the four channels, each of which images it through its own
grating and sensor, say otherwise, and say it alike.
In each channel the median edges of the \OVion\ window, the brightest and the only one whole on every
detector, are carried back to the plane of the field stop by a chief-ray map of the fitted model, and each side
gives its offset from the side of the octagon and its tilt against it.
What the channel's own placement can do to its image of the stop, a rotation, a translation and a scale, is fit
for every channel together with one shape common to all.
That shape tilts the sides by up to a degree against the regular octagon, \SI{0.48}{\degree} rms, and moves
them by \SI{1.2}{\micro\meter} rms, while the channels depart from it by \SI{0.027}{\degree} and
\SI{0.43}{\micro\meter} rms, or a tenth of a pixel; the opposite sides of the stop are not parallel, which no
rotation or shear of a regular octagon can produce.
% TODO: these from field_stop.ecsv metadata of the final run, as macros
The model's field stop is that polygon, which is smaller than the design by \SI{0.4}{\percent}, and the
outline stage fits its roll.
The measurement was made first through a fit with the regular octagon, and again through a fit with the
polygon it gave; the second moved the sides by \SI{0.021}{\degree} rms, less than the channels scatter about
the shape, and is the polygon the model carries.
Measured a third time through the final fit, the shape moves by \SI{0.007}{\degree} and
\SI{0.08}{\micro\meter} rms and its scale by less than \SI{0.05}{\percent}, so the measurement has converged.
With it the edges sit on the model to 0.2 to 0.8~pixels rms in the four channels, where the regular octagon,
with its roll fit the same way, left 1.0 to 2.3, and the merit of every channel rises.
% TODO macros: final outline residuals 0.24/0.48/0.82/0.36 against the regular octagon 2.27/2.10/1.02/1.50 px

\paragraph{The clocking of the field stop}
One corner of the octagon was meant to point to solar north, so the clocking of the instrument is the position
angle of that corner about the centre of the field stop.
Carried to the sky through the fit at \OVion, it is \SI{0.46}{\degree} clockwise, from \SI{0.40}{\degree} to
\SI{0.52}{\degree} in the four channels, which see the stop through different sectors of the primary.
The eight corners together are turned by \SI{0.38}{\degree}, the fitted roll of the stop; the north corner
departs from that because the stop is irregular.
The clocking does not change through the flight: freed in every exposure, the roll of the payload changes by
less than \SI{0.001}{\degree}.
The model holds the roll of the payload fixed and carries the clocking as the roll of the field stop, since the
two cannot be told apart from the images and the clocking is what the pointing needs.
The corners of the octagon picked by hand for the pointing figure of \citet{Parker2022} give the same
\SI{0.46}{\degree}.
The \SI{0.85}{\degree} that paper reports is not the clocking but the rotation of one camera's image against \AIA,
from the sky to the detector, its own mounting included; the fit finds those rotations from \SI{0.38}{\degree}
to \SI{1.1}{\degree} across the four channels, in the same pattern as that alignment gives for each camera to
within \SI{0.05}{\degree}.
% TODO confirm the 0.85 deg source with Jake (camera 0 affine rot_angle in ov_Level3_transform.pickle = +0.87)
% TODO the clocking numbers (clocking5.py on x5) belong in a committed table or the field_stop.ecsv metadata

\paragraph{The focus of each sector}
With the pointing and the drift applied and the focus held at its value at the reference exposure, each
channel's image still translated against the others' by up to \coalignmentBeforeMax, rigid, the same at both
lines and smooth in time.
Tracking the interior of each window and its edges separately against the reference exposure, on the detector,
the image did not move with the edges, so it was not a motion of a grating or a camera, which carry both; nor a
decenter of the field stop or of the primary, which move every window, or every image, by one vector; and an
error of plate scale or roll would have to be eight percent or five degrees.
A focus that differs from sector to sector moves each channel's image along its own dispersion by its own
amount, four parameters per exposure against six measured components, and it fits: it leaves the floor of the
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

\paragraph{The optional channel offsets}
With the focus of each sector applied, the channels' skies still differ from channel 1's by
\registrationLeftBySectors\ rms over the bright exposures, close to the \SI{0.05}{pixels} a single measurement
resolves.
The same measurement, repeated with the sector focus in place, fits what is left as an offset of each channel's
own pitch and yaw, a quadratic in the exposure index that vanishes at the reference exposure and sums to zero
over the channels so that the payload's pointing stays where the scene put it: twelve numbers, at most
\channelOffsetMax\ or \channelOffsetMaxPixels\ on the sensor, which leave \registrationLeftByOffsets\ rms.
They are committed beside the fit and the flight model applies them only when asked, since they are empirical
where the sector focus is a mechanism; an inversion can be run with and without them to see what a few
hundredths of a pixel of registration do to the result.

\paragraph{Lessons}
The field stop's edge was the calibration source, and its weak point: a field stop imaged whole, with margin on
every side of every window, with edges verified sharp on the ground and a deliberate fiducial in each side, would
have decided the question above and would fix the rotation and the scale of every window as well as its
position.
An undispersed channel sharing the field stop would anchor the sky absolutely to a few hundredths of a pixel,
where the \AIA\ proxy anchors it to half a pixel, and would separate a common Doppler shift from a change of
focus outright.
The primary's focus drifted by \defocusRange\ and the windows by up to \windowDriftMax\ across the detectors,
and each moved the images by tenths of a pixel; an athermal metering structure between the optics, or a way to
measure both in flight, is worth
more to the registration of the channels than any improvement of the detectors.

\paragraph{Cost}
The capture takes one to two and a half hours per channel on one GPU, the later stages about three hours more,
and the chain is about six hours of wall time on a cluster if no job is interrupted; on earlier code the same
chain on the host without a GPU took about as long, and the stages from the focus on fit a workstation with \SI{128}{\giga\byte} of memory."""
    )
    result.append(esis_instrument_paper.figures.coalignment_tiles())
    return result
