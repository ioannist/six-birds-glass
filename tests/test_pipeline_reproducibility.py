import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

from sixbirds_glass.io.config import load_config
from sixbirds_glass.io.rational import rational_to_str
from sixbirds_glass.pipeline.reproducibility import rebuild_hump_result_from_config


@pytest.mark.slow
def test_hump_result_rebuilds_exactly_from_config_dict() -> None:
    config = load_config(Path("configs/kovacs_hump_default.json"))
    selected = json.loads(
        Path("artifacts/kovacs_hump_check/result.json").read_text(encoding="utf-8")
    )["payload"]["selected_result"]

    rebuilt = rebuild_hump_result_from_config(config)

    assert [rational_to_str(value) for value in rebuilt.trace] == selected["trace"]
    assert rebuilt.t_k == selected["t_k"]
    assert rebuilt.t_peak == selected["t_peak"]
    assert rebuilt.hump_height is not None
    assert rational_to_str(rebuilt.hump_height) == selected["hump_height"]


def test_frozen_config_validates_if_search_found_hump(tmp_path) -> None:
    config_path = tmp_path / "kovacs_hump_default.json"
    config_path.write_text(
        Path("configs/kovacs_hump_default.json").read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    try:
        config = load_config(config_path)
    except ValidationError as exc:  # pragma: no cover - clearer assertion failure
        raise AssertionError("found hump config must validate") from exc
    assert config["model"]["family"] == "east"


@pytest.mark.slow
def test_rebuild_rejects_non_east_config() -> None:
    config = load_config(Path("configs/kovacs_hump_default.json"))
    config["model"]["family"] = "fa1f"

    try:
        rebuild_hump_result_from_config(config)
    except ValueError as exc:
        assert "only East" in str(exc)
    else:  # pragma: no cover - explicit failure branch
        raise AssertionError("expected ValueError")
