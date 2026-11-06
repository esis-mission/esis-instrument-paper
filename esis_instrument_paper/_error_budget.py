"""
The imaging error budget of a single channel.

Every term of the budget blurs the image of the \\OV\\ line, and is modeled, as
the old draft modeled it, as a Gaussian whose root-mean-square radius is
:math:`\\sigma`. The term leaves a modulation transfer function (MTF) of
:math:`\\exp(-\\pi^2 f^2 \\sigma^2)` at the spatial frequency :math:`f` of the
resolution requirement, the transform of a Gaussian whose standard deviation
along each axis is :math:`\\sigma / \\sqrt{2}`.

The tolerances are the tolerance analysis of the old draft done on the model:
each one is moved to either end of its range, the gratings are realigned, and
the blur is the growth of the RMS spot radius averaged over the field of view,
in quadrature. The figure of the optics is an allocation of the MTF instead,
which a Fourier optics model turned into the specifications of the optics.
"""

import dataclasses
import functools
import importlib.metadata
import warnings
from collections.abc import Callable

import astropy.modeling
import astropy.units as u
import esis
import named_arrays as na
import numpy as np

__all__ = [
    "Term",
    "distance_roll",
    "frequency",
    "mtf_figure_grating",
    "mtf_figure_primary",
    "mtf_gaussian",
    "mtf_rayleigh",
    "mtf_total",
    "sigma_total",
    "terms",
    "wavelength",
    "width_beam",
]

wavelength = esis.flights.f1.spectrum.O_V.wavelength
"""The wavelength of the line the instrument was designed around."""

mtf_figure_primary = 0.7
"""
The MTF allocated to the figure of the primary mirror at the resolution
requirement.
"""

mtf_figure_grating = 0.6
"""
The MTF allocated to the figure of the gratings at the resolution requirement.
"""

distance_roll = 10 * u.arcmin
"""
The distance of the image from the axis the payload rolls about, which the old
draft took to be :math:`10'`.

The model does not carry where the instrument pointed relative to the roll
axis of the pointing system, so this is the old draft's number.
"""

_num_field = 11
"""The number of field angles along each axis the spot radius is averaged over."""

_num_pupil = 11
"""The number of rays along each axis of the pupil traced for each spot."""


@functools.cache
def _nominal() -> esis.optics.Instrument:
    """A single channel as designed."""
    return esis.flights.f1.optics.design_single(num_distribution=0)


@functools.cache
def _uncertain() -> esis.optics.Instrument:
    """
    A single channel as designed, with its tolerances.

    Only the widths of its uncertain parameters are read, so a single sample
    is drawn, with a seed so that building it draws no fresh entropy.
    """
    return esis.flights.f1.optics.design_single(num_distribution=1, seed=0)


def _plate_scale() -> u.Quantity:
    """
    The plate scale along the dispersion, which turns an angle on the sky
    into a distance on the detector.

    The old draft turned its pointing errors and its diffraction limit into
    distances on the detector with this plate scale, and this module turns
    every angle with it, its MTF included, so that a term on the sky and
    the same term on the detector leave the same MTF.
    """
    plate_scale = _nominal().system.plate_scale(wavelength).x
    return na.as_named_array(plate_scale).ndarray.to(u.arcsec / u.pix)


def _pixel() -> u.Quantity:
    """The width of a pixel of the detector, per pixel."""
    return _nominal().camera.sensor.width_pixel / u.pix


def _on_detector(angle: u.Quantity) -> u.Quantity:
    """The distance on the detector which an angle on the sky spans."""
    return (angle / _plate_scale() * _pixel()).to(u.um)


def frequency() -> u.Quantity:
    """
    The spatial frequency at which the MTF is given: one cycle per resolution
    element of the requirement.
    """
    resolution = esis.flights.f1.optics.requirements().resolution_angular
    return (u.cycle / resolution).to(u.cycle / u.arcsec)


def mtf_gaussian(sigma: u.Quantity) -> float:
    """
    The MTF of a Gaussian blur with an RMS radius of `sigma` on the detector,
    at :func:`frequency`.

    Parameters
    ----------
    sigma
        The RMS radius of the blur.
    """
    f = frequency() / u.cycle * _plate_scale() / _pixel()
    exponent = np.square(np.pi * f * sigma).to(u.dimensionless_unscaled)
    return float(np.exp(-exponent.value))


def mtf_rayleigh() -> float:
    r"""
    The MTF of a circular aperture at the resolution limit of the Rayleigh
    criterion, :math:`1.22 \lambda / D`, which is :math:`1 / 1.22` of its
    cutoff frequency :math:`D / \lambda`.
    """
    nu = 1 / 1.22
    return float(2 / np.pi * (np.arccos(nu) - nu * np.sqrt(1 - nu**2)))


@dataclasses.dataclass(frozen=True)
class Term:
    """One row of the imaging error budget."""

    element: str
    """The part of the instrument, or of the payload, the term belongs to."""

    name: str
    """What blurs the image."""

    tolerance: str = ""
    """The tolerance as the table prints it, or nothing for a fixed term."""

    sigma: None | u.Quantity = None
    """
    The RMS radius of the Gaussian which models the blur on the detector, or
    :obj:`None` for a term given as an MTF.
    """

    mtf_allocated: None | float = None
    """The MTF allocated to a term which is not modeled as a Gaussian."""

    @property
    def mtf(self) -> float:
        """The MTF this term leaves at :func:`frequency`."""
        if self.sigma is None:
            return self.mtf_allocated
        return mtf_gaussian(self.sigma)


def _field() -> na.Cartesian2dVectorLinearSpace:
    """The field angles the spot radius is averaged over, normalized."""
    return na.Cartesian2dVectorLinearSpace(
        start=-1,
        stop=1,
        axis=na.Cartesian2dVectorArray("field_x", "field_y"),
        num=_num_field,
        centers=True,
    )


def _pupil() -> na.Cartesian2dVectorLinearSpace:
    """The positions on the pupil of the rays traced for each spot, normalized."""
    return na.Cartesian2dVectorLinearSpace(
        start=-1,
        stop=1,
        axis=na.Cartesian2dVectorArray("pupil_x", "pupil_y"),
        num=_num_pupil,
        centers=True,
    )


def _radius(instrument: esis.optics.Instrument) -> u.Quantity:
    """
    The RMS spot radius of the \\OV\\ line, averaged over the field of view.

    The field angles outside the field stop trace no light, and are left out
    of the average.
    """
    radius = instrument.system.radius_spot(
        wavelength=wavelength,
        field=_field(),
        pupil=_pupil(),
    )
    return np.nanmean(na.as_named_array(radius).ndarray).to(u.um)


def _get(instrument: object, path: str) -> object:
    """The attribute of `instrument` at a dotted path."""
    for name in path.split("."):
        instrument = getattr(instrument, name)
    return instrument


def _replaced(instrument: object, path: str, value: object) -> object:
    """
    A copy of `instrument` with the attribute at a dotted path replaced.

    Each object along the path is replaced rather than changed in place, so
    that no cached raytrace of the original is left stale.
    """
    head, _, tail = path.partition(".")
    if tail:
        value = _replaced(getattr(instrument, head), tail, value)
    return instrument.replace(**{head: value})


@dataclasses.dataclass(frozen=True)
class _Tolerance:
    """A tolerance of the design, and how the analysis moves it."""

    element: str
    """The part of the instrument the tolerance belongs to."""

    name: str
    """What the tolerance moves."""

    width: Callable[[esis.optics.Instrument], u.Quantity]
    """The half-width of the range of the tolerance, read from the uncertain design."""

    move: Callable[[esis.optics.Instrument, u.Quantity], esis.optics.Instrument]
    """Move an instrument by an amount within the range of the tolerance."""

    compensate: bool = True
    """
    Whether the gratings are realigned after the tolerance is moved, rather
    than the tolerance being the residual error of the focus itself, which
    refocusing would remove.
    """

    unit: u.UnitBase = u.mm
    """The unit the table prints the tolerance in."""

    printed: Callable[[u.Quantity], u.Quantity] = lambda width: width
    """The tolerance as the table prints it, given the half-width of its range."""


def _translation(
    element: str,
    name: str,
    paths: tuple[str, ...],
    **kwargs,
) -> _Tolerance:
    """
    A tolerance on a position, or another parameter set by a single number,
    whose range is that of the first of `paths`, and which moves all of them.
    """

    def width(uncertain: esis.optics.Instrument) -> u.Quantity:
        return _get(uncertain, paths[0]).width

    def move(
        instrument: esis.optics.Instrument,
        delta: u.Quantity,
    ) -> esis.optics.Instrument:
        for path in paths:
            instrument = _replaced(instrument, path, _get(instrument, path) + delta)
        return instrument

    return _Tolerance(element, name, width, move, **kwargs)


def _ruling(index: int, name: str, **kwargs) -> _Tolerance:
    """A tolerance on a coefficient of the polynomial ruling spacing."""

    def width(uncertain: esis.optics.Instrument) -> u.Quantity:
        return uncertain.grating.rulings.spacing.coefficients[index].width

    def move(
        instrument: esis.optics.Instrument,
        delta: u.Quantity,
    ) -> esis.optics.Instrument:
        rulings = instrument.grating.rulings
        coefficients = dict(rulings.spacing.coefficients)
        coefficients[index] = coefficients[index] + delta
        spacing = rulings.spacing.replace(coefficients=coefficients)
        rulings = rulings.replace(spacing=spacing)
        return _replaced(instrument, "grating.rulings", rulings)

    return _Tolerance("Grating", name, width, move, **kwargs)


def _density(width: u.Quantity) -> u.Quantity:
    """
    The tolerance on the ruling density, from that on the spacing at the
    center of the grating, which esis carries it as.
    """
    spacing = _nominal().grating.rulings.spacing.coefficients[0]
    return width / np.square(spacing)


def _tolerances() -> list[_Tolerance]:
    """
    The tolerances of the design, in the order of the table.

    The field stop is mounted on the primary mirror, so it moves with it.
    The defocus of the grating is the error of transferring the focus of the
    alignment grating to the flight grating, and the defocus of the detector
    is the error of focusing the detector, so neither is compensated.
    """
    primary = "primary_mirror.translation"
    stop = "field_stop.translation"
    grating = "grating.translation"
    sensor = "camera.sensor.translation"
    return [
        _translation("Primary", "Decenter $x$", (f"{primary}.x", f"{stop}.x")),
        _translation("Primary", "Decenter $y$", (f"{primary}.y", f"{stop}.y")),
        _translation("Grating", "Radius", ("grating.sag.radius",)),
        _translation("Grating", "Decenter $x$", (f"{grating}.x",)),
        _translation("Grating", "Decenter $y$", (f"{grating}.y",)),
        _translation(
            "Grating",
            "Defocus",
            (f"{grating}.z",),
            compensate=False,
            unit=u.um,
        ),
        _translation("Grating", "Clocking", ("grating.roll",), unit=u.mrad),
        _ruling(0, "Ruling density", unit=u.mm**-1, printed=_density),
        _ruling(1, "Ruling $d_1$", unit=u.um / u.mm),
        _ruling(2, "Ruling $d_2$", unit=u.um / u.mm**2),
        _translation(r"\CCD", "Decenter $x$", (f"{sensor}.x",)),
        _translation(r"\CCD", "Decenter $y$", (f"{sensor}.y",)),
        _translation(r"\CCD", "Defocus", (f"{sensor}.z",), compensate=False),
    ]


@esis.memory.cache
def _radii(
    num_field: int,
    num_pupil: int,
    esis_version: str,
    optika_version: str,
) -> tuple[u.Quantity, list[u.Quantity]]:
    """
    The RMS spot radius of the aligned design, averaged over the field of
    view, and of the design with each of :func:`_tolerances` at either end of
    its range, and remember them, since realigning the gratings two dozen
    times takes several minutes.

    The arguments are not read here. They are arguments so that they are part
    of what the cache is keyed on, since the answer depends on them and nothing
    else in the key does: :mod:`joblib` hashes the arguments and the source of
    this function, neither of which knows the size of the grids or which
    versions of the model and of the raytrace computed it.
    """
    aligned = _nominal().align_grating(wavelength=wavelength)
    uncertain = _uncertain()
    radii = []
    for tolerance in _tolerances():
        width = tolerance.width(uncertain)
        radius = []
        for sign in (-1, 1):
            moved = tolerance.move(aligned, sign * width)
            if tolerance.compensate:
                moved = moved.align_grating(wavelength=wavelength)
            radius.append(_radius(moved))
        radii.append(u.Quantity(radius))
    return _radius(aligned), radii


def width_beam() -> u.Quantity:
    """
    The width of the beam on the primary mirror along the dispersion,
    averaged over the field of view.

    The old draft took the diffraction of the instrument to be that of a slit
    as wide as the beam along the dispersion. The dispersion runs outward from
    the center of the primary mirror, toward the center of the beam.
    """
    system = _nominal().system
    rays = system.raytrace(
        wavelength=wavelength,
        field=_field(),
        pupil=na.Cartesian2dVectorLinearSpace(
            start=-1,
            stop=1,
            axis=na.Cartesian2dVectorArray("pupil_x", "pupil_y"),
            num=41,
        ),
        efficiency=False,
    )
    index = [surface.name for surface in system.surfaces_all].index("primary")
    transformation = system.surfaces_all[index].transformation
    position = transformation.inverse(
        rays.outputs.position[{system.axis_surface: index}]
    )
    unvignetted = rays.outputs.unvignetted[{system.axis_surface: ~0}]
    x = np.where(unvignetted, position.x, np.nan)
    y = np.where(unvignetted, position.y, np.nan)
    center_x = np.nanmean(x.ndarray)
    center_y = np.nanmean(y.ndarray)
    radial = (x * center_x + y * center_y) / np.sqrt(center_x**2 + center_y**2)
    axis = ("pupil_x", "pupil_y")
    # The corners of the grid of field angles lie outside the octagonal field
    # stop, so no ray of theirs is left to measure, and they are left out of
    # the average.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", "All-NaN", RuntimeWarning)
        width = np.nanmax(radial, axis=axis) - np.nanmin(radial, axis=axis)
    return np.nanmean(width.ndarray).to(u.mm)


def _sigma_diffraction() -> u.Quantity:
    """
    The diffraction limit, as the old draft found it: the Gaussian which fits
    the diffraction pattern of a slit as wide as :func:`width_beam` across the
    central pixel, as an RMS radius.
    """
    x = np.linspace(-0.5, 0.5, num=100)
    angle = (x * u.pix * _plate_scale()).to(u.rad)
    argument = (width_beam() * np.sin(angle) / wavelength).to(u.dimensionless_unscaled)
    intensity = np.square(np.sinc(argument.value))
    fit = astropy.modeling.fitting.TRFLSQFitter()(
        model=astropy.modeling.models.Gaussian1D(amplitude=1, mean=0, stddev=0.2),
        x=x,
        y=intensity,
    )
    return (np.sqrt(2) * np.abs(fit.stddev.value) * u.pix * _pixel()).to(u.um)


def _sigma_peak_to_peak(angle: u.Quantity) -> u.Quantity:
    """
    The blur on the detector of a pointing error given peak to peak, which the
    old draft took to be :math:`\\sqrt{8}` times its root-mean-square, as for a
    sinusoid.
    """
    return _on_detector(angle / np.sqrt(8))


def _format(value: float) -> str:
    """
    A number to two significant figures, in the notation of LaTeX math mode,
    in scientific notation if it is very large or very small.
    """
    if 1e-2 <= abs(value) < 1e3:
        return f"{value:#.2g}".rstrip(".")
    exponent = int(np.floor(np.log10(abs(value))))
    return rf"{value / 10**exponent:.1f} \times 10^{{{exponent}}}"


def _tolerance(value: u.Quantity, plus_minus: bool = True) -> str:
    """A tolerance as the table prints it, in its own unit."""
    sign = r"\pm" if plus_minus else ""
    return rf"${sign}{_format(value.value)}$\,{value.unit:latex_inline}"


def _sorted(terms: list["Term"]) -> list["Term"]:
    """The terms grouped by element, in the order each element first appears."""
    elements = list(dict.fromkeys(term.element for term in terms))
    return sorted(terms, key=lambda term: elements.index(term.element))


@functools.cache
def terms() -> tuple[Term, ...]:
    """The terms of the imaging error budget, in the order of the table."""
    nominal = _nominal()
    radius_aligned, radii = _radii(
        num_field=_num_field,
        num_pupil=_num_pupil,
        esis_version=importlib.metadata.version("euv-snapshot-imaging-spectrograph"),
        optika_version=importlib.metadata.version("optika"),
    )

    sparcs = esis.flights.f1.nsroc.sparcs()
    exposure = nominal.camera.timedelta_exposure
    drift = _sigma_peak_to_peak(sparcs.drift_pointing * exposure)
    diffusion = nominal.camera.sensor.material.width_charge_diffusion(wavelength)

    def roll(angle: u.Quantity) -> u.Quantity:
        return _sigma_peak_to_peak(2 * np.sin(angle / 2) * distance_roll)

    result = [
        Term("System", "Aberrations", sigma=radius_aligned),
        Term("System", "Diffraction", sigma=_sigma_diffraction()),
        Term("System", "Thermal drift", sigma=drift),
        Term(
            "Primary",
            "Figure",
            tolerance=r"Table~\ref{table:error}",
            mtf_allocated=mtf_figure_primary,
        ),
        Term(
            "Grating",
            "Figure",
            tolerance=r"Table~\ref{table:error}",
            mtf_allocated=mtf_figure_grating,
        ),
    ]
    uncertain = _uncertain()
    for tolerance, radius in zip(_tolerances(), radii, strict=True):
        width = tolerance.printed(tolerance.width(uncertain))
        sigma = np.sqrt(np.maximum(np.square(radius) - np.square(radius_aligned), 0))
        result.append(
            Term(
                element=tolerance.element,
                name=tolerance.name,
                tolerance=_tolerance(width.to(tolerance.unit)),
                sigma=sigma.max(),
            )
        )
    result += [
        Term(r"\CCD", "Charge diffusion", sigma=np.sqrt(2) * diffusion.ndarray),
        Term(
            r"\SPARCSShort",
            "Pointing jitter",
            tolerance=_tolerance(sparcs.jitter_pointing / 2),
            sigma=_sigma_peak_to_peak(sparcs.jitter_pointing),
        ),
        Term(
            r"\SPARCSShort",
            "Pointing drift",
            tolerance=_tolerance(sparcs.drift_pointing, plus_minus=False),
            sigma=drift,
        ),
        Term(
            r"\SPARCSShort",
            "Roll jitter",
            tolerance=_tolerance((sparcs.jitter_roll / 2).to(u.arcsec)),
            sigma=roll(sparcs.jitter_roll),
        ),
        Term(
            r"\SPARCSShort",
            "Roll drift",
            tolerance=_tolerance(sparcs.drift_roll, plus_minus=False),
            sigma=roll(sparcs.drift_roll * exposure),
        ),
    ]
    return tuple(_sorted(result))


def sigma_total() -> u.Quantity:
    """The terms modeled as Gaussians, added in quadrature."""
    sigmas = [term.sigma for term in terms() if term.sigma is not None]
    return np.sqrt(np.sum(np.square(u.Quantity(sigmas))))


def mtf_total() -> float:
    """The MTF of the instrument at :func:`frequency`: the product of every term."""
    return float(np.prod([term.mtf for term in terms()]))
