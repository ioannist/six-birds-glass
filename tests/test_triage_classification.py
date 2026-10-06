from fractions import Fraction

import pytest

from sixbirds_glass.pipeline.diagnostics import DiagnosticsSummary
from sixbirds_glass.triage.classification import ClassificationInput, classify_regime


def test_classify_flat() -> None:
    assert classify_regime(ClassificationInput(flat_summary(), Fraction(0), Fraction(0))) == "flat"


def test_classify_artifact_trap() -> None:
    assert (
        classify_regime(
            ClassificationInput(
                nonflat_summary(),
                support_fixation_status="ok",
                honest_counterpart_flat=True,
            )
        )
        == "artifact_trap"
    )


def test_classify_flattenable() -> None:
    assert (
        classify_regime(
            ClassificationInput(
                nonflat_summary(),
                support_fixation_status="ok",
                flattening_status="passed",
            )
        )
        == "flattenable"
    )


def test_classify_explicit_latent() -> None:
    assert (
        classify_regime(
            ClassificationInput(
                nonflat_summary(),
                support_fixation_status="ok",
                currentization_status="passed",
            )
        )
        == "explicit_latent"
    )


def test_classify_dissipative() -> None:
    assert (
        classify_regime(
            ClassificationInput(
                nonflat_summary(),
                loop_score_current=Fraction(0),
                loop_score_predictive=Fraction(0),
                dissipative_evidence=True,
            )
        )
        == "dissipative"
    )


def test_classify_coherent_candidate() -> None:
    assert (
        classify_regime(
            ClassificationInput(
                nonflat_summary(),
                loop_score_current=Fraction(0),
                loop_score_predictive=Fraction(1),
                flattening_status="skipped",
                currentization_status="skipped",
            )
        )
        == "coherent_candidate"
    )


def test_classify_raises_when_no_regime_matches() -> None:
    unmatched = DiagnosticsSummary(
        history_count=2,
        current_quotient_size=1,
        predictive_quotient_size=2,
        max_fiber_size=1,
        witness_count=0,
        exact_max_abs_future_gap=Fraction(1),
    )

    with pytest.raises(ValueError, match="did not match"):
        classify_regime(ClassificationInput(unmatched))


def flat_summary() -> DiagnosticsSummary:
    return DiagnosticsSummary(
        history_count=2,
        current_quotient_size=1,
        predictive_quotient_size=1,
        max_fiber_size=1,
        witness_count=0,
        exact_max_abs_future_gap=Fraction(0),
    )


def nonflat_summary() -> DiagnosticsSummary:
    return DiagnosticsSummary(
        history_count=2,
        current_quotient_size=1,
        predictive_quotient_size=2,
        max_fiber_size=2,
        witness_count=1,
        exact_max_abs_future_gap=Fraction(1),
    )
