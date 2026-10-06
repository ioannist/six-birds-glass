from dataclasses import fields
from fractions import Fraction

from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.pipeline.diagnostics import (
    DiagnosticsSummary,
    exact_max_abs_future_gap,
    max_fiber_size,
    summarize,
    witness_count,
    witness_pairs,
)
from sixbirds_glass.pipeline.package import Continuation, Event, History, RouteTransportPackage


def test_flip_package_has_no_witnesses_or_hidden_gap() -> None:
    package = flip_package()

    assert witness_pairs(package, "mid") == ()
    assert witness_count(package, "mid") == 0
    assert max_fiber_size(package, "mid") == 1
    assert exact_max_abs_future_gap(package, "mid") == Fraction(0)


def test_predictive_witness_package_diagnostics() -> None:
    package = witness_package()

    assert witness_pairs(package, "mid") == (("h0", "h1"),)
    assert witness_count(package, "mid") == 1
    assert max_fiber_size(package, "mid") == 2
    assert exact_max_abs_future_gap(package, "mid") == Fraction(1)


def test_diagnostics_summary_field_names_and_values() -> None:
    summary = summarize(witness_package(), "mid")

    assert tuple(field.name for field in fields(DiagnosticsSummary)) == (
        "history_count",
        "current_quotient_size",
        "predictive_quotient_size",
        "max_fiber_size",
        "witness_count",
        "exact_max_abs_future_gap",
    )
    assert summary == DiagnosticsSummary(
        history_count=2,
        current_quotient_size=1,
        predictive_quotient_size=2,
        max_fiber_size=2,
        witness_count=1,
        exact_max_abs_future_gap=Fraction(1),
    )


def flip_package() -> RouteTransportPackage:
    return RouteTransportPackage(
        interfaces=("mid", "end"),
        projections={"mid": lambda state: state, "end": lambda state: state},
        histories={
            "mid": (
                History("h0", "mid", {0: Fraction(1)}),
                History("h1", "mid", {1: Fraction(1)}),
            ),
            "end": (),
        },
        continuations={("mid", "end"): (Continuation("to_end", "mid", "end", flip_kernel()),)},
        events={
            "mid": (Event("mid_is_one", {1: Fraction(1)}),),
            "end": (Event("end_is_one", {1: Fraction(1)}),),
        },
        identity={
            "mid": identity_continuation("mid"),
            "end": identity_continuation("end"),
        },
        future_catalog={"mid": (("to_end", "end_is_one"),), "end": ()},
    )


def witness_package() -> RouteTransportPackage:
    return RouteTransportPackage(
        interfaces=("mid", "end"),
        projections={"mid": lambda _state: "same", "end": lambda state: state},
        histories={
            "mid": (
                History("h0", "mid", {0: Fraction(1)}),
                History("h1", "mid", {1: Fraction(1)}),
            ),
            "end": (),
        },
        continuations={("mid", "end"): (Continuation("reveal", "mid", "end", identity_kernel()),)},
        events={
            "mid": (Event("same_now", {"same": Fraction(1)}),),
            "end": (Event("end_is_one", {1: Fraction(1)}),),
        },
        identity={
            "mid": identity_continuation("mid"),
            "end": identity_continuation("end"),
        },
        future_catalog={"mid": (("reveal", "end_is_one"),), "end": ()},
    )


def identity_continuation(interface: str) -> Continuation:
    return Continuation(f"id_{interface}", interface, interface, identity_kernel())


def identity_kernel() -> Kernel:
    return Kernel(
        N=1,
        state_count=2,
        rows={state: {state: Fraction(1)} for state in range(2)},
    )


def flip_kernel() -> Kernel:
    return Kernel(
        N=1,
        state_count=2,
        rows={
            0: {1: Fraction(1)},
            1: {0: Fraction(1)},
        },
    )
