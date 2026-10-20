import collections.abc

import aastex
import astropy.time
import astropy.units as u
import esis
import named_arrays as na
import num2words
import numpy as np
import optika
import pylatex

import esis_instrument_paper
from esis_instrument_paper import _alignment, _error_budget

__all__ = [
    "variables",
]


def variables() -> list[aastex.Variable]:
    """
    A list of LaTeX variables for every numeric quantity cited in the prose.

    Reference these macros in section strings instead of hardcoding numbers so
    that the text stays in sync with the instrument model.

    A few of these are still literals, since the model does not carry the
    quantity they describe: two which belong to MOSES or to the payload
    rather than to the instrument, the allocations of the error budget to the
    figure of the optics, and the spectroscopic name of each emission line,
    whose wavelength the model does carry.
    """
    design = esis.flights.f1.optics.design()

    # `design` is the flight instrument, whose four channels were populated
    # from the six positions of `design_full`.
    num_channels = design.camera.channel.shape[design.axis_channel]

    # the performance the mission required of the instrument, as opposed to
    # the performance the instrument achieved
    requirements = esis.flights.f1.optics.requirements()

    # One channel of the flight instrument. The field of view and the
    # dispersion belong to a channel rather than to the set of them, and the
    # nominal model is used rather than a Monte Carlo population, so that
    # neither carries an axis of its own.
    channel = esis.flights.f1.optics.design_single(num_distribution=0)

    # The traced outline of the field, which for an octagonal field stop is
    # wider corner to corner than edge to edge by a factor of
    # 1 / cos(22.5 degrees). This group means edge to edge when it says field
    # of view, which is twice the least distance from the centre of the field
    # to its outline.
    boundary = channel.system.field_boundary
    fov = 2 * boundary.length.min(channel.system.axis_stops)

    # The observing time is taken from the flight timeline, as the span over
    # which the rate gyros held the payload pointed. The 30 exposures of the
    # Level 1 data sit inside it, beginning 12 seconds after it opens and
    # ending as it closes.
    timeline = esis.flights.f1.nsroc.timeline()
    length_observation = (
        timeline.timedelta_sparcs_rlg_disable - timeline.timedelta_sparcs_rlg_enable
    )

    return [
        # TODO: this describes MOSES rather than ESIS, so it is not something
        # the ESIS model can supply.
        aastex.Variable(
            name="mosesDispersionDoppler",
            value=29 * u.km / u.s / u.pix,
        ),
        # TODO: the current model carries neither of these; they are the 22
        # inch and 3 metre values from the old model and the old draft.
        aastex.Variable(
            # Two decimals, where the old draft gave one. The old draft then
            # wrote the same quantity out again, to two decimals, where it
            # described the skin sections, and so said 0.6 m in one place and
            # 0.56 m in another. One of them is enough.
            name="skinDiameter",
            value=round((22 * u.imperial.inch).to_value(u.m), 2) * u.m,
        ),
        aastex.Variable(
            name="skinLength",
            value=3 * u.m,
        ),
        aastex.Variable(
            name="numChannels",
            value=num_channels,
        ),
        aastex.Variable(
            name="numChannelsWords",
            value=aastex.NoEscape(num2words.num2words(num_channels)),
        ),
        # the same word capitalised, for a sentence which opens with it
        aastex.Variable(
            name="NumChannelsWords",
            value=aastex.NoEscape(num2words.num2words(num_channels).capitalize()),
        ),
        aastex.Variable(
            name="OVwavelength",
            value=esis.flights.f1.spectrum.O_V.wavelength,
        ),
        # The model carries the wavelength of each line but not its name, so
        # the spectroscopic notation is written here.
        aastex.Variable(
            name="OVion",
            value=aastex.NoEscape(r"O\,\textsc{v}"),
        ),
        aastex.Variable(
            name="MgXion",
            value=aastex.NoEscape(r"Mg\,\textsc{x}"),
        ),
        aastex.Variable(
            name="OV",
            value=aastex.NoEscape(r"\OVion~\OVwavelength"),
        ),
        aastex.Variable(
            name="spatialResolutionRequirement",
            value=requirements.resolution_spatial,
        ),
        aastex.Variable(
            name="angularResolutionRequirement",
            value=requirements.resolution_angular.round(1),
        ),
        aastex.Variable(
            name="spectralResolutionRequirement",
            value=requirements.resolution_spectral,
        ),
        aastex.Variable(
            name="fovRequirement",
            value=requirements.fov,
        ),
        aastex.Variable(
            # a plain number rather than the dimensionless quantity it is in
            # the model, which would otherwise be set with an empty unit
            name="snrRequirement",
            value=float(requirements.snr),
        ),
        aastex.Variable(
            name="cadenceRequirement",
            value=requirements.cadence,
        ),
        aastex.Variable(
            name="observingTimeRequirement",
            value=requirements.length_observation,
        ),
        aastex.Variable(
            name="detectorExposureLength",
            value=design.camera.timedelta_exposure,
        ),
        aastex.Variable(
            name="HeIion",
            value=aastex.NoEscape(r"He\,\textsc{i}"),
        ),
        aastex.Variable(
            name="fov",
            value=fov.ndarray.to(u.arcmin).round(1),
        ),
        aastex.Variable(
            # The dispersion varies by about a percent across the passband,
            # and its Doppler equivalent by ten times that, so it is quoted
            # at the line the instrument was designed around rather than
            # averaged over the passband.
            name="dispersionDoppler",
            value=channel.dispersion_doppler(
                wavelength=esis.flights.f1.spectrum.O_V.wavelength,
            ).ndarray.round(1),
            # astropy orders the bases of a composite unit itself, which puts
            # the pixels before the seconds; this is the order it is read in,
            # and the order the requirement beside it is written in
            unit=(u.km, u.s**-1, u.pix**-1),
        ),
        aastex.Variable(
            # The magnification with which a grating images the field stop
            # onto its detector, apart from the anamorphic magnification of
            # the grating and the tilt of the detector. Two decimals: the
            # figure it is quoted beside shows the two outlines a few percent
            # apart, and the third decimal is a tenth of a percent.
            name="armRatio",
            value=round(
                float(channel.magnification.ndarray.to(u.dimensionless_unscaled).value),
                2,
            ),
        ),
        aastex.Variable(
            # The wavelength the distortion model measures its wavelengths
            # from, which is the mean of the lines it was fit at, since the fit
            # centers its inputs on the mean of its samples. Quoted to the
            # hundredth of an angstrom, as the titles of the vignetting and the
            # distortion figures give the lines.
            name="distortionWavelength",
            value=esis_instrument_paper._distortion_model.model()
            .fit.center.wavelength.ndarray.to(u.AA)
            .round(2),
        ),
        aastex.Variable(
            name="observingTime",
            value=length_observation.round(1),
        ),
        aastex.Variable(
            # the number of emission lines drawn in the bunch figure
            name="numEmissionLines",
            value=aastex.NoEscape(
                num2words.num2words(esis_instrument_paper.figures.num_emission_lines)
            ),
        ),
        aastex.Variable(
            # the pressure the quiet sun spectrum is computed at
            name="chiantiPressure",
            value=esis_instrument_paper._spectrum.pressure,
        ),
        aastex.Variable(
            # The files the spectrum was computed from, named rather than
            # described, so that the article says which of the several
            # abundance tables and several differential emission measures
            # CHIANTI carries were the ones read.
            name="chiantiAbundances",
            # `Command` escapes its argument, which these names need: an
            # underscore outside of mathematics is a subscript and does not
            # compile, and every one of these file names has several.
            value=aastex.NoEscape(
                pylatex.Command(
                    "texttt",
                    esis_instrument_paper._spectrum.abundance,
                ).dumps()
            ),
        ),
        aastex.Variable(
            name="chiantiDEM",
            value=aastex.NoEscape(
                pylatex.Command(
                    "texttt",
                    esis_instrument_paper._spectrum.dem,
                ).dumps()
            ),
        ),
        aastex.Variable(
            # Read from the database rather than written down, since which
            # version is installed is what the numbers were computed from,
            # and the two would otherwise drift apart silently. The lines in
            # the passband move by a few percent between versions.
            name="chiantiVersion",
            value=aastex.NoEscape(esis_instrument_paper._spectrum.version()),
        ),
        *_optics(),
        *_optimization(),
        *_coatings(),
        *_sensitivity(),
        *_alignment_and_focus(),
        *_cameras(),
    ]


def _formula(layer: optika.materials.Layer) -> str:
    """The chemical formula of a layer, which its acronym is named after."""
    chemical = layer.chemical
    if isinstance(chemical, str):
        return chemical
    return chemical.formula


def _formulas(stack: optika.materials.MultilayerMirror) -> list[str]:
    """The chemical formula of every layer of a coating, from the top down."""
    layers = optika.materials.LayerSequence(stack.layers).layers_
    return [_formula(layer) for layer in layers]


def _layer(
    stack: optika.materials.MultilayerMirror,
    formula: str,
) -> optika.materials.Layer:
    """
    The one layer of a coating made of the given material.

    The prose names the materials of each coating, so a model with more than
    one layer of a material it names, or none, is no longer the coating the
    prose describes. This refuses rather than quote the wrong layer.
    """
    layers = optika.materials.LayerSequence(stack.layers).layers_
    result = [layer for layer in layers if _formula(layer) == formula]
    if len(result) != 1:
        raise ValueError(
            f"expected one layer of {formula}, the model has {len(result)}"
        )
    return result[0]


def _channels(
    instrument: esis.optics.Instrument,
    manufacturing_numbers: collections.abc.Container[str],
    inverse: bool = False,
) -> list[int]:
    """
    The names of the channels whose gratings are among the given
    manufacturing numbers, or, if `inverse`, are not.
    """
    axis = instrument.axis_channel
    numbers = instrument.grating.manufacturing_number
    result = []
    for index in range(numbers.shape[axis]):
        i = {axis: index}
        if (str(numbers[i].ndarray) in manufacturing_numbers) != inverse:
            result.append(int(instrument.camera.channel[i].ndarray))
    return result


def _reflectance(
    material: optika.materials.AbstractMaterial,
    wavelength: u.Quantity | na.AbstractScalar,
    angle: u.Quantity | na.AbstractScalar,
) -> na.AbstractScalar:
    """The efficiency of a mirror material at an angle of incidence."""
    rays = optika.rays.RayVectorArray(
        wavelength=wavelength,
        direction=na.Cartesian3dVectorArray(np.sin(angle), 0, np.cos(angle)),
    )
    return material.efficiency(rays, na.Cartesian3dVectorArray(0, 0, -1))


def _grooves(
    rulings: optika.rulings.AbstractRulings,
    wavelength: u.Quantity | na.AbstractScalar,
) -> na.AbstractScalar:
    """
    The efficiency of the grooves of a grating at normal incidence.

    The coating subsection predicts the efficiency of a grating from the
    grooves the optics subsection quotes, so both quote them from here.
    """
    rays = optika.rays.RayVectorArray(
        wavelength=wavelength,
        position=na.Cartesian3dVectorArray() * u.mm,
        direction=na.Cartesian3dVectorArray(0, 0, 1),
    )
    return rulings.efficiency(rays, na.Cartesian3dVectorArray(0, 0, -1))


def _fixed(value: u.Quantity, decimals: int) -> aastex.NoEscape:
    """
    A quantity written to a fixed number of decimals.

    :class:`aastex.Variable` writes a quantity as :mod:`astropy` prints it,
    which drops the zeros at the end, so that a plate scale of 0.770 reads as
    0.77 beside one of 0.734.
    """
    result = value.to_string(format="latex_inline", formatter=f".{decimals}f")
    return aastex.NoEscape(rf"\ensuremath{{{result[1:~0]}}}")


def _significant(value: u.Quantity, digits: int) -> u.Quantity:
    """A quantity rounded to a number of significant digits."""
    exponent = int(np.floor(np.log10(np.abs(value.value))))
    return value.round(digits - 1 - exponent)


def _percent(fraction: na.AbstractScalar, decimals: int = 0) -> u.Quantity:
    """A fraction written as a percentage, rounded."""
    fraction = na.as_named_array(fraction).ndarray
    return (fraction * u.dimensionless_unscaled).to(u.percent).round(decimals)


def _series(items: collections.abc.Sequence[object]) -> aastex.NoEscape:
    """A list written out in a sentence, such as 1, 2, 3, and 4."""
    items = [str(item) for item in items]
    return aastex.NoEscape(", ".join(items[:-1]) + f", and {items[-1]}")


def _date(time: astropy.time.Time) -> aastex.NoEscape:
    """A day written as the journal writes dates, such as 2018 January 21."""
    date = time.to_datetime()
    return aastex.NoEscape(f"{date.year} {date:%B} {date.day}")


def _optics() -> list[aastex.Variable]:
    """
    The variables cited by the subsection on the optics and by the table of
    the design parameters.

    Each design parameter is taken from a single channel as designed, and its
    measured counterpart, where there is one, from the instrument that flew.
    Efficiencies are at the O V line, at normal incidence.
    """
    f1 = esis.flights.f1
    spectrum = f1.spectrum
    wavelength = spectrum.O_V.wavelength
    normal = 0 * u.deg

    design = f1.optics.design_single(num_distribution=0)
    as_built = esis_instrument_paper._counts.optics()

    grating = design.grating

    # The measured radius of each grating, quoted as the middle of their
    # range plus or minus half of it, as the old draft quoted them.
    radius = np.abs(na.as_named_array(as_built.grating.sag.radius).ndarray)
    radius_center = (radius.max() + radius.min()) / 2
    radius_spread = (radius.max() - radius.min()) / 2

    # The clear aperture of a grating is an isosceles trapezoid whose legs
    # meet at the axis of the instrument, so its width at a distance from
    # that apex is twice the distance times the tangent of half the angle
    # between the legs.
    aperture = grating.surface.aperture
    height = aperture.x_right - aperture.x_left
    tangent = np.tan(aperture.angle / 2)

    spacing = grating.rulings.spacing.coefficients
    spacing_measured = as_built.grating.rulings.spacing.coefficients

    # A flight grating itself, coating and grooves together, in first order.
    efficiency = f1.optics.gratings.efficiencies.efficiency_vs_wavelength()
    efficiency_grating = na.interp(
        x=wavelength,
        xp=efficiency.inputs.wavelength,
        fp=efficiency.outputs,
    )

    # a filter transmits, and its efficiency is computed as a mirror's is
    efficiency_filter = _reflectance(design.filter.material, wavelength, normal)

    efficiency_primary = _reflectance(
        as_built.primary_mirror.material, wavelength, normal
    )
    efficiency_sensor = as_built.camera.sensor.material.quantum_efficiency_effective(
        wavelength
    )

    # The beam converging on the detector is as long as the exit arm of the
    # grating, which is the stop, and as wide as the grating is tall, as the
    # old draft took it.
    f_number = design.distance_grating_output / height

    plate_scale = design.system.plate_scale(wavelength).to(u.arcsec / u.pix)

    return [
        aastex.Variable(
            name="primaryFocalLength",
            value=_fixed(np.abs(design.primary_mirror.sag.focal_length), 1),
        ),
        aastex.Variable(
            # edge to edge, as the field stop is measured
            name="primaryDiameter",
            value=design.primary_mirror.width_clear.round(),
        ),
        aastex.Variable(
            name="primaryEfficiency",
            value=_percent(
                _reflectance(design.primary_mirror.material, wavelength, normal)
            ),
        ),
        aastex.Variable(
            # the coating fitted to the witness, on the substrate of the mirror
            name="primaryEfficiencyMeasured",
            value=_percent(efficiency_primary),
        ),
        aastex.Variable(
            name="fieldStopDiameter",
            value=design.field_stop.width_clear.round(3),
        ),
        aastex.Variable(
            name="gratingRadius",
            value=_fixed(np.abs(grating.sag.radius), 3),
        ),
        aastex.Variable(
            name="gratingRadiusMeasured",
            value=aastex.NoEscape(
                rf"\ensuremath{{{radius_center.to_value(u.mm):.3f}"
                rf"\pm{radius_spread.to_value(u.mm):.3f}\,\mathrm{{mm}}}}"
            ),
        ),
        aastex.Variable(
            name="gratingHeight",
            value=height.round(1),
        ),
        aastex.Variable(
            name="gratingLongWidth",
            value=(2 * aperture.x_right * tangent).round(1),
        ),
        aastex.Variable(
            name="gratingShortWidth",
            value=(2 * aperture.x_left * tangent).round(1),
        ),
        aastex.Variable(
            name="gratingRulingSpacing",
            value=spacing[0].to(u.um).round(5),
        ),
        aastex.Variable(
            name="gratingRulingSpacingMeasured",
            value=spacing_measured[0].to(u.um).round(5),
        ),
        aastex.Variable(
            name="gratingLinearRulingSpacingCoefficient",
            value=_significant(spacing[1], 4),
            unit=(u.um, u.mm**-1),
        ),
        aastex.Variable(
            name="gratingQuadraticRulingSpacingCoefficient",
            value=_significant(spacing[2], 4),
            unit=(u.um, u.mm**-2),
        ),
        aastex.Variable(
            name="gratingInputAngle",
            value=grating.angle_input,
        ),
        aastex.Variable(
            name="gratingOutputAngle",
            value=grating.angle_output,
        ),
        aastex.Variable(
            name="modeledGratingGrooveEfficiency",
            value=_percent(_grooves(grating.rulings, wavelength)),
        ),
        aastex.Variable(
            # the grooves of the flight gratings are inferred from the
            # efficiency of one of them, over the efficiency of its coating
            name="gratingGrooveEfficiencyMeasured",
            value=_percent(_grooves(as_built.grating.rulings, wavelength)),
        ),
        aastex.Variable(
            name="gratingEfficiencyMeasured",
            value=_percent(efficiency_grating),
        ),
        aastex.Variable(
            name="filterDiameter",
            value=_fixed(2 * design.filter.radius_clear, 1),
        ),
        aastex.Variable(
            name="filterEfficiency",
            value=_percent(efficiency_filter),
        ),
        aastex.Variable(
            name="detectorPixelSize",
            value=design.camera.sensor.width_pixel.round(),
        ),
        aastex.Variable(
            name="fNumber",
            value=aastex.NoEscape(
                f"$f$/{round(float(na.as_named_array(f_number).ndarray))}"
            ),
        ),
        aastex.Variable(
            name="plateScaleDispersion",
            value=_fixed(plate_scale.x.ndarray, 3),
        ),
        aastex.Variable(
            name="plateScaleCrossDispersion",
            value=_fixed(plate_scale.y.ndarray, 3),
        ),
        aastex.Variable(
            name="dispersion",
            value=design.dispersion(wavelength).ndarray.round(1),
            unit=(u.mAA, u.pix**-1),
        ),
        aastex.Variable(
            name="minWavelength",
            value=design.wavelength_min.ndarray.round(2),
        ),
        aastex.Variable(
            name="maxWavelength",
            value=design.wavelength_max.ndarray.round(2),
        ),
        aastex.Variable(
            name="MgXwavelength",
            value=spectrum.Mg_X.wavelength,
        ),
        aastex.Variable(
            # The efficiency of a channel at the O V line: the product of the
            # efficiencies of its parts, each the measured value where there
            # is one.
            name="totalEfficiency",
            value=_fixed(
                _percent(
                    efficiency_primary
                    * efficiency_grating
                    * efficiency_filter
                    * efficiency_sensor,
                    decimals=2,
                ),
                2,
            ),
        ),
    ]


def _coatings() -> list[aastex.Variable]:
    """
    The variables cited by the subsection on the coatings and the filters.

    Where a measurement exists it is used, and a model only stands in for a
    measurement which does not reach the wavelength asked about.
    """
    f1 = esis.flights.f1
    spectrum = f1.spectrum
    gratings = f1.optics.gratings
    primaries = f1.optics.primaries

    # one channel as designed, for the passband and the placement of the
    # filter, and the flight instrument, for which grating flew where
    design = f1.optics.design_single(num_distribution=0)
    as_built = f1.optics.as_built(num_distribution=0)

    # The prose describes the grating coating as pairs of SiC and Mg, with Al
    # beside each Mg layer, and names those materials itself.
    formulas = _formulas(gratings.materials.multilayer_design())
    num_pairs = formulas.count("Mg")
    is_pairs = formulas.count("SiC") == num_pairs
    if not is_pairs or not set(formulas) <= {"SiO2", "SiC", "Al", "Mg"}:
        raise ValueError(f"the grating coating is not SiC/Mg pairs: {formulas}")

    # The witnesses are silicon wafers coated alongside three of the flight
    # gratings, so they measure the coating without the grooves. They are the
    # only measurement which reaches down to He II.
    witness = gratings.materials.multilayer_witness_measured()
    measured = witness.efficiency_measured
    angle_witness = measured.inputs.direction
    inside = (measured.inputs.wavelength >= design.wavelength_min) & (
        measured.inputs.wavelength <= design.wavelength_max
    )
    reflectance_peak = np.where(inside, measured.outputs, 0).max()
    reflectance_ov = _reflectance(witness, spectrum.O_V.wavelength, angle_witness)
    ratio_grating = (
        _reflectance(witness, spectrum.He_II.wavelength, angle_witness) / reflectance_ov
    ).mean()

    # The first-order efficiency the prose predicts, and then confirms against
    # a measurement of a flight grating: the measured reflectance of the
    # coating, times the efficiency of the designed grooves at normal
    # incidence. The grooves of `as_built` are derived from that measurement,
    # so they cannot predict it.
    grooves = _grooves(design.grating.surface.rulings, spectrum.O_V.wavelength)
    efficiency_predicted = reflectance_ov.mean() * grooves

    # The primary witness was measured only down to 450 A, so at He II the
    # coating fitted to it, moved onto the substrate of the mirror, stands in.
    primary = primaries.materials.multilayer_fit()
    witness_primary = primaries.materials.multilayer_witness_measured()
    angle_primary = witness_primary.efficiency_measured.inputs.direction
    ratio_primary = _reflectance(
        primary, spectrum.He_II.wavelength, angle_primary
    ) / _reflectance(primary, spectrum.O_V.wavelength, angle_primary)
    ratio = na.as_named_array(ratio_grating * ratio_primary).ndarray
    rejection = -10 * np.log10(ratio) * u.dB

    # A flight grating itself, coating and grooves together, in first order.
    # Its scans across angle and position were all made at one wavelength.
    efficiency = gratings.efficiencies.efficiency_vs_wavelength()
    scan = gratings.efficiencies.efficiency_vs_angle_0deg()
    (channel_tested,) = _channels(as_built, [gratings.efficiencies.serial_number])
    (channel_missing,) = _channels(
        as_built, witness.serial_number.ndarray, inverse=True
    )

    # The recoated primary: a chromium base for adhesion under the SiC.
    primary_design = primaries.materials.multilayer_design()
    if not set(_formulas(primary_design)) <= {"SiO2", "SiC", "Cr"}:
        raise ValueError("the primary coating is not SiC over Cr")

    # The filter is a thin film of Al on a Ni mesh, which the prose names.
    material = design.filter.material
    if _formula(material.layer) != "Al" or material.mesh.chemical != "Ni":
        raise ValueError("the filter is not Al on a Ni mesh")

    # The filter is round, so its roll orients nothing but its mesh, and the
    # mesh is clocked against the pixels by the difference in roll.
    clocking = design.filter.roll - design.camera.sensor.roll
    distance = design.camera.sensor.translation.z - design.filter.translation.z

    return [
        aastex.Variable(
            name="HeIwavelength",
            value=spectrum.He_I.wavelength,
        ),
        aastex.Variable(
            name="HeI",
            value=aastex.NoEscape(r"\HeIion~\HeIwavelength"),
        ),
        aastex.Variable(
            name="HeIIion",
            value=aastex.NoEscape(r"He\,\textsc{ii}"),
        ),
        aastex.Variable(
            name="HeIIwavelength",
            value=spectrum.He_II.wavelength,
        ),
        aastex.Variable(
            name="HeII",
            value=aastex.NoEscape(r"\HeIIion~\HeIIwavelength"),
        ),
        aastex.Variable(
            name="gratingCoatingNumLayers",
            value=num_pairs,
        ),
        aastex.Variable(
            name="gratingCoatingNumLayersWords",
            value=aastex.NoEscape(num2words.num2words(num_pairs)),
        ),
        aastex.Variable(
            name="gratingWitnessEfficiency",
            value=_percent(reflectance_peak),
        ),
        aastex.Variable(
            name="gratingEfficiency",
            value=_percent(efficiency_predicted),
        ),
        aastex.Variable(
            name="gratingHeIIRejectionRatio",
            value=_percent(ratio_grating, decimals=1),
        ),
        aastex.Variable(
            name="totalHeIIRejection",
            value=rejection.round(),
        ),
        aastex.Variable(
            name="primaryCoatingBaseThickness",
            value=_layer(primary_design, "Cr").thickness,
        ),
        aastex.Variable(
            name="primaryCoatingThickness",
            value=_layer(primary_design, "SiC").thickness,
        ),
        aastex.Variable(
            name="filterThickness",
            value=material.layer.thickness,
        ),
        aastex.Variable(
            name="filterOxideThickness",
            value=material.layer_oxide.thickness,
        ),
        aastex.Variable(
            # a plain number, since the prose reads it as lines per inch
            name="filterMeshPitch",
            value=round(material.mesh.pitch.to_value(1 / u.imperial.inch)),
        ),
        aastex.Variable(
            name="filterMeshRatio",
            value=_percent(material.mesh.efficiency),
        ),
        aastex.Variable(
            name="filterToDetectorDistance",
            value=distance.round(),
        ),
        aastex.Variable(
            name="filterClocking",
            value=clocking.round(),
        ),
        aastex.Variable(
            name="gratingTestWavelength",
            value=scan.inputs.wavelength,
        ),
        aastex.Variable(
            name="testGratingChannelIndex",
            value=channel_tested,
        ),
        aastex.Variable(
            name="testGratingDate",
            value=_date(gratings.efficiencies.time_measurement),
        ),
        aastex.Variable(
            name="gratingMeasurementIncidenceAngle",
            value=efficiency.inputs.direction,
        ),
        aastex.Variable(
            name="gratingWitnessMeasurementIncidenceAngle",
            value=angle_witness,
        ),
        aastex.Variable(
            name="gratingWitnessMeasurementDate",
            value=_date(gratings.materials.time_measurement),
        ),
        aastex.Variable(
            name="gratingWitnessMissingChannel",
            value=channel_missing,
        ),
        aastex.Variable(
            name="primaryWitnessMeasurementIncidenceAngle",
            value=angle_primary,
        ),
        aastex.Variable(
            name="primaryMeasurementDate",
            value=_date(primaries.materials.time_measurement),
        ),
    ]


def _sensitivity() -> list[aastex.Variable]:
    """
    The variables cited by the subsection on the sensitivity and the cadence,
    and by the requirements table, from the signal of a single channel.
    """
    spectrum = esis.flights.f1.spectrum
    counts = esis_instrument_paper._counts

    signal = counts.counts().sum(counts.axis_line)
    noise_read = counts.noise_read()

    # The fewest exposures whose sum meets the signal-to-noise ratio the
    # mission required in a coronal hole, so that the text can say the
    # requirement is met by stacking exposures. The old draft settled on
    # twelve, which the modern model finds too few.
    num = counts.num_stack_required(signal, noise_read)
    snr = counts.snr(signal[counts.index(counts.context_coronal_hole)], noise_read, num)

    # how long it takes to collect a good image in an active region
    num_active_region = counts.num_stack_counts(
        signal=signal[counts.index(counts.context_active_region)],
        counts_min=counts.counts_image,
    )
    exposure = counts.optics().camera.timedelta_exposure

    return [
        aastex.Variable(
            name="MgXdimWavelength",
            value=spectrum.Mg_X_625.wavelength,
        ),
        aastex.Variable(
            # the weaker line of the Mg X doublet, as the old draft named it
            name="MgXdim",
            value=aastex.NoEscape(r"\MgXion~\MgXdimWavelength"),
        ),
        aastex.Variable(
            name="NumExpInStack",
            value=num,
        ),
        aastex.Variable(
            # a plain number rather than the dimensionless quantity it is in
            # the model, as the requirement beside it is written
            name="StackedCoronalHoleSNR",
            value=round(float(na.as_named_array(snr).ndarray), 1),
        ),
        aastex.Variable(
            name="goodImageCounts",
            value=counts.counts_image,
        ),
        aastex.Variable(
            name="activeRegionStackLength",
            value=num_active_region * exposure,
        ),
    ]


def _optimization() -> list[aastex.Variable]:
    """
    The variables cited by the subsection on the optimization and the
    tolerancing of the design.

    The degradation factors are literals. They are the allocations of the
    imaging error budget to the figure of the primary mirror and of the
    gratings, which a Fourier optics model of random figure errors turned into
    the specifications of the optics, and neither that model nor the
    allocations are part of the model of the instrument.
    """
    frequency = _error_budget.frequency()
    return [
        aastex.Variable(
            # the degradation of the MTF at the resolution requirement
            name="primaryMtfDegradationFactor",
            value=aastex.NoEscape(str(_error_budget.mtf_figure_primary)),
        ),
        aastex.Variable(
            name="gratingMtfDegradationFactor",
            value=aastex.NoEscape(str(_error_budget.mtf_figure_grating)),
        ),
        aastex.Variable(
            # Written out rather than set by siunitx, which does not take a
            # cycle for a unit.
            name="mtfFrequency",
            value=aastex.NoEscape(
                rf"\ensuremath{{{frequency.value:.2f}}}~cycles~arcsec$^{{-1}}$"
            ),
        ),
        aastex.Variable(
            # two decimals, as the old draft compared it with the Rayleigh
            # criterion
            name="mtfTotal",
            value=round(_error_budget.mtf_total(), 2),
        ),
        aastex.Variable(
            name="mtfRayleigh",
            value=round(_error_budget.mtf_rayleigh(), 2),
        ),
    ]


def _alignment_and_focus() -> list[aastex.Variable]:
    """
    The variables cited by the subsection on the alignment and the focus,
    from a single channel as designed.
    """
    sensitivity = na.as_named_array(_alignment.defocus_sensitivity()).ndarray

    return [
        aastex.Variable(
            # a whole number, as the old draft quoted it
            name="gratingDefocusSensitivity",
            value=round(float(sensitivity)),
        ),
        aastex.Variable(
            # Two decimals, since a hundredth of a milliradian moves the
            # image about two pixels.
            name="gratingTiltTolerance",
            value=_alignment.tolerance_tilt().round(2),
        ),
    ]


def _cameras() -> list[aastex.Variable]:
    """
    The variables cited by the subsection on the cameras, from the cameras
    that flew.

    The range of the focus adjustment and the masses of the cold block are
    still literals, since the model does not carry them.
    """
    instrument = esis_instrument_paper._counts.optics()
    camera = instrument.camera
    sensor = camera.sensor
    spectrum = esis.flights.f1.spectrum

    # Each tap reads out its masked rows before the rows of the image area,
    # so the rows the sensor images with are the active rows less the masked
    # rows of the two taps along the columns.
    num_pixel_y = sensor.num_pixel_active.y - 2 * sensor.num_masked

    gain = na.as_named_array(camera.gain).ndarray

    return [
        aastex.Variable(
            name="detectorName",
            value=sensor.family,
        ),
        aastex.Variable(
            name="detectorManufacturer",
            value=sensor.manufacturer,
        ),
        aastex.Variable(
            name="detectorAnalogToDigitalBits",
            value=camera.bits_adc,
        ),
        aastex.Variable(
            name="detectorPixelsX",
            value=sensor.num_pixel_x,
        ),
        aastex.Variable(
            name="detectorPixelsY",
            value=num_pixel_y,
        ),
        aastex.Variable(
            # it begins a sentence
            name="DetectorNumOverscanColumnsWords",
            value=aastex.NoEscape(
                num2words.num2words(sensor.num_overscan).capitalize()
            ),
        ),
        aastex.Variable(
            name="detectorNumMaskedRowsWords",
            value=aastex.NoEscape(num2words.num2words(sensor.num_masked)),
        ),
        aastex.Variable(
            name="detectorFrameTransferTime",
            value=camera.timedelta_transfer,
        ),
        aastex.Variable(
            name="detectorReadoutTime",
            value=camera.timedelta_readout,
        ),
        aastex.Variable(
            name="detectorExposureLengthMin",
            value=camera.timedelta_exposure_min,
        ),
        aastex.Variable(
            name="detectorExposureLengthMax",
            value=camera.timedelta_exposure_max,
        ),
        aastex.Variable(
            name="detectorExposureLengthIncrement",
            value=camera.timedelta_exposure_step,
        ),
        aastex.Variable(
            # the name of the channel, which is how the text names the cameras
            name="detectorTriggerChannel",
            value=camera.channel_trigger,
        ),
        aastex.Variable(
            name="detectorSynchronizationError",
            value=camera.timedelta_sync,
        ),
        aastex.Variable(
            name="detectorTemperatureTarget",
            value=sensor.temperature,
        ),
        aastex.Variable(
            name="channelNames",
            value=_series(na.as_named_array(camera.channel).ndarray),
        ),
        aastex.Variable(
            name="detectorSerialNumbers",
            value=_series(na.as_named_array(sensor.serial_number).ndarray),
        ),
        aastex.Variable(
            # Written to two decimals, as the measurements are. The least is a
            # plain number, since the text gives the unit once, after the
            # greatest.
            name="detectorGainMin",
            value=aastex.NoEscape(f"{gain.min().value:.2f}"),
        ),
        aastex.Variable(
            name="detectorGainMax",
            value=gain.max(),
            unit=(u.electron, u.DN**-1),
        ),
        aastex.Variable(
            name="detectorQuantumEfficiencyHeI",
            value=_percent(
                sensor.material.quantum_efficiency_effective(spectrum.He_I.wavelength)
            ),
        ),
        aastex.Variable(
            name="detectorQuantumEfficiencyOV",
            value=_percent(
                sensor.material.quantum_efficiency_effective(spectrum.O_V.wavelength)
            ),
        ),
    ]
