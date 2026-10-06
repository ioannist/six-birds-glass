import importlib.util
import json
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

GB5_NONCLAIM = (
    "buyback saturation or nonsaturation is not a GB5 repair-impossibility certificate; "
    "GB5 requires a separate exhaustive repair-class sweep"
)
SINGLE_SCALAR_NONCLAIM = (
    "the shipped Kovacs buyback curve is a minimal two-history witness with saturation_budget=1; "
    "it demonstrates buyback mechanics, not general single-scalar or TNM insufficiency"
)

pytestmark = pytest.mark.slow


def test_build_gt5_dimension_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "gt5_dimension"
    main = load_main()

    main(output_dir=output_dir)

    max_fiber_artifact = json.loads((output_dir / "max_fiber.json").read_text(encoding="utf-8"))
    buyback_artifact = json.loads((output_dir / "buyback_curve.json").read_text(encoding="utf-8"))

    assert max_fiber_artifact["artifact_kind"] == "max_fiber"
    assert max_fiber_artifact["payload"]["max_fiber_size"] == 2
    assert max_fiber_artifact["payload"]["nontriviality_threshold_met"] is True
    assert max_fiber_artifact["payload"]["current_quotient_size"] == 1
    assert max_fiber_artifact["payload"]["predictive_quotient_size"] == 2
    assert (
        sum(max_fiber_artifact["payload"]["fiber_histogram"].values())
        == max_fiber_artifact["payload"]["predictive_quotient_size"]
    )

    assert buyback_artifact["artifact_kind"] == "buyback_curve"
    assert GB5_NONCLAIM in buyback_artifact["nonclaims"]
    assert SINGLE_SCALAR_NONCLAIM in buyback_artifact["nonclaims"]
    assert buyback_artifact["payload"]["envelope"]["0"] != "0/1"
    assert set(buyback_artifact["payload"]["raw_by_budget"]) == {"0", "1", "2"}

    repo_root = Path(__file__).resolve().parents[1]
    envelope_schema = json.loads(
        (repo_root / "design" / "schemas" / "artifact_envelope.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(envelope_schema).validate(max_fiber_artifact)
    Draft202012Validator(envelope_schema).validate(buyback_artifact)


def load_main():
    script_path = Path(__file__).resolve().parents[1] / "experiments" / "build_gt5_dimension.py"
    spec = importlib.util.spec_from_file_location("build_gt5_dimension", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.main
