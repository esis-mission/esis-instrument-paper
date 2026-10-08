import aastex
import astropy.units as u
import esis
import matplotlib.axes
import matplotlib.lines
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np
import optika
import utu

import esis_instrument_paper

__all__ = [
    "component_efficiency_vs_wavelength",
]

_height = 5
"""The height of the figure in inches."""

_unit_wavelength = u.AA
"""The unit the wavelengths are drawn in."""

_wavelength_min = 250 * _unit_wavelength
"""The shortest wavelength drawn, where the grating witnesses were measured from."""

_wavelength_max = 950 * _unit_wavelength
"""The longest wavelength drawn, where the grating witnesses were measured to."""

_wavelength = na.linspace(_wavelength_min, _wavelength_max, axis="wavelength", num=701)
"""The wavelengths at which the models are drawn."""

_num_lines = 2
"""The number of the brightest emission lines marked in each order."""

_colors_lines = {
    1: ["orangered", "blue"],
    2: ["gray", "black"],
}
"""The colors of the lines marked in each order."""


def _passbands() -> dict[int, tuple[u.Quantity, u.Quantity]]:
    """
    The range of wavelengths a channel images onto its detector, in first and
    in second order.

    Both come from the model, the second by asking the grating for the next
    order rather than by halving the first.
    """
    optics = esis.flights.f1.optics.design_single(num_distribution=0)
    rulings = optics.grating.rulings
    result = {}
    for order in _colors_lines:
        instrument = optics.replace(
            grating=optics.grating.replace(
                rulings=rulings.replace(
                    diffraction_order=order * rulings.diffraction_order,
                ),
            ),
        )
        result[order] = (
            instrument.wavelength_min.ndarray.to(_unit_wavelength),
            instrument.wavelength_max.ndarray.to(_unit_wavelength),
        )
    return result


def _annotate(
    ax: matplotlib.axes.Axes,
    label_orders: bool,
) -> list[matplotlib.lines.Line2D]:
    """
    Shade the wavelengths which miss the detector, and mark the brightest
    lines in each order.

    Parameters
    ----------
    ax
        The axes to annotate.
    label_orders
        Whether to name each order above the axes.
    """
    ax.set_facecolor("lightgray")
    result = []
    for order, (wavelength_min, wavelength_max) in _passbands().items():
        ax.axvspan(
            wavelength_min.value,
            wavelength_max.value,
            color="white",
            zorder=0,
        )
        if label_orders:
            ax.text(
                x=((wavelength_min + wavelength_max) / 2).value,
                y=1.01,
                s=f"$m={order}$",
                transform=ax.get_xaxis_transform(),
                ha="center",
                va="bottom",
            )
        lines = esis_instrument_paper.lines(
            wavelength_min=wavelength_min,
            wavelength_max=wavelength_max,
        )
        lines = lines[{"line": slice(_num_lines)}]
        for index, color in enumerate(_colors_lines[order]):
            line = lines[{"line": index}]
            ion = utu.spectrum.spectroscopic(line.inputs.ion.ndarray, latex=True)
            wavelength = line.inputs.wavelength.ndarray.to(_unit_wavelength)
            result.append(
                ax.axvline(
                    wavelength.value,
                    color=color,
                    linestyle="dotted",
                    label=f"{ion} {wavelength.value:.2f} {_unit_wavelength:latex_inline}",
                )
            )
    return result


def _efficiency(
    material: optika.materials.AbstractMaterial,
    angle: u.Quantity | na.AbstractScalar,
) -> na.AbstractScalar:
    """
    The efficiency of a material over the drawn wavelengths, at an angle of
    incidence.
    """
    rays = optika.rays.RayVectorArray(
        wavelength=_wavelength,
        direction=na.Cartesian3dVectorArray(np.sin(angle), 0, np.cos(angle)),
    )
    return material.efficiency(rays, na.Cartesian3dVectorArray(0, 0, -1))


def _plot(
    ax: matplotlib.axes.Axes,
    wavelength: na.AbstractScalar,
    efficiency: na.AbstractScalar,
    **kwargs: object,
) -> None:
    """Draw an efficiency, as a percentage, against wavelength."""
    ax.plot(
        na.as_named_array(wavelength).ndarray.to_value(_unit_wavelength),
        (na.as_named_array(efficiency).ndarray * u.dimensionless_unscaled).to_value(
            u.percent
        ),
        **kwargs,
    )


def component_efficiency_vs_wavelength() -> aastex.Figure:
    """
    The measured reflectance of the grating witnesses, and the efficiency of
    each of the three optical components of a channel.
    """
    optics = esis.flights.f1.optics
    as_built = optics.as_built(num_distribution=0)
    design = optics.design_single(num_distribution=0)
    axis = as_built.axis_channel

    fig, axs = plt.subplots(
        nrows=2,
        sharex=True,
        figsize=(aastex.column_width_inches, _height),
        constrained_layout=True,
    )

    # each witness is named after the channel its grating flew in, and drawn
    # in the order of the channels
    witness = optics.gratings.materials.multilayer_witness_measured()
    measurement = witness.efficiency_measured
    numbers = list(as_built.grating.manufacturing_number.ndarray)
    channels = {
        int(as_built.camera.channel[{axis: numbers.index(serial)}].ndarray): index
        for index, serial in enumerate(witness.serial_number.ndarray)
    }
    for channel, index in sorted(channels.items()):
        i = {"channel": index}
        _plot(
            ax=axs[0],
            wavelength=measurement.inputs.wavelength[i],
            efficiency=measurement.outputs[i],
            label=f"Channel {channel}",
        )
    axs[0].legend()
    axs[0].set_ylabel(f"efficiency ({u.percent:latex_inline})")
    _annotate(axs[0], label_orders=True)

    # the witness of the primary coating, on a silicon wafer
    witness_primary = optics.primaries.materials.multilayer_witness_measured()
    measurement_primary = witness_primary.efficiency_measured
    _plot(
        ax=axs[1],
        wavelength=measurement_primary.inputs.wavelength,
        efficiency=measurement_primary.outputs,
        label="primary",
        color="tab:red",
    )

    # a flight grating itself, coating and grooves together, in first order
    efficiency = optics.gratings.efficiencies.efficiency_vs_wavelength()
    _plot(
        ax=axs[1],
        wavelength=efficiency.inputs.wavelength,
        efficiency=efficiency.outputs,
        label="grating",
        color="tab:purple",
    )

    # the filter model, at normal incidence
    _plot(
        ax=axs[1],
        wavelength=_wavelength,
        efficiency=_efficiency(design.filter.material, angle=0 * u.deg),
        label="filter",
        color="tab:cyan",
    )

    axs[1].add_artist(axs[1].legend(loc="upper right"))
    handles = _annotate(axs[1], label_orders=False)
    axs[1].set_xlabel(f"wavelength ({_unit_wavelength:latex_inline})")
    axs[1].set_ylabel(f"efficiency ({u.percent:latex_inline})")
    axs[1].set_xlim(_wavelength_min.value, _wavelength_max.value)
    axs[1].legend(
        handles=handles,
        bbox_to_anchor=(0.5, -0.25),
        loc="upper center",
        ncol=2,
    )

    result = aastex.Figure("fig:componentEfficiencyVsWavelength", position="!htb")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
(Top) Measured reflectance for several multilayer coated witness samples
at an incidence angle of \gratingWitnessMeasurementIncidenceAngle\ on
\testGratingDate.
The white regions indicate wavelengths that intercept the detector and the
gray regions indicate wavelengths that miss the detector.
Note the suppression of second order relative to the first order and the
consistency of the coatings between each channel.
The Channel \gratingWitnessMissingChannel\ grating measurement is missing due
to issues in the measurement apparatus.
(Bottom) Comparison of the efficiency of the three main \ESIS\ optical
components: primary mirror, grating and filter.
The primary mirror efficiency is based on measurements of a \Si\ witness
sample taken on \primaryMeasurementDate\ at an angle of incidence of
\primaryWitnessMeasurementIncidenceAngle.
The grating efficiency is from a measurement of the Channel
\testGratingChannelIndex\ grating taken on \testGratingDate\ at an angle of
incidence of \gratingMeasurementIncidenceAngle.
The filter efficiency is a theoretical model that includes the filter mesh,
\filterThickness\ of \Al\ and \filterOxideThickness\ of \Al\ oxide."""))

    return result
