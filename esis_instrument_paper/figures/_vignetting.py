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

The illumination at a field position is the fraction of the pupil which is
unvignetted, so this number sets how finely that fraction can be resolved,
and until the pupil is sampled finely enough the residual of the fit is
mostly that granularity rather than anything about the optics. Sampling half
as finely puts about a quarter of the mean residual back; at this many it has
settled, agreeing to about a percent with the centers of those same cells,
which is a sample with quite different errors, and moving by well under a
percent from one seed to the next.
"""

_seed = 42
"""
The seed of the random draw which places a sample inside each pupil cell.

The draw has to be seeded for the figure to be the same every time the
article is built. The field is not drawn this way: the samples of the field
are the coordinates the map is drawn against, and scattering them inside
their cells leaves a grid whose rows and columns no longer line up.
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
is the evidence for that: the residual of the linear fit stays under two
percent of the illumination everywhere it was fit. A quadratic fit more than
halves that residual, so the field is not exactly linear, but the model
plotted here is the one the text claims.
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


def _grid(
    name: str,
    num: int,
    seed: None | int = None,
) -> na.Cartesian2dVectorArray:
    """
    One sample from each cell of a square grid of `num` by `num` normalized cells.

    A normalized coordinate of $\\pm 1$ is the edge of the field stop, or of
    the pupil, so a grid which includes those values lays a whole ring of
    samples along the rim of the aperture, where every one of them is clipped
    and none of them says anything. These samples are inside the cells that
    ring bounds.

    Parameters
    ----------
    name
        The name of the grid, which its two axes are named after.
    num
        The number of cells along each axis.
    seed
        If given, each sample is drawn at random from inside its own cell
        instead of taken from the center of it, and this seeds that draw.
    """
    axis = (f"{name}_x", f"{name}_y")

    vertices = na.Cartesian2dVectorLinearSpace(
        start=-1,
        stop=+1,
        axis=na.Cartesian2dVectorArray(*axis),
        num=num + 1,
    )

    return vertices.cell_centers(
        axis=axis,
        random=seed is not None,
        seed=seed,
    )


def _model() -> optika.radiometry.PolynomialVignettingModel:
    """Fit the illumination of a single channel as a function of the field."""
    optics = esis.flights.f1.optics.design_single(num_distribution=0)

    return optics.system.vignetting(
        wavelength=_wavelength(),
        field=_grid("field", _num_field),
        pupil=_grid("pupil", _num_pupil, seed=_seed),
        degree=_degree,
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

    # the rows are numbered from the bottom of the figure upwards. The residual
    # is drawn only where the fit was constrained, which is what the model
    # itself does: outside the field stop no ray survives, so there is nothing
    # there for the residual to be the residual of.
    model.plot(ax=ax[{_axis_row: 1}])
    model.plot_residual(ax=ax[{_axis_row: 0}])

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
(Bottom) The residual between that illumination and a linear model of it,
plotted only where the model was fit."""))

    return result
