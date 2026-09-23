"""Exact current and future signatures for route-transport packages."""

from fractions import Fraction

from sixbirds_glass.pipeline.package import History, RouteTransportPackage, observe, push_history


def current_signature(package: RouteTransportPackage, history: History) -> tuple[Fraction, ...]:
    """Return ``s_i^0(h)`` in declared event order."""

    projection = package.projections[history.interface]
    return tuple(
        observe(history.distribution, projection, event)
        for event in package.events[history.interface]
    )


def future_signature(package: RouteTransportPackage, history: History) -> tuple[Fraction, ...]:
    """Return ``s_i^+(h)`` in declared future-catalog order."""

    values: list[Fraction] = []
    for continuation_label, event_label in package.future_catalog[history.interface]:
        continuation = package.continuation_by_label(history.interface, continuation_label)
        event = package.event_by_label(continuation.target, event_label)
        pushed = push_history(history, continuation)
        values.append(observe(pushed, package.projections[continuation.target], event))
    return tuple(values)
