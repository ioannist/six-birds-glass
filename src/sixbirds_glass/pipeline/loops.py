"""Loop actions on current and predictive quotients."""

from __future__ import annotations

from collections.abc import Sequence
from fractions import Fraction
from typing import Literal

from sixbirds_glass.pipeline.package import (
    Continuation,
    History,
    RouteTransportPackage,
    push_history,
)
from sixbirds_glass.pipeline.quotients import (
    Signature,
    SignatureFn,
    current_quotient,
    predictive_quotient,
)
from sixbirds_glass.pipeline.signatures import current_signature, future_signature
from sixbirds_glass.protocols.evolution import Distribution


def find_history_by_distribution(
    package: RouteTransportPackage, interface: str, distribution: Distribution
) -> History:
    """Find the unique declared history with an exactly matching distribution."""

    matches = [
        history for history in package.histories[interface] if history.distribution == distribution
    ]
    if not matches:
        raise ValueError(
            f"no declared history at interface {interface!r} matches distribution {distribution!r}"
        )
    if len(matches) > 1:
        labels = [history.label for history in matches]
        raise ValueError(
            f"multiple declared histories at interface {interface!r} match distribution "
            f"{distribution!r}: {labels}"
        )
    return matches[0]


def loop_action_on_quotient(
    package: RouteTransportPackage,
    interface: str,
    loop: Continuation,
    quotient: dict[Signature, tuple[str, ...]],
    signature_fn: SignatureFn,
) -> dict[Signature, Signature]:
    """Return the action of one loop on a Q- or M-shaped quotient."""

    if loop.source != interface or loop.target != interface:
        raise ValueError(
            f"loop {loop.label!r} must be an endo-continuation at {interface!r}; "
            f"got {loop.source!r}->{loop.target!r}"
        )

    action: dict[Signature, Signature] = {}
    for class_key, labels in quotient.items():
        representative = package.history_by_label(interface, labels[0])
        pushed = push_history(representative, loop)
        result_history = find_history_by_distribution(package, interface, pushed)
        result_key = signature_fn(package, result_history)
        if result_key not in quotient:
            raise ValueError(
                f"loop {loop.label!r} maps representative {representative.label!r} "
                f"to history {result_history.label!r} outside the supplied quotient"
            )
        action[class_key] = result_key
    return action


def loop_moved_fraction(action: dict[Signature, Signature]) -> Fraction:
    """Return the exact fraction of quotient classes moved by an action."""

    if not action:
        return Fraction(0)
    moved = sum(1 for source, target in action.items() if source != target)
    return Fraction(moved, len(action))


def loop_action_score(
    package: RouteTransportPackage,
    interface: str,
    loops: Sequence[Continuation],
    *,
    quotient_kind: Literal["current", "predictive"],
) -> Fraction:
    """Return max moved-class fraction over explicitly listed loops."""

    if not loops:
        return Fraction(0)
    if quotient_kind == "current":
        quotient = current_quotient(package, interface)
        signature_fn = current_signature
    elif quotient_kind == "predictive":
        quotient = predictive_quotient(package, interface)
        signature_fn = future_signature
    else:
        raise ValueError(f"unknown quotient_kind {quotient_kind!r}")

    return max(
        loop_moved_fraction(
            loop_action_on_quotient(package, interface, loop, quotient, signature_fn)
        )
        for loop in loops
    )
