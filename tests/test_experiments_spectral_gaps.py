import importlib.util
import json
from pathlib import Path


def test_compute_spectral_gaps_main_writes_json(tmp_path: Path) -> None:
    output_path = tmp_path / "east.json"
    main = load_main()

    main(output_path=output_path, n_values=(2, 3, 4))

    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    payload = artifact["payload"]
    assert artifact["artifact_kind"] == "spectral_gap_table"
    assert payload["artifact_status"] == "phase0_diagnostic"
    assert "pre-certificate" in payload["note"].lower()
    assert payload["model"] == "east"
    assert len(payload["rows"]) == 21
    for row in payload["rows"]:
        assert set(row) == {"N", "epsilon", "gap", "tau_rel", "mixing_time_bound"}


def load_main():
    script_path = Path(__file__).resolve().parents[1] / "experiments" / "compute_spectral_gaps.py"
    spec = importlib.util.spec_from_file_location("compute_spectral_gaps", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.main
