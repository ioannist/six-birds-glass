from fractions import Fraction

from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.pipeline.diagnostics import DiagnosticsSummary
from sixbirds_glass.pipeline.package import Continuation, Event, History, RouteTransportPackage
from sixbirds_glass.triage.statuses import (
    currentization_status,
    flattening_status,
    support_fixation_status,
    support_labels,
)


def test_support_labels_and_fixation_status() -> None:
    base = support_package(labels=("a", "b"))
    matching = support_package(labels=("a", "b"))
    differing = support_package(labels=("a", "c"))

    assert support_labels(base, "mid") == frozenset({"a", "b"})
    assert support_fixation_status(base, "mid", matching, "mid") == "ok"
    assert support_fixation_status(base, "mid", differing, "mid") == "failed"


def test_flattening_status_pass_and_failures() -> None:
    base = summary(witness_count=1, gap=Fraction(1), q=1, m=2, fiber=2)
    completed_flat = summary(witness_count=0, gap=Fraction(0), q=1, m=1, fiber=1)
    completed_still_bad = summary(witness_count=1, gap=Fraction(1), q=1, m=2, fiber=2)
    already_flat = summary(witness_count=0, gap=Fraction(0), q=1, m=1, fiber=1)

    assert flattening_status(base, completed_flat, "ok") == "passed"
    assert flattening_status(base, completed_flat, "failed") == "skipped"
    assert flattening_status(already_flat, completed_flat, "ok") == "skipped"
    assert flattening_status(base, completed_still_bad, "ok") == "skipped"


def test_currentization_status_pass_and_failures() -> None:
    base = summary(witness_count=1, gap=Fraction(1), q=1, m=2, fiber=2)
    refined_flat = summary(witness_count=0, gap=Fraction(0), q=2, m=2, fiber=1)
    refined_with_fiber = summary(witness_count=0, gap=Fraction(0), q=1, m=2, fiber=2)
    refined_with_gap = summary(witness_count=0, gap=Fraction(1), q=2, m=2, fiber=1)
    already_flat = summary(witness_count=0, gap=Fraction(0), q=1, m=1, fiber=1)

    assert currentization_status(base, refined_flat, "ok") == "passed"
    assert currentization_status(base, refined_flat, "failed") == "skipped"
    assert currentization_status(already_flat, refined_flat, "ok") == "skipped"
    assert currentization_status(base, refined_with_fiber, "ok") == "skipped"
    assert currentization_status(base, refined_with_gap, "ok") == "skipped"


def support_package(labels: tuple[str, str]) -> RouteTransportPackage:
    return RouteTransportPackage(
        interfaces=("mid",),
        projections={"mid": lambda state: labels[state]},
        histories={
            "mid": (
                History("h0", "mid", {0: Fraction(1)}),
                History("h1", "mid", {1: Fraction(1)}),
            )
        },
        continuations={},
        events={"mid": (Event("one", {labels[0]: Fraction(1), labels[1]: Fraction(1)}),)},
        identity={"mid": Continuation("id_mid", "mid", "mid", identity_kernel())},
        future_catalog={"mid": ()},
    )


def identity_kernel() -> Kernel:
    return Kernel(
        N=1,
        state_count=2,
        rows={state: {state: Fraction(1)} for state in range(2)},
    )


def summary(*, witness_count: int, gap: Fraction, q: int, m: int, fiber: int) -> DiagnosticsSummary:
    return DiagnosticsSummary(
        history_count=2,
        current_quotient_size=q,
        predictive_quotient_size=m,
        max_fiber_size=fiber,
        witness_count=witness_count,
        exact_max_abs_future_gap=gap,
    )
