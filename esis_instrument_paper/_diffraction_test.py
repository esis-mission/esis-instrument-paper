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
def test_field(as_built: bool) -> None:
    """
    The chief ray of each field angle lands on the field stop where it should,
    in either model, and the point off axis is the one toward the corner.
    """
    angle = _diffraction.field(as_built=as_built)
    position = _diffraction._position(as_built, angle).to(u.mm)
    expected = _diffraction.position_field_stop().to(u.mm)
    assert np.allclose(position.x.ndarray.value, expected.x.ndarray.value, atol=1e-5)
    assert np.allclose(position.y.ndarray.value, expected.y.ndarray.value, atol=1e-5)


def test_psf() -> None:
    """
    The integral of each point-spread function over its grid is the fraction
    of the power of the beam which lands on the grid: most of it as designed,
    where the mesh of the filter diffracts the rest beyond the grid, and less
    as built, whose measured figures scatter more light beyond it.
    """
    area = np.square(_diffraction.width_image / (_diffraction.num_image - 1))
    total = {}
    for as_built in (False, True):
        psf = _diffraction.psf(as_built=as_built)
        integral = psf.outputs.sum(_diffraction.axis) * area
        total[as_built] = integral.to(u.dimensionless_unscaled).ndarray
    assert np.all((0.75 < total[False]) & (total[False] < 0.9))
    assert np.all((0.65 < total[True]) & (total[True] < total[False]))


def test_mtf() -> None:
    """
    The MTF at zero frequency is the fraction of the power of the beam which
    lands on its grid: nearly all of it as designed, where the mesh of the
    filter diffracts the rest beyond the grid, and less as built, whose
    measured figures scatter more light beyond it.
    """
    zero = {}
    for as_built in (False, True):
        mtf = _diffraction.mtf(as_built=as_built)
        center = {a: mtf.shape[a] // 2 for a in _diffraction.axis}
        frequency = mtf.inputs[center]
        assert np.all(frequency.x.ndarray == 0)
        assert np.all(frequency.y.ndarray == 0)
        zero[as_built] = mtf.outputs[center].ndarray
    assert np.all((0.95 < zero[False]) & (zero[False] < 1))
    assert np.all((0.9 < zero[True]) & (zero[True] < zero[False]))


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
