import importlib.util
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


def test_build_gb1_demo_artifact(tmp_path: Path) -> None:
    output_path = tmp_path / "gb1_demo.json"
    main = _load_main("build_gb1_demo")

    main(output_path=output_path)

    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    _validate_envelope(artifact)
    payload = artifact["payload"]
    assert payload["artifact_status"] == "phase2_math_demo"
    assert payload["pseudo_epr_identity"]["absolute_error"] < 1e-14
    assert all(row["holds"] for row in payload["three_state_demo"]["sigma_vs_bound"])
    assert payload["common_temperature_recovery"]["boundary_rate"] < 1e-14
    assert payload["common_temperature_recovery"]["stationary_epr"] < 1e-14
    assert payload["mixed_square_affinity"]["absolute_error"] < 1e-14
    assert "clock-path expectation" in payload["open_obligation"]


def test_build_gb2_demo_artifact(tmp_path: Path) -> None:
    output_path = tmp_path / "gb2_demo.json"
    main = _load_main("build_gb2_demo")

    main(output_path=output_path)

    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    _validate_envelope(artifact)
    payload = artifact["payload"]
    assert payload["artifact_status"] == "phase2_math_demo"
    consistency = payload["stationary_consistency"]
    assert consistency["absolute_difference"] < 1e-12

    assert payload["lumpable_multi_cell_catalog"]["is_lumpable"] is True
    non_lumpable = payload["non_lumpable_aging_catalog"]
    assert non_lumpable["is_lumpable"] is False
    assert non_lumpable["violation"] is not None
    assert non_lumpable["windowed_cd"] > 0.0
    assert non_lumpable["marginalized_cd"] > 0.0
    assert non_lumpable["windowed_cd"] != non_lumpable["marginalized_cd"]


def _load_main(script_stem: str):
    script_path = Path(__file__).resolve().parents[1] / "experiments" / f"{script_stem}.py"
    spec = importlib.util.spec_from_file_location(script_stem, script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.main


def _validate_envelope(artifact: dict) -> None:
    schema = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "design"
            / "schemas"
            / "artifact_envelope.schema.json"
        ).read_text(encoding="utf-8")
    )
    Draft202012Validator(schema).validate(artifact)
