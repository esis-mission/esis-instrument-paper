import astropy.units as u
import esis
import named_arrays as na
import numpy as np
import pytest

from esis_instrument_paper import _counts


def test_snr() -> None:
    """
    Without read noise the signal-to-noise ratio of a sum is the square root
    of the photons summed, and read noise adds once per exposure.
    """
    signal = na.ScalarArray([100, 400] * u.ph, axes=_counts.axis_context)
    result = _counts.snr(signal, 0 * u.ph, num=4)
    assert np.all(result == na.ScalarArray([20, 40] * u.one, axes=_counts.axis_context))

    result = _counts.snr(signal, 10 * u.ph, num=4)
    expected = 4 * signal / np.sqrt(4 * signal * u.ph + 4 * (10 * u.ph) ** 2)
    assert np.allclose(result, expected)


@pytest.mark.parametrize(
    argnames="snr_min,expected",
    argvalues=[
        (20, 4),
        (20.1, 5),
    ],
)
def test_num_stack(snr_min: float, expected: int) -> None:
    """
    The stack is the fewest exposures which reach the ratio sought.

    Parameters
    ----------
    snr_min
        The signal-to-noise ratio to reach.
    expected
        The fewest exposures which reach it, with a ratio of ten in each.
    """
    assert _counts.num_stack(100 * u.ph, 0 * u.ph, snr_min) == expected


def test_num_stack_required() -> None:
    """
    The text says that the signal requirement is met by stacking exposures,
    and the requirements table quotes the ratio of that stack: it meets the
    requirement, and a stack of one fewer does not.
    """
    signal = _counts.counts().sum(_counts.axis_line)
    noise_read = _counts.noise_read()
    num = _counts.num_stack_required(signal, noise_read)
    signal = signal[_counts.index(_counts.context_coronal_hole)]
    requirement = esis.flights.f1.optics.requirements().snr
    assert _counts.snr(signal, noise_read, num) >= requirement
    assert _counts.snr(signal, noise_read, num - 1) < requirement


def test_num_stack_counts() -> None:
    """
    The text quotes how long it takes to collect a good image in an active
    region: that long collects one, and an exposure less does not.
    """
    signal = _counts.counts().sum(_counts.axis_line)
    signal = signal[_counts.index(_counts.context_active_region)]
    num = _counts.num_stack_counts(signal, _counts.counts_image)
    assert num * signal >= _counts.counts_image * u.ph
    assert (num - 1) * signal < _counts.counts_image * u.ph


def test_shot_noise_limited() -> None:
    """
    The text says that the shot noise dominates the read noise even in a
    coronal hole in a single exposure.
    """
    signal = _counts.counts().sum(_counts.axis_line)
    signal = signal[_counts.index(_counts.context_coronal_hole)]
    assert np.sqrt(signal * u.ph) > _counts.noise_read()
