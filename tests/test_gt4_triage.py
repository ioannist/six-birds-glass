import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

GT4_ARTIFACT = Path("artifacts/gt4_triage/regime_table.json")
PHASE1_PARITY_ARTIFACT = Path("artifacts/benchmark_suite/phase1_parity.json")

EXPECTED_REGIMES = {
    "flat_control": "flat",
    "protocol_trap_naive": "artifact_trap",
    "protocol_trap_honest": "flat",
    "flattenable_raw": "flattenable",
    "flattenable_completed": "flat",
    "latent_memory_base": "explicit_latent",
    "latent_memory_refined": "flat",
    "dissipative_memory@mid": "dissipative",
    "dissipative_memory@end": "flat",
    "kovacs_wheel": "coherent_candidate",
}


def test_gt4_triage_artifact_validates_against_envelope() -> None:
    artifact = _load(GT4_ARTIFACT)

    Draft202012Validator(_schema()).validate(artifact)
    assert artifact["artifact_kind"] == "triage_regime_table"
    assert artifact["claim_id"] == "GT4.regime_triage.east_benchmarks"
    assert artifact["claim_grade"] == "theorem_audited_class"


def test_gt4_regime_classifications_match_declared_panel() -> None:
    artifact = _load(GT4_ARTIFACT)
    regimes = {row["benchmark"]: row["regime"] for row in artifact["payload"]["benchmarks"]}

    assert regimes == EXPECTED_REGIMES
    assert artifact["payload"]["summary"]["claim_pass"] is True
    assert artifact["payload"]["summary"]["coherent_candidate"] == "kovacs_wheel"
    assert artifact["payload"]["summary"]["coherent_candidate_regime"] == "coherent_candidate"


def test_gt4_noncoherent_controls_and_cleared_counterparts_are_explicit() -> None:
    summary = _load(GT4_ARTIFACT)["payload"]["summary"]
    controls = summary["noncoherent_regime_controls"]

    assert controls["flat"]["regime"] == "flat"
    assert controls["artifact_trap"]["raw_regime"] == "artifact_trap"
    assert controls["artifact_trap"]["cleared_regime"] == "flat"
    assert controls["flattenable"]["raw_regime"] == "flattenable"
    assert controls["flattenable"]["cleared_regime"] == "flat"
    assert controls["explicit_latent"]["raw_regime"] == "explicit_latent"
    assert controls["explicit_latent"]["cleared_regime"] == "flat"
    assert controls["dissipative"]["raw_regime"] == "dissipative"
    assert controls["dissipative"]["cleared_regime"] == "flat"


def test_gt4_artifact_is_consistent_with_phase1_parity_source() -> None:
    gt4 = _load(GT4_ARTIFACT)
    phase1 = _load(PHASE1_PARITY_ARTIFACT)

    assert gt4["payload"]["benchmarks"] == phase1["payload"]["benchmarks"]
    assert gt4["payload"]["summary"]["row_count"] == 10
    assert gt4["payload"]["summary"]["benchmark_family_count"] == 9


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
