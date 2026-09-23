"""Small thermal benchmark packages for the six-regime triage suite."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from fractions import Fraction

from sixbirds_glass.lenses.catalog import l_energy, l_panel, l_panel_reflection_invariant, reflect
from sixbirds_glass.models.east import build_east_kernel, east_stationary
from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.pipeline.package import Continuation, Event, History, RouteTransportPackage

SMALL_N = 4
WHEEL_N = 8
EPS_A = Fraction(1, 5)
EPS_B = Fraction(1, 2)
STATE_LEFT = 0b0110
STATE_RIGHT = 0b1001
WHEEL_STATE = 0b00000111


def flat_control(epsilon: Fraction = EPS_A) -> RouteTransportPackage:
    """Return the equilibrium flat-control package."""

    stationary = east_stationary(SMALL_N, epsilon)
    state_count = 1 << SMALL_N
    return RouteTransportPackage(
        interfaces=("mid", "out"),
        projections={
            "mid": lambda state: l_energy(state, SMALL_N),
            "out": lambda state: l_energy(state, SMALL_N),
        },
        histories={
            "mid": (
                History("h_eq_0", "mid", stationary),
                History("h_eq_1", "mid", stationary),
            ),
            "out": (),
        },
        continuations={
            ("mid", "out"): (
                Continuation("to_out", "mid", "out", build_east_kernel(SMALL_N, epsilon)),
            )
        },
        events={
            "mid": (_constant_event("same_energy_panel"),),
            "out": (
                Event("out_energy", {energy: Fraction(energy) for energy in range(SMALL_N + 1)}),
            ),
        },
        identity={
            "mid": _identity_continuation("mid", SMALL_N, state_count),
            "out": _identity_continuation("out", SMALL_N, state_count),
        },
        future_catalog={"mid": (("to_out", "out_energy"),), "out": ()},
    )


def protocol_trap_naive(
    state_left: int = STATE_LEFT, state_right: int = STATE_RIGHT
) -> RouteTransportPackage:
    """Return the naive protocol-trap package with external schedule residue."""

    return _two_state_package(
        state_left=state_left,
        state_right=state_right,
        mid_event=Event("schedule_blind", {state_left: Fraction(1), state_right: Fraction(1)}),
        to_out=_identity_between("to_out", "mid", "out", SMALL_N, 1 << SMALL_N),
        out_event=_left_state_event("route_residue", state_left, state_right),
    )


def protocol_trap_honest(
    state_left: int = STATE_LEFT, state_right: int = STATE_RIGHT
) -> RouteTransportPackage:
    """Return the honest/internalized protocol-trap control package."""

    return _two_state_package(
        state_left=state_left,
        state_right=state_right,
        mid_event=Event("schedule_blind", {state_left: Fraction(1), state_right: Fraction(1)}),
        to_out=_constant_continuation("to_out", "mid", "out", SMALL_N, state_left),
        out_event=_left_state_event("route_residue", state_left, state_right),
    )


def flattenable_raw(
    state_left: int = STATE_LEFT, state_right: int = STATE_RIGHT
) -> RouteTransportPackage:
    """Return the raw incomplete-catalog package."""

    return _two_state_package(
        state_left=state_left,
        state_right=state_right,
        mid_event=Event("incomplete_blind", {state_left: Fraction(1), state_right: Fraction(1)}),
        to_out=_identity_between("to_out", "mid", "out", SMALL_N, 1 << SMALL_N),
        out_event=_left_state_event("completed_direction", state_left, state_right),
    )


def flattenable_completed(
    state_left: int = STATE_LEFT, state_right: int = STATE_RIGHT
) -> RouteTransportPackage:
    """Return the completed fixed-support package."""

    return _two_state_package(
        state_left=state_left,
        state_right=state_right,
        mid_event=Event("completed_blind", {state_left: Fraction(1), state_right: Fraction(1)}),
        to_out=_constant_continuation("to_out", "mid", "out", SMALL_N, state_left),
        out_event=_left_state_event("completed_direction", state_left, state_right),
    )


def latent_memory_base(
    state_left: int = STATE_LEFT, state_right: int = STATE_RIGHT
) -> RouteTransportPackage:
    """Return the base latent-memory package: same current value, different future."""

    return _two_state_package(
        state_left=state_left,
        state_right=state_right,
        mid_event=Event("energy_blind", {state_left: Fraction(1), state_right: Fraction(1)}),
        to_out=_identity_between("to_out", "mid", "out", SMALL_N, 1 << SMALL_N),
        out_event=_left_state_event("specific_bit_pattern", state_left, state_right),
    )


def latent_memory_refined(
    state_left: int = STATE_LEFT, state_right: int = STATE_RIGHT
) -> RouteTransportPackage:
    """Return the refined latent-memory package where the split is current-visible."""

    return _two_state_package(
        state_left=state_left,
        state_right=state_right,
        mid_event=_left_state_event("specific_bit_pattern_now", state_left, state_right),
        to_out=_identity_between("to_out", "mid", "out", SMALL_N, 1 << SMALL_N),
        out_event=_left_state_event("specific_bit_pattern", state_left, state_right),
    )


def dissipative_memory(
    state_left: int = STATE_LEFT, state_right: int = STATE_RIGHT
) -> RouteTransportPackage:
    """Return the three-interface dissipative-memory package."""

    _validate_state_pair(state_left, state_right, SMALL_N)
    state_count = 1 << SMALL_N
    histories_mid = _two_dirac_histories("mid", state_left, state_right)
    merged = {state_left: Fraction(1)}
    return RouteTransportPackage(
        interfaces=("mid", "probe", "end"),
        projections={
            "mid": _state_projection,
            "probe": _state_projection,
            "end": _state_projection,
        },
        histories={
            "mid": histories_mid,
            "probe": (),
            "end": (
                History("end_from_left", "end", merged),
                History("end_from_right", "end", merged),
            ),
        },
        continuations={
            ("mid", "probe"): (
                Continuation("to_probe", "mid", "probe", _identity_kernel(SMALL_N, state_count)),
            ),
            ("mid", "end"): (_constant_continuation("to_end", "mid", "end", SMALL_N, state_left),),
        },
        events={
            "mid": (Event("early_blind", {state_left: Fraction(1), state_right: Fraction(1)}),),
            "probe": (_left_state_event("short_probe", state_left, state_right),),
            "end": (_left_state_event("merged_end", state_left, state_right),),
        },
        identity={
            "mid": _identity_continuation("mid", SMALL_N, state_count),
            "probe": _identity_continuation("probe", SMALL_N, state_count),
            "end": _identity_continuation("end", SMALL_N, state_count),
        },
        future_catalog={
            "mid": (("to_probe", "short_probe"), ("to_end", "merged_end")),
            "probe": (),
            "end": (),
        },
    )


def kovacs_wheel(state: int = WHEEL_STATE) -> RouteTransportPackage:
    """Return the reflection-pair Kovacs wheel package."""

    reflected = reflect(state, WHEEL_N)
    if reflected == state:
        raise ValueError("kovacs_wheel state must be non-palindromic under reflection")
    state_count = 1 << WHEEL_N
    left_panel = l_panel(state, WHEEL_N)
    if left_panel == l_panel(reflected, WHEEL_N):
        raise ValueError("kovacs_wheel state must be distinguishable by l_panel after reflection")
    invariant_panel = l_panel_reflection_invariant(state, WHEEL_N)
    return RouteTransportPackage(
        interfaces=("mid", "out"),
        projections={
            "mid": lambda state: l_panel_reflection_invariant(state, WHEEL_N),
            "out": lambda state: l_panel(state, WHEEL_N),
        },
        histories={
            "mid": (
                History("h_mid_0", "mid", {state: Fraction(1)}),
                History("h_mid_1", "mid", {reflected: Fraction(1)}),
            ),
            "out": (),
        },
        continuations={
            ("mid", "out"): (
                Continuation("to_out", "mid", "out", _identity_kernel(WHEEL_N, state_count)),
            ),
            ("mid", "mid"): (Continuation("swap_mid", "mid", "mid", _reflection_kernel(WHEEL_N)),),
        },
        events={
            "mid": (Event("reflection_panel", {invariant_panel: Fraction(1)}),),
            "out": (Event("first_spin_panel", {left_panel: Fraction(1)}),),
        },
        identity={
            "mid": _identity_continuation("mid", WHEEL_N, state_count),
            "out": _identity_continuation("out", WHEEL_N, state_count),
        },
        future_catalog={"mid": (("to_out", "first_spin_panel"),), "out": ()},
    )


def _two_state_package(
    *,
    state_left: int,
    state_right: int,
    mid_event: Event,
    to_out: Continuation,
    out_event: Event,
) -> RouteTransportPackage:
    _validate_state_pair(state_left, state_right, SMALL_N)
    state_count = 1 << SMALL_N
    return RouteTransportPackage(
        interfaces=("mid", "out"),
        projections={"mid": _state_projection, "out": _state_projection},
        histories={"mid": _two_dirac_histories("mid", state_left, state_right), "out": ()},
        continuations={("mid", "out"): (to_out,)},
        events={"mid": (mid_event,), "out": (out_event,)},
        identity={
            "mid": _identity_continuation("mid", SMALL_N, state_count),
            "out": _identity_continuation("out", SMALL_N, state_count),
        },
        future_catalog={"mid": (("to_out", out_event.label),), "out": ()},
    )


def _two_dirac_histories(
    interface: str, state_left: int, state_right: int
) -> tuple[History, History]:
    return (
        History("h_left", interface, {state_left: Fraction(1)}),
        History("h_right", interface, {state_right: Fraction(1)}),
    )


def _left_state_event(label: str, state_left: int, state_right: int) -> Event:
    return Event(label, {state_left: Fraction(1), state_right: Fraction(0)})


def _constant_event(label: str) -> Event:
    return Event(label, {label_value: Fraction(1) for label_value in range(SMALL_N + 1)})


def _identity_continuation(interface: str, N: int, state_count: int) -> Continuation:
    return Continuation(f"id_{interface}", interface, interface, _identity_kernel(N, state_count))


def _identity_between(
    label: str, source: str, target: str, N: int, state_count: int
) -> Continuation:
    return Continuation(label, source, target, _identity_kernel(N, state_count))


def _identity_kernel(N: int, state_count: int) -> Kernel:
    return _deterministic_kernel(N, state_count, lambda state: state)


def _constant_continuation(
    label: str, source: str, target: str, N: int, target_state: int
) -> Continuation:
    return Continuation(
        label, source, target, _deterministic_kernel(N, 1 << N, lambda _state: target_state)
    )


def _reflection_kernel(N: int) -> Kernel:
    return _deterministic_kernel(N, 1 << N, lambda state: reflect(state, N))


def _deterministic_kernel(N: int, state_count: int, target: Callable[[int], int]) -> Kernel:
    return Kernel(
        N=N,
        state_count=state_count,
        rows={state: {target(state): Fraction(1)} for state in range(state_count)},
    )


def _state_projection(state: int) -> Hashable:
    return state


def _validate_state_pair(state_left: int, state_right: int, N: int) -> None:
    state_count = 1 << N
    if state_left == state_right:
        raise ValueError("benchmark states must be distinct")
    if not (0 <= state_left < state_count and 0 <= state_right < state_count):
        raise ValueError(f"benchmark states must lie in 0..{state_count - 1}")
