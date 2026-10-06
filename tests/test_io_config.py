from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from jsonschema import ValidationError

from sixbirds_glass.io.config import (
    canonical_json_bytes,
    config_hash,
    load_config,
    load_config_with_hash,
)

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_config_validates_example_fixture() -> None:
    config, digest = load_config_with_hash(FIXTURES / "example_config.json")

    assert config["model"]["family"] == "east"
    assert config["model"]["N"] == 6
    assert config["epsilon_grid"] == ["1/5"]
    assert digest == config_hash(config)
    assert len(digest) == 64


def test_load_config_rejects_missing_required_field(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "example_config.json")
    del config["arithmetic"]
    path = tmp_path / "missing_required.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValidationError, match="'arithmetic' is a required property"):
        load_config(path)


def test_load_config_rejects_bad_rational_pattern(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "example_config.json")
    config["epsilon_grid"] = ["1/0"]
    path = tmp_path / "bad_rational.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValidationError, match="does not match"):
        load_config(path)


def test_load_config_rejects_noncanonical_rational(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "example_config.json")
    config["epsilon_grid"] = ["2/4"]
    path = tmp_path / "noncanonical_rational.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValidationError, match="canonical rational"):
        load_config(path)


@pytest.mark.parametrize(
    ("epsilon", "message"),
    [
        ("0/1", "open interval"),
        ("1/1", "open interval"),
        ("6/5", "open interval"),
        ("-1/5", "open interval"),
    ],
)
def test_load_config_rejects_epsilon_grid_values_outside_open_unit_interval(
    tmp_path: Path, epsilon: str, message: str
) -> None:
    config = load_config(FIXTURES / "example_config.json")
    config["epsilon_grid"] = [epsilon]
    config["protocol"]["word"][0]["epsilon"] = epsilon
    path = tmp_path / "bad_epsilon_domain.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValidationError, match=message):
        load_config(path)


def test_load_config_rejects_duplicate_epsilon_grid_entries(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "example_config.json")
    config["epsilon_grid"] = ["1/5", "1/5"]
    path = tmp_path / "duplicate_grid.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValidationError, match="unique"):
        load_config(path)


def test_load_config_rejects_protocol_epsilon_outside_declared_grid(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "example_config.json")
    config["epsilon_grid"] = ["1/5"]
    config["protocol"]["word"][0]["epsilon"] = "2/5"
    path = tmp_path / "off_grid_protocol.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValidationError, match=r"protocol.word\[0\].epsilon.*epsilon_grid"):
        load_config(path)


def test_load_config_rejects_trap_weight_key_outside_declared_grid(tmp_path: Path) -> None:
    config = load_config(FIXTURES / "example_config.json")
    config["model"] = {
        "family": "trap",
        "N": 6,
        "boundary": "none",
        "trap_weights": {"2/5": ["1/2"]},
    }
    path = tmp_path / "off_grid_trap_weight.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    with pytest.raises(ValidationError, match=r"trap_weights.*epsilon_grid"):
        load_config(path)


def test_canonical_hash_is_deterministic_and_sensitive_to_values() -> None:
    first = {
        "model": {"N": 6, "family": "east"},
        "epsilon_grid": ["1/5"],
    }
    second = {
        "epsilon_grid": ["1/5"],
        "model": {"family": "east", "N": 6},
    }
    changed = copy.deepcopy(second)
    changed["model"]["N"] = 8

    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert config_hash(first) == config_hash(second)
    assert config_hash(first) != config_hash(changed)
