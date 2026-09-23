import importlib.util
import json
from fractions import Fraction
from pathlib import Path

import pytest

from sixbirds_glass.io.rational import rational_to_str
from sixbirds_glass.pipeline.kovacs_hump import analyze_hump_trace, detect_kovacs_hump


def test_analyze_hump_trace_detects_crossing_overshoot_and_return() -> None:
    analysis = analyze_hump_trace(
        [Fraction(-2), Fraction(-1), Fraction(1), Fraction(3), Fraction(2)],
        Fraction(0),
    )

    assert analysis.found
    assert analysis.t_k == 1
    assert analysis.t_peak == 3
    assert analysis.hump_height == Fraction(3)


def test_analyze_hump_trace_rejects_crossing_without_overshoot() -> None:
    analysis = analyze_hump_trace(
        [Fraction(-2), Fraction(-1), Fraction(1), Fraction(1, 2), Fraction(1, 4)],
        Fraction(0),
    )

    assert not analysis.found
    assert analysis.miss_reason == "crossed but never overshot"


def test_analyze_hump_trace_rejects_overshoot_without_return() -> None:
    analysis = analyze_hump_trace(
        [Fraction(-2), Fraction(-1), Fraction(1), Fraction(3), Fraction(4)],
        Fraction(0),
    )

    assert not analysis.found
    assert analysis.miss_reason == "no return from peak"


def test_analyze_hump_trace_rejects_reversed_direction_dip() -> None:
    analysis = analyze_hump_trace(
        [Fraction(2), Fraction(1), Fraction(-1), Fraction(-3), Fraction(-2)],
        Fraction(0),
    )

    assert not analysis.found
    assert analysis.miss_reason == "does not start below equilibrium"


def test_analyze_hump_trace_rejects_negative_post_crossing_side() -> None:
    analysis = analyze_hump_trace(
        [Fraction(-2), Fraction(0), Fraction(-1), Fraction(-3), Fraction(-2)],
        Fraction(0),
    )

    assert not analysis.found
    assert analysis.miss_reason == "post-crossing side is not above equilibrium"


def test_analyze_hump_trace_rejects_no_crossing() -> None:
    analysis = analyze_hump_trace(
        [Fraction(-2), Fraction(-1), Fraction(-1, 2)],
        Fraction(0),
    )

    assert not analysis.found
    assert analysis.miss_reason == "no crossing"


def test_detect_kovacs_hump_denominator_abort_path() -> None:
    result = detect_kovacs_hump(
        2,
        Fraction(7, 10),
        Fraction(1, 10),
        Fraction(2, 5),
        t_w=1,
        tau_probe=1,
        denominator_bit_cap=0,
    )

    assert not result.found
    assert result.abort_reason is not None
    assert "max_denominator_bits" in result.abort_reason


@pytest.mark.slow
def test_declared_real_search_runs_to_completion() -> None:
    search = load_search_module()
    found, results, closest = search.run_search(
        n_values=(10,), t_w_values=(40,), tau_probe_values=(60,)
    )

    assert len(results) == 1
    assert closest in results
    assert found is not None
    assert found.found
    assert_found_matches_frozen_files(found)


def test_committed_kovacs_artifact_records_widened_grid() -> None:
    artifact = json.loads(
        Path("artifacts/kovacs_hump_check/result.json").read_text(encoding="utf-8")
    )["payload"]

    assert artifact["search_grid"]["N_values"] == [6, 10]
    assert len(artifact["results"]) == 24
    assert any(result["N"] == 10 and result["found"] for result in artifact["results"])


def assert_found_matches_frozen_files(found) -> None:
    config = json.loads(Path("configs/kovacs_hump_default.json").read_text(encoding="utf-8"))
    artifact = json.loads(
        Path("artifacts/kovacs_hump_check/result.json").read_text(encoding="utf-8")
    )["payload"]
    selected = artifact["selected_result"]

    assert config["model"]["N"] == found.N
    assert config["protocol"]["word"] == [
        {"epsilon": rational_to_str(found.epsilon_hi), "steps": found.tau_hot},
        {"epsilon": rational_to_str(found.epsilon_lo), "steps": found.t_w},
        {"epsilon": rational_to_str(found.epsilon_mid), "steps": found.tau_probe},
    ]
    assert selected["N"] == found.N
    assert selected["epsilon_hi"] == rational_to_str(found.epsilon_hi)
    assert selected["epsilon_lo"] == rational_to_str(found.epsilon_lo)
    assert selected["epsilon_mid"] == rational_to_str(found.epsilon_mid)
    assert selected["t_w"] == found.t_w
    assert selected["tau_probe"] == found.tau_probe
    assert selected["t_k"] == found.t_k
    assert selected["t_peak"] == found.t_peak
    assert selected["hump_height"] == rational_to_str(found.hump_height or Fraction(0))


def load_search_module():
    script_path = Path(__file__).resolve().parents[1] / "experiments" / "search_kovacs_hump.py"
    spec = importlib.util.spec_from_file_location("search_kovacs_hump", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
