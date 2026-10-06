from fractions import Fraction

import pytest

from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.pipeline.loops import (
    find_history_by_distribution,
    loop_action_score,
)
from sixbirds_glass.pipeline.package import Continuation, Event, History, RouteTransportPackage


def test_swap_loop_scores_match_memory_wheel_pattern() -> None:
    package = swap_loop_package()
    loop = package.continuation_by_label("mid", "swap_mid")

    assert loop_action_score(package, "mid", (loop,), quotient_kind="current") == Fraction(0)
    assert loop_action_score(package, "mid", (loop,), quotient_kind="predictive") == Fraction(1)


def test_find_history_by_distribution_raises_on_zero_matches() -> None:
    package = swap_loop_package()

    with pytest.raises(ValueError, match="no declared history"):
        find_history_by_distribution(package, "mid", {2: Fraction(1)})


def test_find_history_by_distribution_raises_on_multiple_matches() -> None:
    package = duplicate_distribution_package()

    with pytest.raises(ValueError, match="multiple declared histories"):
        find_history_by_distribution(package, "mid", {0: Fraction(1)})


def test_loop_action_rejects_non_endo_continuation() -> None:
    package = swap_loop_package()
    not_loop = package.continuation_by_label("mid", "reveal")

    with pytest.raises(ValueError, match="endo-continuation"):
        loop_action_score(package, "mid", (not_loop,), quotient_kind="current")


def swap_loop_package() -> RouteTransportPackage:
    return RouteTransportPackage(
        interfaces=("mid", "out"),
        projections={"mid": lambda _state: "same", "out": lambda state: state},
        histories={
            "mid": (
                History("h0", "mid", {0: Fraction(1)}),
                History("h1", "mid", {1: Fraction(1)}),
            ),
            "out": (),
        },
        continuations={
            ("mid", "mid"): (Continuation("swap_mid", "mid", "mid", swap_kernel()),),
            ("mid", "out"): (Continuation("reveal", "mid", "out", identity_kernel()),),
        },
        events={
            "mid": (Event("same_now", {"same": Fraction(1)}),),
            "out": (Event("out_is_one", {1: Fraction(1)}),),
        },
        identity={
            "mid": identity_continuation("mid"),
            "out": identity_continuation("out"),
        },
        future_catalog={"mid": (("reveal", "out_is_one"),), "out": ()},
    )


def duplicate_distribution_package() -> RouteTransportPackage:
    return RouteTransportPackage(
        interfaces=("mid",),
        projections={"mid": lambda _state: "same"},
        histories={
            "mid": (
                History("h0", "mid", {0: Fraction(1)}),
                History("h0_copy", "mid", {0: Fraction(1)}),
            )
        },
        continuations={},
        events={"mid": (Event("same_now", {"same": Fraction(1)}),)},
        identity={"mid": identity_continuation("mid")},
        future_catalog={"mid": ()},
    )


def identity_continuation(interface: str) -> Continuation:
    return Continuation(f"id_{interface}", interface, interface, identity_kernel())


def identity_kernel() -> Kernel:
    return Kernel(
        N=1,
        state_count=2,
        rows={state: {state: Fraction(1)} for state in range(2)},
    )


def swap_kernel() -> Kernel:
    return Kernel(
        N=1,
        state_count=2,
        rows={
            0: {1: Fraction(1)},
            1: {0: Fraction(1)},
        },
    )
