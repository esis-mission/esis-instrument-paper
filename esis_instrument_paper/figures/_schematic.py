import aastex
import astropy.units as u
import esis
import matplotlib.axes
import matplotlib.figure
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np
import optika

__all__ = [
    "schematic",
]

_decimals = 1
"""The number of decimal places every dimension is written to, as in the old draft."""

_unit = u.mm
"""The unit every distance is drawn and written in."""

_linewidth = 1.5
"""The width of the lines the parts are drawn with, as in the old draft."""

_color_mechanical = "gray"
"""The color of the mechanical border around a clear aperture."""

_color_obscuration = "darkgray"
"""The color of the central obscuration."""

_color_footprint = "red"
"""The color of the footprint of the beam of each channel on the primary mirror."""

_alpha_unpopulated = 0.5
"""How opaque the footprint of a channel which did not fly is drawn."""

_kwargs_extension = {"color": "black", "linewidth": 0.5}
"""The extension lines of every dimension, thin and black as in the old draft."""

_kwargs_arrow = {
    "arrowstyle": "->",
    "linewidth": 0.75,
    "relpos": (0.5, 0.5),
    "shrinkA": 2,
    "shrinkB": 2,
}
"""The arrows which point from the name of a part to the part, as in the old draft."""

_num_field = 10
"""
The number of cells along each axis of the field which the footprints on the
primary mirror are traced from.

The footprint of a channel is the hull of every ray which reaches its
detector, so it is set by the rays from the edges of the field, which the
vertices of the cells reach.
"""

_num_pupil = 40
"""
The number of cells along each axis of the pupil which the footprints on the
primary mirror are traced from.

The pupil is the aperture of the grating, so its edge sets the edge of the
footprint. Of the rays at the vertices of the cells, those which fall just
outside the grating are lost, so the footprint is short of its true edge by
up to a cell, a fortieth of the aperture.
"""


def _instrument() -> esis.optics.Instrument:
    """
    A single channel of the flight instrument, as designed.

    The model turns the channel about the optic axis so that it lies in the
    plane of :math:`x` and :math:`z`, which is the plane panel (a) draws.
    """
    return esis.flights.f1.optics.design_single(num_distribution=0)


def _position(
    instrument: esis.optics.Instrument,
    surface: optika.surfaces.Surface,
) -> na.Cartesian3dVectorArray:
    """Where the origin of a surface is, in the coordinates of the drawing."""
    transformation = instrument.system.transformation @ surface.transformation
    return transformation(na.Cartesian3dVectorArray() * _unit)


def _direction(
    instrument: esis.optics.Instrument,
    surface: optika.surfaces.Surface,
) -> u.Quantity:
    """
    The direction the face of a surface runs in panel (a), measured
    counterclockwise from the optic axis.

    It is the direction of the local :math:`x` axis of the surface, which
    lies in the plane of the drawing for every part that is tilted.
    """
    transformation = instrument.system.transformation @ surface.transformation
    zero = transformation(na.Cartesian3dVectorArray() * _unit)
    one = transformation(na.Cartesian3dVectorArray(1, 0, 0) * _unit)
    d = one - zero
    return np.arctan2(d.x, d.z).to(u.deg)


def _vertices(
    aperture: optika.apertures.AbstractPolygonalAperture,
    transformation: None | na.transformations.AbstractTransformation = None,
) -> na.Cartesian2dVectorArray:
    """
    The vertices of an aperture in the frame of its surface, or in another
    frame if a transformation into it is given.

    Each aperture carries a transformation of its own, which places it on
    its surface, and the clear and mechanical apertures of a part are not
    placed the same way.
    """
    result = aperture.vertices
    if aperture.transformation is not None:
        result = aperture.transformation(result)
    if transformation is not None:
        result = transformation(result)
    return result.xy.to(_unit)


def _value(a: u.Quantity | na.AbstractScalar) -> float:
    """A plain number from a scalar, in :data:`_unit` if it has a unit."""
    a = na.as_named_array(a).ndarray
    if isinstance(a, u.Quantity):
        a = a.to_value(_unit)
    return float(a)


def _label(length: u.Quantity | na.AbstractScalar) -> str:
    """A distance written the way :func:`named_arrays.plt.dimension` writes it."""
    length = na.as_named_array(length).to(_unit)
    return na.as_named_array(length.to_string_array(f"%.{_decimals}f")).ndarray.item()


def _channel(ax: matplotlib.axes.Axes) -> None:
    """
    Panel (a): a single channel seen from the side, with the distances between
    its parts and how far each is tilted.
    """
    instrument = _instrument()
    system = instrument.system

    system.plot(
        ax=ax,
        components=("z", "x"),
        plot_rays=False,
        color="black",
        linewidth=_linewidth,
    )

    ax.axhline(linestyle=(0, (20, 10)), linewidth=0.4, color="gray")
    ax.text(x=-500, y=0, s="axis of symmetry", ha="center", va="bottom")

    obscuration = instrument.central_obscuration
    primary = instrument.primary_mirror
    field_stop = instrument.field_stop
    grating = instrument.grating
    filter_ = instrument.filter
    camera = instrument.camera

    position = {
        "obscuration": _position(instrument, obscuration.surface),
        "primary": _position(instrument, primary.surface),
        "field stop": _position(instrument, field_stop.surface),
        "grating": _position(instrument, grating.surface),
        "filter": _position(instrument, filter_.surface),
        "detector": _position(instrument, camera.surface),
    }
    z = {k: _value(v.z) for k, v in position.items()}
    x = {k: _value(v.x) for k, v in position.items()}

    # How far each part reaches up the drawing, which is where the extension
    # lines of the distances along the axis start from.
    halfwidth_grating = _value(grating.halfwidth_outer + grating.width_border)
    top = {
        "obscuration": _value(obscuration.halfwidth),
        "grating": x["grating"] + halfwidth_grating,
        "field stop": _value(field_stop.radius_mechanical),
        "primary": _value(primary.width_clear / 2 + primary.width_border),
        "filter": x["filter"] + _value(filter_.radius_clear),
        "detector": x["detector"] + _value(camera.sensor.width_active.x / 2),
    }

    # The distances along the axis, on two rows high above the drawing, as in
    # the old draft, which leaves room between the parts and the rows for the
    # tilts. Each is measured along the axis only, from the top of one part to
    # the top of the other, so each extension line starts at its own part.
    row_upper = 280
    row_lower = 225

    def axial(a: str, b: str, row: float, label: None | str = None) -> None:
        """Dimension the distance along the axis from part `a` to part `b`."""
        na.plt.dimension(
            a=na.Cartesian2dVectorArray(z[a], top[a]) * _unit,
            b=na.Cartesian2dVectorArray(z[b], top[b]) * _unit,
            offset=(row - top[a]) * _unit,
            label=label,
            decimals=_decimals,
            along="x",
            ax=ax,
            kwargs_extension=_kwargs_extension,
        )

    axial("obscuration", "field stop", row_upper)
    axial("grating", "field stop", row_lower)
    axial("field stop", "primary", row_upper)
    axial("filter", "primary", row_lower, label="")
    axial("primary", "detector", row_upper, label="")

    # The two short distances are written beside their dimension lines, which
    # are too short to hold them, where the old draft wrote them.
    ax.text(
        x=z["filter"] - 8,
        y=row_lower,
        s=_label((z["primary"] - z["filter"]) * _unit),
        ha="right",
        va="center",
    )
    ax.text(
        x=(z["primary"] + z["detector"]) / 2,
        y=row_upper + 8,
        s=_label((z["detector"] - z["primary"]) * _unit),
        ha="center",
        va="bottom",
    )

    # How far each part sits from the axis, dimensioned well to one side of
    # the part, so that the arrows which name the parts pass clear of it. The
    # dimension is measured up from the axis, which serves as its lower
    # extension line, to the height of the part, which is joined to it by an
    # extension line of its own, as in the old draft. The distance from the
    # grating is too short to hold its label, which is written beside it.
    for part, side, label in [
        ("grating", +100, ""),
        ("filter", -150, None),
        ("detector", +120, None),
    ]:
        na.plt.dimension(
            a=na.Cartesian2dVectorArray(z[part] + side, 0) * _unit,
            b=na.Cartesian2dVectorArray(z[part], x[part]) * _unit,
            label=label,
            decimals=_decimals,
            rotate=False,
            along="y",
            ax=ax,
            kwargs_extension=_kwargs_extension,
        )
    ax.text(
        x=z["grating"] + 100 + 8,
        y=x["grating"] / 2,
        s=_label(x["grating"] * _unit),
        ha="left",
        va="center",
    )

    # How far each part is tilted from the vertical. The vertical side of each
    # angle is the extension line of the distance along the axis above the
    # part, and the arc sits halfway up it, as in the old draft. The tilts are
    # a few degrees, too few for an arc to hold arrowheads at this scale, so
    # the arcs are drawn without them, also as in the old draft.
    tilted = [
        ("grating", grating.surface, halfwidth_grating, row_lower, "left"),
        ("filter", filter_.surface, _value(filter_.radius_clear), row_lower, "right"),
        (
            "detector",
            camera.surface,
            _value(camera.sensor.width_active.x / 2),
            row_upper,
            "left",
        ),
    ]
    for part, surface, radius_inner, row, ha in tilted:
        direction = _direction(instrument, surface)
        sign = +1 if ha == "left" else -1
        # The direction carries a rounding error of a few parts in 1e16,
        # enough to write the 3.45 degrees of the filter as 3.4, so the
        # tilt is rounded to a millionth of a degree before it is written.
        tilt = np.round(np.abs(direction - 90 * u.deg).to(u.deg), 6)
        na.plt.dimension_angular(
            center=na.Cartesian2dVectorArray(z[part], x[part]) * _unit,
            radius=((top[part] + row) / 2 - x[part]) * _unit,
            angle_a=90 * u.deg,
            angle_b=direction,
            radius_inner=radius_inner * _unit,
            angle_label=90 * u.deg - sign * 8 * u.deg,
            label=na.as_named_array(tilt).to_string_array(
                f"%.{_decimals}f", pad_unit=""
            ),
            arrowstyle="-",
            ax=ax,
            kwargs_extension=_kwargs_extension,
            kwargs_text={"ha": ha, "backgroundcolor": "none"},
        )

    # The name of each part, below the drawing.
    row_name = -150
    # Where each name is written relative to its part, and the lengths in
    # points of the two vertical arms of its arrow, as in the old draft.
    names = [
        ("obscuration", (z["obscuration"], -top["obscuration"]), 0, None),
        ("grating", (z["grating"], x["grating"] - halfwidth_grating), +150, (15, 15)),
        ("field stop", (z["field stop"], -top["field stop"]), 0, None),
        (
            "filter",
            (z["filter"], x["filter"] - _value(filter_.radius_clear)),
            -100,
            (20, 30),
        ),
        ("primary", (z["primary"] + 15, -top["primary"]), 0, None),
        (
            "detector",
            (z["detector"], 2 * x["detector"] - top["detector"]),
            +100,
            (20, 35),
        ),
    ]
    for name, xy, shift, arms in names:
        arrowprops = dict(_kwargs_arrow)
        if arms is not None:
            arm_a, arm_b = arms
            arrowprops["connectionstyle"] = (
                f"arc,angleA=90,angleB=-90,armA={arm_a},armB={arm_b}"
            )
        ax.annotate(
            text=name,
            xy=xy,
            xytext=(xy[0] + shift, row_name),
            ha="center",
            va="top",
            arrowprops=arrowprops,
        )

    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_xlim(-1480, 300)
    ax.set_ylim(-200, 315)


def _primary(ax: matplotlib.axes.Axes) -> None:
    """
    Panel (b): the primary mirror face on, with its central obscuration and
    the footprint of the beam of each channel.
    """
    single = _instrument()
    flown = esis.flights.f1.optics.design(num_distribution=0)

    # Every position a channel could take, turned the way the single channel
    # is, so that the footprints sit where the beam of panel (a) falls.
    instrument = esis.flights.f1.optics.design_full(num_distribution=0)
    instrument = instrument.replace(roll=single.roll)
    system = instrument.system

    channel = instrument.camera.channel
    populated = np.isin(channel.ndarray, flown.camera.channel.ndarray)

    primary = instrument.primary_mirror
    obscuration = instrument.central_obscuration
    transformation = system.transformation @ primary.surface.transformation
    transformation_obscuration = (
        system.transformation @ obscuration.surface.transformation
    )

    mechanical = _vertices(primary.surface.aperture_mechanical, transformation)
    clear = _vertices(primary.surface.aperture, transformation)
    obscured = _vertices(obscuration.surface.aperture, transformation_obscuration)

    kwargs = {"ax": ax, "axis": "vertex", "edgecolor": "black", "linewidth": _linewidth}
    na.plt.fill(mechanical.x, mechanical.y, facecolor=_color_mechanical, **kwargs)
    na.plt.fill(clear.x, clear.y, facecolor="white", **kwargs)
    na.plt.fill(obscured.x, obscured.y, facecolor=_color_obscuration, **kwargs)

    # The footprint of each channel is the hull of the rays which reach its
    # detector, where they cross the primary mirror.
    surfaces = [surface.name for surface in system.surfaces_all]
    rays = system.raytrace(
        wavelength=esis.flights.f1.spectrum.O_V.wavelength,
        field=na.Cartesian2dVectorLinearSpace(
            start=-1,
            stop=1,
            axis=na.Cartesian2dVectorArray("field_x", "field_y"),
            num=_num_field + 1,
        ),
        pupil=na.Cartesian2dVectorLinearSpace(
            start=-1,
            stop=1,
            axis=na.Cartesian2dVectorArray("pupil_x", "pupil_y"),
            num=_num_pupil + 1,
        ),
        efficiency=False,
    ).outputs
    footprint = na.geometry.convex_hull(
        points=rays.position[{system.axis_surface: surfaces.index("primary")}].xy,
        axis=("field_x", "field_y", "pupil_x", "pupil_y"),
        where=rays.unvignetted[{system.axis_surface: ~0}],
    ).to(_unit)

    halfwidth_mechanical = _value(primary.width_clear / 2 + primary.width_border)
    halfwidth_obscuration = _value(obscuration.halfwidth)
    radius_label = (halfwidth_obscuration + halfwidth_mechanical) / 2
    azimuth = na.as_named_array(instrument.grating.azimuth + single.roll + 180 * u.deg)

    for index in range(channel.shape[instrument.axis_channel]):
        i = {instrument.axis_channel: index}
        alpha = 1 if populated[index] else _alpha_unpopulated
        f = footprint[i]
        na.plt.fill(
            f.x,
            f.y,
            ax=ax,
            axis="vertex",
            facecolor="none",
            edgecolor=_color_footprint,
            alpha=alpha,
        )
        angle = azimuth[i].ndarray
        label = f"Channel {channel[i].ndarray}"
        if not populated[index]:
            label += "\n(inactive)"
        ax.text(
            x=radius_label * np.cos(angle).value,
            y=radius_label * np.sin(angle).value,
            s=label,
            ha="center",
            va="center",
            color=_color_footprint,
            alpha=alpha,
        )

    ax.text(x=0, y=radius_label, s="primary\nclear aperture", ha="center", va="center")
    ax.text(x=0, y=0, s="central\nobscuration", ha="center", va="center")

    # The widths of the octagons, from flat to flat, stacked above the mirror.
    angle = 360 * u.deg / primary.num_folds / 2
    for halfwidth, row in [
        (halfwidth_mechanical, 105),
        (_value(primary.width_clear / 2), 95),
        (halfwidth_obscuration, 85),
    ]:
        height = halfwidth * np.tan(angle).value
        na.plt.dimension(
            a=na.Cartesian2dVectorArray(-halfwidth, height) * _unit,
            b=na.Cartesian2dVectorArray(halfwidth, height) * _unit,
            offset=(row - height) * _unit,
            decimals=_decimals,
            ax=ax,
            kwargs_extension=_kwargs_extension,
        )

    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_xlim(-85, 85)
    ax.set_ylim(-82, 115)


def _grating(ax: matplotlib.axes.Axes) -> None:
    """Panel (c): a grating face on, with its clear and mechanical apertures."""
    surface = _instrument().grating.surface
    clear = _vertices(surface.aperture)
    mechanical = _vertices(surface.aperture_mechanical)

    kwargs = {"ax": ax, "axis": "vertex", "edgecolor": "black", "linewidth": _linewidth}
    na.plt.fill(mechanical.x, mechanical.y, facecolor=_color_mechanical, **kwargs)
    na.plt.fill(clear.x, clear.y, facecolor="white", **kwargs)

    # The vertices run from the inner edge's top, to the outer edge's top and
    # bottom, to the inner edge's bottom.
    def vertex(
        points: na.Cartesian2dVectorArray, index: int
    ) -> na.Cartesian2dVectorArray:
        return points[{"vertex": index}]

    # The lengths of the two apertures, measured along the grating only,
    # from the corner of each at its inner edge to the corner at its outer
    # edge, with the dimension lines stacked above the grating, as in the
    # old draft.
    top = vertex(mechanical, 1).y
    kw = {
        "ax": ax,
        "decimals": _decimals,
        "kwargs_extension": _kwargs_extension,
    }
    for points, row in [(mechanical, 3.5 * _unit), (clear, 1 * _unit)]:
        na.plt.dimension(
            a=vertex(points, 0),
            b=vertex(points, 1),
            offset=top - vertex(points, 0).y + row,
            along="x",
            **kw,
        )

    # The widths of the clear aperture at its outer and inner edges.
    na.plt.dimension(
        a=vertex(clear, 2),
        b=vertex(clear, 1),
        offset=-(vertex(mechanical, 1).x - vertex(clear, 1).x + 5 * _unit),
        rotate=False,
        **kw,
    )
    na.plt.dimension(
        a=vertex(clear, 3),
        b=vertex(clear, 0),
        offset=-4 * _unit,
        rotate=False,
        **kw,
    )

    ax.text(
        x=0.3 * _value(vertex(clear, 1).x),
        y=0,
        s="grating\nclear aperture",
        ha="center",
        va="center",
    )

    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.set_xlim(-15, 21)
    ax.set_ylim(-14, 17)


def schematic() -> aastex.FigureStar:
    """
    A schematic of a single channel and of the mechanical features of the
    primary mirror and the gratings, from the model of the instrument as
    designed.
    """
    fig = plt.figure(
        figsize=(aastex.text_width_inches, 6.6),
        constrained_layout=True,
    )
    upper, lower = fig.subfigures(nrows=2, height_ratios=[3.0, 3.6])
    ax_channel = upper.subplots()
    ax_primary, ax_grating = lower.subplots(ncols=2)

    _channel(ax_channel)
    _primary(ax_primary)
    _grating(ax_grating)

    for ax, label in [(ax_channel, "(a)"), (ax_primary, "(b)"), (ax_grating, "(c)")]:
        ax.text(
            x=0.5,
            y=0,
            s=label,
            transform=ax.transAxes,
            ha="center",
            va="top",
        )

    result = aastex.FigureStar("fig:schematic", position="!htb")
    result.add_fig(fig, width=aastex.NoEscape(r"\textwidth"))
    result.add_caption(aastex.NoEscape(r"""
(a) Schematic diagram of a single channel of the \ESIS\ optical system.
(b) Clear aperture of the primary mirror, size of the central obscuration, and the footprint of the beam for each
channel.
(c) Clear aperture of one diffraction grating."""))

    return result
