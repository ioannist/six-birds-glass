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
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

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
AXIOMS_BY_LEAN_NAME = {
    "futurePredictiveEquiv_implies_currentEventEquiv": [],
    "predictiveToCurrent_commutes_with_transport": ["propext", "Quot.sound"],
    "predictiveQuotient_futureSufficient": [],
    "futureSufficient_stateEq_implies_futurePredictiveEquiv": [],
    "futureSufficient_factorsThroughPredictiveQuotient_onReachable": [
        "Classical.choice",
        "Quot.sound",
    ],
    "futureSufficient_factorization_unique_onReachable": [
        "Classical.choice",
        "Quot.sound",
    ],
    "strictRefinement_iff_nonempty_predictiveWitness": ["propext", "Quot.sound"],
    "loopAsymmetry_exhibits_movedPredictive_fixedCurrent": ["propext", "Quot.sound"],
    "current_implies_future_GENERIC": [],
    "predictiveWitness_impossible_GENERIC": [],
    "strictRefinement_impossible_GENERIC": ["propext", "Quot.sound"],
    "glassPredictiveQuotient_futureSufficient": [],
}
AXIOM_REPORT_BY_LEAN_NAME = {
    name: (
        "does not depend on any axioms"
        if axioms == []
        else "depends on axioms: [" + ", ".join(axioms) + "]"
    )
    for name, axioms in AXIOMS_BY_LEAN_NAME.items()
}
SCOPE_BOUNDARY_FINDING = (
    "For every RouteTransportCore instance, CurrentEventEquiv implies "
    "FuturePredictiveEquiv via pullEvent and observe_push. PredictiveWitness, "
    "StrictRefinement, and non-vacuous LoopAsymmetry therefore cannot be "
    "instantiated honestly in this core; the real Kovacs numeric witness remains "
    "an exact-rational Python certificate only. The closest precedents are "
    "Kemeny-Snell strong lumpability for the proof shape and Chu-space "
    "biextensional collapse for the vocabulary."
)
VACUOUS_NOTE = (
    "True as a general implication, but its antecedent is unsatisfiable for any "
    "RouteTransportCore instance -- see strictRefinement_impossible_GENERIC "
    "(P4-11) -- so this theorem cannot be witnessed non-vacuously by any "
    "concrete instance, glass or otherwise."
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
    rows = _rows()
    return {
        "artifact_kind": "lean_fidelity_table",
        "claim_id": "GB9.lean_fidelity_table",
        "config_hash": config_hash(
            {
                "rows": rows,
                "scope_boundary_finding": SCOPE_BOUNDARY_FINDING,
                "fidelity_legend": FIDELITY_LEGEND,
            }
        ),
        "config_path": "lean/",
        "code_version": _code_version(),
        "claim_grade": "recognition",
        "evidence_type": "lean_checked",
        "scope_boundary_finding": SCOPE_BOUNDARY_FINDING,
        "quantifier_domain": {
            "model_families": ["abstract_route_transport", "glass_structural_instance"],
            "N_values": [],
            "epsilon_grid": [],
            "lens_catalog_hash": config_hash({"lean": "RouteTransportCore"}),
            "protocol_catalog_hash": config_hash({"lean": "HolonomyMemory+GlassWitness"}),
        },
        "nonclaims": [
            "The real Kovacs numeric split-pair witness is not encoded in Lean.",
            (
                "No non-vacuous PredictiveWitness, StrictRefinement, or LoopAsymmetry instance "
                "is claimed."
            ),
            (
                "The GlassWitness instance is structural and index-based, not a real numeric "
                "package export."
            ),
        ],
        "payload": {
            "fidelity_legend": FIDELITY_LEGEND,
            "allowed_extra_fidelity": COMPUTATIONAL_ONLY,
            "native_decide_grep_result": _native_decide_grep_result(),
            "rows": rows,
        },
    }


def _rows() -> list[dict[str, Any]]:
    rows = [
        _row(
            "A Thm 3.1: future predictive equivalence implies current event equivalence",
            "futurePredictiveEquiv_implies_currentEventEquiv",
            "lean/HolonomyMemory/Equivalences.lean",
            "verified",
            "Vendored unchanged; abstract generic implication.",
        ),
        _row(
            "A Thm 3.2: predictive-to-current map commutes with transport",
            "predictiveToCurrent_commutes_with_transport",
            "lean/HolonomyMemory/Transport.lean",
            "verified",
            "Vendored unchanged; abstract generic implication.",
        ),
        _row(
            "A Thm 3.3: predictive quotient is future-sufficient",
            "predictiveQuotient_futureSufficient",
            "lean/HolonomyMemory/Sufficiency.lean",
            "verified",
            "Vendored unchanged; abstract generic theorem.",
        ),
        _row(
            "Kernel-refinement lemma: sufficient state equality implies future equivalence",
            "futureSufficient_stateEq_implies_futurePredictiveEquiv",
            "lean/HolonomyMemory/Sufficiency.lean",
            "verified",
            "Vendored unchanged; abstract generic theorem.",
        ),
        _row(
            (
                "A Thm 3.4: future-sufficient states factor through predictive quotient on "
                "reachable states"
            ),
            "futureSufficient_factorsThroughPredictiveQuotient_onReachable",
            "lean/HolonomyMemory/Sufficiency.lean",
            "verified",
            "Vendored unchanged; abstract generic theorem.",
        ),
        _row(
            "A Thm 3.4: reachable factorization uniqueness",
            "futureSufficient_factorization_unique_onReachable",
            "lean/HolonomyMemory/Sufficiency.lean",
            "verified",
            "Vendored unchanged; abstract generic theorem.",
        ),
        _row(
            "A Thm 3.5: strict refinement iff nonempty predictive witness",
            "strictRefinement_iff_nonempty_predictiveWitness",
            "lean/HolonomyMemory/Witnesses.lean",
            "verified",
            VACUOUS_NOTE,
        ),
        _row(
            "A Thm 3.6: loop asymmetry exhibits moved predictive class with fixed current image",
            "loopAsymmetry_exhibits_movedPredictive_fixedCurrent",
            "lean/HolonomyMemory/Asymmetry.lean",
            "verified",
            VACUOUS_NOTE,
        ),
        _row(
            "GB9 scope-boundary lemma: current equivalence implies future equivalence",
            "current_implies_future_GENERIC",
            "lean/GlassWitness/ScopeBoundary.lean",
            "verified",
            "New derivation from RouteTransportCore axioms.",
        ),
        _row(
            "GB9 corollary: predictive witnesses are impossible in RouteTransportCore",
            "predictiveWitness_impossible_GENERIC",
            "lean/GlassWitness/ScopeBoundary.lean",
            "verified",
            "New corollary of current_implies_future_GENERIC.",
        ),
        _row(
            "GB9 corollary: strict refinement is impossible in RouteTransportCore",
            "strictRefinement_impossible_GENERIC",
            "lean/GlassWitness/ScopeBoundary.lean",
            "verified",
            "Proved through predictiveWitness_impossible_GENERIC and the vendored iff theorem.",
        ),
        _row(
            "glassInstance coherence proof: push_id",
            "push_id",
            "lean/GlassWitness/Instance.lean",
            "narrowed / parametric",
            "Real proof over one small structural glass-shaped instance.",
        ),
        _row(
            "glassInstance coherence proof: observe_push",
            "observe_push",
            "lean/GlassWitness/Instance.lean",
            "narrowed / parametric",
            "Real proof over one small structural glass-shaped instance.",
        ),
        _row(
            "glassInstance coherence proof: push_compose",
            "push_compose",
            "lean/GlassWitness/Instance.lean",
            "narrowed / parametric",
            "Real proof over one small structural glass-shaped instance.",
        ),
        _row(
            "glassInstance structural RouteTransportCore data",
            "glassInstance",
            "lean/GlassWitness/Instance.lean",
            "typed mirror",
            "Typed structural mirror of the two-interface Kovacs package shape.",
        ),
        _row(
            "Specialization of predictive quotient sufficiency to glassInstance at mid",
            "glassPredictiveQuotient_futureSufficient",
            "lean/GlassWitness/Instance.lean",
            "schema (projection)",
            "Specializes an already-proven generic theorem to one instance.",
        ),
        {
            "paper_or_project_claim": "Real Kovacs exact-rational numeric split-pair witness",
            "lean_name": None,
            "lean_file": None,
            "fidelity": COMPUTATIONAL_ONLY,
            "native_decide_used": False,
            "notes": (
                "No Lean encoding is claimed or attempted for this witness's real numeric values; "
                "current_implies_future_GENERIC shows any such attempt would be incoherent under "
                "RouteTransportCore's axioms. This certificate's exact-rational Python computation "
                "(evidence_type: exact_rational in its own artifact envelope) is the only claim "
                "made about it: artifacts/gt2_witnesses/kovacs_moment.json."
            ),
        },
    ]
    return rows


def _row(
    paper_or_project_claim: str,
    lean_name: str,
    lean_file: str,
    fidelity: str,
    notes: str,
) -> dict[str, Any]:
    row = {
        "paper_or_project_claim": paper_or_project_claim,
        "lean_name": lean_name,
        "lean_file": lean_file,
        "fidelity": fidelity,
        "native_decide_used": False,
        "notes": notes,
    }
    if lean_name in AXIOMS_BY_LEAN_NAME:
        row["axioms"] = AXIOMS_BY_LEAN_NAME[lean_name]
        row["axioms_raw"] = AXIOM_REPORT_BY_LEAN_NAME[lean_name]
    return row


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
