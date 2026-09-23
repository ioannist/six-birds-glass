"""Run configuration loading, schema validation, and content hashing."""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, ValidationError

from sixbirds_glass.io.rational import str_to_rational

MODEL_CONFIG_SCHEMA = "model_config.schema.json"


def _repo_root() -> Path:
    """Find the repository root by locating the design schema directory."""

    for parent in Path(__file__).resolve().parents:
        schema_path = parent / "design" / "schemas" / MODEL_CONFIG_SCHEMA
        if schema_path.is_file():
            return parent
    raise FileNotFoundError(
        f"could not locate design/schemas/{MODEL_CONFIG_SCHEMA} above {Path(__file__).resolve()}"
    )


def _model_config_schema_path() -> Path:
    return _repo_root() / "design" / "schemas" / MODEL_CONFIG_SCHEMA


def _load_model_config_schema() -> dict[str, Any]:
    with _model_config_schema_path().open(encoding="utf-8") as schema_file:
        schema = json.load(schema_file)
    if not isinstance(schema, dict):
        raise TypeError(f"{_model_config_schema_path()} did not contain a JSON object")
    return schema


def _require_canonical_rational(value: Any, path: str) -> Fraction:
    if not isinstance(value, str):
        raise ValidationError(f"{path} must be a rational string")
    try:
        return str_to_rational(value)
    except ValueError as exc:
        raise ValidationError(f"{path} must be a canonical rational string: {exc}") from exc


def _validate_canonical_rationals(config: dict[str, Any]) -> None:
    """Enforce canonical rational strings where the schema declares rationals."""

    for index, epsilon in enumerate(config.get("epsilon_grid", [])):
        _require_canonical_rational(epsilon, f"epsilon_grid[{index}]")

    model = config.get("model", {})
    if isinstance(model, dict):
        trap_weights = model.get("trap_weights", {})
        if isinstance(trap_weights, dict):
            for epsilon, weights in trap_weights.items():
                if isinstance(weights, list):
                    for index, weight in enumerate(weights):
                        _require_canonical_rational(
                            weight, f"model.trap_weights[{epsilon!r}][{index}]"
                        )

    protocol = config.get("protocol", {})
    if isinstance(protocol, dict):
        word = protocol.get("word", [])
        if isinstance(word, list):
            for index, leg in enumerate(word):
                if isinstance(leg, dict) and "epsilon" in leg:
                    _require_canonical_rational(leg["epsilon"], f"protocol.word[{index}].epsilon")

        initial_explicit = protocol.get("initial_explicit", {})
        if isinstance(initial_explicit, dict):
            for state, probability in initial_explicit.items():
                _require_canonical_rational(probability, f"protocol.initial_explicit[{state!r}]")


def _validate_epsilon_domain(config: dict[str, Any]) -> None:
    grid_values = [
        _require_canonical_rational(epsilon, f"epsilon_grid[{index}]")
        for index, epsilon in enumerate(config.get("epsilon_grid", []))
    ]
    for index, epsilon in enumerate(grid_values):
        if not Fraction(0) < epsilon < Fraction(1):
            raise ValidationError(f"epsilon_grid[{index}] must lie in the open interval (0, 1)")

    if len(set(grid_values)) != len(grid_values):
        raise ValidationError("epsilon_grid entries must be unique")

    grid_set = set(grid_values)
    protocol = config.get("protocol", {})
    if isinstance(protocol, dict):
        word = protocol.get("word", [])
        if isinstance(word, list):
            for index, leg in enumerate(word):
                if isinstance(leg, dict) and "epsilon" in leg:
                    epsilon = _require_canonical_rational(
                        leg["epsilon"], f"protocol.word[{index}].epsilon"
                    )
                    if epsilon not in grid_set:
                        raise ValidationError(
                            f"protocol.word[{index}].epsilon must be a member of epsilon_grid"
                        )

    model = config.get("model", {})
    if isinstance(model, dict):
        trap_weights = model.get("trap_weights", {})
        if isinstance(trap_weights, dict):
            for epsilon_text in trap_weights:
                epsilon = _require_canonical_rational(
                    epsilon_text, f"model.trap_weights key {epsilon_text!r}"
                )
                if epsilon not in grid_set:
                    raise ValidationError(
                        f"model.trap_weights key {epsilon_text!r} must be a member of epsilon_grid"
                    )


def load_config(path: Path) -> dict[str, Any]:
    """Load a JSON run config and validate it against ``design/schemas``.

    The schema file is read from the repository's ``design/`` tree so the code
    cannot drift from the authoritative artifact contract.
    """

    with path.open(encoding="utf-8") as config_file:
        config = json.load(config_file)
    if not isinstance(config, dict):
        raise ValidationError(f"config at {path} must be a JSON object")

    validator = Draft202012Validator(_load_model_config_schema())
    validator.validate(config)
    _validate_canonical_rationals(config)
    _validate_epsilon_domain(config)
    return config


def canonical_json_bytes(obj: dict[str, Any]) -> bytes:
    """Return the canonical JSON byte representation used for run hashes."""

    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def config_hash(obj: dict[str, Any]) -> str:
    """Return the sha256 hash of a config's canonical JSON bytes."""

    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()


def load_config_with_hash(path: Path) -> tuple[dict[str, Any], str]:
    """Load, validate, and hash a run config."""

    config = load_config(path)
    return config, config_hash(config)
