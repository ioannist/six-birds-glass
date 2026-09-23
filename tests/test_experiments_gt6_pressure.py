import importlib.util
import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.slow


def test_build_gt6_pressure_closure_artifact(tmp_path: Path) -> None:
    output_path = tmp_path / "pressure_closure.json"
    main = _load_main()

    main(output_path=output_path)

    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    assert artifact["artifact_kind"] == "pressure_closure"
    assert artifact["claim_grade"] == "certificate_shell_local"
    rows = artifact["payload"]["rows"]
    computed = [row for row in rows if row["status"] == "computed"]
    skipped = [row for row in rows if row["status"] == "skipped_dense_threshold"]

    assert computed
    assert skipped
    assert all(row["shell_exits"] == 0 for row in rows)
    assert all(row["subadditivity_verified"] for row in computed)
    assert all(row["N"] == 8 for row in computed)
    assert all(row["N"] == 10 for row in skipped)
    assert all("dense_state_threshold" in row["skip_reason"] for row in skipped)


def _load_main():
    script_path = (
        Path(__file__).resolve().parents[1] / "experiments" / "build_gt6_pressure_closure.py"
    )
    spec = importlib.util.spec_from_file_location("build_gt6_pressure_closure", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.main
