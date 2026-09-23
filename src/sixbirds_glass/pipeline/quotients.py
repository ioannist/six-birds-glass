"""Current and predictive quotient computation."""

from collections.abc import Callable
from fractions import Fraction

from sixbirds_glass.pipeline.package import History, RouteTransportPackage
from sixbirds_glass.pipeline.signatures import current_signature, future_signature

Signature = tuple[Fraction, ...]
SignatureFn = Callable[[RouteTransportPackage, History], Signature]


def partition_by_signature(
    package: RouteTransportPackage, interface: str, signature_fn: SignatureFn
) -> dict[Signature, tuple[str, ...]]:
    """Group declared history labels by exact signature, preserving declared order."""

    groups: dict[Signature, list[str]] = {}
    for history in package.histories[interface]:
        signature = signature_fn(package, history)
        groups.setdefault(signature, []).append(history.label)
    return {signature: tuple(labels) for signature, labels in groups.items()}


def current_quotient(
    package: RouteTransportPackage, interface: str
) -> dict[Signature, tuple[str, ...]]:
    """Return ``Q_i`` keyed by current signatures."""

    return partition_by_signature(package, interface, current_signature)


def predictive_quotient(
    package: RouteTransportPackage, interface: str
) -> dict[Signature, tuple[str, ...]]:
    """Return ``M_i`` keyed by future signatures."""

    return partition_by_signature(package, interface, future_signature)


def comparison_map(package: RouteTransportPackage, interface: str) -> dict[Signature, Signature]:
    """Return ``pi_i: M_i -> Q_i`` and verify predictive refinement."""

    mapping: dict[Signature, Signature] = {}
    for predictive_key, labels in predictive_quotient(package, interface).items():
        current_keys = {
            current_signature(package, package.history_by_label(interface, label))
            for label in labels
        }
        if len(current_keys) != 1:
            raise ValueError(
                f"predictive class {predictive_key!r} does not refine one current class"
            )
        mapping[predictive_key] = next(iter(current_keys))
    return mapping
