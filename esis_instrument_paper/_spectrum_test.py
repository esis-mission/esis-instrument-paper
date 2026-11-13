import astropy.units as u
import esis
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
    intensity = (result.outputs * spectrum.emission_measure()).sum(spectrum._axis)
    assert np.all(intensity == lines.outputs)
