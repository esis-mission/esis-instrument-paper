"""The signal one channel collects in a pixel, and its noise."""

import astropy.units as u
import named_arrays as na
import numpy as np
import pylatex

from esis_instrument_paper import _counts

__all__ = [
    "counts",
]

_sources = (r"\VR", r"\VR", r"\VR", r"\CDS")
"""Who measured the radiances of each column, in the order of the contexts."""

_contexts = (r"\QSShort", r"\CHShort", r"\ARShort", r"\ARShort")
"""The kind of region each column is, in the order of the contexts."""

_lines = (r"\OV", r"\MgXdim")
"""The name of each line, in the order of the lines."""


def _row(name: str, values: na.AbstractScalar, decimals: int) -> list[str]:
    """
    A row of the table: its name, then its value in each context.

    Parameters
    ----------
    name
        The name of the row.
    values
        The value in each context, in photons or without a unit.
    decimals
        The number of decimals to give each value to.
    """
    values = u.Quantity(na.as_named_array(values).ndarray).value
    return [name] + [f"{v:.{decimals}f}" for v in values]


def counts() -> pylatex.Table:
    """
    The photons a single channel collects in a pixel from each line in each
    context, with the noise and signal-to-noise ratio of a single exposure
    and of the stack of exposures the text quotes.
    """
    signal = _counts.counts()
    noise_read = _counts.noise_read()
    total = signal.sum(_counts.axis_line)
    num = _counts.num_stack_required(total, noise_read)

    result = pylatex.Table(position="!htb")

    result.add_caption(
        pylatex.NoEscape(
            r"""
Estimated signal statistics per channel (in photon counts) for \ESIS\ lines in \CH, \QS, and \AR.
Note that the \SNR\ estimates are lower bounds since charge diffusion decreases the shot noise."""
        )
    )

    # the read noise is the same in every context
    noise_read_value = float(na.as_named_array(noise_read).ndarray.to_value(u.ph))

    with (
        result.create(pylatex.Center()) as centering,
        centering.create(pylatex.Tabular(table_spec="lrrrr")) as tabular,
    ):
        tabular.escape = False
        tabular.add_row(["Source", *_sources])
        tabular.add_row(["Solar context", *_contexts])
        tabular.add_hline()
        tabular.add_hline()
        tabular.append(
            pylatex.NoEscape(
                r"\multicolumn{5}{c}{1 $\times$ \detectorExposureLength\ exp.}\\"
            )
        )
        for i, name in enumerate(_lines):
            tabular.add_row(_row(name, signal[{_counts.axis_line: i}], decimals=0))
        tabular.add_hline()
        tabular.add_row(_row("Total", total, decimals=0))
        tabular.add_row(_row("Shot noise", np.sqrt(total * u.ph), decimals=1))
        tabular.add_row(["Read noise", *len(_contexts) * [f"{noise_read_value:.1f}"]])
        tabular.add_row(_row(r"\SNRShort", _counts.snr(total, noise_read), decimals=1))
        tabular.add_hline()
        tabular.add_hline()
        tabular.append(
            pylatex.NoEscape(
                r"\multicolumn{5}{c}"
                r"{\NumExpInStack\ $\times$ \detectorExposureLength\ exp.}\\"
            )
        )
        tabular.add_row(_row("Total", num * total, decimals=0))
        tabular.add_row(
            _row(r"\SNRShort", _counts.snr(total, noise_read, num), decimals=1)
        )
        tabular.add_hline()
        tabular.add_hline()

    result.append(pylatex.Label("table:counts"))

    return result
