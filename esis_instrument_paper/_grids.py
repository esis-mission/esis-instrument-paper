"""
The wavelengths and the cells at which the article samples the model of a
single channel.

The vignetting figure, the distortion figures and the distortion table share
them, so that their maps are drawn and their models fit at the same lines and
over the same cells.
"""

import astropy.units as u
import esis
import named_arrays as na

__all__ = [
    "axis_wavelength",
    "vertices",
    "wavelength",
]

axis_wavelength = "wavelength"
"""The name of the axis along which the wavelength varies."""


def wavelength() -> na.ScalarArray:
    """
    The rest wavelengths at which the model of a single channel is shown.

    They are the lines this flight set out to observe which fall inside the
    passband, and they span it from end to end.
    """
    spectrum = esis.flights.f1.spectrum
    return na.ScalarArray(
        ndarray=u.Quantity(
            [
                spectrum.He_I.wavelength,
                spectrum.Mg_X.wavelength,
                spectrum.O_V.wavelength,
            ]
        ),
        axes=(axis_wavelength,),
    )


def vertices(name: str, num: int) -> na.Cartesian2dVectorLinearSpace:
    """
    The vertices of a square grid of `num` by `num` normalized cells.

    A normalized coordinate of $\\pm 1$ is the edge of the field stop, or of
    the pupil, so these vertices bound the aperture and their cells tile it.

    Parameters
    ----------
    name
        The name of the grid, which its two axes are named after.
    num
        The number of cells along each axis.
    """
    return na.Cartesian2dVectorLinearSpace(
        start=-1,
        stop=+1,
        axis=na.Cartesian2dVectorArray(f"{name}_x", f"{name}_y"),
        num=num + 1,
    )
