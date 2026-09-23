"""Deterministic discrete robustness bundles for Phase 1 benchmarks."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fractions import Fraction

from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID
from sixbirds_glass.pipeline.diagnostics import DiagnosticsSummary, summarize
from sixbirds_glass.pipeline.loops import loop_action_score
from sixbirds_glass.pipeline.package import RouteTransportPackage
from sixbirds_glass.triage import benchmarks
from sixbirds_glass.triage.classification import ClassificationInput, Regime, classify_regime

CLEARED_THRESHOLD = Fraction(95, 100)
PERSISTENCE_THRESHOLD = Fraction(4, 5)


@dataclass(frozen=True)
class PerturbationTrial:
    """One deterministic structural perturbation of a benchmark factory."""

    label: str
    factory_kwargs: dict[str, object]


STATE_PAIR_TRIALS = (
    PerturbationTrial("default", {}),
    PerturbationTrial("pair_0011_1100", {"state_left": 0b0011, "state_right": 0b1100}),
    PerturbationTrial("pair_0101_1010", {"state_left": 0b0101, "state_right": 0b1010}),
)

FLAT_CONTROL_TRIALS = (
    PerturbationTrial("default", {}),
    PerturbationTrial("epsilon_low", {"epsilon": DEFAULT_EPSILON_GRID[0]}),
    PerturbationTrial("epsilon_mid", {"epsilon": DEFAULT_EPSILON_GRID[4]}),
)
PROTOCOL_TRAP_NAIVE_TRIALS = STATE_PAIR_TRIALS
PROTOCOL_TRAP_HONEST_TRIALS = STATE_PAIR_TRIALS
FLATTENABLE_RAW_TRIALS = STATE_PAIR_TRIALS
FLATTENABLE_COMPLETED_TRIALS = STATE_PAIR_TRIALS
LATENT_MEMORY_BASE_TRIALS = STATE_PAIR_TRIALS
LATENT_MEMORY_REFINED_TRIALS = STATE_PAIR_TRIALS
DISSIPATIVE_MEMORY_TRIALS = STATE_PAIR_TRIALS
KOVACS_WHEEL_TRIALS = (
    PerturbationTrial("default", {}),
    PerturbationTrial("state_00001101", {"state": 0b00001101}),
    PerturbationTrial("state_00101001", {"state": 0b00101001}),
)


def survival_fraction(
    factory: Callable[..., RouteTransportPackage],
    trials: Sequence[PerturbationTrial],
    expected_regime: Regime,
    classification_builder: Callable[[RouteTransportPackage], ClassificationInput],
) -> Fraction:
    """Return the exact fraction of trials that retain ``expected_regime``."""

    if not trials:
        raise ValueError("trials must contain at least one perturbation")
    matches = 0
    for trial in trials:
        package = factory(**trial.factory_kwargs)
        if classify_regime(classification_builder(package)) == expected_regime:
            matches += 1
    return Fraction(matches, len(trials))


def flat_control_cleared() -> Fraction:
    return survival_fraction(
        benchmarks.flat_control, FLAT_CONTROL_TRIALS, "flat", flat_classification
    )


def protocol_trap_naive_persists() -> Fraction:
    return survival_fraction(
        benchmarks.protocol_trap_naive,
        PROTOCOL_TRAP_NAIVE_TRIALS,
        "artifact_trap",
        artifact_trap_classification,
    )


def protocol_trap_honest_cleared() -> Fraction:
    return survival_fraction(
        benchmarks.protocol_trap_honest,
        PROTOCOL_TRAP_HONEST_TRIALS,
        "flat",
        flat_classification,
    )


def flattenable_raw_persists() -> Fraction:
    return survival_fraction(
        benchmarks.flattenable_raw,
        FLATTENABLE_RAW_TRIALS,
        "flattenable",
        flattenable_classification,
    )


def flattenable_completed_cleared() -> Fraction:
    return survival_fraction(
        benchmarks.flattenable_completed,
        FLATTENABLE_COMPLETED_TRIALS,
        "flat",
        flat_classification,
    )


def latent_memory_base_persists() -> Fraction:
    return survival_fraction(
        benchmarks.latent_memory_base,
        LATENT_MEMORY_BASE_TRIALS,
        "explicit_latent",
        explicit_latent_classification,
    )


def latent_memory_refined_cleared() -> Fraction:
    return survival_fraction(
        benchmarks.latent_memory_refined,
        LATENT_MEMORY_REFINED_TRIALS,
        "flat",
        flat_classification,
    )


def dissipative_memory_persists() -> Fraction:
    return survival_fraction(
        benchmarks.dissipative_memory,
        DISSIPATIVE_MEMORY_TRIALS,
        "dissipative",
        dissipative_classification,
    )


def dissipative_memory_end_cleared() -> Fraction:
    return survival_fraction(
        benchmarks.dissipative_memory,
        DISSIPATIVE_MEMORY_TRIALS,
        "flat",
        dissipative_end_classification,
    )


def kovacs_wheel_persists() -> Fraction:
    return survival_fraction(
        benchmarks.kovacs_wheel,
        KOVACS_WHEEL_TRIALS,
        "coherent_candidate",
        kovacs_wheel_classification,
    )


def flat_classification(package: RouteTransportPackage) -> ClassificationInput:
    return ClassificationInput(
        base_summary=_summary(package),
        loop_score_current=Fraction(0),
        loop_score_predictive=Fraction(0),
    )


def artifact_trap_classification(package: RouteTransportPackage) -> ClassificationInput:
    return ClassificationInput(
        base_summary=_summary(package),
        loop_score_current=Fraction(0),
        loop_score_predictive=Fraction(0),
        support_fixation_status="ok",
        honest_counterpart_flat=True,
    )


def flattenable_classification(package: RouteTransportPackage) -> ClassificationInput:
    return ClassificationInput(
        base_summary=_summary(package),
        loop_score_current=Fraction(0),
        loop_score_predictive=Fraction(0),
        support_fixation_status="ok",
        flattening_status="passed",
    )


def explicit_latent_classification(package: RouteTransportPackage) -> ClassificationInput:
    return ClassificationInput(
        base_summary=_summary(package),
        loop_score_current=Fraction(0),
        loop_score_predictive=Fraction(0),
        support_fixation_status="ok",
        currentization_status="passed",
    )


def dissipative_classification(package: RouteTransportPackage) -> ClassificationInput:
    return ClassificationInput(
        base_summary=_summary(package),
        loop_score_current=Fraction(0),
        loop_score_predictive=Fraction(0),
        dissipative_evidence=True,
    )


def dissipative_end_classification(package: RouteTransportPackage) -> ClassificationInput:
    return ClassificationInput(
        base_summary=_summary(package, interface="end"),
        loop_score_current=Fraction(0),
        loop_score_predictive=Fraction(0),
    )


def kovacs_wheel_classification(package: RouteTransportPackage) -> ClassificationInput:
    loop = package.continuation_by_label("mid", "swap_mid")
    return ClassificationInput(
        base_summary=_summary(package),
        loop_score_current=loop_action_score(package, "mid", (loop,), quotient_kind="current"),
        loop_score_predictive=loop_action_score(
            package, "mid", (loop,), quotient_kind="predictive"
        ),
        flattening_status="skipped",
        currentization_status="skipped",
    )


def _summary(package: RouteTransportPackage, *, interface: str = "mid") -> DiagnosticsSummary:
    return summarize(package, interface)
