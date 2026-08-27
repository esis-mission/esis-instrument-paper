import dataclasses

import aastex
import astropy.units as u
import esis
import matplotlib.pyplot as plt
import matplotlib.transforms
import mpl_toolkits.mplot3d
import named_arrays as na
import numpy as np
import optika

__all__ = [
    "layout",
]

_elevation_view = 0
"""The elevation the instrument is viewed from, as the old draft had it."""

_azimuth_view = -40
"""The azimuth the instrument is viewed from, as the old draft had it."""

_components_view = ("y", "z", "x")
"""
Which component of the instrument is drawn along which axis of the plot.

The optical axis is :math:`z`, and it runs along the horizontal.
"""

_channel_traced = 3
"""
Which channel the light is traced through.

Any one of them would do to show the path. This one is chosen because its beam
is the clearest: it approaches the primary along the top of the drawing and
leaves towards the bottom, so it crosses neither the face of the mirror nor any
of the labels. The two channels nearest the viewer show about twice as much of
the beam, and run it straight through the field stop annotation.
"""

_color_rays = "tab:blue"
"""The colour of the light traced through the instrument."""

_clearance_entrance = 50 * u.mm
"""
How far beyond the gratings the light is drawn entering the instrument.

The object is at infinity, so the rays begin at the front aperture, which sits
far enough back that the gratings would otherwise be stranded well inside the
frame. The front aperture carries no aperture of its own, so moving it changes
only where the incoming rays start being drawn. The old draft did the same with
``source.piston = 1425 mm`` against a grating at ``1374.7 mm``.
"""

_linestyle_unpopulated = ":"
"""
The line style marking a channel which was not populated for the flight.

Written as a style rather than a dash pattern: a pattern such as
``(0, (1, 3))`` cannot be broadcast by :mod:`named_arrays`, which reads the
nested tuple as a ragged array.
"""


def _grid() -> optika.vectors.ObjectVectorArray:
    """
    A handful of rays, which is all a layout needs.

    Nearly the handful the old draft used, which asked for
    ``final(pupil_samples=Cartesian2dVectorArray(3, 1), field_samples=1)``
    with ``num_emission_lines = 1``: one field point, one wavelength, and the
    pupil sampled along a single axis.

    Four across the pupil rather than three, because only the rays which reach
    a detector are drawn and the instrument vignettes: it has no mask on the
    primary, and the primary and the grating each clip whatever falls outside
    them. Of three samples one survives, which reads as a line rather than as
    a beam; of four, two do.

    ``centers=True`` matters: the corners of the square in normalized pupil
    coordinates fall outside the pupil, so a grid without it draws nothing but
    vignetted rays, and a single sample has nowhere to sit but an edge.
    """
    return optika.vectors.ObjectVectorArray(
        wavelength=esis.flights.f1.spectrum.O_V.wavelength,
        field=na.Cartesian2dVectorLinearSpace(
            start=-1,
            stop=1,
            axis=na.Cartesian2dVectorArray("field_x", "field_y"),
            num=1,
            centers=True,
        ),
        pupil=na.Cartesian2dVectorLinearSpace(
            start=-1,
            stop=1,
            axis=na.Cartesian2dVectorArray("pupil_x", "pupil_y"),
            num=na.Cartesian2dVectorArray(4, 1),
            centers=True,
        ),
    )


def _channels_populated(
    full: esis.optics.Instrument,
    flown: esis.optics.Instrument,
) -> np.ndarray:
    """
    Which of the available channel positions carried a channel on the flight.

    Read from the two models rather than written down, so that it cannot
    disagree with them.
    """
    azimuth_full = na.value(full.camera.sensor.azimuth).ndarray
    azimuth_flown = na.value(flown.camera.sensor.azimuth).ndarray
    return np.isin(np.round(azimuth_full, 3), np.round(azimuth_flown, 3))


def _active_area(
    sensor: optika.sensors.AbstractImagingSensor,
) -> optika.sensors.AbstractImagingSensor:
    """
    A detector drawn as the silicon which sees light, and nothing else.

    Its mechanical aperture is the package around the silicon, 42 by 61 mm
    against an active area of 30.7 by 15.6, so drawing both puts a second
    rectangle of four times the area around every detector. That outer
    rectangle says nothing about the layout and, six times over around the
    primary, is most of the ink in the drawing.
    """
    return dataclasses.replace(sensor, aperture_mechanical=None)


def _surfaces_drawn(instrument: esis.optics.Instrument) -> tuple:
    """
    The surfaces of the instrument the layout shows.

    The central obscuration and the filters are left out, as they were in the
    old draft: neither says anything about the layout, and both crowd the
    channels where the drawing is already busiest. They are omitted from the
    drawing only, not from the model, so the light is still traced through
    them.
    """
    return (
        instrument.front_aperture.surface,
        instrument.primary_mirror.surface,
        instrument.field_stop.surface,
        instrument.grating.surface,
        _active_area(instrument.camera.surface),
    )


def _millimeters(value: u.Quantity | na.AbstractScalar) -> float:
    """The value in millimeters, as a plain number for :mod:`matplotlib`."""
    return float(getattr(value, "ndarray", value).to_value(u.mm))


def layout() -> aastex.FigureStar:
    """
    The optical layout of ESIS, drawn from the flight model.

    The surfaces of every available channel are drawn, the two which were never
    populated dashed, and one channel is traced with light.
    """
    grid = _grid()
    full = esis.flights.f1.optics.design_full(grid=grid, num_distribution=0)
    flown = esis.flights.f1.optics.design(grid=grid, num_distribution=0)

    populated = _channels_populated(full, flown)

    # brought in before anything asks the instrument for its optical system,
    # which is where the position is read
    flown.front_aperture.translation.z = (
        flown.grating.translation.z - _clearance_entrance
    )

    # The optics are drawn as solids, which only a 3D axes can do: a filled
    # polygon there is sorted by depth, so an optic in front hides what is
    # behind it. Drawn flat, the six gratings overlap into a scribble.
    kwargs_surface = {
        "ax": None,
        "components": _components_view,
        "unit": u.mm,
        "color": "black",
        "linewidth": 0.5,
    }

    # A square figure, cropped to a band on the way out. Matplotlib sizes a 3D
    # axes to hold a cube, so in a short wide figure the instrument comes out
    # small with the width left empty. Drawn square it fills the frame, and the
    # band is what is kept. This is what the old draft did.
    fig = plt.figure(
        figsize=(aastex.text_width_inches, aastex.text_width_inches),
    )
    ax = fig.add_subplot(111, projection="3d")
    ax.set_axis_off()

    # an instrument layout should not be foreshortened
    ax.set_proj_type("ortho")

    kwargs_surface["ax"] = ax

    # the parts of the instrument which flew
    for surface in _surfaces_drawn(flown):
        surface.plot(**kwargs_surface)

    # the light through one of the channels. The whole system is used, so
    # the rays still pass through the filter and the obscuration even
    # though neither is drawn.
    flown.isel(channel=_channel_traced).system.plot(
        plot_rays=True,
        # only the light which reaches a detector. The old draft drew the
        # vignetted rays as well, but a ray clipped at the primary and drawn
        # to the sensor anyway says something about the layout that is not so.
        plot_rays_vignetted=False,
        kwargs_rays={"color": _color_rays, "linewidth": 0.5},
        **(kwargs_surface | {"linewidth": 0, "alpha": 0}),
    )

    # the positions which were available but never populated. Only the
    # surfaces belonging to a channel are drawn, since the primary and the
    # field stop are shared and have already been drawn solid.
    for index in np.nonzero(~populated)[0]:
        channel = full.isel(channel=int(index))
        for surface in (
            channel.grating.surface,
            _active_area(channel.camera.surface),
        ):
            surface.plot(**(kwargs_surface | {"linestyle": _linestyle_unpopulated}))

    _annotate(ax, flown)

    xlim, ylim, zlim = ax.get_xlim(), ax.get_ylim(), ax.get_zlim()
    ax.set_box_aspect(
        (xlim[1] - xlim[0], ylim[1] - ylim[0], zlim[1] - zlim[0]),
        zoom=1.15,
    )
    ax.view_init(elev=_elevation_view, azim=_azimuth_view)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)

    result = aastex.FigureStar("fig:layout", position="!ht")
    result.append(aastex.NoEscape(r"\centering"))
    result.add_fig(
        fig,
        width=aastex.NoEscape(r"\textwidth"),
        bbox_inches=_band(fig),
    )
    plt.close(fig)
    result.add_caption(aastex.NoEscape(r"""
The \ESIS\ optical layout.
Dotted lines indicate the positions of unpopulated channels.
The blue lines represent the path of O V through the system.
The \ESIS\ instrument is a pseudo-Gregorian design.
The secondary mirror is replaced by a segmented array of concave diffraction gratings.
The field stop at prime focus defines instrument spatial/spectral \FOV.
\CCDs\ are arrayed around the primary mirror, each associated with a particular grating.
Eight grating positions are available in principle; only six fit within the volume of the rocket payload.
\NumChannelsWords\ channels are populated for the first flight."""))

    return result


def _annotate(
    ax: mpl_toolkits.mplot3d.Axes3D,
    instrument: esis.optics.Instrument,
) -> None:
    """Label the four parts of the instrument the caption talks about."""
    primary = instrument.primary_mirror
    field_stop = instrument.field_stop
    grating = instrument.grating
    sensor = instrument.camera.sensor

    halfwidth_primary = primary.width_clear / 2 + primary.width_border

    # the detector is sized in micrometres, being a grid of pixels, while the
    # optics are in millimetres
    halfwidth_sensor = instrument.camera.surface.aperture.half_width.x.to(u.mm)

    labels = [
        (
            "primary mirror",
            na.Cartesian3dVectorArray(
                x=halfwidth_primary + 15 * u.mm,
                y=0 * u.mm,
                z=primary.translation.z + 20 * u.mm,
            ),
            {"ha": "right", "va": "bottom"},
        ),
        (
            "detectors",
            na.Cartesian3dVectorArray(
                x=-(sensor.distance_radial + halfwidth_sensor) - 20 * u.mm,
                y=0 * u.mm,
                z=sensor.translation.z + 20 * u.mm,
            ),
            {"ha": "center", "va": "center"},
        ),
        (
            "field stop",
            na.Cartesian3dVectorArray(
                x=-field_stop.radius_mechanical - 5 * u.mm,
                y=0 * u.mm,
                z=field_stop.translation.z,
            ),
            {"ha": "center", "va": "top"},
        ),
        (
            "diffraction gratings",
            na.Cartesian3dVectorArray(
                x=-(grating.distance_radial + grating.halfwidth_outer) - 15 * u.mm,
                y=0 * u.mm,
                z=grating.translation.z - 50 * u.mm,
            ),
            {"ha": "left", "va": "top"},
        ),
    ]

    for text, position, kwargs in labels:
        # the label goes where the part is, in the order the axes are drawn in
        coordinates = [_millimeters(getattr(position, c)) for c in _components_view]
        ax.text(*coordinates, text, fontsize=8, **kwargs)


def _band(fig: plt.Figure, margin: float = 0.06) -> matplotlib.transforms.Bbox:
    """
    The part of the figure the instrument was actually drawn in.

    Matplotlib gives a 3D axes the whole figure whatever it draws, so
    `get_tightbbox` returns everything and `bbox_inches="tight"` crops nothing
    useful. The old draft answered this with a hardcoded band, which is right
    until anything moves. This finds the band by looking at which pixels of the
    rendered figure have anything in them.

    Cropped on all four sides, so the drawing is scaled up to the width of the
    text rather than padded out to it, and is centred in the bargain.
    """
    fig.canvas.draw()
    image = np.asarray(fig.canvas.buffer_rgba())[..., :3]
    inked = (image < 250).any(axis=~0)

    rows = np.nonzero(inked.any(axis=1))[0]
    cols = np.nonzero(inked.any(axis=0))[0]

    width, height = fig.get_size_inches()

    if not len(rows):
        # nothing was drawn, which is worth seeing as a blank figure rather
        # than as an error raised from inside a measurement
        return matplotlib.transforms.Bbox([[0, 0], [width, height]])

    num_rows, num_cols = inked.shape

    # a pixel has a size of its own, so the far edge of the last inked row or
    # column is the outside of that pixel rather than the inside
    top = (1 - rows.min() / num_rows) * height
    bottom = (1 - (rows.max() + 1) / num_rows) * height
    left = (cols.min() / num_cols) * width
    right = ((cols.max() + 1) / num_cols) * width

    pad = margin * (top - bottom)
    return matplotlib.transforms.Bbox(
        [[left - pad, bottom - pad], [right + pad, top + pad]]
    )
