"""Validate (and re-stamp/render) the Phase 5 paper claims ledger.

The ledger (``paper/claims_ledger.json``) is hand-authored content: its wording is the
paper's final claim wording, so there is no generator. This checker keeps it honest:

- structural schema per row (required fields, allowed kinds, required row ids),
- every cited artifact resolves against ``paper/evidence_manifest.json`` AND current bytes,
- every enveloped artifact under ``artifacts/`` is reachable from at least one row,
- wording guards (the remediation denylist plus per-row required qualifiers),
- F-II section-16 item ids and paper-section labels are from the declared finite sets,
- the manifest binding, the ledger self-hash, and the rendered markdown are all current.

Usage:
    python experiments/check_claims_ledger.py            # validate, exit nonzero on failure
    python experiments/check_claims_ledger.py --stamp    # re-stamp content_hash + render md
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from sixbirds_glass.io.config import canonical_json_bytes  # noqa: E402

LEDGER_PATH = REPO_ROOT / "paper" / "claims_ledger.json"
LEDGER_MD_PATH = REPO_ROOT / "paper" / "claims_ledger.md"
MANIFEST_PATH = REPO_ROOT / "paper" / "evidence_manifest.json"

ALLOWED_KINDS = ("gt_claim", "gb_bridge", "finding", "honest_negative")

REQUIRED_ROW_IDS = (
    "GT1",
    "GT2",
    "GT3",
    "GT4",
    "GT5",
    "GT6",
    "GT7",
    "GB1",
    "GB2",
    "GB9",
    "GB10",
    "FINDING.trap_epsilon_invariance",
    "FINDING.lean_collapse",
    "NEG.material_forcing_absent",
    "NEG.gt7_transfer_failures",
    "NEG.gb5_repair_sweep_not_built",
    "NEG.gt2_loop_certificate_not_built",
    "NEG.gt1_b_parity_control_open",
    "NEG.lean_instance_structural",
)

REQUIRED_ROW_FIELDS = (
    "row_id",
    "kind",
    "title",
    "claim_statement",
    "claim_grade",
    "grade_note",
    "quantifier_domain",
    "anchor_rows",
    "anchor_note",
    "artifacts",
    "disclosure_refs",
    "nonclaims",
    "f2_s16_items",
    "paper_section",
)

F2_S16_ITEM_IDS = (
    "A1",
    "A2",
    "A3",
    "B1",
    "B2",
    "B3",
    "B4",
    "B5",
    "C1",
    "C2",
    "C3",
    "D1",
    "D2",
    "D3",
    "D4",
    "E1",
    "E2",
    "E3",
    "F1",
    "F2",
    "F3",
    "G1",
    "G2",
    "G3",
    "G4",
    "H1",
    "H2",
    "H3",
)

PAPER_SECTIONS = tuple(f"W-{index:02d}" for index in range(1, 13))

# Phrases the external-review remediation removed from the repo; they must never
# reappear in the paper's final claim wording.
DENYLIST_PHRASES = (
    "full obligation stack satisfied",
    "provably insufficient",
    "git history is the proof",
)


def load_ledger() -> dict[str, Any]:
    data = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("ledger root must be a JSON object")
    return data


def load_manifest() -> dict[str, Any]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError("manifest root must be a JSON object")
    return data


def content_hash_of(body: dict[str, Any]) -> str:
    stripped = {key: value for key, value in body.items() if key != "content_hash"}
    return hashlib.sha256(canonical_json_bytes(stripped)).hexdigest()


def enveloped_artifact_paths() -> set[str]:
    paths: set[str] = set()
    for source in sorted((REPO_ROOT / "artifacts").rglob("*.json")):
        data = json.loads(source.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "artifact_kind" in data:
            paths.add(source.relative_to(REPO_ROOT).as_posix())
    return paths


def validate(ledger: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if ledger.get("ledger_kind") != "paper_claims_ledger":
        errors.append("ledger_kind must be 'paper_claims_ledger'")

    manifest = load_manifest()
    binding = ledger.get("evidence_manifest_binding", {})
    if binding.get("path") != "paper/evidence_manifest.json":
        errors.append("evidence_manifest_binding.path must be paper/evidence_manifest.json")
    if binding.get("content_hash") != manifest.get("content_hash"):
        errors.append(
            "evidence_manifest_binding.content_hash is stale against the current manifest"
        )
    manifest_hashes = {entry["path"]: entry["sha256"] for entry in manifest["entries"]}

    rows = ledger.get("rows", [])
    row_ids = [row.get("row_id") for row in rows]
    if len(row_ids) != len(set(row_ids)):
        errors.append("row_id values must be unique")
    for required_id in REQUIRED_ROW_IDS:
        if required_id not in row_ids:
            errors.append(f"required row missing: {required_id}")

    cited_paths: set[str] = set()
    for row in rows:
        rid = row.get("row_id", "<missing row_id>")
        for field in REQUIRED_ROW_FIELDS:
            if field not in row:
                errors.append(f"{rid}: missing field {field}")
        if row.get("kind") not in ALLOWED_KINDS:
            errors.append(f"{rid}: kind {row.get('kind')!r} not in {ALLOWED_KINDS}")
        statement = row.get("claim_statement", "")
        if not isinstance(statement, str) or not statement.strip():
            errors.append(f"{rid}: claim_statement must be a nonempty string")
        for phrase in DENYLIST_PHRASES:
            if phrase in statement.lower():
                errors.append(f"{rid}: claim_statement contains denylisted phrase {phrase!r}")
        for item in row.get("f2_s16_items", []):
            if item not in F2_S16_ITEM_IDS:
                errors.append(f"{rid}: unknown F-II section-16 item id {item!r}")
        if row.get("paper_section") not in PAPER_SECTIONS:
            errors.append(f"{rid}: paper_section {row.get('paper_section')!r} not in W-01..W-12")
        if row.get("claim_grade") is not None and "G1" not in row.get("f2_s16_items", []):
            errors.append(f"{rid}: graded row must include F-II section-16 item G1")
        for citation in row.get("artifacts", []):
            path, sha = citation.get("path"), citation.get("sha256")
            cited_paths.add(path)
            if path not in manifest_hashes:
                errors.append(f"{rid}: cited path not in evidence manifest: {path}")
                continue
            if manifest_hashes[path] != sha:
                errors.append(f"{rid}: cited sha256 disagrees with manifest for {path}")
            actual = hashlib.sha256((REPO_ROOT / path).read_bytes()).hexdigest()
            if actual != sha:
                errors.append(f"{rid}: cited sha256 disagrees with current bytes for {path}")
        for ref in row.get("disclosure_refs") or []:
            if not (REPO_ROOT / ref).is_file():
                errors.append(f"{rid}: disclosure_ref does not exist: {ref}")

    for path in sorted(enveloped_artifact_paths() - cited_paths):
        errors.append(f"enveloped artifact not cited by any ledger row: {path}")

    by_id = {row.get("row_id"): row for row in rows}
    gt6_statement = by_id.get("GT6", {}).get("claim_statement", "").lower()
    if "not invoked" not in gt6_statement:
        errors.append(
            "GT6 claim_statement must state paper [C]'s thm:strict-extension is NOT invoked"
        )
    if "saturation_budget" not in by_id.get("GT5", {}).get("claim_statement", ""):
        errors.append("GT5 claim_statement must state the shipped witness's saturation_budget")
    gt3_statement = by_id.get("GT3", {}).get("claim_statement", "")
    if "declared" not in gt3_statement:
        errors.append("GT3 claim_statement must scope the foreclosure to the declared class")
    if "no order parameter exists" in gt3_statement.lower():
        errors.append("GT3 claim_statement must not assert a scope-free impossibility")

    counts = ledger.get("counts", {})
    observed = {kind: sum(1 for row in rows if row.get("kind") == kind) for kind in ALLOWED_KINDS}
    observed["total"] = len(rows)
    if counts != observed:
        errors.append(f"counts field {counts} disagrees with observed {observed}")

    if ledger.get("content_hash") != content_hash_of(ledger):
        errors.append("ledger content_hash does not verify (run --stamp after edits)")

    if not LEDGER_MD_PATH.is_file() or LEDGER_MD_PATH.read_text(encoding="utf-8") != render_md(
        ledger
    ):
        errors.append("paper/claims_ledger.md is stale (run --stamp)")

    return errors


def render_md(ledger: dict[str, Any]) -> str:
    kind_titles = {
        "gt_claim": "GT claims",
        "gb_bridge": "GB bridges",
        "finding": "Findings",
        "honest_negative": "Honest negatives",
    }
    lines = [
        "# Paper claims ledger (rendered)",
        "",
        "Generated from `paper/claims_ledger.json` by `experiments/check_claims_ledger.py",
        "--stamp`; do not edit by hand. The JSON is the operative ledger.",
        "",
        f"Evidence manifest binding: `{ledger['evidence_manifest_binding']['content_hash']}`",
        "",
    ]
    for kind in ALLOWED_KINDS:
        rows = [row for row in ledger["rows"] if row["kind"] == kind]
        if not rows:
            continue
        lines += [f"## {kind_titles[kind]}", ""]
        for row in rows:
            lines += [f"### {row['row_id']} — {row['title']}", ""]
            lines += [row["claim_statement"], ""]
            grade = row["claim_grade"] if row["claim_grade"] is not None else "(none)"
            if row["grade_note"]:
                grade += f" — {row['grade_note']}"
            lines += [f"- **Grade:** {grade}"]
            if row["anchor_rows"] is not None:
                anchors = "; ".join(f"{key}: {value}" for key, value in row["anchor_rows"].items())
                lines += [f"- **Anchors (proposal §4):** {anchors}"]
            if row["anchor_note"]:
                lines += [f"- **Anchor note:** {row['anchor_note']}"]
            if row["artifacts"]:
                lines += ["- **Artifacts:**"]
                lines += [
                    f"  - `{citation['path']}` `{citation['sha256']}`"
                    for citation in row["artifacts"]
                ]
            if row["disclosure_refs"]:
                refs = ", ".join(f"`{ref}`" for ref in row["disclosure_refs"])
                lines += [f"- **Disclosed in:** {refs}"]
            if row["nonclaims"]:
                lines += ["- **Nonclaims:**"]
                lines += [f"  - {nonclaim}" for nonclaim in row["nonclaims"]]
            items = ", ".join(row["f2_s16_items"]) or "(none)"
            lines += [
                f"- **F-II §16 items:** {items}",
                f"- **Paper section:** {row['paper_section']}",
                "",
            ]
    counts = ledger["counts"]
    lines += [
        "## Totals",
        "",
        "| kind | rows |",
        "|---|---|",
    ]
    lines += [f"| {kind} | {counts[kind]} |" for kind in ALLOWED_KINDS]
    lines += [f"| **total** | **{counts['total']}** |", ""]
    return "\n".join(lines)


def stamp() -> None:
    ledger = load_ledger()
    ledger["content_hash"] = content_hash_of(ledger)
    LEDGER_PATH.write_bytes(
        json.dumps(ledger, sort_keys=True, indent=1, ensure_ascii=True).encode("utf-8") + b"\n"
    )
    LEDGER_MD_PATH.write_text(render_md(load_ledger()), encoding="utf-8")


def main() -> int:
    if "--stamp" in sys.argv[1:]:
        stamp()
        print(f"stamped {LEDGER_PATH.relative_to(REPO_ROOT)} and rendered markdown")
    errors = validate(load_ledger())
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    ledger = load_ledger()
    print(f"PASS claims_ledger ({ledger['counts']['total']} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
