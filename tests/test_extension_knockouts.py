from pathlib import Path

import pytest

from sixbirds_glass.extension.knockouts import full_loop_nondegeneracy, run_knockout_panel
from sixbirds_glass.io.config import load_config

pytestmark = pytest.mark.slow


def test_six_knockouts_have_distinct_expected_degradations() -> None:
    config = load_config(Path("configs/gt6_shell_witness_n8.json"))

    results = run_knockout_panel(config)
    by_primitive = {result.primitive: result for result in results}

    assert set(by_primitive) == {"P1", "P2", "P3", "P4", "P5", "P6"}
    assert [by_primitive[primitive].kind for primitive in ("P1", "P2", "P3")] == [
        "numeric",
        "numeric",
        "numeric",
    ]
    assert [by_primitive[primitive].kind for primitive in ("P4", "P5", "P6")] == [
        "capability_loss",
        "capability_loss",
        "capability_loss",
    ]
    assert all(result.degraded for result in results)
    assert by_primitive["P1"].knockout_value["trace_variation"] == 0
    assert by_primitive["P2"].knockout_value["unconstrained_exactly_lumpable"] is True
    assert by_primitive["P3"].knockout_value["hump_found"] is False
    assert by_primitive["P4"].knockout_value["saturation_budget"] is None
    assert by_primitive["P5"].knockout_value is None
    assert by_primitive["P6"].knockout_value is None


def test_full_loop_nondegeneracy_all_axes_active() -> None:
    config = load_config(Path("configs/gt6_shell_witness_n8.json"))

    baseline = full_loop_nondegeneracy(config)

    assert all(baseline.values())
