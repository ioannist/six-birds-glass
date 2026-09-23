import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

CD_ARTIFACT = Path("artifacts/gt1_cd_tables/east_n8_l_energy.json")
DELTA_ARTIFACT = Path("artifacts/gt1_delta_tables/east_n8_l_energy.json")


def test_gt1_artifacts_validate_against_envelope() -> None:
    schema = _schema()
    cd = _load(CD_ARTIFACT)
    delta = _load(DELTA_ARTIFACT)

    Draft202012Validator(schema).validate(cd)
    Draft202012Validator(schema).validate(delta)
    assert cd["claim_id"] == "GT1.east.8.L_energy"
    assert delta["claim_id"] == "GT1.east.8.L_energy.delta"
    assert "runtime_seconds" not in cd["payload"]
    assert "runtime_seconds" not in delta["payload"]


@pytest.mark.slow
def test_gt1_artifact_builder_is_byte_deterministic() -> None:
    builder = _load_builder()

    first_cd, first_delta = builder.build_artifacts()
    second_cd, second_delta = builder.build_artifacts()

    assert _canonical_json(first_cd) == _canonical_json(second_cd)
    assert _canonical_json(first_delta) == _canonical_json(second_delta)


def test_lumpable_control_is_exact_zero() -> None:
    control = _load(CD_ARTIFACT)["payload"]["controls"]["lumpable_unconstrained"]

    assert control["pass"] is True
    assert all(row["is_exactly_lumpable"] for row in control["rows"])
    assert all(row["within_zero_tolerance"] for row in control["rows"])


def test_gb2_consistency_gate_passes_for_equilibrium_control() -> None:
    payload = _load(CD_ARTIFACT)["payload"]
    control = payload["controls"]["east_equilibrium_stationary_consistency"]

    assert payload["gb2_consistency_gate_pass"] is True
    assert control["pass"] is True
    assert all(row["cd_residual"] < 1e-12 for row in control["rows"])


def test_glassy_cd_exceeds_equilibrium_baseline_by_declared_margin() -> None:
    payload = _load(CD_ARTIFACT)["payload"]
    thresholds = payload["thresholds"]
    rows = payload["grid"]

    assert thresholds["aging_exceeds_equilibrium_margin"] is True
    assert thresholds["achieved_min_cd_ratio"] >= 1.5
    tau_8 = next(row for row in rows if row["tau"] == 8)
    assert tau_8["cd"] > tau_8["equilibrium_baseline_cd"]


def test_delta_contrast_exceeds_equilibrium_baseline() -> None:
    payload = _load(DELTA_ARTIFACT)["payload"]

    assert payload["thresholds"]["aging_exceeds_equilibrium_margin"] is True
    assert payload["thresholds"]["achieved_delta_ratio"] == "289/121"
    rows = payload["grid"]
    hot = next(
        row
        for row in rows
        if row["case"] == "equilibrium_hot_baseline" and row["prototype_rule"] == "gibbs"
    )
    cold = next(
        row for row in rows if row["case"] == "aging_cold_leg" and row["prototype_rule"] == "gibbs"
    )
    assert hot["delta_pq"] == "1225/4624"
    assert cold["delta_pq"] == "1225/1936"


def test_reduced_scope_and_skipped_b_parity_are_filed() -> None:
    cd = _load(CD_ARTIFACT)
    delta = _load(DELTA_ARTIFACT)
    nonclaims = " ".join(cd["nonclaims"])

    assert "FA" in nonclaims
    assert "L_panel" in nonclaims
    assert "tau ladder" in nonclaims
    assert cd["payload"]["controls"]["b_benchmark_parity"]["status"] == "skipped"
    assert delta["payload"]["controls"]["b_benchmark_parity"]["status"] == "skipped"


def _load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def _schema() -> dict[str, Any]:
    data = json.loads(
        Path("design/schemas/artifact_envelope.schema.json").read_text(encoding="utf-8")
    )
    assert isinstance(data, dict)
    return data


def _canonical_json(data: dict[str, Any]) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"))


def _load_builder():
    script_path = Path("experiments/build_gt1_closure_deficit.py")
    spec = importlib.util.spec_from_file_location("build_gt1_closure_deficit", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module
