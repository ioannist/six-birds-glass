import json
from pathlib import Path

from jsonschema import Draft202012Validator


def test_all_artifacts_json_files_validate_against_common_envelope() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    schema = json.loads(
        (repo_root / "design" / "schemas" / "artifact_envelope.schema.json").read_text(
            encoding="utf-8"
        )
    )
    validator = Draft202012Validator(schema)
    paths = sorted((repo_root / "artifacts").rglob("*.json"))

    assert paths
    assert repo_root / "artifacts" / "gt7_constants" / "observations.json" not in paths
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        validator.validate(data)
