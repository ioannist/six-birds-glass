from dataclasses import dataclass
from fractions import Fraction

from sixbirds_glass.pipeline.diagnostics import summarize
from sixbirds_glass.pipeline.loops import loop_action_score
from sixbirds_glass.pipeline.package import Continuation, RouteTransportPackage
from sixbirds_glass.triage.benchmarks import (
    dissipative_memory,
    flat_control,
    flattenable_completed,
    flattenable_raw,
    kovacs_wheel,
    latent_memory_base,
    latent_memory_refined,
    protocol_trap_honest,
    protocol_trap_naive,
)
from sixbirds_glass.triage.classification import ClassificationInput, classify_regime
from sixbirds_glass.triage.statuses import (
    currentization_status,
    flattening_status,
    support_fixation_status,
)


@dataclass(frozen=True)
class MetricRow:
    q_size: int
    m_size: int
    max_fiber: int
    witnesses: int
    gap_positive: bool
    loop_q: Fraction
    loop_m: Fraction


def test_flat_control_reproduces_table_and_classifies_flat() -> None:
    package = flat_control()

    row = benchmark_row(package)

    assert row == MetricRow(1, 1, 1, 0, False, Fraction(0), Fraction(0))
    assert classify_regime(classification(package)) == "flat"


def test_protocol_trap_pair_reproduces_table_and_classifies_artifact_trap() -> None:
    naive = protocol_trap_naive()
    honest = protocol_trap_honest()

    naive_row = benchmark_row(naive)
    honest_row = benchmark_row(honest)
    support = support_fixation_status(naive, "mid", honest, "mid")

    assert naive_row == MetricRow(1, 2, 2, 1, True, Fraction(0), Fraction(0))
    assert honest_row == MetricRow(1, 1, 1, 0, False, Fraction(0), Fraction(0))
    assert support == "ok"
    assert (
        classify_regime(
            classification(
                naive,
                support_status=support,
                honest_counterpart_flat=classify_regime(classification(honest)) == "flat",
            )
        )
        == "artifact_trap"
    )


def test_flattenable_pair_reproduces_table_and_classifies_flattenable() -> None:
    raw = flattenable_raw()
    completed = flattenable_completed()
    raw_summary = summarize(raw, "mid")
    completed_summary = summarize(completed, "mid")
    support = support_fixation_status(raw, "mid", completed, "mid")
    status = flattening_status(raw_summary, completed_summary, support)

    assert benchmark_row(raw) == MetricRow(1, 2, 2, 1, True, Fraction(0), Fraction(0))
    assert benchmark_row(completed) == MetricRow(1, 1, 1, 0, False, Fraction(0), Fraction(0))
    assert status == "passed"
    assert classify_regime(classification(raw, support_status=support, flattening=status)) == (
        "flattenable"
    )
    assert classify_regime(classification(completed)) == "flat"


def test_latent_memory_pair_reproduces_table_and_classifies_explicit_latent() -> None:
    base = latent_memory_base()
    refined = latent_memory_refined()
    base_summary = summarize(base, "mid")
    refined_summary = summarize(refined, "mid")
    support = support_fixation_status(base, "mid", refined, "mid")
    status = currentization_status(base_summary, refined_summary, support)

    assert benchmark_row(base) == MetricRow(1, 2, 2, 1, True, Fraction(0), Fraction(0))
    assert benchmark_row(refined) == MetricRow(2, 2, 1, 0, False, Fraction(0), Fraction(0))
    assert status == "passed"
    assert classify_regime(classification(base, support_status=support, currentization=status)) == (
        "explicit_latent"
    )
    assert classify_regime(classification(refined)) == "flat"


def test_dissipative_memory_reproduces_table_and_classifies_dissipative() -> None:
    package = dissipative_memory()

    mid_row = benchmark_row(package)
    end_summary = summarize(package, "end")
    end_row = MetricRow(
        q_size=end_summary.current_quotient_size,
        m_size=end_summary.predictive_quotient_size,
        max_fiber=end_summary.max_fiber_size,
        witnesses=end_summary.witness_count,
        gap_positive=end_summary.exact_max_abs_future_gap > 0,
        loop_q=Fraction(0),
        loop_m=Fraction(0),
    )

    assert mid_row == MetricRow(1, 2, 2, 1, True, Fraction(0), Fraction(0))
    assert end_row == MetricRow(1, 1, 1, 0, False, Fraction(0), Fraction(0))
    assert classify_regime(classification(package, dissipative_evidence=True)) == "dissipative"
    assert (
        classify_regime(
            ClassificationInput(
                base_summary=end_summary, loop_score_current=0, loop_score_predictive=0
            )
        )
        == "flat"
    )


def test_kovacs_wheel_reproduces_table_and_classifies_coherent_candidate() -> None:
    package = kovacs_wheel()
    swap_mid = package.continuation_by_label("mid", "swap_mid")

    row = benchmark_row(package, loops=(swap_mid,))

    assert row == MetricRow(1, 2, 2, 1, True, Fraction(0), Fraction(1))
    assert (
        classify_regime(
            classification(
                package,
                loops=(swap_mid,),
                flattening="skipped",
                currentization="skipped",
            )
        )
        == "coherent_candidate"
    )


def benchmark_row(
    package: RouteTransportPackage,
    *,
    interface: str = "mid",
    loops: tuple[Continuation, ...] = (),
) -> MetricRow:
    summary = summarize(package, interface)
    return MetricRow(
        q_size=summary.current_quotient_size,
        m_size=summary.predictive_quotient_size,
        max_fiber=summary.max_fiber_size,
        witnesses=summary.witness_count,
        gap_positive=summary.exact_max_abs_future_gap > 0,
        loop_q=loop_action_score(package, interface, loops, quotient_kind="current"),
        loop_m=loop_action_score(package, interface, loops, quotient_kind="predictive"),
    )


def classification(
    package: RouteTransportPackage,
    *,
    interface: str = "mid",
    loops: tuple[Continuation, ...] = (),
    support_status: str | None = None,
    honest_counterpart_flat: bool = False,
    flattening: str | None = None,
    currentization: str | None = None,
    dissipative_evidence: bool = False,
) -> ClassificationInput:
    return ClassificationInput(
        base_summary=summarize(package, interface),
        loop_score_current=loop_action_score(package, interface, loops, quotient_kind="current"),
        loop_score_predictive=loop_action_score(
            package, interface, loops, quotient_kind="predictive"
        ),
        support_fixation_status=support_status,  # type: ignore[arg-type]
        honest_counterpart_flat=honest_counterpart_flat,
        flattening_status=flattening,  # type: ignore[arg-type]
        currentization_status=currentization,  # type: ignore[arg-type]
        dissipative_evidence=dissipative_evidence,
    )
