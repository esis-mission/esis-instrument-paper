"""The contribution functions of the brightest lines in the passband."""

import aastex
import astropy.units as u
import esis
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np
import utu

import esis_instrument_paper

__all__ = [
    "contribution_function",
]

_height = 3.0
"""The height of the figure in inches, with room for the legend beneath it."""

_unit = u.erg * u.cm**3 / u.s / u.sr
"""The unit the contribution functions are drawn in."""

_range = 1e3
"""How many times smaller than the largest value the vertical axis reaches."""

_step = 0.01
"""
The spacing of the temperatures the functions are drawn at, in their
logarithm.

A tenth of the spacing the spectrum is computed at, which draws each
function as a smooth curve rather than as the few straight segments that
grid gives it.
"""


def contribution_function() -> aastex.Figure:
    """
    The contribution function of each of the lines labeled in
    :func:`esis_instrument_paper.figures.bunch`, against the temperature of
    the plasma.

    The lines are the same ones, from the same cache, and their contribution
    functions are computed with the same abundances and pressure, so they
    are the functions the radiances in that figure were summed from, drawn
    at temperatures ten times closer together. Each line is the color it is
    in :func:`esis_instrument_paper.figures.field_stop_projections`.
    """
    optics = esis.flights.f1.optics.design_single(num_distribution=0)

    # the same arguments as the passband figure, which reads the lines from
    # the same cache
    wavelength_min = optics.wavelength_min.to(u.AA).ndarray
    wavelength_max = optics.wavelength_max.to(u.AA).ndarray
    num = esis_instrument_paper.figures.num_emission_lines
    g = esis_instrument_paper._spectrum.contribution_function(
        wavelength_min=wavelength_min,
        wavelength_max=wavelength_max,
        num=num,
        step=_step,
    )
    temperature = esis_instrument_paper._spectrum.temperature(_step)
    axis = esis_instrument_paper._spectrum._axis

    wavelength = g.inputs.components["wavelength"]
    names = utu.spectrum.spectroscopic(
        ion=g.inputs.components["ion"],
        latex=True,
    )
    order = np.argsort(na.as_named_array(wavelength).ndarray.value)
    colormap = plt.get_cmap(esis_instrument_paper.figures.colormap_emission_lines)
    colors = colormap(np.linspace(0, 1, num))
    # the emission is isotropic, so each function is spread over the whole
    # sphere, the way the passband figure spreads the intensities into
    # radiances
    outputs = (g.outputs / (4 * np.pi * u.sr)).to(_unit)

    fig, ax = plt.subplots(
        figsize=(aastex.column_width_inches, _height),
        constrained_layout=True,
    )

    for color, index in zip(colors, order):
        i = {"line": int(index)}
        w = na.as_named_array(wavelength[i]).ndarray.to_value(u.AA)
        ax.plot(
            temperature.ndarray.to_value(u.K),
            outputs[i].ndarray_aligned((axis,)).value,
            color=color,
            label=rf"{names[i].ndarray} {w:.2f}\,\AA",
        )

    # the horizontal axis is cut to the temperatures where some line reaches
    # the bottom of the vertical axis
    top = np.max(outputs)
    bottom = top / _range
    shown = np.where(np.max(outputs, axis="line") >= bottom, temperature, np.nan)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(
        np.nanmin(shown).ndarray.to_value(u.K),
        np.nanmax(shown).ndarray.to_value(u.K),
    )
    ax.set_ylim(bottom.ndarray.value, 2 * top.ndarray.value)
    ax.set_xlabel(f"temperature ({u.K:latex_inline})")
    ax.set_ylabel(f"$G(T)$ ({_unit:latex_inline})")
    fig.legend(loc="outside lower center", ncol=2)

    result = aastex.Figure("fig:contributionFunction", position="!htb")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
Contribution functions of the \numEmissionLines\ emission lines in Figure~\ref{fig:bunch}, computed from the same
version of CHIANTI with the same abundances and pressure."""))

    return result
