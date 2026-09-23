from fractions import Fraction

import pytest

from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.pipeline.package import (
    Continuation,
    Event,
    History,
    RouteTransportPackage,
    observe,
    push_history,
)
from sixbirds_glass.pipeline.quotients import (
    comparison_map,
    current_quotient,
    predictive_quotient,
)
from sixbirds_glass.pipeline.signatures import current_signature, future_signature


def test_hand_built_package_has_expected_quotients_and_comparison_map() -> None:
    """Hand computation:

    h0=delta_0 and h1=delta_1 at mid. The current event reads state label 1,
    so s0(h0)=(0,) and s0(h1)=(1,), giving two Q classes. The continuation
    flips 0<->1 before the end event reads label 1, so s+(h0)=(1,) and
    s+(h1)=(0,), giving two M classes. Therefore pi maps (1,)->(0,) and
    (0,)->(1,).
    """

    package = hand_built_flip_package()

    assert current_quotient(package, "mid") == {
        (Fraction(0),): ("h0",),
        (Fraction(1),): ("h1",),
    }
    assert predictive_quotient(package, "mid") == {
        (Fraction(1),): ("h0",),
        (Fraction(0),): ("h1",),
    }
    assert comparison_map(package, "mid") == {
        (Fraction(1),): (Fraction(0),),
        (Fraction(0),): (Fraction(1),),
    }


def test_predictive_witness_has_one_current_class_and_two_predictive_classes() -> None:
    package = predictive_witness_package()

    q_mid = current_quotient(package, "mid")
    m_mid = predictive_quotient(package, "mid")
    pi_mid = comparison_map(package, "mid")

    assert len(q_mid) == 1
    assert len(m_mid) == 2
    assert set(pi_mid.values()) == set(q_mid)


def test_signatures_push_and_observe_are_exact() -> None:
    package = hand_built_flip_package()
    history = package.history_by_label("mid", "h0")
    continuation = package.continuation_by_label("mid", "to_end")
    event = package.event_by_label("end", "end_is_one")

    pushed = push_history(history, continuation)

    assert pushed == {1: Fraction(1)}
    assert observe(pushed, package.projections["end"], event) == Fraction(1)
    assert current_signature(package, history) == (Fraction(0),)
    assert future_signature(package, history) == (Fraction(1),)


def test_malformed_future_catalog_raises_value_error() -> None:
    with pytest.raises(ValueError, match="continuation label 'missing'"):
        predictive_witness_package(future_catalog=(("missing", "end_is_one"),))


def test_history_distribution_must_sum_to_one() -> None:
    with pytest.raises(ValueError, match="distribution must sum to 1"):
        predictive_witness_package(h0_distribution={0: Fraction(2)})


def test_history_distribution_must_be_nonnegative() -> None:
    with pytest.raises(ValueError, match="history 'h0' has negative mass at state 1"):
        predictive_witness_package(h0_distribution={0: Fraction(2), 1: Fraction(-1)})


def test_history_distribution_masses_must_be_fractions() -> None:
    with pytest.raises(ValueError, match="history 'h0' has non-Fraction mass at state 0"):
        predictive_witness_package(h0_distribution={0: 1.0})  # type: ignore[dict-item]


def test_kernel_row_entries_must_be_fractions() -> None:
    kernel = Kernel(
        N=1,
        state_count=2,
        rows={
            0: {0: 1.0},  # type: ignore[dict-item]
            1: {1: Fraction(1)},
        },
    )

    with pytest.raises(ValueError, match="row 0 has non-Fraction entry"):
        package_with_custom_continuation(kernel)


def test_kernel_negative_entry_on_untouched_row_raises() -> None:
    kernel = Kernel(
        N=1,
        state_count=2,
        rows={
            0: {0: Fraction(1)},
            1: {0: Fraction(2), 1: Fraction(-1)},
        },
    )

    with pytest.raises(ValueError, match="row 1 has negative entry"):
        package_with_custom_continuation(kernel)


def test_kernel_bad_sum_on_untouched_row_raises() -> None:
    kernel = Kernel(
        N=1,
        state_count=2,
        rows={
            0: {0: Fraction(1)},
            1: {1: Fraction(2)},
        },
    )

    with pytest.raises(ValueError, match="row 1 must sum to 1"):
        package_with_custom_continuation(kernel)


def test_kernel_missing_row_raises() -> None:
    kernel = Kernel(
        N=1,
        state_count=2,
        rows={
            0: {0: Fraction(1)},
        },
    )

    with pytest.raises(ValueError, match="lacks row for state 1"):
        package_with_custom_continuation(kernel)


def test_event_weights_must_be_fractions() -> None:
    with pytest.raises(ValueError, match="non-Fraction weight"):
        package_with_custom_event(Event("bad_weight", {0: 1}))  # type: ignore[dict-item]


def hand_built_flip_package() -> RouteTransportPackage:
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
            "mid": identity_continuation("mid", 2),
            "end": identity_continuation("end", 2),
        },
        future_catalog={"mid": (("to_end", "end_is_one"),), "end": ()},
    )


def predictive_witness_package(
    *,
    future_catalog: tuple[tuple[str, str], ...] = (("reveal", "end_is_one"),),
    h0_distribution: dict[int, Fraction] | None = None,
) -> RouteTransportPackage:
    return RouteTransportPackage(
        interfaces=("mid", "end"),
        projections={"mid": lambda _state: "same", "end": lambda state: state},
        histories={
            "mid": (
                History("h0", "mid", h0_distribution or {0: Fraction(1)}),
                History("h1", "mid", {1: Fraction(1)}),
            ),
            "end": (),
        },
        continuations={("mid", "end"): (Continuation("reveal", "mid", "end", identity_kernel(2)),)},
        events={
            "mid": (Event("same_now", {"same": Fraction(1)}),),
            "end": (Event("end_is_one", {1: Fraction(1)}),),
        },
        identity={
            "mid": identity_continuation("mid", 2),
            "end": identity_continuation("end", 2),
        },
        future_catalog={"mid": future_catalog, "end": ()},
    )


def package_with_custom_continuation(kernel: Kernel) -> RouteTransportPackage:
    return RouteTransportPackage(
        interfaces=("mid", "end"),
        projections={"mid": lambda state: state, "end": lambda state: state},
        histories={
            "mid": (History("h0", "mid", {0: Fraction(1)}),),
            "end": (),
        },
        continuations={("mid", "end"): (Continuation("custom", "mid", "end", kernel),)},
        events={
            "mid": (Event("mid_is_zero", {0: Fraction(1)}),),
            "end": (Event("end_is_zero", {0: Fraction(1)}),),
        },
        identity={
            "mid": identity_continuation("mid", 2),
            "end": identity_continuation("end", 2),
        },
        future_catalog={"mid": (("custom", "end_is_zero"),), "end": ()},
    )


def package_with_custom_event(event: Event) -> RouteTransportPackage:
    return RouteTransportPackage(
        interfaces=("mid",),
        projections={"mid": lambda state: state},
        histories={"mid": (History("h0", "mid", {0: Fraction(1)}),)},
        continuations={},
        events={"mid": (event,)},
        identity={"mid": identity_continuation("mid", 1)},
        future_catalog={"mid": ()},
    )


def identity_continuation(interface: str, state_count: int) -> Continuation:
    return Continuation(f"id_{interface}", interface, interface, identity_kernel(state_count))


def identity_kernel(state_count: int) -> Kernel:
    return Kernel(
        N=1,
        state_count=state_count,
        rows={state: {state: Fraction(1)} for state in range(state_count)},
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
