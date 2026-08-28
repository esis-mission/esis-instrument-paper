import aastex
import astropy.units as u
import esis
import matplotlib.pyplot as plt
import named_arrays as na

__all__ = [
    "bunch",
]

_num_wavelength = 51
"""The number of wavelengths at which the effective area is computed."""

_color_area = "red"
"""The colour of the effective area curve."""


def _spectrum() -> dict[str, u.Quantity]:
    """
    The named emission lines the model carries, with their wavelengths.
    """
    spectrum = esis.flights.f1.spectrum
    return {
        r"He\,\textsc{i}": spectrum.He_I.wavelength,
        r"Mg\,\textsc{x}": spectrum.Mg_X.wavelength,
        r"O\,\textsc{v}": spectrum.O_V.wavelength,
        r"Si\,\textsc{iv}": spectrum.Si_IV.wavelength,
    }


def bunch() -> aastex.FigureStar:
    """
    The effective area of one channel across the passband of the instrument.

    The apertures of the filter and the sensor are opened before the area is
    computed, so that the curve is the response of the coatings and the filter
    rather than a map of where the light happens to land. Left as built, the
    curve falls to zero at either end of the passband, where the light of that
    wavelength misses the sensor.
    """
    optics = esis.flights.f1.optics.design_single(num_distribution=0)

    # the passband of the instrument as it is built, measured before the
    # apertures are opened, so the curve is sampled over the range the
    # instrument actually observes
    wavelength_min = optics.wavelength_min.to(u.AA)
    wavelength_max = optics.wavelength_max.to(u.AA)

    wavelength = na.linspace(
        start=wavelength_min,
        stop=wavelength_max,
        axis="wavelength",
        num=_num_wavelength,
    )

    # Opening the apertures widens the passband, so the limits above are the
    # ones to keep: they say where the instrument as built is sensitive.
    optics.filter.radius_clear = 1000 * u.mm
    optics.camera.sensor.num_pixel_x = 4096
    optics.camera.sensor.num_pixel_y = 2048

    area = optics.system.area_effective(wavelength=wavelength)(wavelength)

    fig, ax = plt.subplots(
        figsize=(aastex.text_width_inches, 2),
        constrained_layout=True,
    )

    na.plt.plot(
        wavelength.to(u.AA),
        area.to(u.cm**2),
        ax=ax,
        axis="wavelength",
        color=_color_area,
    )

    ax.set_xlabel(f"wavelength ({u.AA:latex_inline})")
    ax.set_ylabel(f"effective area ({(u.cm ** 2):latex_inline})")
    ax.set_xlim(
        na.value(wavelength_min).ndarray,
        na.value(wavelength_max).ndarray,
    )
    ax.set_ylim(bottom=0)

    # Each line the model carries is marked where it falls, and the ones
    # outside the passband are left off rather than drawn against the edge of
    # the axes.
    for name, w in _spectrum().items():
        w = w.to_value(u.AA)
        if not ax.get_xlim()[0] <= w <= ax.get_xlim()[1]:
            continue
        ax.axvline(w, color="black", linewidth=0.5, zorder=0)
        ax.annotate(
            text=aastex.NoEscape(name),
            xy=(w, ax.get_ylim()[1]),
            xytext=(2, -9),
            textcoords="offset points",
            fontsize=7,
        )

    result = aastex.FigureStar("fig:bunch", position="!htb")
    result.append(aastex.NoEscape(r"\centering"))
    result.add_fig(fig, width=aastex.NoEscape(r"\textwidth"))
    result.add_caption(aastex.NoEscape(r"""
The effective area of a single \ESIS\ channel over its passband, with the
emission lines carried by the instrument model marked where they fall.
The spectrum of the \textbf{??} brightest lines in the passband is still owed."""))

    return result
