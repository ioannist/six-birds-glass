"""Six-regime classification rules from [A]'s route-transport triage."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Literal

from sixbirds_glass.pipeline.diagnostics import DiagnosticsSummary
from sixbirds_glass.triage.statuses import RepairStatus, SupportFixationStatus

Regime = Literal[
    "flat",
    "artifact_trap",
    "flattenable",
    "explicit_latent",
    "dissipative",
    "coherent_candidate",
]


@dataclass(frozen=True)
class ClassificationInput:
    """All declared facts needed for one six-regime classification decision."""

    base_summary: DiagnosticsSummary
    loop_score_current: Fraction | None = None
    loop_score_predictive: Fraction | None = None
    support_fixation_status: SupportFixationStatus | None = None
    honest_counterpart_flat: bool = False
    flattening_status: RepairStatus | None = None
    currentization_status: RepairStatus | None = None
    dissipative_evidence: bool = False


def classify_regime(classification: ClassificationInput) -> Regime:
    """Classify one benchmark row by the ordered six-regime rules.

    Priority is part of the doctrine: check flat first, then paired-repair
    regimes, then dissipative, then coherent-candidate as the residual
    loop-asymmetry case.
    """

    summary = classification.base_summary
    if _is_flat(summary) and _loop_scores_are_flat(classification):
        return "flat"

    if (
        _is_nonflat(summary)
        and classification.support_fixation_status == "ok"
        and classification.honest_counterpart_flat
    ):
        return "artifact_trap"

    if (
        _is_nonflat(summary)
        and classification.support_fixation_status == "ok"
        and classification.flattening_status == "passed"
    ):
        return "flattenable"

    if (
        _is_nonflat(summary)
        and classification.support_fixation_status == "ok"
        and classification.currentization_status == "passed"
    ):
        return "explicit_latent"

    if (
        _is_nonflat(summary)
        and classification.dissipative_evidence
        and _loop_scores_are_flat(classification)
    ):
        return "dissipative"

    if (
        summary.witness_count >= 1
        and summary.max_fiber_size >= 2
        and summary.exact_max_abs_future_gap > 0
        and classification.loop_score_current == 0
        and classification.loop_score_predictive is not None
        and classification.loop_score_predictive > 0
        and classification.flattening_status == "skipped"
        and classification.currentization_status == "skipped"
    ):
        return "coherent_candidate"

    raise ValueError(f"classification input did not match any six-regime rule: {classification!r}")


def _is_flat(summary: DiagnosticsSummary) -> bool:
    return (
        summary.current_quotient_size == summary.predictive_quotient_size
        and summary.max_fiber_size == 1
        and summary.witness_count == 0
        and summary.exact_max_abs_future_gap == 0
    )


def _is_nonflat(summary: DiagnosticsSummary) -> bool:
    return (
        summary.predictive_quotient_size > summary.current_quotient_size
        and summary.witness_count >= 1
    )


def _loop_scores_are_flat(classification: ClassificationInput) -> bool:
    current = classification.loop_score_current
    predictive = classification.loop_score_predictive
    return (current is None or current == 0) and (predictive is None or predictive == 0)
