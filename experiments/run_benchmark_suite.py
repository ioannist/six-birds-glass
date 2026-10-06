"""Run the Phase 1 thermal benchmark-parity suite."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.io.config import config_hash  # noqa: E402
from sixbirds_glass.io.rational import rational_to_str  # noqa: E402
from sixbirds_glass.pipeline.diagnostics import summarize  # noqa: E402
from sixbirds_glass.pipeline.loops import loop_action_score  # noqa: E402
from sixbirds_glass.pipeline.package import Continuation, RouteTransportPackage  # noqa: E402
from sixbirds_glass.triage import benchmarks, robustness  # noqa: E402
from sixbirds_glass.triage.classification import ClassificationInput, classify_regime  # noqa: E402
from sixbirds_glass.triage.statuses import (  # noqa: E402
    currentization_status,
    flattening_status,
    support_fixation_status,
)

DEFAULT_OUTPUT_PATH = REPO_ROOT / "artifacts" / "benchmark_suite" / "phase1_parity.json"


@dataclass(frozen=True)
class BenchmarkRowSpec:
    name: str
    package: RouteTransportPackage
    interface: str
    classification: ClassificationInput
    loops: tuple[Continuation, ...]
    support_status: str
    flattening: str
    currentization: str
    robustness_fraction: Fraction
    robustness_threshold: float
    robustness_predicate_name: str


def build_row_specs() -> tuple[BenchmarkRowSpec, ...]:
    """Build all Phase 1 benchmark rows with paired-control statuses."""

    flat = benchmarks.flat_control()
    naive = benchmarks.protocol_trap_naive()
    honest = benchmarks.protocol_trap_honest()
    raw = benchmarks.flattenable_raw()
    completed = benchmarks.flattenable_completed()
    latent_base = benchmarks.latent_memory_base()
    latent_refined = benchmarks.latent_memory_refined()
    dissipative = benchmarks.dissipative_memory()
    wheel = benchmarks.kovacs_wheel()
    wheel_loop = wheel.continuation_by_label("mid", "swap_mid")

    trap_support = support_fixation_status(naive, "mid", honest, "mid")
    flat_support = support_fixation_status(raw, "mid", completed, "mid")
    latent_support = support_fixation_status(latent_base, "mid", latent_refined, "mid")

    raw_flattening = flattening_status(
        summarize(raw, "mid"), summarize(completed, "mid"), flat_support
    )
    latent_currentization = currentization_status(
        summarize(latent_base, "mid"), summarize(latent_refined, "mid"), latent_support
    )

    return (
        _row_spec(
            "flat_control",
            flat,
            classification=robustness.flat_classification(flat),
            robustness_fraction=robustness.flat_control_cleared(),
            robustness_threshold=0.95,
            robustness_predicate_name="flat_control_cleared",
        ),
        _row_spec(
            "protocol_trap_naive",
            naive,
            classification=ClassificationInput(
                base_summary=summarize(naive, "mid"),
                loop_score_current=Fraction(0),
                loop_score_predictive=Fraction(0),
                support_fixation_status=trap_support,
                honest_counterpart_flat=classify_regime(robustness.flat_classification(honest))
                == "flat",
            ),
            support_status=trap_support,
            robustness_fraction=robustness.protocol_trap_naive_persists(),
            robustness_threshold=0.80,
            robustness_predicate_name="protocol_trap_naive_persists",
        ),
        _row_spec(
            "protocol_trap_honest",
            honest,
            classification=robustness.flat_classification(honest),
            support_status=trap_support,
            robustness_fraction=robustness.protocol_trap_honest_cleared(),
            robustness_threshold=0.95,
            robustness_predicate_name="protocol_trap_honest_cleared",
        ),
        _row_spec(
            "flattenable_raw",
            raw,
            classification=ClassificationInput(
                base_summary=summarize(raw, "mid"),
                loop_score_current=Fraction(0),
                loop_score_predictive=Fraction(0),
                support_fixation_status=flat_support,
                flattening_status=raw_flattening,
            ),
            support_status=flat_support,
            flattening=raw_flattening,
            robustness_fraction=robustness.flattenable_raw_persists(),
            robustness_threshold=0.80,
            robustness_predicate_name="flattenable_raw_persists",
        ),
        _row_spec(
            "flattenable_completed",
            completed,
            classification=robustness.flat_classification(completed),
            support_status=flat_support,
            robustness_fraction=robustness.flattenable_completed_cleared(),
            robustness_threshold=0.95,
            robustness_predicate_name="flattenable_completed_cleared",
        ),
        _row_spec(
            "latent_memory_base",
            latent_base,
            classification=ClassificationInput(
                base_summary=summarize(latent_base, "mid"),
                loop_score_current=Fraction(0),
                loop_score_predictive=Fraction(0),
                support_fixation_status=latent_support,
                currentization_status=latent_currentization,
            ),
            support_status=latent_support,
            currentization=latent_currentization,
            robustness_fraction=robustness.latent_memory_base_persists(),
            robustness_threshold=0.80,
            robustness_predicate_name="latent_memory_base_persists",
        ),
        _row_spec(
            "latent_memory_refined",
            latent_refined,
            classification=robustness.flat_classification(latent_refined),
            support_status=latent_support,
            robustness_fraction=robustness.latent_memory_refined_cleared(),
            robustness_threshold=0.95,
            robustness_predicate_name="latent_memory_refined_cleared",
        ),
        _row_spec(
            "dissipative_memory@mid",
            dissipative,
            classification=robustness.dissipative_classification(dissipative),
            robustness_fraction=robustness.dissipative_memory_persists(),
            robustness_threshold=0.80,
            robustness_predicate_name="dissipative_memory_persists",
        ),
        _row_spec(
            "dissipative_memory@end",
            dissipative,
            interface="end",
            classification=robustness.dissipative_end_classification(dissipative),
            robustness_fraction=robustness.dissipative_memory_end_cleared(),
            robustness_threshold=0.95,
            robustness_predicate_name="dissipative_memory_end_cleared",
        ),
        _row_spec(
            "kovacs_wheel",
            wheel,
            loops=(wheel_loop,),
            classification=robustness.kovacs_wheel_classification(wheel),
            flattening="skipped",
            currentization="skipped",
            robustness_fraction=robustness.kovacs_wheel_persists(),
            robustness_threshold=0.80,
            robustness_predicate_name="kovacs_wheel_persists",
        ),
    )


def main(output_path: Path = DEFAULT_OUTPUT_PATH) -> None:
    """Write the Phase 1 benchmark-parity artifact and print a summary table."""

    row_specs = build_row_specs()
    payload = {
        "artifact_status": "phase1_benchmark_parity",
        "note": (
            "Phase 1 benchmark-parity diagnostic; not an honesty-ledger-graded GT certificate."
        ),
        "benchmarks": [_row_payload(spec) for spec in row_specs],
    }
    artifact = {
        "artifact_kind": "triage_regime_table",
        "claim_id": "P1.benchmark_suite.phase1_parity",
        "config_hash": config_hash({"benchmarks": [spec.name for spec in row_specs]}),
        "code_version": _code_version(),
        "claim_grade": "control",
        "evidence_type": "exact_rational",
        "quantifier_domain": {
            "model_families": ["toy_benchmarks"],
            "N_values": [],
            "epsilon_grid": [],
            "lens_catalog_hash": config_hash({"lens": "benchmark_declared_panels"}),
            "protocol_catalog_hash": config_hash({"benchmarks": [spec.name for spec in row_specs]}),
        },
        "nonclaims": [
            "Phase 1 benchmark parity is a control suite, not a standalone GT4 triage certificate.",
            "Dedicated GT4 regime-table promotion, if present, is filed in a separate artifact.",
        ],
        "payload": payload,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(_summary_table(row_specs))
    print(f"wrote {len(row_specs)} rows to {output_path}")


def _row_spec(
    name: str,
    package: RouteTransportPackage,
    *,
    classification: ClassificationInput,
    interface: str = "mid",
    loops: tuple[Continuation, ...] = (),
    support_status: str = "skipped",
    flattening: str = "skipped",
    currentization: str = "skipped",
    robustness_fraction: Fraction,
    robustness_threshold: float,
    robustness_predicate_name: str,
) -> BenchmarkRowSpec:
    return BenchmarkRowSpec(
        name=name,
        package=package,
        interface=interface,
        classification=classification,
        loops=loops,
        support_status=support_status,
        flattening=flattening,
        currentization=currentization,
        robustness_fraction=robustness_fraction,
        robustness_threshold=robustness_threshold,
        robustness_predicate_name=robustness_predicate_name,
    )


def _row_payload(spec: BenchmarkRowSpec) -> dict[str, object]:
    summary = summarize(spec.package, spec.interface)
    loop_q, loop_m = _loop_scores(spec.package, spec.interface, spec.loops)
    regime = classify_regime(spec.classification)
    return {
        "benchmark": spec.name,
        "interface": spec.interface,
        "history_count": summary.history_count,
        "current_quotient_size": summary.current_quotient_size,
        "predictive_quotient_size": summary.predictive_quotient_size,
        "max_fiber_size": summary.max_fiber_size,
        "witness_count": summary.witness_count,
        "exact_max_abs_future_gap": rational_to_str(summary.exact_max_abs_future_gap),
        "discrepancy_metric_value": rational_to_str(summary.exact_max_abs_future_gap),
        "loop_action_score_current_quotient": rational_to_str(loop_q),
        "loop_action_score_predictive_quotient": rational_to_str(loop_m),
        "support_fixation_status": spec.support_status,
        "flattening_status": spec.flattening,
        "currentization_status": spec.currentization,
        "robustness_fraction": rational_to_str(spec.robustness_fraction),
        "robustness_threshold": spec.robustness_threshold,
        "robustness_predicate_name": spec.robustness_predicate_name,
        "regime": regime,
    }


def _summary_table(row_specs: tuple[BenchmarkRowSpec, ...]) -> str:
    lines = [
        "benchmark                 Q  M  fiber  wit  gap  loopQ  loopM  robust  thresh  regime"
    ]
    for spec in row_specs:
        summary = summarize(spec.package, spec.interface)
        loop_q, loop_m = _loop_scores(spec.package, spec.interface, spec.loops)
        regime = classify_regime(spec.classification)
        lines.append(
            f"{spec.name:<25} "
            f"{summary.current_quotient_size:>1}  "
            f"{summary.predictive_quotient_size:>1}  "
            f"{summary.max_fiber_size:>5}  "
            f"{summary.witness_count:>3}  "
            f"{rational_to_str(summary.exact_max_abs_future_gap):>3}  "
            f"{rational_to_str(loop_q):>5}  "
            f"{rational_to_str(loop_m):>5}  "
            f"{rational_to_str(spec.robustness_fraction):>6}  "
            f"{spec.robustness_threshold:>6.2f}  "
            f"{regime}"
        )
    return "\n".join(lines)


def _loop_scores(
    package: RouteTransportPackage, interface: str, loops: tuple[Continuation, ...]
) -> tuple[Fraction, Fraction]:
    return (
        loop_action_score(package, interface, loops, quotient_kind="current"),
        loop_action_score(package, interface, loops, quotient_kind="predictive"),
    )


def _code_version() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


if __name__ == "__main__":
    main()
