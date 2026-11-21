import astropy.units as u
import esis
import named_arrays as na
import numpy as np
import pytest

from esis_instrument_paper import _diffraction, _error_budget


def test_channel() -> None:
    """The channel as built is the channel the design models."""
    design = esis.flights.f1.optics.design_single(num_distribution=0)
    assert design.camera.channel == _diffraction.channel


@pytest.mark.parametrize("as_built", [False, True])
def test_psf(as_built: bool) -> None:
    """The intensity of each point-spread function sums to one over its grid."""
    psf = _diffraction.psf(as_built=as_built)
    total = psf.outputs.sum(_diffraction.axis)
    expected = na.ScalarArray(np.ones(2), axes=_diffraction.axis_field)
    assert np.allclose(total.ndarray, expected.ndarray)


@pytest.mark.parametrize("as_built", [False, True])
def test_mtf(as_built: bool) -> None:
    """The MTF is one at zero frequency, at every field angle."""
    mtf = _diffraction.mtf(as_built=as_built)
    center = {a: mtf.shape[a] // 2 for a in _diffraction.axis}
    zero = mtf.inputs[center]
    assert np.all(zero.x.ndarray == 0)
    assert np.all(zero.y.ndarray == 0)
    expected = na.ScalarArray(np.ones(2), axes=_diffraction.axis_field)
    assert np.allclose(mtf.outputs[center].ndarray, expected.ndarray)


def test_mtf_figure_error() -> None:
    """
    The measured figures lower the MTF of the channel at the spatial frequency
    of the resolution requirement, along the dispersion, at every field angle.
    """
    axis_x, axis_y = _diffraction.axis
    frequency = _error_budget.frequency().to_value(u.cycle / u.arcsec)
    result = {}
    for as_built in (False, True):
        mtf = _diffraction.mtf(as_built=as_built)
        cut = mtf[{axis_y: mtf.shape[axis_y] // 2}]
        sky = _diffraction.frequency_sky(cut.inputs).x.to(1 / u.arcsec).value
        index = np.argmin(np.abs(sky - frequency), axis=axis_x)
        result[as_built] = cut.outputs[index]
    assert np.all((result[True] < result[False]).ndarray)


def test_frequency_sky() -> None:
    """
    The spatial frequency of one cycle per pixel on the detector is one cycle
    per plate scale on the sky.
    """
    design = esis.flights.f1.optics.design_single(num_distribution=0)
    plate_scale = design.system.plate_scale(_diffraction.wavelength)
    pixel = design.camera.sensor.width_pixel
    result = _diffraction.frequency_sky(na.Cartesian2dVectorArray(1 / pixel, 1 / pixel))
    expected_x = (1 / (plate_scale.x * u.pix)).to(1 / u.arcsec)
    expected_y = (1 / (plate_scale.y * u.pix)).to(1 / u.arcsec)
    assert np.allclose(result.x.to(1 / u.arcsec).ndarray, expected_x.ndarray)
    assert np.allclose(result.y.to(1 / u.arcsec).ndarray, expected_y.ndarray)
