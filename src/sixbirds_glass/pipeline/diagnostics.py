"""Exact route-transport diagnostics from [A] §10."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations

from sixbirds_glass.pipeline.package import RouteTransportPackage
from sixbirds_glass.pipeline.quotients import comparison_map, current_quotient, predictive_quotient
from sixbirds_glass.pipeline.signatures import future_signature


@dataclass(frozen=True)
class DiagnosticsSummary:
    """Artifact-facing diagnostic field bundle."""

    history_count: int
    current_quotient_size: int
    predictive_quotient_size: int
    max_fiber_size: int
    witness_count: int
    exact_max_abs_future_gap: Fraction


def witness_pairs(package: RouteTransportPackage, interface: str) -> tuple[tuple[str, str], ...]:
    """Return unordered witness pairs of declared history labels."""

    pairs: list[tuple[str, str]] = []
    future_by_label = {
        history.label: future_signature(package, history)
        for history in package.histories[interface]
    }
    for labels in current_quotient(package, interface).values():
        for left, right in combinations(labels, 2):
            if future_by_label[left] != future_by_label[right]:
                pairs.append((left, right) if left <= right else (right, left))
    return tuple(pairs)


def witness_count(package: RouteTransportPackage, interface: str) -> int:
    """Return the number of predictive witness pairs at an interface."""

    return len(witness_pairs(package, interface))


def max_fiber_size(package: RouteTransportPackage, interface: str) -> int:
    """Return ``max_fiber_size`` for ``pi_i: M_i -> Q_i``."""

    pi = comparison_map(package, interface)
    if not pi:
        return 0
    counts = Counter(pi.values())
    return max(counts.values())


def exact_max_abs_future_gap(package: RouteTransportPackage, interface: str) -> Fraction:
    """Return ``exact_max_abs_future_gap`` over current-class-mate pairs."""

    if len(package.histories[interface]) <= 1:
        return Fraction(0)

    future_by_label = {
        history.label: future_signature(package, history)
        for history in package.histories[interface]
    }
    gap = Fraction(0)
    for labels in current_quotient(package, interface).values():
        for left, right in combinations(labels, 2):
            gap = max(gap, _signature_gap(future_by_label[left], future_by_label[right]))
    return gap


def summarize(package: RouteTransportPackage, interface: str) -> DiagnosticsSummary:
    """Compute all interface diagnostics in one artifact-facing bundle."""

    q_i = current_quotient(package, interface)
    m_i = predictive_quotient(package, interface)
    return DiagnosticsSummary(
        history_count=len(package.histories[interface]),
        current_quotient_size=len(q_i),
        predictive_quotient_size=len(m_i),
        max_fiber_size=max_fiber_size(package, interface),
        witness_count=witness_count(package, interface),
        exact_max_abs_future_gap=exact_max_abs_future_gap(package, interface),
    )


def _signature_gap(left: tuple[Fraction, ...], right: tuple[Fraction, ...]) -> Fraction:
    if not left and not right:
        return Fraction(0)
    return max(
        abs(left_value - right_value) for left_value, right_value in zip(left, right, strict=True)
    )
