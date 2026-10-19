import aastex

__all__ = [
    "mission_profile",
]


def mission_profile() -> aastex.Section:
    """
    The section describing the flight.

    The old draft wrote this section before the launch and added the flight
    as an update. :cite:t:`Parker2022` has since described the flight and its
    data in detail, so this section only summarizes it, with the times of its
    events from the timeline of the flight, and leaves the rest to that paper.
    The changes made to the instrument before the flight, which the old
    draft's update described, are in the subsections on the instrument.
    """
    result = aastex.Section("Mission Profile")
    result.append(
        r"""
\ESIS\ was launched on a Terrier Black Brant sounding rocket from White Sands Missile Range on 2019 September 30,
alongside \MOSES.
\citet{Parker2022} describe the flight, the conditions on the Sun, and the data in detail, so we summarize the flight only
briefly here.
The cameras exposed continuously from launch, at a cadence of \detectorExposureLength, and the exposures taken while the
payload shutter door was closed serve as darks.
The door opened \timeShutterOpen\ after launch.
The ring-laser gyroscope of the \SPARCS\ held the pointing from \timeRlgEnable\ to \timeRlgDisable\ after launch, which
gives the observing time of \observingTime\ in Table~\ref{table:scireq}, and the door closed at \timeShutterClose.
The Sun was very quiet that day, so \ESIS\ was pointed at disk center, and thermal expansion inside the instrument made
the image drift slowly across the detectors during the flight~\citep{Parker2022}.
The images were stored on board and retrieved after the payload descended on a parachute and was recovered, while some
were also sent to the ground during the flight (Section~\ref{subsec:PointingSystem}).
The mechanical shutter of \MOSES\ failed, so no \MOSES\ data were obtained during this flight."""
    )
    return result
