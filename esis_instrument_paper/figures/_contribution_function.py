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


def contribution_function() -> aastex.Figure:
    """
    The contribution function of each of the lines labeled in
    :func:`esis_instrument_paper.figures.bunch`, against the temperature of
    the plasma.

    The lines are the same ones, from the same cache, and their contribution
    functions are computed with the same abundances and pressure, so they
    are the functions the radiances in that figure were summed from.
    """
    optics = esis.flights.f1.optics.design_single(num_distribution=0)

    # the same arguments as the passband figure, which reads the lines from
    # the same cache
    wavelength_min = optics.wavelength_min.to(u.AA).ndarray
    wavelength_max = optics.wavelength_max.to(u.AA).ndarray
    g = esis_instrument_paper._spectrum.contribution_function(
        wavelength_min=wavelength_min,
        wavelength_max=wavelength_max,
        num=esis_instrument_paper.figures.num_emission_lines,
    )
    temperature = esis_instrument_paper._spectrum.temperature()
    axis = esis_instrument_paper._spectrum._axis

    wavelength = g.inputs.components["wavelength"]
    names = utu.spectrum.spectroscopic(
        ion=g.inputs.components["ion"],
        latex=True,
    )
    order = np.argsort(na.as_named_array(wavelength).ndarray.value)
    # the emission is isotropic, so each function is spread over the whole
    # sphere, the way the passband figure spreads the intensities into
    # radiances
    outputs = (g.outputs / (4 * np.pi * u.sr)).to(_unit)

    fig, ax = plt.subplots(
        figsize=(aastex.column_width_inches, _height),
        constrained_layout=True,
    )

    for index in order:
        i = {"line": int(index)}
        w = na.as_named_array(wavelength[i]).ndarray.to_value(u.AA)
        ax.plot(
            temperature.ndarray.to_value(u.K),
            outputs[i].ndarray_aligned((axis,)).value,
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
