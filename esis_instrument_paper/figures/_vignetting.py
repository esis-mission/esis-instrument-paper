import aastex
import astropy.units as u
import esis
import named_arrays as na
import optika

__all__ = [
    "vignetting",
]

_num_field = 21
"""The number of field positions sampled along each axis."""

_num_pupil = 81
"""
The number of pupil positions sampled along each axis.

The illumination at a field position is the unvignetted area of its pupil,
so this number sets how finely that area can be resolved, and the residual
of the fit is mostly that granularity rather than anything about the optics:
sampling half as finely doubles the mean residual. At this many the fitted
illumination typically moves by two hundredths of a percent from one seed to
the next, and by at most about five hundredths among eleven of them.
"""

_seed_pupil = 42
"""
The seed of the random draw which places a sample inside each pupil cell.

The model draws each sample from inside its cell rather than taking the
center, which keeps the quadrature from aliasing against the edge of an
aperture which falls between two samples, and draws the pupil again at every
field position, so that the error is scattered across the map rather than
printed on it in bands.

The draw has to be seeded for the figure to be the same every time the
article is built.
"""

_seed_field = None
"""
The seed of the random draw which places a sample inside each field cell.

There is none, so the field is taken at the centers of its cells, since this
figure is meant to show the model. At the centers the field is a regular
grid, and every edge of the \\FOV\\ is drawn as the cells it covers, that of
the detector at the shortest wavelength included. Drawn at random, which the
model does by default, the field averages over the edge of the \\FOV\\
without bias, but the edge of the detector comes out ragged.
"""

_unit_field = u.arcsec
"""
The unit the field position is drawn in.

The model describes the field in degrees, where the \\FOV\\ is a tenth of one
and every tick on the axis is spent on leading zeros. The same field in
arcseconds is numbered in hundreds.
"""

_axis_wavelength = "wavelength"
"""The name of the axis along which the wavelength varies."""

_axis_row = "row"
"""The name of the axis along which the two rows of the figure vary."""

_height = 4.2
"""
The height of the figure in inches.

Its width is the width of the text, and the panels are square since the
\\FOV\\ is, so this is chosen to leave as little space as possible around
them.
"""

_degree = 1
"""
The degree of the polynomial fit to the illumination.

The text describes the vignetting as a simple linear field, and this figure
is the evidence for that: the residual of the linear fit stays under one
percent of the illumination everywhere it was fit. A quadratic fit cuts the
mean residual by a fifth and leaves the largest almost where it was, so what
remains is the sampling of the pupil rather than any curvature in the field.
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
        axes=(_axis_wavelength,),
    )


def _vertices(name: str, num: int) -> na.Cartesian2dVectorLinearSpace:
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


def _model() -> optika.radiometry.PolynomialVignettingModel:
    """Fit the illumination of a single channel as a function of the field."""
    optics = esis.flights.f1.optics.design_single(num_distribution=0)

    return optics.system.vignetting(
        wavelength=_wavelength(),
        field=_vertices("field", _num_field),
        pupil=_vertices("pupil", _num_pupil),
        degree=_degree,
        seed_field=_seed_field,
        seed_pupil=_seed_pupil,
    )


def vignetting() -> aastex.FigureStar:
    """
    The illumination of a single channel, and the residual of a linear fit to it.

    The system is modeled without the aperture stop that the original design
    placed at the primary mirror, since the stop was removed before flight.
    """
    model = _model()

    fig, ax = na.plt.subplots(
        axis_rows=_axis_row,
        nrows=2,
        axis_cols=_axis_wavelength,
        ncols=na.shape(_wavelength())[_axis_wavelength],
        sharex=True,
        sharey=True,
        squeeze=False,
        figsize=(aastex.text_width_inches, _height),
        constrained_layout=True,
    )

    # the rows are numbered from the bottom of the figure upwards. The model is
    # fit only over the cells inside the \FOV whose light lands on the
    # detector, and draws only those, so both rows show the \FOV as the cells
    # it covers.
    model.plot(ax=ax[{_axis_row: 1}], unit=_unit_field)
    model.plot_residual(ax=ax[{_axis_row: 0}], unit=_unit_field)

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

    result = aastex.FigureStar("fig:vignetting", position="!htb")
    result.append(aastex.NoEscape(r"\centering"))
    result.add_fig(fig, width=aastex.NoEscape(r"\textwidth"))
    result.add_caption(aastex.NoEscape(r"""
(Top) The relative illumination of a single \ESIS\ channel as a function of
position in the \FOV, at each of the three target lines in the passband.
The illumination is the fraction of the pupil which is unvignetted, normalized
so that its average over the \FOV\ is unity.
(Bottom) The residual between that illumination and a linear model of it.
Both rows are plotted only where the model was fit: the cells inside the \FOV\
whose light lands on the detector.
In the leftmost column, at \HeIion, the \FOV\ is cut off on the left by the
edge of the detector."""))

    return result
