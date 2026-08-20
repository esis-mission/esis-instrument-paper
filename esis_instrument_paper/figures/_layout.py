import aastex
import astropy.units as u
import esis
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np
import optika
from astropy.visualization import quantity_support

__all__ = [
    "layout",
]

_angle_view = 40 * u.deg
"""
The angle the instrument is turned through before it is drawn.

The old draft viewed a 3D axes with ``view_init(elev=0, azim=-40)`` and its
components mapped as ``x->y, y->z, z->x``. Under an orthographic projection
that is exactly a rotation of this angle about the optical axis, drawn as the
``("z", "x")`` components: matplotlib projects :math:`y` and :math:`x` onto the
horizontal in the ratio :math:`\\tan 40^\\circ`, and leaves :math:`x` alone on
the vertical.
"""

_color_rays = "tab:blue"
"""The colour of the light traced through the instrument."""

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

    ``centers=True`` matters: the corners of the square in normalized pupil
    coordinates fall outside the pupil, so a grid without it draws nothing but
    vignetted rays.
    """
    return optika.vectors.ObjectVectorArray(
        wavelength=esis.flights.f1.spectrum.O_V.wavelength,
        field=na.Cartesian2dVectorLinearSpace(
            start=-1,
            stop=1,
            axis=na.Cartesian2dVectorArray("field_x", "field_y"),
            num=2,
            centers=True,
        ),
        pupil=na.Cartesian2dVectorLinearSpace(
            start=-1,
            stop=1,
            axis=na.Cartesian2dVectorArray("pupil_x", "pupil_y"),
            num=na.Cartesian2dVectorArray(3, 1),
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


def _components_drawn(instrument: esis.optics.Instrument) -> tuple:
    """
    The parts of the instrument the layout shows.

    The central obscuration and the filters are left out, as they were in the
    old draft: neither says anything about the layout, and both crowd the
    channels where the drawing is already busiest. They are omitted from the
    drawing only, not from the model, so the light is still traced through
    them.
    """
    return (
        instrument.front_aperture,
        instrument.primary_mirror,
        instrument.field_stop,
        instrument.grating,
        instrument.camera,
    )


def _millimeters(value: u.Quantity | na.AbstractScalar) -> float:
    """The value in millimeters, as a plain number for :mod:`matplotlib`."""
    return float(getattr(value, "ndarray", value).to_value(u.mm))


def _project(
    position: na.Cartesian3dVectorArray,
    transformation: na.transformations.AbstractTransformation,
) -> tuple[float, float]:
    """Turn a position in the instrument into a point on the page."""
    result = transformation(position)
    return _millimeters(result.z), _millimeters(result.x)


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
    transformation = na.transformations.Cartesian3dRotationX(_angle_view)

    kwargs_surface = {
        "ax": None,
        "transformation": transformation,
        "components": ("z", "x"),
        "color": "black",
        "linewidth": 0.5,
    }

    with quantity_support():
        fig, ax = plt.subplots(
            figsize=(aastex.text_width_inches, 0.34 * aastex.text_width_inches),
            constrained_layout=True,
        )
        ax.set_axis_off()
        ax.set_aspect("equal")
        kwargs_surface["ax"] = ax

        # the parts of the instrument which flew
        for component in _components_drawn(flown):
            component.surface.plot(**kwargs_surface)

        # the light through one of the channels. The whole system is used, so
        # the rays still pass through the filter and the obscuration even
        # though neither is drawn.
        flown.isel(channel=1).system.plot(
            plot_rays=True,
            kwargs_rays={"color": _color_rays, "linewidth": 0.5},
            **(kwargs_surface | {"linewidth": 0, "alpha": 0}),
        )

        # the positions which were available but never populated. Only the
        # surfaces belonging to a channel are drawn, since the primary and the
        # field stop are shared and have already been drawn solid.
        for index in np.nonzero(~populated)[0]:
            channel = full.isel(channel=int(index))
            for component in (channel.grating, channel.camera):
                component.surface.plot(
                    **(kwargs_surface | {"linestyle": _linestyle_unpopulated})
                )

        _annotate(ax, flown, transformation)

        result = aastex.FigureStar("fig:layout", position="!ht")
        result.append(aastex.NoEscape(r"\centering"))
        result.add_fig(fig, width=None)
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
    ax: plt.Axes,
    instrument: esis.optics.Instrument,
    transformation: na.transformations.AbstractTransformation,
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
        x, y = _project(position, transformation)
        ax.text(x=x, y=y, s=text, fontsize=8, **kwargs)
