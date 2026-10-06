"""Validate GB10 empirical bridge records."""

from __future__ import annotations

import json
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_DIR = ROOT / "bridges"
ARTIFACT_DIR = ROOT / "artifacts"
SCHEMA_PATH = ROOT / "design" / "schemas" / "empirical_bridge.schema.json"
BRIDGE_PATHS = (
    BRIDGE_DIR / "kovacs_pvac.json",
    BRIDGE_DIR / "spin_glass_memory.json",
    BRIDGE_DIR / "colloid_aging.json",
)
MANDATORY_NONCLAIMS = frozenset(
    {
        "no realization claim",
        "no continuum-limit claim",
        "microscopic detail suppressed",
        "KCM kinetics are not the lab kinetics",
    }
)
DENYLIST = ("realizes", "is the", "derived from first principles")
NONCLAIM_KEYS = {"suppressed_structure_nonclaims"}


@dataclass(frozen=True)
class BridgeCheckResult:
    ok: bool
    errors: tuple[str, ...]


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _schema() -> dict[str, Any]:
    return _load_json(SCHEMA_PATH)


def _artifact_hashes() -> dict[str, Path]:
    hashes: dict[str, Path] = {}
    for path in ARTIFACT_DIR.rglob("*.json"):
        hashes[sha256(path.read_bytes()).hexdigest()] = path
    return hashes


def _strings_outside_nonclaims(value: Any, *, excluded: bool = False) -> Iterable[str]:
    if isinstance(value, str):
        if not excluded:
            yield value
        return
    if isinstance(value, list):
        for item in value:
            yield from _strings_outside_nonclaims(item, excluded=excluded)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _strings_outside_nonclaims(
                item,
                excluded=excluded or key in NONCLAIM_KEYS,
            )


def validate_bridge(
    path: Path, *, artifact_hashes: dict[str, Path] | None = None
) -> tuple[str, ...]:
    """Return validation errors for one bridge record."""

    errors: list[str] = []
    artifact_hashes = _artifact_hashes() if artifact_hashes is None else artifact_hashes
    try:
        bridge = _load_json(path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return (f"{path}: cannot load bridge JSON: {exc}",)

    schema = _schema()
    schema_errors = sorted(Draft202012Validator(schema).iter_errors(bridge), key=str)
    errors.extend(f"{path}: schema error: {error.message}" for error in schema_errors)

    nonclaims = bridge.get("suppressed_structure_nonclaims", [])
    if isinstance(nonclaims, list):
        missing = MANDATORY_NONCLAIMS.difference(nonclaims)
        if missing:
            errors.append(f"{path}: missing mandatory nonclaims: {sorted(missing)}")
    else:
        errors.append(f"{path}: suppressed_structure_nonclaims must be a list")

    for index, entry in enumerate(bridge.get("level_map", [])):
        if not isinstance(entry, dict):
            continue
        artifact_hash = entry.get("formal_artifact_hash")
        if artifact_hash not in artifact_hashes:
            errors.append(f"{path}: level_map[{index}] hash does not resolve: {artifact_hash}")

    for text in _strings_outside_nonclaims(bridge):
        lowered = text.lower()
        for denied in DENYLIST:
            if denied in lowered:
                errors.append(f"{path}: denylisted phrase outside nonclaims: {denied!r}")

    return tuple(errors)


def check_all(paths: Iterable[Path] = BRIDGE_PATHS) -> BridgeCheckResult:
    artifact_hashes = _artifact_hashes()
    errors: list[str] = []
    for path in paths:
        errors.extend(validate_bridge(path, artifact_hashes=artifact_hashes))
    return BridgeCheckResult(ok=not errors, errors=tuple(errors))


def main() -> None:
    result = check_all()
    if result.ok:
        print(f"PASS: validated {len(BRIDGE_PATHS)} empirical bridge records")
        return
    for error in result.errors:
        print(error, file=sys.stderr)
    raise SystemExit(1)


if __name__ == "__main__":
    main()
