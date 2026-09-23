import importlib.util
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

EXPECTED_STATEMENT = (
    "the distinguishing readout (n_1-based) is not in Def(l_energy); constructive witness "
    "exhibited, not generic counting"
)
EXPECTED_PROVENANCE = (
    "standalone W_reflection witness constructed for this sweep; not chained to the "
    "GT2.kovacs_moment certificate (a separate witness family per "
    "design/specs/04_gt2_witnesses.md §4)."
)


def test_build_gt3_foreclosure_sweep_artifact(tmp_path: Path) -> None:
    output_path = tmp_path / "lens_class_sweep.json"
    main = load_main()

    main(output_path=output_path)

    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    assert artifact["artifact_kind"] == "foreclosure_sweep"
    assert artifact["claim_id"] == "GT3.energy_lens_sweep.east_N8"

    payload = artifact["payload"]
    assert payload["total_predicates"] == 512
    assert payload["agreeing_predicates"] == 512
    assert payload["all_agree"] is True
    assert payload["first_disagreement"] is None
    assert payload["separating_entry"]["abs_gap"] == "169/1536"
    assert payload["t_for_02_statement"] == EXPECTED_STATEMENT
    assert payload["witness_provenance"] == EXPECTED_PROVENANCE

    repo_root = Path(__file__).resolve().parents[1]
    envelope_schema = json.loads(
        (repo_root / "design" / "schemas" / "artifact_envelope.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(envelope_schema).validate(artifact)


def load_main():
    script_path = (
        Path(__file__).resolve().parents[1] / "experiments" / "build_gt3_foreclosure_sweep.py"
    )
    spec = importlib.util.spec_from_file_location("build_gt3_foreclosure_sweep", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.main
