"""Constructive full-energy-law bridges and meaningful false-target controls."""

import importlib.util
import json
from copy import deepcopy
from fractions import Fraction
from pathlib import Path

import pytest

from sixbirds_glass.io.config import load_config
from sixbirds_glass.models.east import build_east_kernel
from sixbirds_glass.models.unconstrained import build_unconstrained_kernel
from sixbirds_glass.pipeline.energy_witness import (
    build_energy_mixture_witness,
    build_energy_mixture_witness_from_config,
    separating_energy_values,
    split_stopping_laws,
)
from sixbirds_glass.pipeline.reflection_witness import energy_level_distribution
from sixbirds_glass.protocols.evolution import hold

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "configs/gt6_shell_witness_n8.json"


def _module(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "experiments" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def witness():
    return build_energy_mixture_witness_from_config(load_config(CONFIG_PATH))


def test_actual_preparations_are_convex_and_match_complete_energy_law(witness) -> None:
    w, m = witness, witness.mixtures
    assert m.rank == 9 and m.free_column == 9
    assert w.stop_times == tuple(range(10))
    assert m.plus != m.minus
    kernel = build_east_kernel(w.N, w.epsilon_mid)
    for stop, law in zip(w.stop_times, w.source_laws, strict=True):
        assert law == hold(w.source_laws[0], kernel, stop)
    for law, weights in [(m.plus, m.plus_weights), (m.minus, m.minus_weights)]:
        assert min(weights) >= 0 and sum(weights) == 1
        assert min(law.values()) >= 0 and sum(law.values()) == 1
        for state in range(1 << w.N):
            assert law.get(state, 0) == sum(
                weight * source.get(state, 0)
                for weight, source in zip(weights, w.source_laws, strict=True)
            )
        assert energy_level_distribution(law, w.N) == m.energy_law


def test_every_declared_continuation_separates_and_fits_source_window(witness) -> None:
    assert list(witness.future_values) == list(range(1, 22))
    assert all(a != b for a, b in witness.future_values.values())
    assert max(witness.stop_times) + max(witness.future_values) == witness.tau_probe


def test_probe_ablation_preserves_same_sources_and_erases_every_split(witness) -> None:
    control = separating_energy_values(
        witness.mixtures,
        witness.N,
        build_unconstrained_kernel(witness.N, witness.epsilon_mid),
        tuple(witness.future_values),
    )
    assert all(a == b for a, b in control.values())


def test_null_selector_cannot_force_a_false_target() -> None:
    law = {0: Fraction(1)}
    mixtures = split_stopping_laws((law, law, law), 1)
    assert mixtures.plus == mixtures.minus == law
    with pytest.raises(ValueError, match="do not split"):
        build_energy_mixture_witness(2, Fraction(1, 2), Fraction(1, 2), Fraction(1, 2), 0, 10)


def test_arithmetic_cap_is_not_ignored() -> None:
    config = load_config(CONFIG_PATH)
    config["arithmetic"]["max_denominator_bits"] = 2
    with pytest.raises(ValueError, match="exceed cap"):
        build_energy_mixture_witness_from_config(config)


@pytest.fixture(scope="module")
def certificate():
    audit = _module("audit_gt6_energy_witness")
    original = json.loads((ROOT / "math/gt6_energy_mixture_witness.json").read_text())
    audit.verify_certificate(original)
    return audit, original


@pytest.mark.parametrize("field", ["current", "weights", "gap", "stability"])
def test_certificate_replay_rejects_corrupt_scientific_fields(certificate, field: str) -> None:
    audit, original = certificate
    changed = deepcopy(original)
    if field == "current":
        changed["object_maps"]["pi0"]["h_minus"][0] = "0"
    elif field == "weights":
        changed["construction"]["positive_stopping_weights"][0] = "1"
    elif field == "gap":
        changed["future_energy"]["5"]["absolute_gap"] = "1"
    else:
        changed["packaging_fixed_point_obstruction"]["conclusion"] = "many fixed points"
    with pytest.raises(ValueError, match="exact source replay"):
        audit.verify_certificate(changed)


def test_full_energy_lean_export_is_bound_to_recomputed_sources() -> None:
    exporter = _module("export_lean_energy_witness")
    rendered = exporter.render_witness()
    assert (ROOT / "lean/GlassWitness/EnergyN8.lean").read_text() == rendered
    assert exporter.render_witness() == rendered
