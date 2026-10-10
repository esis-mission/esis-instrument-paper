import aastex
import astropy.units as u
import matplotlib
import named_arrays as na
import numpy as np
import optika
import pytest

matplotlib.use("agg")

import esis_instrument_paper
from esis_instrument_paper.figures import _distortion


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


def test_distortion() -> None:
    """The prose and the captions refer to this figure by its label."""
    result = esis_instrument_paper.figures.distortion()
    assert isinstance(result, aastex.Figure)
    assert "fig:distortion}" in result.dumps()


def test_distortion_residual() -> None:
    """The prose and the captions refer to this figure by its label."""
    result = esis_instrument_paper.figures.distortion_residual()
    assert isinstance(result, aastex.FigureStar)
    assert "fig:distortionResidual" in result.dumps()


@pytest.mark.parametrize(
    argnames="degree,below_one_pixel",
    argvalues=[
        (_distortion._degree_linear, False),
        (_distortion._degree, True),
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
    model = _distortion._model(_distortion._optics(), degree=degree)
    assert (_residual_max(model) < 1 * u.pix) == below_one_pixel
