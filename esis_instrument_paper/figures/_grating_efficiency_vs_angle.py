import aastex
import astropy.units as u
import esis
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np
import optika

__all__ = [
    "grating_efficiency_vs_angle",
]

_height = 2
"""The height of the figure in inches."""

_unit_angle = u.deg
"""The unit the angles are drawn in."""


def _angle_order(wavelength: u.Quantity | na.AbstractScalar) -> u.Quantity:
    """
    The angle from the normal at which the designed grating sends the order
    it was designed for, when lit at normal incidence.

    A ray is traced off the grating in its own frame, so the angle is the one
    the rulings and the shape of the grating give, rather than one written
    down beside them.

    Parameters
    ----------
    wavelength
        The wavelength of the ray.
    """
    optics = esis.flights.f1.optics.design_single(num_distribution=0)
    surface = optics.grating.surface.replace(transformation=None)
    rays = optika.rays.RayVectorArray(
        wavelength=wavelength,
        position=na.Cartesian3dVectorArray(0, 0, -1) * u.mm,
        direction=na.Cartesian3dVectorArray(0, 0, 1),
    )
    direction = surface.propagate_rays(rays, efficiency=False).direction
    sin = np.sqrt(np.square(direction.x) + np.square(direction.y))
    angle = np.arctan2(sin, -direction.z) << u.rad
    return na.as_named_array(angle).ndarray.to(_unit_angle)


def grating_efficiency_vs_angle() -> aastex.Figure:
    """
    The measured efficiency of a flight grating as a function of the angle
    at which the light leaves it, for two angles of incidence.
    """
    efficiencies = esis.flights.f1.optics.gratings.efficiencies
    scans = [
        efficiencies.efficiency_vs_angle_0deg(),
        efficiencies.efficiency_vs_angle_3deg(),
    ]

    fig, ax = plt.subplots(
        figsize=(aastex.column_width_inches, _height),
        constrained_layout=True,
    )

    for scan in scans:
        direction = scan.inputs.direction
        angle_input = na.as_named_array(direction.input).ndarray.to(_unit_angle)
        efficiency = scan.outputs.ndarray * u.dimensionless_unscaled
        ax.plot(
            direction.output.ndarray.to_value(_unit_angle),
            efficiency.to_value(u.percent),
            label=f"input angle {angle_input.round():latex_inline}",
        )

    # the orders at normal incidence: the specular reflection, and the order
    # the grating was designed for
    orders = {
        "$m=0$": 0 * _unit_angle,
        "$m=1$": _angle_order(scans[0].inputs.wavelength),
    }
    for label, angle in orders.items():
        ax.axvline(angle.to_value(_unit_angle), linestyle="dashed", color="black")
        ax.text(
            x=angle.to_value(_unit_angle),
            y=1.01,
            s=label,
            transform=ax.get_xaxis_transform(),
            ha="center",
            va="bottom",
        )

    ax.set_xlabel(f"output angle ({_unit_angle:latex_inline})")
    ax.set_ylabel(f"efficiency ({u.percent:latex_inline})")
    ax.legend()

    result = aastex.Figure("fig:gratingEfficiencyVsAngle", position="!htb")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
Measured efficiency at \gratingTestWavelength\ of the Channel
\testGratingChannelIndex\ grating as a function of reflection angle on
\testGratingDate.
Note flat response in first order over instrument \FOV\ and suppression of
zero order."""))

    return result
