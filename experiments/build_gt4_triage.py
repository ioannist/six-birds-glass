"""Build the GT4 six-regime triage artifact from the benchmark suite rows."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
EXPERIMENTS_ROOT = REPO_ROOT / "experiments"
for path in (SRC_ROOT, EXPERIMENTS_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import run_benchmark_suite  # noqa: E402

from sixbirds_glass.io.config import config_hash  # noqa: E402

OUTPUT_PATH = REPO_ROOT / "artifacts" / "gt4_triage" / "regime_table.json"
PHASE1_PARITY_PATH = REPO_ROOT / "artifacts" / "benchmark_suite" / "phase1_parity.json"


def main(output_path: Path = OUTPUT_PATH) -> None:
    """Write the GT4 regime-triage artifact."""

    artifact = build_artifact()
    _validate_artifact(artifact)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(
        "gt4_triage "
        f"rows={len(artifact['payload']['benchmarks'])} "
        f"coherent={artifact['payload']['summary']['coherent_candidate']} "
        f"wrote={output_path}"
    )


def build_artifact() -> dict[str, Any]:
    """Return the GT4 triage artifact built from the Phase-1 benchmark row specs."""

    row_specs = run_benchmark_suite.build_row_specs()
    rows = [run_benchmark_suite._row_payload(spec) for spec in row_specs]
    summary = _summary(rows)
    config = {
        "benchmarks": [row["benchmark"] for row in rows],
        "interfaces": [row["interface"] for row in rows],
    }
    return {
        "artifact_kind": "triage_regime_table",
        "claim_id": "GT4.regime_triage.east_benchmarks",
        "config_hash": config_hash(config),
        "code_version": _code_version(),
        "claim_grade": "theorem_audited_class",
        "evidence_type": "exact_rational",
        "quantifier_domain": {
            "model_families": ["thermal_benchmarks"],
            "N_values": [],
            "epsilon_grid": [],
            "lens_catalog_hash": config_hash({"lens": "benchmark_declared_panels"}),
            "protocol_catalog_hash": config_hash(config),
        },
        "nonclaims": [
            (
                "GT4 triage is over the declared finite benchmark family, not a "
                "shell-general theorem."
            ),
            (
                "The artifact promotes the Phase-1 benchmark-suite data; it does "
                "not change the underlying classification logic."
            ),
            (
                "GB1 protocol-trap caveat remains a theorem-wrapper limitation; "
                "this table files the deterministic triage computation."
            ),
        ],
        "payload": {
            "artifact_status": "gt4_regime_triage",
            "source_artifact": {
                "path": str(PHASE1_PARITY_PATH.relative_to(REPO_ROOT)),
                "sha256": _sha256_file(PHASE1_PARITY_PATH),
            },
            "summary": summary,
            "benchmarks": rows,
        },
    }


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    regimes = {row["benchmark"]: row["regime"] for row in rows}
    return {
        "row_count": len(rows),
        "benchmark_family_count": len({_family_id(row["benchmark"]) for row in rows}),
        "coherent_candidate": "kovacs_wheel",
        "coherent_candidate_regime": regimes["kovacs_wheel"],
        "noncoherent_regime_controls": {
            "flat": {"raw": "flat_control", "regime": regimes["flat_control"]},
            "artifact_trap": {
                "raw": "protocol_trap_naive",
                "raw_regime": regimes["protocol_trap_naive"],
                "cleared": "protocol_trap_honest",
                "cleared_regime": regimes["protocol_trap_honest"],
            },
            "flattenable": {
                "raw": "flattenable_raw",
                "raw_regime": regimes["flattenable_raw"],
                "cleared": "flattenable_completed",
                "cleared_regime": regimes["flattenable_completed"],
            },
            "explicit_latent": {
                "raw": "latent_memory_base",
                "raw_regime": regimes["latent_memory_base"],
                "cleared": "latent_memory_refined",
                "cleared_regime": regimes["latent_memory_refined"],
            },
            "dissipative": {
                "raw": "dissipative_memory@mid",
                "raw_regime": regimes["dissipative_memory@mid"],
                "cleared": "dissipative_memory@end",
                "cleared_regime": regimes["dissipative_memory@end"],
            },
        },
        "claim_pass": _claim_pass(regimes),
        "note": (
            "There are nine benchmark families; dissipative_memory contributes two "
            "rows because its mid/end interfaces file persistence and clearing."
        ),
    }


def _claim_pass(regimes: dict[str, str]) -> bool:
    return regimes == {
        "flat_control": "flat",
        "protocol_trap_naive": "artifact_trap",
        "protocol_trap_honest": "flat",
        "flattenable_raw": "flattenable",
        "flattenable_completed": "flat",
        "latent_memory_base": "explicit_latent",
        "latent_memory_refined": "flat",
        "dissipative_memory@mid": "dissipative",
        "dissipative_memory@end": "flat",
        "kovacs_wheel": "coherent_candidate",
    }


def _family_id(benchmark: str) -> str:
    if benchmark.startswith("dissipative_memory@"):
        return "dissipative_memory"
    return benchmark


def _validate_artifact(artifact: dict[str, Any]) -> None:
    schema = json.loads(
        (REPO_ROOT / "design" / "schemas" / "artifact_envelope.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(schema).validate(artifact)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
