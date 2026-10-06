import importlib.util
import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.slow


def test_build_gt6_shell_and_knockouts_artifact(tmp_path: Path) -> None:
    output_path = tmp_path / "knockouts.json"
    main = _load_main()

    main(output_path=output_path)

    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    assert artifact["artifact_kind"] == "knockout_panel"
    assert artifact["claim_grade"] == "certificate_shell_local"
    assert artifact["payload"]["thresholds"]["tau_alpha_lower_divisor"] == 100000
    assert len(artifact["payload"]["shell_witnesses"]) == 2
    assert all(witness["exit_count"] == 0 for witness in artifact["payload"]["shell_witnesses"])
    assert len(artifact["payload"]["knockouts"]) == 6
    assert all(row["degraded"] for row in artifact["payload"]["knockouts"])
    assert {
        row["kind"]
        for row in artifact["payload"]["knockouts"]
        if row["primitive"] in {"P1", "P2", "P3"}
    } == {"numeric"}
    assert {
        row["kind"]
        for row in artifact["payload"]["knockouts"]
        if row["primitive"] in {"P4", "P5", "P6"}
    } == {"capability_loss"}
    assert all(artifact["payload"]["full_loop_nondegeneracy"].values())


def _load_main():
    script_path = (
        Path(__file__).resolve().parents[1] / "experiments" / "build_gt6_shell_and_knockouts.py"
    )
    spec = importlib.util.spec_from_file_location("build_gt6_shell_and_knockouts", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.main
