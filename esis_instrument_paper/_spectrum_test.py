import astropy.units as u
import esis
import named_arrays as na
import numpy as np

import esis_instrument_paper


def test_contribution_function() -> None:
    """
    The contribution functions are the ones the intensities of the lines
    were summed from: each one, times the emission measure, sums over the
    temperatures to the intensity of its line.

    The passband is that of the figures, so that the lines come from the
    same cache.
    """
    optics = esis.flights.f1.optics.design_single(num_distribution=0)
    wavelength_min = optics.wavelength_min.to(u.AA).ndarray
    wavelength_max = optics.wavelength_max.to(u.AA).ndarray
    num = esis_instrument_paper.figures.num_emission_lines

    spectrum = esis_instrument_paper._spectrum
    result = spectrum.contribution_function(
        wavelength_min=wavelength_min,
        wavelength_max=wavelength_max,
        num=num,
    )
    lines = esis_instrument_paper.lines(
        wavelength_min=wavelength_min,
        wavelength_max=wavelength_max,
    )[{"line": slice(num)}]

    for component in ("wavelength", "ion"):
        expected = lines.inputs.components[component]
        assert np.all(result.inputs.components[component] == expected)

    # utu.spectrum.lines() sums each line along a contiguous axis of
    # temperature, and numpy adds the terms of a sum in a different order
    # along a strided axis, which can change the last bit, so the sum is
    # taken in the same layout here
    axes = ("line", spectrum._axis)
    g = na.ScalarArray(result.outputs.ndarray_aligned(axes).copy(order="C"), axes)
    intensity = (g * spectrum.emission_measure()).sum(spectrum._axis)
    assert np.all(intensity == lines.outputs)
