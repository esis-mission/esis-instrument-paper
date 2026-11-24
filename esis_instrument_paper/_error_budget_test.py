import astropy.units as u
import numpy as np
import pytest

from esis_instrument_paper import _diffraction, _error_budget


def test_terms() -> None:
    """
    Every term is either a Gaussian blur, which leaves an MTF between zero and
    one, or an MTF given some other way, and the elements are grouped together.
    """
    terms = _error_budget.terms()
    assert terms
    for term in terms:
        assert term.element
        assert term.name
        assert 0 < term.mtf <= 1
        if term.sigma is None:
            assert term.mtf_given is not None
        else:
            assert term.sigma >= 0 * u.um
    elements = [term.element for term in terms]
    groups = [e for i, e in enumerate(elements) if i == 0 or e != elements[i - 1]]
    assert len(groups) == len(set(groups))


def test_terms_figure() -> None:
    """The figure of each optic is the MTF allocated to it, not a blur."""
    figure = {
        term.element: term.mtf
        for term in _error_budget.terms()
        if term.name == "Figure"
    }
    assert figure == {
        "Primary": _error_budget.mtf_figure_primary,
        "Grating": _error_budget.mtf_figure_grating,
    }


def test_terms_mesh() -> None:
    """
    The mesh of the filter is the factor by which it lowers the MTF of the
    Huygens point-spread function, between the grating and the detector.
    """
    terms = _error_budget.terms()
    elements = list(dict.fromkeys(term.element for term in terms))
    assert elements.index("Grating") < elements.index("Filter")
    assert elements.index("Filter") < elements.index(r"\CCD")
    mesh = [term for term in terms if term.element == "Filter"]
    expected = _error_budget.Term(
        element="Filter",
        name="Mesh diffraction",
        mtf_given=_diffraction.mtf_mesh(),
    )
    assert mesh == [expected]
    assert 0.75 < expected.mtf < 0.85


def test_terms_uncompensated() -> None:
    """
    The defocus of the detector is the error of focusing it, which the
    gratings are not refocused to take out, so it blurs the image more than
    any tolerance which they are realigned to compensate.
    """
    terms = {(t.element, t.name): t for t in _error_budget.terms()}
    defocus = terms[(r"\CCD", "Defocus")].sigma
    compensated = [
        terms[("Primary", "Decenter $x$")].sigma,
        terms[("Grating", "Decenter $x$")].sigma,
        terms[(r"\CCD", "Decenter $x$")].sigma,
    ]
    assert all(defocus > sigma for sigma in compensated)


def test_mtf_gaussian() -> None:
    """
    No blur leaves the MTF whole, and an angle on the sky leaves the MTF of a
    Gaussian of that RMS radius at the frequency of the requirement, whichever
    way it is turned into a distance on the detector.
    """
    assert _error_budget.mtf_gaussian(0 * u.um) == 1
    angle = 0.5 * u.arcsec
    f = _error_budget.frequency() / u.cycle
    expected = np.exp(-np.square(np.pi * f * angle).to_value(u.dimensionless_unscaled))
    result = _error_budget.mtf_gaussian(_error_budget._on_detector(angle))
    assert np.isclose(result, expected)


def test_frequency() -> None:
    """One cycle per resolution element of the requirement, about 2 arcseconds."""
    frequency = _error_budget.frequency()
    assert np.isclose(
        frequency, 0.48 * u.cycle / u.arcsec, atol=0.01 * u.cycle / u.arcsec
    )


def test_mtf_rayleigh() -> None:
    """The old draft quoted the Rayleigh criterion as an MTF of 0.09."""
    assert np.isclose(_error_budget.mtf_rayleigh(), 0.0894, atol=1e-4)


def test_mtf_total() -> None:
    """
    The MTF of the instrument is the product of its terms, and the Gaussian
    terms multiply to the MTF of their sum in quadrature.
    """
    terms = _error_budget.terms()
    result = _error_budget.mtf_total()
    assert np.isclose(result, np.prod([term.mtf for term in terms]))
    given = np.prod([t.mtf for t in terms if t.sigma is None])
    expected = given * _error_budget.mtf_gaussian(_error_budget.sigma_total())
    assert np.isclose(result, expected)
    assert 0 < result < 1


def test_width_beam() -> None:
    """
    The beam of a single channel covers a sector of the primary mirror, a few
    centimeters wide.
    """
    width = _error_budget.width_beam()
    assert 2 * u.cm < width < 6 * u.cm


@pytest.mark.parametrize(
    argnames="value,expected",
    argvalues=[
        (1, "1.0"),
        (15.27, "15"),
        (0.512, "0.51"),
        (5.12e-7, r"5.1 \times 10^{-7}"),
    ],
)
def test_format(value: float, expected: str) -> None:
    """
    A tolerance has two significant figures, and is written in scientific
    notation if it is very small.
    """
    assert _error_budget._format(value) == expected
