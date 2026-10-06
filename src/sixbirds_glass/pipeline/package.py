"""Exact-finite route-transport package declarations."""

from __future__ import annotations

from collections.abc import Callable, Hashable
from dataclasses import dataclass
from fractions import Fraction

from sixbirds_glass.models.kernels import Kernel, validate_kernel_rows
from sixbirds_glass.protocols.evolution import Distribution, push

Projection = Callable[[int], Hashable]


@dataclass(frozen=True)
class History:
    """A declared rational distribution at an interface."""

    label: str
    interface: str
    distribution: Distribution


@dataclass(frozen=True)
class Event:
    """A rational weight function on visible support labels."""

    label: str
    weights: dict[Hashable, Fraction]


@dataclass(frozen=True)
class Continuation:
    """A declared continuation kernel from one interface to another."""

    label: str
    source: str
    target: str
    kernel: Kernel


@dataclass(frozen=True)
class RouteTransportPackage:
    """Declared exact-finite route-transport package."""

    interfaces: tuple[str, ...]
    projections: dict[str, Projection]
    histories: dict[str, tuple[History, ...]]
    continuations: dict[tuple[str, str], tuple[Continuation, ...]]
    events: dict[str, tuple[Event, ...]]
    identity: dict[str, Continuation]
    future_catalog: dict[str, tuple[tuple[str, str], ...]]

    def __post_init__(self) -> None:
        self._validate_interfaces()
        self._validate_histories()
        self._validate_events()
        self._validate_continuations()
        self._validate_future_catalog()

    def continuation_by_label(self, source: str, label: str) -> Continuation:
        matches = [
            continuation
            for continuation in self.identity.values()
            if continuation.source == source and continuation.label == label
        ]
        matches.extend(
            continuation
            for (continuation_source, _target), continuations in self.continuations.items()
            if continuation_source == source
            for continuation in continuations
            if continuation.label == label
        )
        if len(matches) != 1:
            raise ValueError(
                f"continuation label {label!r} from interface {source!r} "
                f"resolved to {len(matches)} declarations"
            )
        return matches[0]

    def event_by_label(self, interface: str, label: str) -> Event:
        matches = [event for event in self.events[interface] if event.label == label]
        if len(matches) != 1:
            raise ValueError(
                f"event label {label!r} at interface {interface!r} "
                f"resolved to {len(matches)} declarations"
            )
        return matches[0]

    def history_by_label(self, interface: str, label: str) -> History:
        matches = [history for history in self.histories[interface] if history.label == label]
        if len(matches) != 1:
            raise ValueError(
                f"history label {label!r} at interface {interface!r} "
                f"resolved to {len(matches)} declarations"
            )
        return matches[0]

    def _validate_interfaces(self) -> None:
        interface_set = set(self.interfaces)
        if not self.interfaces or len(interface_set) != len(self.interfaces):
            raise ValueError("interfaces must be nonempty and unique")
        for mapping_name, keys in (
            ("projections", self.projections.keys()),
            ("histories", self.histories.keys()),
            ("events", self.events.keys()),
            ("identity", self.identity.keys()),
            ("future_catalog", self.future_catalog.keys()),
        ):
            unknown = set(keys) - interface_set
            if unknown:
                raise ValueError(
                    f"{mapping_name} contains undeclared interfaces: {sorted(unknown)}"
                )
            missing = interface_set - set(keys)
            if missing:
                raise ValueError(f"missing {mapping_name} for interfaces: {sorted(missing)}")

    def _validate_histories(self) -> None:
        for interface, histories in self.histories.items():
            labels = [history.label for history in histories]
            if len(set(labels)) != len(labels):
                raise ValueError(f"duplicate history labels at interface {interface!r}")
            for history in histories:
                if history.interface != interface:
                    raise ValueError(
                        f"history {history.label!r} declared under {interface!r} "
                        f"but has interface {history.interface!r}"
                    )
                for state, mass in history.distribution.items():
                    if not isinstance(mass, Fraction):
                        raise ValueError(
                            f"history {history.label!r} has non-Fraction mass at state "
                            f"{state}: {mass!r}"
                        )
                    if mass < 0:
                        raise ValueError(
                            f"history {history.label!r} has negative mass at state {state}: {mass}"
                        )
                total = sum(history.distribution.values(), start=Fraction(0))
                if total != Fraction(1):
                    raise ValueError(f"history {history.label!r} distribution must sum to 1")

    def _validate_events(self) -> None:
        for interface, events in self.events.items():
            labels = [event.label for event in events]
            if len(set(labels)) != len(labels):
                raise ValueError(f"duplicate event labels at interface {interface!r}")
            for event in events:
                for label, weight in event.weights.items():
                    if not isinstance(weight, Fraction):
                        raise ValueError(
                            f"event {event.label!r} at interface {interface!r} has "
                            f"non-Fraction weight for label {label!r}: {weight!r}"
                        )

    def _validate_continuations(self) -> None:
        interface_set = set(self.interfaces)
        for interface, identity in self.identity.items():
            if identity.source != interface or identity.target != interface:
                raise ValueError(f"identity at {interface!r} must be an endo-continuation")
            self._validate_kernel_rows(identity)
            for state, row in identity.kernel.rows.items():
                if row.get(state, Fraction(0)) != 1:
                    raise ValueError(f"identity at {interface!r} does not fix state {state}")
            for history in self.histories[interface]:
                for state in history.distribution:
                    if not isinstance(state, int) or not 0 <= state < identity.kernel.state_count:
                        raise ValueError(
                            f"history {history.label!r} has out-of-range state {state}"
                        )
        for (source, target), continuations in self.continuations.items():
            if source not in interface_set or target not in interface_set:
                raise ValueError("continuations contains an undeclared source/target key")
            for continuation in continuations:
                if continuation.source != source or continuation.target != target:
                    raise ValueError(f"continuation {continuation.label!r} disagrees with its key")
        labels_by_source: set[tuple[str, str]] = set()
        all_continuations = [
            *self.identity.values(),
            *(
                continuation
                for continuations in self.continuations.values()
                for continuation in continuations
            ),
        ]
        for continuation in all_continuations:
            if continuation.source not in interface_set or continuation.target not in interface_set:
                raise ValueError(
                    f"continuation {continuation.label!r} has undeclared source/target "
                    f"{continuation.source!r}->{continuation.target!r}"
                )
            label_key = (continuation.source, continuation.label)
            if label_key in labels_by_source:
                raise ValueError(
                    f"duplicate continuation label {continuation.label!r} "
                    f"from {continuation.source!r}"
                )
            labels_by_source.add(label_key)
            self._validate_kernel_rows(continuation)
            if any(
                continuation.kernel.state_count != self.identity[interface].kernel.state_count
                for interface in (continuation.source, continuation.target)
            ):
                raise ValueError(
                    f"continuation {continuation.label!r} has inconsistent carrier size"
                )

    def _validate_kernel_rows(self, continuation: Continuation) -> None:
        validate_kernel_rows(continuation.kernel, label=f"continuation {continuation.label!r}")

    def _validate_future_catalog(self) -> None:
        interface_set = set(self.interfaces)
        unknown = set(self.future_catalog) - interface_set
        if unknown:
            raise ValueError(f"future_catalog contains undeclared interfaces: {sorted(unknown)}")
        for source, entries in self.future_catalog.items():
            for continuation_label, event_label in entries:
                continuation = self.continuation_by_label(source, continuation_label)
                self.event_by_label(continuation.target, event_label)


def push_history(history: History, continuation: Continuation) -> Distribution:
    """Push one declared history through one declared continuation."""

    if history.interface != continuation.source:
        raise ValueError(
            f"history {history.label!r} at {history.interface!r} cannot be pushed "
            f"through continuation {continuation.label!r} from {continuation.source!r}"
        )
    return push(history.distribution, continuation.kernel)


def observe(distribution: Distribution, projection: Projection, event: Event) -> Fraction:
    """Observe an event after projecting internal states to visible labels."""

    return sum(
        (
            mass * event.weights.get(projection(state), Fraction(0))
            for state, mass in distribution.items()
        ),
        start=Fraction(0),
    )
