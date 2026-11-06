import aastex
import astropy.units as u
import esis
import matplotlib.pyplot as plt

__all__ = [
    "grating_efficiency_vs_position",
]

_height = 2.5
"""The height of the figure in inches."""

_unit_position = u.mm
"""The unit the positions are drawn in."""


def grating_efficiency_vs_position() -> aastex.FigureStar:
    """
    The measured efficiency of a flight grating along two orthogonal slices
    across its surface.
    """
    efficiencies = esis.flights.f1.optics.gratings.efficiencies
    scans = {
        "x": efficiencies.efficiency_vs_x(),
        "y": efficiencies.efficiency_vs_y(),
    }

    fig, axs = plt.subplots(
        ncols=len(scans),
        sharey=True,
        figsize=(aastex.text_width_inches, _height),
        constrained_layout=True,
    )

    for ax, (component, scan) in zip(axs, scans.items()):
        efficiency = scan.outputs.ndarray * u.dimensionless_unscaled
        ax.plot(
            scan.inputs.position.ndarray.to_value(_unit_position),
            efficiency.to_value(u.percent),
        )
        ax.set_xlabel(f"${component}$ position ({_unit_position:latex_inline})")

    axs[0].set_ylabel(f"efficiency ({u.percent:latex_inline})")

    result = aastex.FigureStar("fig:gratingEfficiencyVsPosition", position="!htb")
    result.append(aastex.NoEscape(r"\centering"))
    result.add_fig(fig, width=aastex.NoEscape(r"\textwidth"))
    result.add_caption(aastex.NoEscape(r"""
Channel \testGratingChannelIndex\ grating efficiency at \gratingTestWavelength\
vs.\ position for two orthogonal slices across the optical surface on
\testGratingDate."""))

    return result
