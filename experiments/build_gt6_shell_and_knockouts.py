"""Build the GB6 shell declaration and six-primitive knockout artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.extension.knockouts import (  # noqa: E402
    KnockoutResult,
    full_loop_nondegeneracy,
    run_knockout_panel,
)
from sixbirds_glass.extension.shell import (  # noqa: E402
    NON_EQUILIBRATION_TOLERANCE,
    TAU_ALPHA_LOWER_DIVISOR,
    build_shell_witnesses,
)
from sixbirds_glass.io.config import config_hash, load_config  # noqa: E402
from sixbirds_glass.io.rational import rational_to_str  # noqa: E402
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID  # noqa: E402

OUTPUT_PATH = REPO_ROOT / "artifacts" / "gt6_bridge" / "knockouts.json"
N10_CONFIG_PATH = REPO_ROOT / "configs" / "kovacs_hump_default.json"


def main(output_path: Path = OUTPUT_PATH) -> None:
    """Write the GT6 shell-and-knockout artifact."""

    artifact = build_artifact()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(
        "gt6_shell_knockouts "
        f"witness_exits={[row['exit_count'] for row in artifact['payload']['shell_witnesses']]} "
        f"degraded={sum(row['degraded'] for row in artifact['payload']['knockouts'])}/6 "
        f"wrote={output_path}"
    )


def build_artifact() -> dict[str, Any]:
    """Return the GT6 shell and knockout-panel artifact."""

    witnesses = build_shell_witnesses()
    config = load_config(N10_CONFIG_PATH)
    panel = run_knockout_panel(config)
    return {
        "artifact_kind": "knockout_panel",
        "claim_id": "GT6.knockout_panel.glass_shell",
        "config_hash": config_hash(config),
        "config_path": str(N10_CONFIG_PATH.resolve().relative_to(REPO_ROOT)),
        "code_version": _code_version(),
        "claim_grade": "certificate_shell_local",
        "evidence_type": "float64_deterministic",
        "quantifier_domain": {
            "model_families": ["east"],
            "N_values": [8, 10],
            "epsilon_grid": [rational_to_str(epsilon) for epsilon in DEFAULT_EPSILON_GRID],
            "lens_catalog_hash": config_hash({"lens": "L_energy"}),
            "protocol_catalog_hash": config_hash(config["protocol"]),
        },
        "nonclaims": [
            "Knockout rows are shell-local diagnostics, not shell-general strict-extension proofs.",
            "P4-P6 rows are capability-loss degradations, not numeric re-simulation degradations.",
        ],
        "payload": {
            "artifact_status": "phase3_shell_lawfulness_panel",
            "note": (
                "GB6 shell and primitive-knockout panel; pressure closure and strict-extension "
                "hypotheses are later Phase 3 packets."
            ),
            "thresholds": {
                "tau_alpha_lower_divisor": TAU_ALPHA_LOWER_DIVISOR,
                "non_equilibration_tolerance": rational_to_str(NON_EQUILIBRATION_TOLERANCE),
                "numeric_knockouts": {
                    "P1": "identity trace variation must be exactly 0 while baseline varies",
                    "P2": "unconstrained control must be exactly lumpable under L_energy",
                    "P3": "constant-epsilon replacement must fail the hump detector",
                },
                "capability_loss_knockouts": {
                    "P4": "empty scalar pool leaves only B=0 buyback and no saturation budget",
                    "P5": "packaging endomap disabled, so delta_tau_f and strata are undefined",
                    "P6": "affinity/EPR audit disabled, so P6_drive classification is unavailable",
                },
            },
            "shell_witnesses": [_witness_payload(witness) for witness in witnesses],
            "full_loop_nondegeneracy": _jsonable(full_loop_nondegeneracy(config)),
            "knockouts": [_knockout_payload(row) for row in panel],
            "numeric_vs_capability_loss_note": (
                "P1-P3 are numeric re-simulation degradations; P4-P6 are structural "
                "capability-loss degradations."
            ),
        },
    }


def _witness_payload(witness: Any) -> dict[str, Any]:
    return {
        "label": witness.label,
        "config_path": str(witness.config_path.resolve().relative_to(REPO_ROOT)),
        "N": witness.N,
        "exit_count": witness.exit_count,
        "in_shell": witness.membership.in_shell,
        "checkpoints": [
            {"label": checkpoint.label, "passed": checkpoint.passed, "notes": checkpoint.notes}
            for checkpoint in witness.membership.checkpoints
        ],
    }


def _knockout_payload(row: KnockoutResult) -> dict[str, Any]:
    data = asdict(row)
    return _jsonable(data)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Fraction):
        return rational_to_str(value)
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


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
