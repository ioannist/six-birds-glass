"""Check the Python-to-Lean numeric bridge against actual certificate values."""

import importlib.util
import json
from pathlib import Path

import pytest

from sixbirds_glass.io.config import load_config
from sixbirds_glass.pipeline.kovacs_witness import build_kovacs_moment_witness_from_config

ROOT = Path(__file__).resolve().parents[1]


def _exporter():
    path = ROOT / "experiments/export_lean_witness.py"
    spec = importlib.util.spec_from_file_location("export_lean_witness", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "n,config", [(8, "gt6_shell_witness_n8.json"), (10, "kovacs_hump_default.json")]
)
def test_checked_in_numeric_export_matches_exact_recomputation(n: int, config: str) -> None:
    exporter = _exporter()
    actual_n, rendered = exporter.render_witness(ROOT / "configs" / config)
    assert actual_n == n
    assert (ROOT / "lean/GlassWitness" / f"NumericN{n}.lean").read_text() == rendered
    # Regeneration is byte-stable, including the signature binding.
    assert exporter.render_witness(ROOT / "configs" / config) == (n, rendered)


def test_recomputed_n10_numeric_values_match_the_existing_exact_certificate() -> None:
    from fractions import Fraction

    exporter = _exporter()
    _n, rendered = exporter.render_witness(ROOT / "configs/kovacs_hump_default.json")
    artifact = json.loads((ROOT / "artifacts/gt2_witnesses/kovacs_moment.json").read_text())
    pair = artifact["payload"]["witness_pairs"][0]
    values = [
        pair["s0_equal_entries"][0]["value"],
        pair["separating_entry"]["value_h"],
        pair["separating_entry"]["value_hprime"],
    ]
    for value in values:
        rational = Fraction(value)
        assert f"({rational.numerator} : Rat) / {rational.denominator}" in rendered


@pytest.mark.parametrize("field,value", [("family", "fa"), ("boundary", "periodic")])
def test_numeric_builder_cannot_silently_replace_the_declared_model(field: str, value: str) -> None:
    config = load_config(ROOT / "configs/gt6_shell_witness_n8.json")
    config["model"][field] = value
    with pytest.raises(ValueError, match="wall-up East"):
        build_kovacs_moment_witness_from_config(config)


def test_numeric_continuation_must_fit_declared_window() -> None:
    config = load_config(ROOT / "configs/gt6_shell_witness_n8.json")
    with pytest.raises(ValueError, match="fit the declared probe window"):
        build_kovacs_moment_witness_from_config(config, probe_steps=31)


def test_numeric_builder_enforces_declared_arithmetic_cap() -> None:
    config = load_config(ROOT / "configs/gt6_shell_witness_n8.json")
    config["arithmetic"]["max_denominator_bits"] = 2
    with pytest.raises(ValueError, match="exceeded cap"):
        build_kovacs_moment_witness_from_config(config)
