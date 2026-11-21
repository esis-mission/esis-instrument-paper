"""The modulation transfer function of a single channel at O V, with diffraction."""

import aastex
import astropy.units as u
import matplotlib.pyplot as plt
import named_arrays as na

from esis_instrument_paper import _diffraction, _error_budget

__all__ = [
    "mtf",
]

_height = 3.6
"""The height of the figure in inches."""

_frequency_max = 3 * u.cycle / u.arcsec
"""The highest spatial frequency drawn, just past the cutoff of the channel."""

_color = {
    False: "black",
    True: "tab:red",
}
"""The color of the channel as designed and as built."""

_linestyle = ("solid", "dashed")
"""The style of the line of each field angle."""


def mtf() -> aastex.Figure:
    """
    The modulation transfer function of a single channel at O V, as designed
    and as built, at the center of the field of view and off axis, along each
    axis of the detector, against the spatial frequency on the sky.

    The dotted line is the spatial frequency of the resolution requirement.
    See :mod:`esis_instrument_paper._diffraction` for how the functions are
    computed.
    """
    axis_field = _diffraction.axis_field
    axis = _diffraction.axis
    num_field = _diffraction.position_field_stop().x.shape[axis_field]
    frequency_requirement = _error_budget.frequency()

    fig, axs = plt.subplots(
        nrows=2,
        sharex=True,
        sharey=True,
        figsize=(aastex.column_width_inches, _height),
        constrained_layout=True,
    )

    for as_built in (False, True):
        mtf = _diffraction.mtf(as_built=as_built)
        frequency = _diffraction.frequency_sky(mtf.inputs)
        center = {a: mtf.shape[a] // 2 for a in axis}
        for col in range(num_field):
            index = {axis_field: col}
            label = "as built" if as_built else "design"
            label = f"{label}, {'off axis' if col else 'center'}"
            kwargs = {
                "color": _color[as_built],
                "linestyle": _linestyle[col],
                "linewidth": 1,
                "label": label,
            }
            # along x, through zero frequency along y, and the other way round;
            # the negative frequencies are left of the axes
            for ax, component, a in zip(axs, ("x", "y"), axis):
                cut = {b: center[b] for b in axis if b != a}
                f = getattr(frequency, component)[index | cut]
                na.plt.plot(
                    f.to(1 / u.arcsec).value,
                    mtf.outputs[index | cut],
                    ax=ax,
                    axis=a,
                    **kwargs,
                )

    for ax, name in zip(axs, ("along the dispersion", "across the dispersion")):
        ax.axvline(
            frequency_requirement.to_value(u.cycle / u.arcsec),
            color="black",
            linestyle="dotted",
            linewidth=1,
        )
        ax.set_xlim(0, _frequency_max.value)
        ax.set_ylim(0, 1.02)
        ax.set_ylabel("MTF")
        ax.set_title(name)
    axs[-1].set_xlabel("spatial frequency (cycles arcsec$^{-1}$)")
    axs[0].legend(fontsize="x-small", loc="upper right")

    angle = _diffraction.field(as_built=False)[{axis_field: 1}]
    x = na.value(angle.x).ndarray
    y = na.value(angle.y).ndarray
    width = _diffraction.width_mtf.to_value(u.um)

    result = aastex.Figure("fig:mtf", position="!htb")
    result.add_fig(fig, width=None)
    result.add_caption(
        aastex.NoEscape(
            rf"""
\MTF\ of each of the \PSFs\ of Figure~\ref{{fig:psfDiffraction}}, along (top) and across (bottom) the dispersion,
against spatial frequency on the sky, as designed (black) and as built (red), at the center of the \FOV\ (solid) and
at $({x:.1f}', {y:.1f}')$ (dashed).
Each was computed from the \PSF\ on a grid \SI{{{width:.0f}}}{{\micro\meter}} wide on the \CCD, normalized to the
power of the whole beam, so that the light which the measured figures scatter beyond the grid lowers the \MTF.
The dotted line marks \mtfFrequency, the spatial frequency of the \angularResolutionRequirement\ resolution
requirement.
Only the optics are included: the pixels of the \CCD\ and the diffusion of charge within it are not."""
        )
    )

    return result
