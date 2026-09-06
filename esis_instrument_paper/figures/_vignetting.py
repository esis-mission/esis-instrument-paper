import aastex
import astropy.units as u
import esis
import named_arrays as na
import numpy as np
import optika

__all__ = [
    "vignetting",
]

_num_field = 21
"""The number of field positions sampled along each axis."""

_num_pupil = 81
"""
The number of pupil positions sampled along each axis.

The illumination at a field position is the fraction of the pupil which is
unvignetted, so this number sets how finely that fraction can be resolved,
and until the pupil is sampled finely enough the residual of the fit is
mostly that granularity rather than anything about the optics. Sampling half
as finely puts about a tenth of the mean residual back; at this many it has
settled, agreeing to about a percent with a stratified sample of the same
size, which is an estimator with quite different errors.
"""

_degree = 1
"""
The degree of the polynomial fit to the illumination.

The text describes the vignetting as a simple linear field, and this figure
is the evidence for that: the residual of the linear fit stays under two
percent of the illumination everywhere it was fit. A quadratic fit halves
that residual, so the field is not exactly linear, but the model plotted
here is the one the text claims.
"""


def _wavelength() -> na.ScalarArray:
    """
    The rest wavelengths at which the vignetting is shown.

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
        axes=("wavelength",),
    )


def _grid(name: str, num: int) -> na.Cartesian2dVectorLinearSpace:
    """A square grid of `num` by `num` normalized coordinates."""
    return na.Cartesian2dVectorLinearSpace(
        start=-1,
        stop=+1,
        axis=na.Cartesian2dVectorArray(f"{name}_x", f"{name}_y"),
        num=num,
    )


def _model() -> optika.radiometry.PolynomialVignettingModel:
    """Fit the illumination of a single channel as a function of the field."""
    optics = esis.flights.f1.optics.design_single(num_distribution=0)

    return optics.system.vignetting(
        wavelength=_wavelength(),
        field=_grid("field", _num_field),
        pupil=_grid("pupil", _num_pupil),
        degree=_degree,
    )


def vignetting() -> aastex.FigureStar:
    """
    The illumination of a single channel, and the residual of a linear fit to it.

    The system is modeled without the aperture stop that the original design
    placed at the primary mirror, since the stop was removed before flight.
    """
    model = _model()

    figsize = (aastex.text_width_inches, 2.6)

    fig_illumination, _ = model.plot(figsize=figsize)

    # The fit is constrained only where some part of the pupil is unvignetted,
    # so outside the field stop there is nothing for the residual to be the
    # residual of. Those points are left out: kept in, they are the largest
    # values in the plot and so set the color scale for everything else.
    model_inside = model.replace(
        illumination=np.where(model.where, model.illumination, np.nan),
    )

    residual = abs(model_inside.illumination - model_inside.fit.predictions)

    fig_residual, _ = model_inside.plot_residual(
        figsize=figsize,
        vmax=np.nanmax(residual.ndarray),
    )

    result = aastex.FigureStar("fig:vignetting", position="!htb")
    result.append(aastex.NoEscape(r"\centering"))
    result.add_fig(fig_illumination, width=aastex.NoEscape(r"\textwidth"))

    # Without the break the two panels are set on the same line, and the
    # second one runs off the edge of the page.
    result.append(aastex.NoEscape(r"\\"))

    result.add_fig(fig_residual, width=aastex.NoEscape(r"\textwidth"))
    result.add_caption(aastex.NoEscape(r"""
(Top) The relative illumination of a single \ESIS\ channel as a function of
position in the \FOV, at each of the three target lines in the passband.
The illumination is the fraction of the pupil which is unvignetted, normalized
so that its average over the \FOV\ is unity.
(Bottom) The residual between that illumination and a linear model of it,
plotted only where the model was fit."""))

    return result
