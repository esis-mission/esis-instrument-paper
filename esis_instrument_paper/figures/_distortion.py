"""
The distortion of a single channel: the image of the field stop on the
detector, and how closely a polynomial describes where the field lands.

Both figures read the same model, fit by
:meth:`optika.systems.SequentialSystem.distortion` over the cells and at the
lines of the vignetting figure.
"""

import aastex
import astropy.units as u
import astropy.visualization
import esis
import matplotlib.pyplot as plt
import named_arrays as na
import optika

from esis_instrument_paper.figures import _grids

__all__ = [
    "distortion",
    "distortion_residual",
]

_num_field = 21
"""
The number of field positions sampled along each axis.

The same as in the vignetting figure, so that the two maps are drawn over the
same cells.
"""

_num_pupil = 21
"""
The number of pupil positions sampled along each axis.

Where a field cell lands on the detector is the mean over its pupil samples,
and that mean hardly depends on how finely the pupil is sampled: four times
as finely moves the largest residual of the quadratic fit by about a
thousandth of a pixel. So the residual is the distortion itself rather than
the quadrature, and the pupil need not be sampled as finely as the vignetting
figure samples it to resolve the area of the pupil.
"""

_seed_pupil = 42
"""
The seed of the random draw which places a sample inside each pupil cell.

The same as in the vignetting figure. The draw has to be seeded for the
figures to be the same every time the article is built.
"""

_seed_field = None
"""
The seed of the random draw which places a sample inside each field cell.

There is none, as in the vignetting figure, so the field is taken at the
centers of its cells and the residual is drawn as a regular grid.
"""

_unit_field = u.arcsec
"""The unit the field position is drawn in, as in the vignetting figure."""

_degree = 2
"""
The degree of the distortion model the text writes out.

The text gives the model as a quadratic in position and wavelength, and the
residual figure is the evidence that a quadratic is enough.
"""

_degree_linear = 1
"""The degree of the model the residual figure compares the quadratic with."""

_axis_row = "row"
"""The name of the axis along which the two rows of the residual figure vary."""

_height = 4.2
"""
The height of the residual figure in inches.

The same as the vignetting figure, which it is laid out like: two rows of
three square panels across the width of the text.
"""

_height_image = 3.3
"""
The height of the image figure in inches.

Its width is the width of a column, and the image of the field stop is about
as tall as it is wide.
"""

_color_image = "red"
"""The color of the image of the field stop, as in the old draft."""

_color_stop = "black"
"""The color of the magnified field stop, as in the old draft."""


def _optics() -> esis.optics.Instrument:
    """A single channel of the flight instrument, as designed."""
    return esis.flights.f1.optics.design_single(num_distribution=0)


def _model(
    optics: esis.optics.Instrument,
    degree: int,
) -> optika.distortion.PolynomialDistortionModel:
    """
    Fit a polynomial to where the field of a single channel lands on its
    detector, as a function of field position and wavelength.

    Parameters
    ----------
    optics
        The channel to fit.
    degree
        The degree of the polynomial.
    """
    return optics.system.distortion(
        wavelength=_grids.wavelength(),
        field=_grids.vertices("field", _num_field),
        pupil=_grids.vertices("pupil", _num_pupil),
        degree=degree,
        seed_field=_seed_field,
        seed_pupil=_seed_pupil,
    )


def distortion() -> aastex.Figure:
    """
    The image of the field stop on the detector at O V, against the field
    stop magnified by the ratio of the arms of the grating.

    The image is the outline of the field of view carried onto the detector
    by the quadratic distortion model, which is how the caption says it was
    calculated. The magnified field stop is the stop as it sits in the frame
    of the channel, scaled by the ratio of the exit arm of the grating to its
    entrance arm. Both are centered on the image of the center of the field,
    so that what is left between them is the distortion.
    """
    optics = _optics()
    system = optics.system
    sensor = system.sensor
    wavelength = esis.flights.f1.spectrum.O_V.wavelength

    model = _model(optics, degree=_degree)

    def image(field: na.AbstractCartesian2dVectorArray) -> na.Cartesian2dVectorArray:
        """Where the model puts a field position on the detector at O V."""
        return model.distort(
            na.SpectralPositionalVectorArray(wavelength=wavelength, position=field)
        ).position

    # the outline of the field of view, in field angles
    outline = system.field_stop_polygon(wavelength).wire().xy
    center = 0 * outline[{"wire": 0}]
    outline = image(outline) - image(center)

    # The field stop in the frame of the channel, which is rolled so that the
    # channel disperses along x, as the detector does. Pixels are counted from
    # a corner of the detector, so the magnified stop is measured from where
    # its center would land.
    field_stop = system.field_stop
    origin = na.Cartesian3dVectorArray() * u.mm
    stop = field_stop.transformation(field_stop.aperture.wire())
    stop = (stop - field_stop.transformation(origin)).xy
    magnification = optics.distance_grating_output / optics.distance_grating_input
    stop = sensor.pixels(magnification * stop) - sensor.pixels(0 * stop)

    # named as the caption names it, with the wavelength the model carries
    label_image = rf"O\,\textsc{{v}} {wavelength.to_value(u.AA)}\,\AA"

    with astropy.visualization.quantity_support():
        fig, ax = plt.subplots(
            figsize=(aastex.column_width_inches, _height_image),
            constrained_layout=True,
        )
        na.plt.plot(
            outline,
            ax=ax,
            axis="wire",
            color=_color_image,
            label=label_image,
        )
        # drawn over the image, where the two coincide
        na.plt.plot(
            stop,
            ax=ax,
            axis="wire",
            color=_color_stop,
            label="magnified field stop",
        )

    ax.set_aspect("equal")
    ax.set_xlabel(f"detector $x$ ({u.pix:latex_inline})")
    ax.set_ylabel(f"detector $y$ ({u.pix:latex_inline})")

    # the middle of the field stop is empty, and the legend fits inside it
    ax.legend(loc="center")

    result = aastex.Figure("fig:distortion", position="!htb")
    result.append(aastex.NoEscape(r"\centering"))
    result.add_fig(fig, width=aastex.NoEscape(r"\columnwidth"))
    result.add_caption(aastex.NoEscape(r"""
Plot of the magnified, undistorted field stop aperture vs. the distorted \OV\ image of the
field stop aperture on the \ESIS\ detector.
The magnification factor used for the undistorted field stop aperture is the ratio of the grating exit arm to the
grating entrance arm (\armRatio).
The distorted image of the field stop aperture was calculated using the \ESIS\ distortion model, described in
Table~\ref{table:distortion}."""))

    return result


def distortion_residual() -> aastex.FigureStar:
    """
    The residual of a linear and of a quadratic distortion model, at each of
    the three target lines in the passband.

    The residual is the distance on the detector between where the model puts
    a field cell and where the traced rays land, in pixels.
    """
    optics = _optics()

    fig, ax = na.plt.subplots(
        axis_rows=_axis_row,
        nrows=2,
        axis_cols=_grids.axis_wavelength,
        ncols=na.shape(_grids.wavelength())[_grids.axis_wavelength],
        sharex=True,
        sharey=True,
        squeeze=False,
        figsize=(aastex.text_width_inches, _height),
        constrained_layout=True,
    )

    # The rows are numbered from the bottom of the figure upwards, so the
    # linear model is on top and the quadratic below, as in the caption. Each
    # row has its own colorbar, since the two residuals differ by a factor of
    # a hundred.
    _model(optics, degree=_degree_linear).plot_residual(
        ax=ax[{_axis_row: 1}],
        unit=_unit_field,
    )
    _model(optics, degree=_degree).plot_residual(
        ax=ax[{_axis_row: 0}],
        unit=_unit_field,
    )

    # both axes of every panel are field angles, so a degree has to be the same
    # length along each of them for the shape of the \FOV to be the shape drawn
    na.plt.set_aspect("equal", ax=ax)

    # every panel shares its axes with its neighbors, so only those on the
    # outside of the grid need to say what the axes are
    for axs in ax.ndarray.reshape(-1):
        axs.label_outer()

    # the two rows are the same three wavelengths in the same three columns,
    # so naming them once at the top of the figure is enough
    for axs in ax[{_axis_row: 0}].ndarray.reshape(-1):
        axs.set_title("")

    result = aastex.FigureStar("fig:distortionResidual", position="!htb")
    result.append(aastex.NoEscape(r"\centering"))
    result.add_fig(fig, width=aastex.NoEscape(r"\textwidth"))
    result.add_caption(aastex.NoEscape(r"""
Magnitude of the residual between a linear distortion model and the raytrace model (top) and between a quadratic
distortion model and the raytrace model (bottom). This figure demonstrates that a quadratic distortion model is
sufficient to achieve sub-pixel accuracy."""))

    return result
