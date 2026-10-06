"""Build the GB9 Lean fidelity inventory artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from experiments.audit_lean_axioms import build_audit  # noqa: E402

from sixbirds_glass.io.config import config_hash  # noqa: E402

OUTPUT_PATH = REPO_ROOT / "artifacts" / "lean_fidelity_table.json"

FIDELITY_LEGEND = [
    "verified",
    "narrowed / parametric",
    "schema (projection)",
    "trivial",
    "typed mirror",
]
COMPUTATIONAL_ONLY = "computational evidence only"
SCOPE_BOUNDARY_FINDING = (
    "The legacy HolonomyMemory core is pullback-closed, so current equivalence "
    "already implies future equivalence and its strictness antecedents are "
    "unsatisfiable. The corrected DeclaredMemory core removes this collapse "
    "premise and admits non-vacuous exported N8/N10 mean-energy witnesses and "
    "the N8 full-energy-law witness. Python replays preparation and evolution; "
    "Lean checks the actual rational tables and their logical consequences."
)
VACUOUS_NOTE = (
    "In the legacy HolonomyMemory core, the strictness/asymmetry antecedent is "
    "unsatisfiable; see strictRefinement_impossible_GENERIC and "
    "loopAsymmetry_impossible_GENERIC. This limitation does not apply to the "
    "corrected DeclaredMemory core."
)


def main(output_path: Path = OUTPUT_PATH) -> None:
    artifact = build_artifact()
    _validate_artifact(artifact)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(
        "lean_fidelity_table "
        f"rows={len(artifact['payload']['rows'])} "
        f"claim_grade={artifact['claim_grade']} "
        f"wrote={output_path}"
    )


def build_artifact() -> dict[str, Any]:
    audit = build_audit()
    rows = _rows(audit)
    return {
        "artifact_kind": "lean_fidelity_table",
        "claim_id": "GB9.lean_fidelity_table",
        "config_hash": config_hash(
            {
                "rows": rows,
                "theorem_count": audit["theorem_count"],
                "source_sha256": audit["source_sha256"],
                "factorization_direction": (
                    "ReachableState(S) -> PredictiveQuotient(M): M factors through S. "
                    "S need not be a function of M; it may retain redundant information."
                ),
                "scope_boundary_finding": SCOPE_BOUNDARY_FINDING,
                "fidelity_legend": FIDELITY_LEGEND,
            }
        ),
        "config_path": "lean/",
        "code_version": _code_version(),
        "claim_grade": "bridge_record",
        "evidence_type": "lean_checked",
        "scope_boundary_finding": SCOPE_BOUNDARY_FINDING,
        "quantifier_domain": {
            "model_families": [
                "legacy_pullback_closed_core",
                "declared_event_core",
                "glass_numeric_lookup",
            ],
            "N_values": [],
            "epsilon_grid": [],
            "lens_catalog_hash": config_hash({"lean": "RouteTransportCore"}),
            "protocol_catalog_hash": config_hash(
                {"lean": "HolonomyMemory+DeclaredMemory+GlassWitness"}
            ),
        },
        "nonclaims": [
            "Full East kernel evolution, preparation and tuning are exact Python evidence.",
            "Lean's numeric strictness concerns the exported finite observation tables.",
            "No shell-general, asymptotic or packaging-fixed-point theorem is mechanized.",
            "The legacy glassInstance remains a structural index-based instance.",
        ],
        "payload": {
            "fidelity_legend": FIDELITY_LEGEND,
            "allowed_extra_fidelity": COMPUTATIONAL_ONLY,
            "native_decide_grep_result": _native_decide_grep_result(),
            "rows": rows,
            "theorem_count": audit["theorem_count"],
            "source_sha256": audit["source_sha256"],
            "factorization_direction": (
                "ReachableState(S) -> PredictiveQuotient(M): M factors through S. "
                "S need not be a function of M; it may retain redundant information."
            ),
        },
    }


def _rows(audit: dict[str, Any]) -> list[dict[str, Any]]:
    import re

    declarations: dict[str, str] = {}
    for relative in audit["source_sha256"]:
        source = (REPO_ROOT / relative).read_text()
        namespaces = re.findall(r"^namespace ([^\s]+)", source, re.M)
        if not namespaces:
            continue
        if len(namespaces) != 1:
            raise ValueError(f"ambiguous namespace in {relative}")
        for name in re.findall(r"^(?:@\[[^\n]*\]\s*)?theorem\s+([^\s]+)", source, re.M):
            declarations[f"{namespaces[0]}.{name}"] = relative
    rows = []
    for theorem in audit["theorems"]:
        full_name = theorem["declaration"]
        relative = declarations[full_name]
        fidelity, notes = _scope(full_name, relative)
        rows.append(
            {
                "paper_or_project_claim": full_name,
                "lean_name": full_name.rsplit(".", 1)[1],
                "qualified_lean_name": full_name,
                "lean_file": relative,
                "fidelity": fidelity,
                "native_decide_used": False,
                "axioms": theorem["axioms"],
                "axioms_raw": theorem["raw"],
                "notes": notes,
            }
        )
    rows.append(
        {
            "paper_or_project_claim": (
                "Full East preparation, stopping-mixture construction and evolution"
            ),
            "lean_name": None,
            "qualified_lean_name": None,
            "lean_file": None,
            "fidelity": COMPUTATIONAL_ONLY,
            "native_decide_used": False,
            "notes": (
                "Exact Python source replay; rational lookup consequences are separately in Lean."
            ),
        }
    )
    return rows


def _scope(name: str, relative: str) -> tuple[str, str]:
    if relative.startswith("lean/HolonomyMemory/"):
        notes = "Generic theorem in the legacy pullback-closed core."
        if relative.endswith(("Witnesses.lean", "Asymmetry.lean")):
            notes += " " + VACUOUS_NOTE
        elif "Sufficiency" in relative:
            notes += " The factor map has direction ReachableState(S) -> PredictiveQuotient(M)."
        return "verified", notes
    if relative.startswith("lean/DeclaredMemory/"):
        notes = "Generic theorem in the corrected declared-event core."
        if "commutes" in name:
            notes += " Transport compatibility is an explicit hypothesis."
        if "Sufficiency" in relative:
            notes += " The factor map has direction ReachableState(S) -> PredictiveQuotient(M)."
        return "verified", notes
    if "ScopeBoundary" in relative:
        return "verified", "Proves the legacy core's collapse and impossibility consequences."
    if "NumericN" in relative or "EnergyN" in relative:
        return "narrowed / parametric", (
            "Actual recomputed rational lookup witness in the corrected core; "
            "kernel evolution remains exact Python. EnergyN8 covers the complete "
            "current energy law and every future horizon 1..21; NumericN8/N10 "
            "cover current mean energy and one declared continuation."
        )
    if "NumericCore" in relative or "EnergyCore" in relative:
        return "narrowed / parametric", (
            "Finite lookup implication in the corrected core; strictness requires "
            "an actual rational split. Constant-future negative controls are proved."
        )
    return "schema (projection)", "Specializes a generic theorem to the legacy structural instance."


def _native_decide_grep_result() -> str:
    result = subprocess.run(
        ["rg", "-n", "native_decide", "lean"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _validate_artifact(artifact: dict[str, Any]) -> None:
    Draft202012Validator(
        _load_json(REPO_ROOT / "design/schemas/artifact_envelope.schema.json")
    ).validate(artifact)


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"{path} did not contain a JSON object")
    return data


def _code_version() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return "unknown" if result.returncode != 0 else result.stdout.strip()


if __name__ == "__main__":
    main()
