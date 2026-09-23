import hashlib
import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = REPO_ROOT / "paper" / "claims_ledger.json"
MANIFEST_PATH = REPO_ROOT / "paper" / "evidence_manifest.json"


def _checker():
    script_path = REPO_ROOT / "experiments" / "check_claims_ledger.py"
    spec = importlib.util.spec_from_file_location("check_claims_ledger", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_checker_validates_shipped_ledger() -> None:
    assert _checker().validate(_load(LEDGER_PATH)) == []


def test_required_rows_present() -> None:
    checker = _checker()
    row_ids = {row["row_id"] for row in _load(LEDGER_PATH)["rows"]}
    assert set(checker.REQUIRED_ROW_IDS) <= row_ids


def test_ledger_citations_are_manifest_subset_and_current() -> None:
    manifest_hashes = {entry["path"]: entry["sha256"] for entry in _load(MANIFEST_PATH)["entries"]}
    for row in _load(LEDGER_PATH)["rows"]:
        for citation in row["artifacts"]:
            assert citation["path"] in manifest_hashes, (row["row_id"], citation["path"])
            assert citation["sha256"] == manifest_hashes[citation["path"]]
            actual = hashlib.sha256((REPO_ROOT / citation["path"]).read_bytes()).hexdigest()
            assert citation["sha256"] == actual, (row["row_id"], citation["path"])


def test_every_enveloped_artifact_is_cited() -> None:
    cited = {
        citation["path"] for row in _load(LEDGER_PATH)["rows"] for citation in row["artifacts"]
    }
    enveloped = _checker().enveloped_artifact_paths()
    assert enveloped
    assert enveloped <= cited


def test_wording_guards() -> None:
    rows = {row["row_id"]: row for row in _load(LEDGER_PATH)["rows"]}
    for row in rows.values():
        lowered = row["claim_statement"].lower()
        assert "full obligation stack satisfied" not in lowered, row["row_id"]
        assert "provably insufficient" not in lowered, row["row_id"]
        assert "git history is the proof" not in lowered, row["row_id"]
    assert "not invoked" in rows["GT6"]["claim_statement"].lower()
    assert "saturation_budget" in rows["GT5"]["claim_statement"]
    assert "declared" in rows["GT3"]["claim_statement"]
    assert "no order parameter exists" not in rows["GT3"]["claim_statement"].lower()
    assert "14 fail" in rows["GT7"]["claim_statement"]


def test_manifest_binding_and_self_hash_are_current() -> None:
    checker = _checker()
    ledger = _load(LEDGER_PATH)
    manifest = _load(MANIFEST_PATH)
    assert ledger["evidence_manifest_binding"]["content_hash"] == manifest["content_hash"]
    assert ledger["content_hash"] == checker.content_hash_of(ledger)


def test_gt3_wording_matches_artifact_provenance() -> None:
    artifact = _load(REPO_ROOT / "artifacts" / "gt3_foreclosure" / "lens_class_sweep.json")
    provenance = artifact["payload"]["witness_provenance"]
    statement = next(row for row in _load(LEDGER_PATH)["rows"] if row["row_id"] == "GT3")[
        "claim_statement"
    ]
    if "not chained" in provenance:
        assert "GT2-provenance" not in statement
        assert "W_reflection" in statement


def test_graded_rows_carry_g1() -> None:
    for row in _load(LEDGER_PATH)["rows"]:
        if row["claim_grade"] is not None:
            assert "G1" in row["f2_s16_items"], row["row_id"]


def test_gt7_failure_pattern_tallies_match_ledger_and_gap_register() -> None:
    scores = _load(REPO_ROOT / "artifacts" / "gt7_constants" / "gt7_transfer_scores.json")
    cells = scores["payload"]["cells"]
    assert scores["payload"]["aggregate"] == {
        "n_pass": 8,
        "n_fail": 14,
        "n_no_prediction": 294,
        "n_unobserved": 22,
        "total": 338,
    }
    fails = [cell for cell in cells if cell["verdict"] == "fail"]
    assert len(fails) == 14
    assert all(cell["target_family"] == "fa1f" for cell in fails)
    assert all(cell["prediction_type"] == "interval" for cell in fails)
    # Every failure is one-sided high: observed exceeds the predicted upper bound.
    # The predicted field is the scorer's string rendering of the interval, e.g. "[0, 2]".
    for cell in fails:
        lo, hi = (Fraction(part.strip()) for part in cell["predicted"].strip("[]").split(","))
        assert lo < hi
        assert Fraction(str(cell["observed"])) > hi, cell["cell_id"]
    eps_mid = [cell["cell_id"].split(":")[2].split("_")[2] for cell in fails]
    assert sum(1 for value in eps_mid if value == "2-5") == 12

    unobserved = [cell for cell in cells if cell["verdict"] == "unobserved"]
    assert len(unobserved) == 22
    assert all(cell["target_family"] == "trap" for cell in unobserved)
    trap = _load(REPO_ROOT / "artifacts" / "gt7_constants" / "trap_target.json")
    surface = trap["payload"]["hump_surface_exact"]
    assert len(surface) == 56
    assert all(entry["found"] is False for entry in surface)
    assert all(entry["miss_reason"] == "does not start below equilibrium" for entry in surface)

    ledger_row = next(
        row for row in _load(LEDGER_PATH)["rows"] if row["row_id"] == "NEG.gt7_transfer_failures"
    )["claim_statement"]
    assert "one-sided high" in ledger_row
    assert "12 of 14" in ledger_row
    assert "does not start below equilibrium" in ledger_row
    gap_register = (REPO_ROOT / "paper" / "gap_register.md").read_text(encoding="utf-8")
    assert "8 pass, 14 fail, 294 no_prediction, 22 unobserved" in gap_register
    assert "one-sided high" in gap_register
    assert "found=false in all 56 surface cells" in gap_register


def test_rendered_markdown_is_fresh() -> None:
    checker = _checker()
    rendered = checker.render_md(_load(LEDGER_PATH))
    assert (REPO_ROOT / "paper" / "claims_ledger.md").read_text(encoding="utf-8") == rendered
