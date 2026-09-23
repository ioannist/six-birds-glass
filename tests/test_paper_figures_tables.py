import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_module(relative_path: str, module_name: str):
    script_path = REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _figures():
    return _load_module("paper/figures/build_figures.py", "build_figures")


def _tables():
    return _load_module("paper/tables/build_tables.py", "build_tables")


def _manifest_paths() -> set[str]:
    manifest = json.loads((REPO_ROOT / "paper" / "evidence_manifest.json").read_text())
    return {entry["path"] for entry in manifest["entries"]}


def test_figure_source_artifacts_are_in_evidence_manifest() -> None:
    figures = _figures()
    manifest_paths = _manifest_paths()
    assert figures.SOURCE_ARTIFACTS
    assert set(figures.SOURCE_ARTIFACTS) <= manifest_paths


def test_table_source_artifacts_are_in_evidence_manifest() -> None:
    tables = _tables()
    manifest_paths = _manifest_paths()
    assert tables.SOURCE_ARTIFACTS
    assert set(tables.SOURCE_ARTIFACTS) <= manifest_paths


def test_figure_series_are_deterministic() -> None:
    figures = _figures()
    first = figures.build_all_series()
    second = figures.build_all_series()
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)


def test_figure_series_reject_undeclared_paths() -> None:
    figures = _figures()
    try:
        figures._load("artifacts/gb1_demo.json")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for an artifact outside SOURCE_ARTIFACTS")


def test_table_fragments_are_deterministic() -> None:
    tables = _tables()
    first = tables.build_all()
    second = tables.build_all()
    assert first == second


def test_table_fragments_reject_undeclared_paths() -> None:
    tables = _tables()
    try:
        tables._load("artifacts/gb1_demo.json")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for an artifact outside SOURCE_ARTIFACTS")


def test_table_paper_file_sources_are_declared_and_guarded() -> None:
    tables = _tables()
    assert tables.SOURCE_PAPER_FILES == ("paper/claims_ledger.json",)
    tables._load_paper_file("paper/claims_ledger.json")
    try:
        tables._load_paper_file("paper/evidence_manifest.json")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for a paper file outside SOURCE_PAPER_FILES")


def test_table_output_is_fresh() -> None:
    tables = _tables()
    assert tables.check_fresh() == []


def test_figures_output_pdfs_exist_and_are_nonempty() -> None:
    figures = _figures()
    for name, _collect, _render in figures.FIGURES:
        path = figures.OUT_DIR / name
        assert path.is_file(), name
        assert path.stat().st_size > 500, name


def test_gt7_transfer_scoreboard_series_matches_ledger_aggregate() -> None:
    figures = _figures()
    series = figures.collect_transfer_scoreboard()
    assert series["aggregate"] == {
        "n_pass": 8,
        "n_fail": 14,
        "n_no_prediction": 294,
        "n_unobserved": 22,
        "total": 338,
    }
    fail_cells = [c for c in series["fa_interval_cells"] if c["verdict"] == "fail"]
    assert len(fail_cells) == 14
    assert all(cell["observed"] > cell["hi"] for cell in fail_cells)


def test_nonclaims_table_covers_every_ledger_nonclaim() -> None:
    tables = _tables()
    ledger = json.loads((REPO_ROOT / "paper" / "claims_ledger.json").read_text())
    expected = sum(len(row["nonclaims"]) for row in ledger["rows"])
    rendered = tables.build_nonclaims_full()
    row_lines = [line for line in rendered.splitlines() if " & " in line and r"\\" in line]
    # subtract the two header occurrences ("claim & nonclaim")
    data_lines = [line for line in row_lines if not line.startswith("claim &")]
    assert len(data_lines) == expected


def test_lean_fidelity_table_covers_every_row() -> None:
    tables = _tables()
    fidelity = json.loads((REPO_ROOT / "artifacts" / "lean_fidelity_table.json").read_text())
    expected = len(fidelity["payload"]["rows"])
    rendered = tables.build_lean_fidelity_full()
    row_lines = [
        line
        for line in rendered.splitlines()
        if " & " in line and r"\\" in line and not line.startswith("Lean name")
    ]
    assert len(row_lines) == expected
