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

__all__ = [
    "variables",
]


def _pending(name: str) -> aastex.Variable:
    """
    A quantity the model cannot supply yet, marked where it is cited.

    Every number in this article is computed from the instrument model, and
    these are the ones the model has no answer for. They are written into the
    text as ``??`` rather than guessed at or left out, so that a draft shows
    plainly what is still owed and no placeholder can be mistaken for a
    measurement.
    """
    return aastex.Variable(name=name, value=aastex.NoEscape(r"\textbf{??}"))


def variables() -> list[aastex.Variable]:
    """
    A list of LaTeX variables for every numeric quantity cited in the prose.

    Reference these macros in section strings instead of hardcoding numbers so
    that the text stays in sync with the instrument model.

    A few of these are still literals, since the model does not carry the
    quantity they describe: two which belong to MOSES or to the payload
    rather than to the instrument, and the spectroscopic name of each
    emission line, whose wavelength the model does carry.
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
            name="observingTime",
            value=length_observation.round(1),
        ),
        aastex.Variable(
            # How many exposures to stack is chosen rather than derived: it
            # buys signal at the cost of the cadence the torsional waves need,
            # and the old draft settled on twelve. It is written here because
            # the count rates are computed from it, not the other way about.
            name="NumExpInStack",
            value=12,
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
        # Quantities the model cannot supply yet. Each is a capability of the
        # instrument rather than a requirement of the mission, and each waits
        # on analysis which has not been ported: the spatial resolution on the
        # error budget, and the stacked signal-to-noise ratio on the count
        # rates.
        _pending("spatialResolutionTotal"),
        _pending("StackedCoronalHoleSNR"),
        *_coatings(),
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


def _percent(fraction: na.AbstractScalar, decimals: int = 0) -> u.Quantity:
    """A fraction written as a percentage, rounded."""
    fraction = na.as_named_array(fraction).ndarray
    return (fraction * u.dimensionless_unscaled).to(u.percent).round(decimals)


def _date(time: astropy.time.Time) -> aastex.NoEscape:
    """A day written as the journal writes dates, such as 2018 January 21."""
    date = time.to_datetime()
    return aastex.NoEscape(f"{date.year} {date:%B} {date.day}")


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
    rays = optika.rays.RayVectorArray(
        wavelength=spectrum.O_V.wavelength,
        position=na.Cartesian3dVectorArray() * u.mm,
        direction=na.Cartesian3dVectorArray(0, 0, 1),
    )
    grooves = design.grating.surface.rulings.efficiency(
        rays, na.Cartesian3dVectorArray(0, 0, -1)
    )
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
