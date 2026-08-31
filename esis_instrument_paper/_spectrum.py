"""The spectrum of the quiet Sun, as this article computes it."""

import pathlib

import astropy.units as u
import esis
import named_arrays as na
import numpy as np
import utu

__all__ = [
    "abundance",
    "dem",
    "emission_measure",
    "lines",
    "pressure",
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


@esis.memory.cache
def _lines(
    wavelength_min: u.Quantity,
    wavelength_max: u.Quantity,
) -> na.FunctionArray:
    """Compute the lines, and remember them, since it takes several minutes."""
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
    return _lines(wavelength_min, wavelength_max)
