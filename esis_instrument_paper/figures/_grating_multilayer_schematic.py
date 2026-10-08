import aastex
import astropy.units as u
import astropy.visualization
import esis
import matplotlib.pyplot as plt

__all__ = [
    "grating_multilayer_schematic",
]

_height = 2.2
"""The height of the figure in inches."""

_thickness_substrate = 20 * u.nm
"""How much of the substrate to draw beneath the coating."""


def grating_multilayer_schematic() -> aastex.Figure:
    """
    A diagram of the layers of the multilayer coating on the gratings.

    The stack is the designed one, drawn by the model itself, so it shows the
    layers the model computes the reflectance of.
    """
    material = esis.flights.f1.optics.gratings.materials.multilayer_design()

    fig, ax = plt.subplots(
        figsize=(aastex.column_width_inches, _height),
        constrained_layout=True,
    )

    # the layers are drawn to scale, so their thicknesses are quantities
    with astropy.visualization.quantity_support():
        material.plot_layers(
            ax=ax,
            thickness_substrate=_thickness_substrate,
        )

    ax.set_axis_off()

    result = aastex.Figure("fig:gratingMultilayerSchematic", position="!htb")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
Schematic of the \AlShort/\SiCShort/\MgShort\ multilayer with
$N=\gratingCoatingNumLayers$ layers."""))

    return result
