import astropy.units as u
import pytest

from esis_instrument_paper import _distortion_model


@pytest.mark.parametrize(
    argnames="degree,below_one_pixel",
    argvalues=[
        (_distortion_model.degree_linear, False),
        (_distortion_model.degree, True),
    ],
)
def test_sub_pixel(degree: int, below_one_pixel: bool) -> None:
    """
    The text and the caption of the residual figure say that a quadratic
    model is enough for sub-pixel accuracy, which the linear model beside it
    is not.

    Parameters
    ----------
    degree
        The degree of the model.
    below_one_pixel
        Whether the largest residual of the model should be under a pixel.
    """
    assert (_distortion_model.residual_max(degree) < 1 * u.pix) == below_one_pixel
