"""The design parameters of the instrument, and their measured values."""

import esis
import optika
import pylatex

__all__ = [
    "prescription",
]

_shapes: dict[type, str] = {
    optika.sags.ParabolicSag: "Parabolic",
    optika.sags.SphericalSag: "Spherical",
    optika.apertures.RegularPolygonalAperture: "Octagonal",
    optika.apertures.IsoscelesTrapezoidalAperture: "Trapezoidal",
    optika.apertures.CircularAperture: "Circular",
}
"""The name the table gives each shape of surface and of aperture."""


def _shape(shape: optika.sags.AbstractSag | optika.apertures.AbstractAperture) -> str:
    """
    The name of a shape of surface or of aperture.

    The table names the shapes itself, so a model whose parts are no longer
    the shapes it names is refused rather than described wrongly.
    """
    result = _shapes[type(shape)]
    polygon = optika.apertures.RegularPolygonalAperture
    if isinstance(shape, polygon) and shape.num_vertices != 8:
        raise ValueError(f"a polygon of {shape.num_vertices} sides is not octagonal")
    return result


def prescription() -> pylatex.Table:
    """
    The design parameters of each part of the instrument, with the measured
    value beside each one that was measured.

    The numbers are the variables of :func:`esis_instrument_paper.variables`,
    so that the table and the prose quote the same ones. Where a design
    parameter was not measured, it stands alone.
    """
    design = esis.flights.f1.optics.design_single(num_distribution=0)
    primary = design.primary_mirror.surface
    field_stop = design.field_stop.surface
    grating = design.grating.surface
    filter = design.filter.surface

    if not isinstance(
        grating.rulings.spacing, optika.rulings.Polynomial1dRulingSpacing
    ):
        raise TypeError("the rulings of the gratings are not a polynomial in position")

    components = {
        "Primary": [
            ("Surface shape", _shape(primary.sag)),
            ("Focal length", r"\primaryFocalLength"),
            ("Aperture shape", _shape(primary.aperture)),
            ("Aperture diameter", r"\primaryDiameter"),
            ("Coating", r"\SiCShort\ single layer, optimized for \OV"),
            (
                r"Efficiency (\OV)",
                r"\primaryEfficiency\ (\primaryEfficiencyMeasured)",
            ),
        ],
        "Field stop": [
            ("Sky plane diameter", r"\fov"),
            ("Aperture shape", _shape(field_stop.aperture)),
            ("Aperture diameter", r"\fieldStopDiameter"),
        ],
        r"Gratings (\numChannels)": [
            ("Surface shape", _shape(grating.sag)),
            ("Surface radius", r"\gratingRadius\ (\gratingRadiusMeasured)"),
            ("Aperture shape", _shape(grating.aperture)),
            ("Aperture height", r"\gratingHeight"),
            ("Aperture long base", r"\gratingLongWidth"),
            ("Aperture short base", r"\gratingShortWidth"),
            ("Ruling type", "Varied line spacing"),
            (
                "Constant ruling spacing coefficient",
                r"\gratingRulingSpacing\ (\gratingRulingSpacingMeasured)",
            ),
            (
                "Linear ruling spacing coefficient",
                r"\gratingLinearRulingSpacingCoefficient",
            ),
            (
                "Quadratic ruling spacing coefficient",
                r"\gratingQuadraticRulingSpacingCoefficient",
            ),
            ("Input angle", r"\gratingInputAngle"),
            (r"Output angle (\OV)", r"\gratingOutputAngle"),
            ("Manufacturing process", "Individual master gratings"),
            (
                "Coating",
                r"\MgShort/\SiCShort/\AlShort\ multilayer, optimized for \OV",
            ),
            (
                r"Groove efficiency (\OV)",
                r"\modeledGratingGrooveEfficiency\ (\gratingGrooveEfficiencyMeasured)",
            ),
            (
                r"Efficiency (\OV)",
                r"\gratingEfficiency\ (\gratingEfficiencyMeasured)",
            ),
        ],
        r"Filters (\numChannels)": [
            ("Aperture shape", _shape(filter.aperture)),
            ("Aperture diameter", r"\filterDiameter"),
            ("Material", r"\AlShort"),
            ("Thickness", r"\filterThickness"),
            ("Mesh transmission", r"\filterMeshRatio"),
            ("Mesh material", r"\NiShort"),
            (r"Efficiency (\OV)", r"\filterEfficiency"),
        ],
        r"Detectors (\numChannels)": [
            ("Manufacturer", r"\detectorManufacturer"),
            ("Model", r"\detectorName"),
            ("Active area", r"\detectorPixelsX\ $\times$ \detectorPixelsY"),
            ("Pixel size", r"\detectorPixelSize"),
            (r"Quantum efficiency (\OV)", r"\detectorQuantumEfficiencyOV"),
            ("Minimum cadence", r"\detectorExposureLengthMin"),
        ],
        "System": [
            ("Magnification", r"\armRatio"),
            ("$f$-number", r"\fNumber"),
            ("Plate scale along dispersion", r"\plateScaleDispersion"),
            ("Plate scale across dispersion", r"\plateScaleCrossDispersion"),
            ("Dispersion", r"\dispersion\ (\dispersionDoppler)"),
            ("Passband", r"\minWavelength\ to \maxWavelength"),
            (r"Efficiency (\OV)", r"\totalEfficiency"),
        ],
    }

    result = pylatex.Table(position="!htb")
    result._star_latex_name = True

    result.add_caption(pylatex.NoEscape(r"\ESIS\ design parameters."))

    with (
        result.create(pylatex.Center()) as centering,
        centering.create(pylatex.Tabular(table_spec="lll")) as tabular,
    ):
        tabular.escape = False
        tabular.add_row(["Component", "Parameter", "Calculated value (measured value)"])
        for component, rows in components.items():
            tabular.add_hline()
            for index, (parameter, value) in enumerate(rows):
                tabular.add_row([component if index == 0 else "", parameter, value])
        tabular.add_hline()

    result.append(pylatex.Label("table:prescription"))

    return result
