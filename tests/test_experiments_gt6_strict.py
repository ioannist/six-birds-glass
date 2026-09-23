import importlib.util
import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

pytestmark = pytest.mark.slow


def test_build_gt6_strict_hypotheses_artifact(tmp_path: Path) -> None:
    output_path = tmp_path / "strict_extension.json"
    main = _load_main()

    main(output_path=output_path)

    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    assert artifact["artifact_kind"] == "strict_extension_hypotheses"
    assert artifact["claim_grade"] == "certificate_shell_local"
    payload = artifact["payload"]
    assert payload["H2_endomap"]["well_defined"] is True
    assert payload["H3_saturation"]["saturated"] is True
    assert payload["H3_saturation"]["strata_count"] == 9
    # Current audited shell honest negative: the conditioned and unconditioned
    # saturation runs produce the same final strata, so no material forcing
    # strata are filed for this shell.
    assert payload["H4_forcing"]["material_forcing_count"] == 0
    assert payload["H4_forcing"]["material_forcing_strata"] == []
    assert (
        payload["H4_forcing"]["with_conditioning"]["final_strata"]
        == payload["H4_forcing"]["without_conditioning"]["final_strata"]
    )
    repo_root = Path(__file__).resolve().parents[1]
    h5 = payload["H5_macro_admissibility_obstruction"]
    h5_path = repo_root / h5["artifact_path"]
    assert h5_path.is_file()
    assert "gt1_cd_tables" in h5["artifact_path"]
    cited = json.loads(h5_path.read_text(encoding="utf-8"))
    assert cited["claim_id"].startswith("GT1.")
    assert payload["nonfactorization"]["rate"] == "1/1"

    schema = json.loads(
        (
            Path(__file__).resolve().parents[1]
            / "design"
            / "schemas"
            / "artifact_envelope.schema.json"
        ).read_text(encoding="utf-8")
    )
    Draft202012Validator(schema).validate(artifact)


def _load_main():
    script_path = (
        Path(__file__).resolve().parents[1] / "experiments" / "build_gt6_strict_hypotheses.py"
    )
    spec = importlib.util.spec_from_file_location("build_gt6_strict_hypotheses", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.main
