import esis
import numpy as np
import pylatex

__all__ = [
    "distortion_fit",
]


def _row(label: str, values, digits: int) -> list[str]:
    """One row of the table: a label and a number per channel."""
    return [label] + [f"{float(v):.{digits}f}" for v in values]


def distortion_fit() -> pylatex.Table:
    r"""
    The correlation of each channel's model with the flight after each stage of the fit.

    Read from the committed tables of the fit: the scores the reference
    table records after the capture, the placement of the windows and the
    shared polish; the mean correlation over the scored exposures of the
    acceptance table, which include the reference exposure; and the
    residual of the internal alignment.
    """
    reference = esis.flights.f1.optics.distortion_fit_table("reference")
    acceptance = esis.flights.f1.optics.distortion_fit_table("acceptance")
    scores = reference.meta["scores"]
    channels = sorted({int(c) for c in acceptance["channel"]})
    scored = np.isfinite(np.asarray(acceptance["correlation"], dtype=float))
    across = [
        np.mean(
            np.asarray(acceptance["correlation"], dtype=float)[
                scored & (np.asarray(acceptance["channel"]) == c)
            ]
        )
        for c in channels
    ]
    num_across = len({int(t) for t in np.asarray(acceptance["frame"])[scored]})

    result = pylatex.Table(position="!htb")
    result._star_latex_name = True
    result.add_caption(
        pylatex.NoEscape(
            r"""
The correlation of each channel's model image with its exposure after each stage of the
distortion fit, against the reference exposure, and the mean over """
            + str(num_across)
            + r""" exposures across the
flight, the reference among them, with each exposure's own pitch and yaw applied.
The last row is how far the internal alignment leaves each channel's sky from channel 1's at
the reference exposure, in pixels."""
        )
    )
    with (
        result.create(pylatex.Center()) as centering,
        centering.create(
            pylatex.Tabular(table_spec="l" + "c" * len(channels))
        ) as tabular,
    ):
        tabular.escape = False
        tabular.add_row(["Stage"] + [f"Channel {c}" for c in channels])
        tabular.add_hline()
        tabular.add_row(_row("Capture", scores["absolute"], 3))
        tabular.add_row(_row("Windows placed", scores["outline"]["merit"], 3))
        tabular.add_row(_row("Shared polish", scores["shared"], 3))
        tabular.add_row(_row("Across the flight", across, 3))
        tabular.add_hline()
        tabular.add_row(_row("Alignment residual [pix]", scores["alignment"], 2))
    result.append(pylatex.Label("table:distortionFit"))
    return result
