"""The spectrum of the quiet Sun, as this article computes it."""

import importlib.metadata
import pathlib

import astropy.units as u
import esis
import named_arrays as na
import numpy as np
import utu

__all__ = [
    "abundance",
    "area_effective",
    "dem",
    "emission_measure",
    "lines",
    "num_grid",
    "pressure",
    "seed",
    "version",
]

abundance = "sun_coronal_2012_schmelz_ext"
"""
The abundances of the elements, measured by :cite:t:`Schmelz2012`.

The extended table rather than the one it extends, which is a workaround
rather than a choice: the two agree exactly on every element in the
passband, and differ only in the ones too rare to appear here. But
:func:`fiasco.proton_electron_ratio` sums over every element in the
database and means to skip the ones an abundance file leaves out:

.. code-block:: python

    try:
        abundance = el.abundance
    except KeyError:
        log.warning(f'Not including {el.atomic_symbol}. ...')

:mod:`fiasco` raises :class:`fiasco.util.exceptions.MissingDatasetException`
there, which inherits from :class:`Exception` and not from :class:`KeyError`,
so the guard never fires and the sum dies on the first element the file
omits, which is lithium. The extended table omits none of them.
"""

dem = "quiet_sun.dem"
"""The differential emission measure of the quiet Sun, from CHIANTI."""

pressure = 1e15 * u.K / u.cm**3
"""The pressure of the quiet Sun, which sets the density at each temperature."""

seed = 42
"""
The seed of the sampling which estimates the effective area.

The field and the pupil are sampled at a point drawn inside each of their
cells, which keeps the quadrature from aliasing against the edge of an
aperture, at the cost of a different answer on every call: about two percent
on this instrument, which is enough to see in a figure. Fixing the seed fixes
the figure.
"""

num_grid = 20
"""
How finely the field and the pupil are sampled, as cells along each axis.

Twelve is the default and leaves the curve visibly rough. Twenty takes the
roughness down by a factor of three, which is what a quarter of a million
rays per wavelength buys and follows the square root of their number.
Twenty-eight takes it a further tenth, and no further: what is left is the
structure of the measured coatings rather than anything left to average away.
"""

_axis = "temperature"
"""The name of the axis along the temperatures of the plasma."""


def temperature() -> na.AbstractScalar:
    """The temperatures the spectrum is computed at."""
    return na.ScalarArray(
        ndarray=10 ** np.arange(4, 8.1, 0.1) * u.K,
        axes=(_axis,),
    )


def emission_measure() -> na.AbstractScalar:
    """
    How much quiet Sun there is at each temperature.

    Read from the CHIANTI differential emission measure file and interpolated
    in the logarithm of both quantities, since both run over several decades
    and a straight line through them is a straight line in neither.
    """
    import fiasco

    t = temperature()

    path = pathlib.Path(fiasco.defaults["ascii_dbase_root"]) / "dem" / dem
    rows = []
    for line in path.read_text().splitlines():
        field = line.split()
        if not field or field[0].startswith("%"):
            continue
        if float(field[0]) == -1:
            break
        rows.append((float(field[0]), float(field[1])))
    log_t, log_dem = np.array(rows).T

    result = np.interp(
        x=np.log10(t.ndarray.to_value(u.K)),
        xp=log_t,
        fp=log_dem,
        left=-np.inf,
        right=-np.inf,
    )
    result = (10**result) / (u.cm**5 * u.K)

    # the measure of each bin is the differential measure across it, the grid
    # being even in the logarithm
    result = result * t.ndarray * np.log(10) * 0.1

    return na.ScalarArray(result, axes=(_axis,))


def version() -> str:
    """The version of the CHIANTI database these numbers were computed from."""
    import fiasco
    from fiasco.util import read_chianti_version

    return str(read_chianti_version(fiasco.defaults["ascii_dbase_root"]))


@esis.memory.cache
def _lines(
    wavelength_min: u.Quantity,
    wavelength_max: u.Quantity,
    chianti_version: str,
) -> na.FunctionArray:
    """
    Compute the lines, and remember them, since it takes several minutes.

    ``chianti_version`` is not read here. It is an argument so that it is part of
    what the cache is keyed on, since the answer depends on it and nothing
    else in the key does: :mod:`joblib` hashes the arguments and the source
    of this function, neither of which knows which database is installed.
    Without it, installing a new database would go on returning the numbers
    computed from the old one, under a caption naming the new.
    """
    t = temperature()
    return utu.spectrum.lines(
        temperature=t,
        density=pressure / t,
        emission_measure=emission_measure(),
        wavelength_min=wavelength_min,
        wavelength_max=wavelength_max,
        abundance=abundance,
        axis_temperature=_axis,
    )


def lines(
    wavelength_min: u.Quantity,
    wavelength_max: u.Quantity,
) -> na.FunctionArray:
    """
    The emission lines of the quiet Sun in a range of wavelengths, brightest
    first.

    Every part of this article which needs a line needs the same list of
    them: the figure of the passband draws it, and the tables of the count
    rates and of the error budget pick the \\OV\\ and \\MgXion\\ lines out of
    it. Computing it once and remembering it keeps the three of them saying
    the same thing, and keeps a rebuild of the article from taking a quarter
    of an hour.

    Parameters
    ----------
    wavelength_min
        The shortest wavelength to compute.
    wavelength_max
        The longest wavelength to compute.
    """
    return _lines(wavelength_min, wavelength_max, version())


@esis.memory.cache
def _area_effective(
    wavelength: u.Quantity,
    num_grid: int,
    seed: int,
    optika_version: str,
) -> na.AbstractScalar:
    """
    Trace the rays, and remember where they landed.

    ``optika_version`` is not read here. It is an argument so that it is part
    of what the cache is keyed on, since the answer depends on which version
    traced the rays and nothing else in the key does. Between 2.5 and 2.6 the
    answer moved by about two percent.
    """
    optics = esis.flights.f1.optics.design_single(num_distribution=0)

    # The apertures are opened so that the curve is the response of the
    # coatings and the filter, rather than a map of where the light happens
    # to land.
    optics.filter.radius_clear = 1000 * u.mm
    optics.camera.sensor.num_pixel_x = 4096
    optics.camera.sensor.num_pixel_y = 2048

    def vertices(name: str) -> na.Cartesian2dVectorLinearSpace:
        return na.Cartesian2dVectorLinearSpace(
            start=-1,
            stop=1,
            axis=na.Cartesian2dVectorArray(f"{name}_x", f"{name}_y"),
            num=num_grid,
        )

    model = optics.system.area_effective(
        wavelength=wavelength,
        field=vertices("field"),
        pupil=vertices("pupil"),
        seed=seed,
    )

    return model(wavelength).to(u.cm**2)


def area_effective(wavelength: u.Quantity) -> na.AbstractScalar:
    """
    The effective area of one channel, at each of ``wavelength``.

    Computed once and remembered, as the lines are: a quarter of a million
    rays per wavelength take half a minute, which is not something to pay on
    every rebuild of the article.

    Parameters
    ----------
    wavelength
        The wavelengths to compute the effective area at.
    """
    return _area_effective(
        wavelength=wavelength,
        num_grid=num_grid,
        seed=seed,
        optika_version=importlib.metadata.version("optika"),
    )
