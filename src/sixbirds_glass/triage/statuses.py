"""Paired-control status helpers for the six-regime triage layer."""

from __future__ import annotations

from collections.abc import Hashable
from typing import Literal

from sixbirds_glass.pipeline.diagnostics import DiagnosticsSummary
from sixbirds_glass.pipeline.package import RouteTransportPackage

SupportFixationStatus = Literal["ok", "failed"]
RepairStatus = Literal["passed", "skipped"]


def support_labels(package: RouteTransportPackage, interface: str) -> frozenset[Hashable]:
    """Return visible support labels realized by declared histories at an interface."""

    projection = package.projections[interface]
    return frozenset(
        projection(state)
        for history in package.histories[interface]
        for state in history.distribution
    )


def support_fixation_status(
    base_package: RouteTransportPackage,
    base_interface: str,
    other_package: RouteTransportPackage,
    other_interface: str,
) -> SupportFixationStatus:
    """Return whether two compared packages share the same visible support."""

    if support_labels(base_package, base_interface) != support_labels(
        other_package, other_interface
    ):
        return "failed"
    return "ok"


def flattening_status(
    base_summary: DiagnosticsSummary,
    completed_summary: DiagnosticsSummary,
    support_status: SupportFixationStatus,
) -> RepairStatus:
    """Return completion/flattening status for a base/completed pair."""

    if (
        support_status == "ok"
        and base_summary.witness_count > 0
        and completed_summary.witness_count == 0
        and completed_summary.exact_max_abs_future_gap == 0
    ):
        return "passed"
    return "skipped"


def currentization_status(
    base_summary: DiagnosticsSummary,
    refined_summary: DiagnosticsSummary,
    support_status: SupportFixationStatus,
) -> RepairStatus:
    """Return currentization status for a base/refined pair."""

    if (
        support_status == "ok"
        and base_summary.witness_count > 0
        and refined_summary.witness_count == 0
        and refined_summary.exact_max_abs_future_gap == 0
        and refined_summary.max_fiber_size == 1
    ):
        return "passed"
    return "skipped"
