import json
from pathlib import Path


def test_spectral_gap_artifact_status_field() -> None:
    artifact = json.loads(Path("artifacts/spectral_gaps/east.json").read_text(encoding="utf-8"))
    payload = artifact["payload"]

    assert artifact["artifact_kind"] == "spectral_gap_table"
    assert payload["artifact_status"] == "phase0_diagnostic"
    assert "pre-certificate" in payload["note"].lower()


def test_kovacs_hump_artifact_status_field() -> None:
    artifact = json.loads(
        Path("artifacts/kovacs_hump_check/result.json").read_text(encoding="utf-8")
    )
    payload = artifact["payload"]

    assert artifact["artifact_kind"] == "window_table"
    assert payload["artifact_status"] == "phase0_exploratory_result"
    assert "pre-certificate" in payload["note"].lower()
