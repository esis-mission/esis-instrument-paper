"""The point-spread function of a single channel at O V, with diffraction."""

import aastex
import astropy.units as u
import matplotlib.colors
import matplotlib.patches
import matplotlib.pyplot as plt
import named_arrays as na

from esis_instrument_paper import _diffraction

__all__ = [
    "psf_diffraction",
]

_height = 2.6
"""The height of the figure in inches."""

_half_width = 25 * u.um
"""How far each panel reaches either way from the centroid of its image."""

_floor = 1e-4
"""The faintest intensity drawn, relative to the peak of each panel."""

_dpi = 300
"""The resolution of the images."""


def psf_diffraction() -> aastex.Figure:
    """
    The point-spread function of a single channel at O V, as designed and as
    built, at the center of the field of view and off axis, framed by a box
    one pixel across.

    Each panel is centered on the centroid of its image and normalized to its
    own peak. See :mod:`esis_instrument_paper._diffraction` for how the
    point-spread functions are computed.
    """
    axis_field = _diffraction.axis_field
    axis = _diffraction.axis
    num_field = _diffraction.field.x.shape[axis_field]
    pixel = _diffraction.system(as_built=False).sensor.width_pixel.to_value(u.um)
    half_width = _half_width.to_value(u.um)
    norm = matplotlib.colors.LogNorm(vmin=_floor, vmax=1)

    fig, axs = plt.subplots(
        nrows=2,
        ncols=num_field,
        sharex=True,
        sharey=True,
        figsize=(aastex.column_width_inches, _height),
        squeeze=False,
        constrained_layout=True,
    )

    mappable = None
    for row, as_built in enumerate((False, True)):
        psf = _diffraction.psf(as_built=as_built)
        for col in range(num_field):
            index = {axis_field: col}
            position = psf.inputs.position[index]
            intensity = psf.outputs[index]
            centroid = (position * intensity).sum(axis) / intensity.sum(axis)
            ax = axs[row, col]
            mappable = na.plt.pcolormesh(
                (position - centroid).to(u.um).value,
                C=intensity / intensity.max(axis),
                ax=ax,
                cmap="gray_r",
                norm=norm,
                rasterized=True,
            ).ndarray.item()
            ax.add_patch(
                matplotlib.patches.Rectangle(
                    xy=(-pixel / 2, -pixel / 2),
                    width=pixel,
                    height=pixel,
                    fill=False,
                    edgecolor="tab:red",
                    linewidth=0.8,
                )
            )
            ax.set_xlim(-half_width, half_width)
            ax.set_ylim(-half_width, half_width)
            ax.set_aspect("equal")
            if row == 0:
                ax.set_title("off axis" if col else "center")
            if row == 1:
                ax.set_xlabel(r"$x$ ($\mu$m)")
            if col == 0:
                label = "as built" if as_built else "design"
                ax.set_ylabel(f"{label}\n" + r"$y$ ($\mu$m)")

    fig.colorbar(mappable, ax=axs, label="relative intensity")

    result = aastex.Figure("fig:psfDiffraction", position="!htb")
    result.add_fig(fig, width=None, dpi=_dpi)
    # the caption is left for the authors to write; it carries the label
    result.add_caption(aastex.NoEscape(""))

    return result
