import importlib.util
import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

pytestmark = pytest.mark.slow

P4_NONCLAIM = "filed as P4 staged dependence, not a directionality or irreversibility claim"


def test_build_gt2_kovacs_witness_artifact_validates_and_routes_p4(tmp_path: Path) -> None:
    output_path = tmp_path / "kovacs_moment.json"
    main = load_main()

    main(output_path=output_path)

    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    assert artifact["artifact_kind"] == "witness_certificate"
    assert artifact["claim_id"] == "GT2.kovacs_moment.east_N10"
    assert P4_NONCLAIM in artifact["nonclaims"]

    repo_root = Path(__file__).resolve().parents[1]
    envelope_schema = json.loads(
        (repo_root / "design" / "schemas" / "artifact_envelope.schema.json").read_text(
            encoding="utf-8"
        )
    )
    witness_schema = json.loads(
        (repo_root / "design" / "schemas" / "witness_certificate.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(envelope_schema).validate(artifact)
    Draft202012Validator(witness_schema).validate(artifact["payload"])

    without_nonclaims = dict(artifact)
    without_nonclaims["nonclaims"] = []
    artifact_text = json.dumps(without_nonclaims, sort_keys=True).lower()
    for denied in ("irreversib", "arrow", "entropy production"):
        assert denied not in artifact_text


def load_main():
    script_path = (
        Path(__file__).resolve().parents[1] / "experiments" / "build_gt2_kovacs_witness.py"
    )
    spec = importlib.util.spec_from_file_location("build_gt2_kovacs_witness", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.main
