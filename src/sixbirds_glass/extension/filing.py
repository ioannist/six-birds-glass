"""GT6 filing records and verdict recomputation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Verdict = Literal["strict", "non_strict", "failed"]
REQUIRED_GATES = (
    "G_suff",
    "G_desc",
    "G_stab",
    "G_ctrl",
    "G_nosmuggle",
    "G_vis",
    "G_audit",
    "G_strict",
    "G_locglob",
)
EXCLUSION_CHECKS = (
    "missing_or_infinite_component",
    "host_tag_outside_host",
    "level_tag_outside_lev",
    "package_failing_admpkg",
    "inadmissible_instrument",
    "inadmissible_profile",
    "witness_update_actor_informant_violation",
    "unresolved_or_incomplete_record_reference",
    "malformed_audit_record",
    "unknown_or_contradictory_source",
    "missing_required_nonclaim",
    "model_realization_asserted_as_universal_theorem",
)


@dataclass(frozen=True)
class GateRecord:
    """One F-III gate row."""

    gate: str
    status: str
    required: bool
    evidence: str


@dataclass(frozen=True)
class GateTable:
    """The nine-gate GT6 strict-extension filing table."""

    gates: tuple[GateRecord, ...]


@dataclass(frozen=True)
class ExclusionCheck:
    """One AdmDomain exclusion-condition check."""

    check: str
    violated: bool
    note: str


@dataclass(frozen=True)
class AdmDomainRecord:
    """Minimal finite AdmDomain record for the KCM host."""

    primitives: tuple[str, ...]
    levels: tuple[str, ...]
    host: tuple[str, ...]
    content: tuple[str, ...]
    instrument: tuple[str, ...]
    packages: tuple[str, ...]
    witnesses: tuple[str, ...]
    updates: tuple[str, ...]
    defects: tuple[str, ...]
    judgments: tuple[str, ...]
    status: tuple[str, ...]
    gates: tuple[str, ...]
    dependencies: tuple[str, ...]
    audit: tuple[str, ...]
    source: tuple[str, ...]
    visibility: tuple[str, ...]
    nonclaims: tuple[str, ...]
    realization: str
    exclusion_checks: tuple[ExclusionCheck, ...]
    notes: tuple[str, ...]


@dataclass(frozen=True)
class BridgeRecord:
    """Full 17-field glass T0 -> T1 bridge record."""

    id: str
    T0: str
    T1: str
    carrier_S: dict[str, object]
    O0: dict[str, object]
    O1: dict[str, object]
    pi0: dict[str, object]
    pi1: dict[str, object]
    L: dict[str, object]
    V: dict[str, object]
    Theta: dict[str, object]
    A: dict[str, object]
    delta: dict[str, object]
    GateResults: list[dict[str, str | bool]]
    N: tuple[str, ...]
    HostTag: str
    lambda_prom: dict[str, object]


def build_gate_table() -> GateTable:
    """Assemble the spec-fixed GT6 gate values with upstream evidence labels."""

    return GateTable(
        gates=(
            GateRecord("G_suff", "pass", True, "audit.json filing assembled"),
            GateRecord(
                "G_desc",
                "not_required",
                False,
                "glass bridge claims strict object-map enrichment, not closed macro dynamics",
            ),
            GateRecord("G_stab", "pass", True, "P3-04 saturated strata under E_{tau,f}"),
            GateRecord("G_ctrl", "pass", True, "P3-01 knockout panel controls"),
            GateRecord("G_nosmuggle", "pass", True, "six no-smuggling violation kinds checked"),
            GateRecord("G_vis", "pass", True, "visible citations and nonclaims filed"),
            GateRecord("G_audit", "pass", True, "checker validates hashes and verdict"),
            GateRecord("G_strict", "strict_pass", True, "GT2/GT3 constructive split witnesses"),
            GateRecord(
                "G_locglob",
                "not_required",
                False,
                "shell-bound single bridge only; no stacked or glued promotions claimed",
            ),
        )
    )


def validate_gate_table(gate_table: GateTable) -> None:
    """Require the closed declared gate set: no missing, extra, or duplicated gates."""

    names = [record.gate for record in gate_table.gates]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    if duplicates:
        raise ValueError(f"duplicate gate entries: {duplicates}")
    observed = set(names)
    expected = set(REQUIRED_GATES)
    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    if missing or extra:
        raise ValueError(f"gate table mismatch: missing={missing}, extra={extra}")


def recompute_verdict(gate_table: GateTable) -> Verdict:
    """Recompute the filing verdict from gate values."""

    try:
        validate_gate_table(gate_table)
    except ValueError:
        return "failed"
    gate_status = {record.gate: record.status for record in gate_table.gates}
    required_failures = [
        record
        for record in gate_table.gates
        if record.required and record.gate != "G_strict" and record.status != "pass"
    ]
    if required_failures:
        return "failed"
    if gate_status.get("G_desc") not in {"not_required", "pass"}:
        return "failed"
    if gate_status.get("G_locglob") != "not_required":
        return "failed"
    strict_status = gate_status.get("G_strict")
    if strict_status == "strict_pass":
        return "strict"
    if strict_status in {"pass", "not_strict"}:
        return "non_strict"
    return "failed"


def gate_table_to_payload(gate_table: GateTable) -> list[dict[str, str | bool]]:
    """Serialize a gate table to JSON-compatible rows."""

    return [
        {
            "gate": record.gate,
            "status": record.status,
            "required": record.required,
            "evidence": record.evidence,
        }
        for record in gate_table.gates
    ]


def gate_table_from_payload(rows: list[dict[str, object]]) -> GateTable:
    """Parse JSON rows back into a gate table."""

    return GateTable(
        gates=tuple(
            GateRecord(
                gate=str(row["gate"]),
                status=str(row["status"]),
                required=bool(row["required"]),
                evidence=str(row["evidence"]),
            )
            for row in rows
        )
    )


def default_exclusion_checks() -> tuple[ExclusionCheck, ...]:
    """Return the all-clear F-III AdmDomain exclusion ledger for this filing."""

    notes = {
        "missing_or_infinite_component": "all components are finite JSON records",
        "host_tag_outside_host": "HostTag is H_prob and Host contains H_prob",
        "level_tag_outside_lev": "levels are restricted to Beh, Ver, Str",
        "package_failing_admpkg": "packages are named finite RouteTransport/packaging records",
        "inadmissible_instrument": "instrument is the finite East simulator plus pytest checker",
        "inadmissible_profile": "lambda_prom is the shell-local strict-promotion profile",
        "witness_update_actor_informant_violation": "P1-P6 witness/update roles follow GT6 mapping",
        "unresolved_or_incomplete_record_reference": "checker resolves artifact hashes and fields",
        "malformed_audit_record": "artifact envelope schema validates",
        "unknown_or_contradictory_source": "sources are design specs and generated artifacts",
        "missing_required_nonclaim": "checker verifies the required nonclaim set",
        "model_realization_asserted_as_universal_theorem": "nonclaims file model-only shell scope",
    }
    return tuple(
        ExclusionCheck(check=check, violated=False, note=notes[check]) for check in EXCLUSION_CHECKS
    )
