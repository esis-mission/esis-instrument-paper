import pylatex

__all__ = [
    "requirements",
]


def requirements() -> pylatex.Table:
    """
    What the mission asked of the instrument, and what the instrument does.

    The requirement in each row is taken from
    :func:`esis.flights.f1.optics.requirements`. Several of the capabilities
    are still marked ``??``: see :func:`esis_instrument_paper.variables`.
    """
    result = pylatex.Table(position="!htb")
    result._star_latex_name = True

    result.add_caption(
        pylatex.NoEscape(
            r"""\ESIS\ instrument requirements and capabilties. Note that MTF exceeds the Rayleigh criterion of 0.109."""
        )
    )

    with (
        result.create(pylatex.Center()) as centering,
        centering.create(pylatex.Tabular(table_spec="llll")) as tabular,
    ):
        tabular.escape = False
        tabular.add_row(["Parameter", "Requirement", "Science Driver", "Capabilities"])
        tabular.add_hline()
        tabular.add_row(
            [
                r"Spectral line",
                r"\OV",
                r"\EEs",
                r"\OVion, \MgXion, \HeIion, Figure~\ref{fig:bunch}",
            ]
        )
        tabular.add_row(
            [
                r"Spectral sampling",
                r"\spectralResolutionRequirement",
                r"Broadening from \MHD\ waves",
                r"\dispersionDoppler, Table~\ref{table:prescription}",
            ]
        )
        tabular.add_row(
            [
                r"Spatial resolution",
                r"\angularResolutionRequirement (\spatialResolutionRequirement)",
                r"\EEs",
                r"\spatialResolutionTotal, Table~\ref{table:errorBudget}",
            ]
        )
        tabular.add_row(
            [
                r"\SNRShort",
                r"\snrRequirement\ (\CHShort)",
                r"\MHD\ waves in \CHShort",
                (
                    r"\StackedCoronalHoleSNR\ "
                    r"($\NumExpInStack \times \text{\detectorExposureLength}$ exp.), "
                    r"Table~\ref{table:counts}"
                ),
            ]
        )
        tabular.add_row(
            [
                r"Cadence",
                r"\cadenceRequirement",
                r"Torsional waves",
                r"\detectorExposureLength\ eff., Section~\ref{subsec:SensitivityandCadence}",
            ]
        )
        tabular.add_row(
            [
                r"Observing time",
                r"\observingTimeRequirement",
                r"\EEs",
                r"\observingTime, Section~\ref{sec:MissionProfile}",
            ]
        )
        tabular.add_row(
            [
                r"\FOV\ diameter",
                r"\fovRequirement",
                r"Span \QSShort, \ARShort, and limb",
                r"\fov, Table~\ref{table:prescription}",
            ]
        )

    result.append(pylatex.Label("table:scireq"))

    return result
