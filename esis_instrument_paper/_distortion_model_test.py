import astropy.units as u
import named_arrays as na
import numpy as np
import optika
import pytest

from esis_instrument_paper import _distortion_model


def _residual_max(model: optika.distortion.PolynomialDistortionModel) -> u.Quantity:
    """
    The largest residual of a distortion model over the cells it was fit to,
    as the residual figure draws it.

    Parameters
    ----------
    model
        The fitted model.
    """
    residual = (model.coordinates_sensor - model.fit.predictions).length
    residual = np.where(model.where, residual, -np.inf * na.unit(residual))
    return residual.max().ndarray


@pytest.mark.parametrize(
    argnames="degree,below_one_pixel",
    argvalues=[
        (_distortion_model.degree_linear, False),
        (_distortion_model.degree, True),
    ],
)
def test_sub_pixel(degree: int, below_one_pixel: bool) -> None:
    """
    The caption of the residual figure says that a quadratic model is enough
    for sub-pixel accuracy, which the linear model beside it is not.

    Parameters
    ----------
    degree
        The degree of the model.
    below_one_pixel
        Whether the largest residual of the model should be under a pixel.
    """
    model = _distortion_model.model(degree)
    assert (_residual_max(model) < 1 * u.pix) == below_one_pixel
