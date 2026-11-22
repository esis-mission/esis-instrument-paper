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

    # the last bits can differ: the lines may come from the cache of another
    # machine, whose powers of ten can round differently from this one's, and
    # numpy adds the terms of a sum in a different order along a strided axis
    # than along a contiguous one. A difference in what computed them moves
    # the sums by far more than a part in a trillion: the lines computed by
    # fiasco 0.8.3 and utu 0.6.1 are two parts in a billion from these.
    intensity = (result.outputs * spectrum.emission_measure()).sum(spectrum._axis)
    expected = lines.outputs
    assert np.all(np.abs(intensity - expected) <= 1e-12 * np.abs(expected))
