import importlib.util
import json
import sys
from pathlib import Path


def test_run_benchmark_suite_writes_phase1_parity_artifact(tmp_path) -> None:
    output_path = tmp_path / "phase1_parity.json"
    main = load_main()

    main(output_path)

    artifact = json.loads(output_path.read_text(encoding="utf-8"))
    payload = artifact["payload"]
    assert artifact["artifact_kind"] == "triage_regime_table"
    assert payload["artifact_status"] == "phase1_benchmark_parity"
    rows = payload["benchmarks"]
    assert len(rows) == 10

    required = {
        "benchmark",
        "interface",
        "history_count",
        "current_quotient_size",
        "predictive_quotient_size",
        "max_fiber_size",
        "witness_count",
        "exact_max_abs_future_gap",
        "discrepancy_metric_value",
        "loop_action_score_current_quotient",
        "loop_action_score_predictive_quotient",
        "support_fixation_status",
        "flattening_status",
        "currentization_status",
        "robustness_fraction",
        "robustness_threshold",
        "robustness_predicate_name",
        "regime",
    }
    assert all(required <= set(row) for row in rows)
    assert {row["benchmark"] for row in rows} == {
        "flat_control",
        "protocol_trap_naive",
        "protocol_trap_honest",
        "flattenable_raw",
        "flattenable_completed",
        "latent_memory_base",
        "latent_memory_refined",
        "dissipative_memory@mid",
        "dissipative_memory@end",
        "kovacs_wheel",
    }
    assert all(row["robustness_fraction"] == "1/1" for row in rows)


def load_main():
    script_path = Path(__file__).resolve().parents[1] / "experiments" / "run_benchmark_suite.py"
    spec = importlib.util.spec_from_file_location("run_benchmark_suite", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.main
