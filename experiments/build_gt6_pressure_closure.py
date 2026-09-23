"""Build the GT6 Fekete pressure-closure support artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.extension.pressure import (  # noqa: E402
    fekete_gap,
    pressure_ladder,
    tilted_transfer_matrix,
    verify_subadditivity,
)
from sixbirds_glass.extension.shell import SPECTRAL_GAPS_PATH, build_shell_witnesses  # noqa: E402
from sixbirds_glass.io.config import config_hash, load_config  # noqa: E402
from sixbirds_glass.io.rational import rational_to_str, str_to_rational  # noqa: E402
from sixbirds_glass.lenses.catalog import l_energy  # noqa: E402
from sixbirds_glass.models.east import build_east_kernel  # noqa: E402
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID  # noqa: E402

OUTPUT_PATH = REPO_ROOT / "artifacts" / "gt6_bridge" / "pressure_closure.json"
TILT_GRID = (Fraction(-1, 2), Fraction(-1, 5), Fraction(0), Fraction(1, 5), Fraction(1, 2))
N_VALUES = tuple(range(1, 9))
N_MIN = 4
DENSE_STATE_THRESHOLD = 256
SUBADDITIVITY_PAIRS = ((1, 1), (1, 2), (2, 3), (3, 4))


def main(output_path: Path = OUTPUT_PATH) -> None:
    """Write the pressure-closure artifact."""

    artifact = build_artifact()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    computed = [row for row in artifact["payload"]["rows"] if row["status"] == "computed"]
    print(
        "gt6_pressure_closure "
        f"computed_rows={len(computed)} "
        f"skipped_rows={len(artifact['payload']['rows']) - len(computed)} "
        f"wrote={output_path}"
    )


def build_artifact() -> dict[str, Any]:
    """Return the pressure-closure support artifact."""

    spectral_rows = _load_spectral_rows()
    witnesses = build_shell_witnesses(materialize_n8=False)
    rows: list[dict[str, Any]] = []
    for witness in witnesses:
        config = load_config(witness.config_path)
        epsilon_mid = str_to_rational(config["protocol"]["word"][2]["epsilon"])
        state_count = 1 << witness.N
        for tilt in TILT_GRID:
            if state_count > DENSE_STATE_THRESHOLD:
                rows.append(_skipped_row(witness, tilt, state_count))
                continue
            rows.append(
                _computed_row(
                    witness_label=witness.label,
                    N=witness.N,
                    shell_exits=witness.exit_count,
                    epsilon=epsilon_mid,
                    tilt=tilt,
                    spectral=spectral_rows[(witness.N, rational_to_str(epsilon_mid))],
                )
            )
    return {
        "artifact_kind": "pressure_closure",
        "claim_id": "GT6.pressure_closure.glass_shell",
        "config_hash": config_hash(
            {
                "tilt_grid": [rational_to_str(value) for value in TILT_GRID],
                "n_values": list(N_VALUES),
                "n_min": N_MIN,
                "dense_state_threshold": DENSE_STATE_THRESHOLD,
                "subadditivity_pairs": [list(pair) for pair in SUBADDITIVITY_PAIRS],
            }
        ),
        "code_version": _code_version(),
        "claim_grade": "certificate_shell_local",
        "evidence_type": "float64_deterministic",
        "quantifier_domain": {
            "model_families": ["east"],
            "N_values": [8, 10],
            "epsilon_grid": [rational_to_str(epsilon) for epsilon in DEFAULT_EPSILON_GRID],
            "lens_catalog_hash": config_hash({"lens": "L_energy"}),
            "protocol_catalog_hash": config_hash({"witnesses": ["kovacs_N8", "kovacs_N10"]}),
        },
        "nonclaims": [
            "Pressure closure is a float64 Fekete diagnostic, not an exact-rational certificate.",
            (
                "N=10 dense pressure rows may be skipped by declared threshold "
                "and are reported as such."
            ),
        ],
        "payload": {
            "artifact_status": "phase3_pressure_closure_support",
            "note": (
                "Fekete pressure-closure support table for route (a); N=10 dense rows are "
                "explicitly skipped when they exceed the declared dense threshold."
            ),
            "declarations": {
                "tilt_grid": [rational_to_str(value) for value in TILT_GRID],
                "n_values": list(N_VALUES),
                "n_min": N_MIN,
                "dense_state_threshold": DENSE_STATE_THRESHOLD,
                "subadditivity_pairs": [list(pair) for pair in SUBADDITIVITY_PAIRS],
            },
            "rows": rows,
        },
    }


def _computed_row(
    *,
    witness_label: str,
    N: int,
    shell_exits: int,
    epsilon: Fraction,
    tilt: Fraction,
    spectral: dict[str, Any],
) -> dict[str, Any]:
    kernel = build_east_kernel(N, epsilon)
    s = float(tilt)
    ladder = pressure_ladder(kernel, l_energy, N, s, N_VALUES)
    matrix = tilted_transfer_matrix(kernel, l_energy, N, s)
    checks = verify_subadditivity(matrix, SUBADDITIVITY_PAIRS)
    n_max = max(ladder)
    return {
        "witness": witness_label,
        "N": N,
        "size": 1 << N,
        "epsilon": rational_to_str(epsilon),
        "tilt": rational_to_str(tilt),
        "status": "computed",
        "shell_exits": shell_exits,
        "fekete_gap": fekete_gap(ladder, N_MIN),
        "growth_bound": ladder[n_max],
        "computed_ladder_inf": min(ladder.values()),
        "ladder": {str(n): value for n, value in ladder.items()},
        "subadditivity_verified": all(check.passed for check in checks),
        "subadditivity_checks": [
            {
                "n": check.n,
                "m": check.m,
                "log_phi_n_plus_m": check.log_phi_n_plus_m,
                "log_phi_n_plus_log_phi_m": check.log_phi_n_plus_log_phi_m,
                "passed": check.passed,
                "tolerance": check.tolerance,
            }
            for check in checks
        ],
        "margins": {
            "spectral_gap": spectral["gap"],
            "tau_rel": spectral["tau_rel"],
            "mixing_time_bound": spectral["mixing_time_bound"],
        },
    }


def _skipped_row(witness: Any, tilt: Fraction, state_count: int) -> dict[str, Any]:
    return {
        "witness": witness.label,
        "N": witness.N,
        "size": state_count,
        "tilt": rational_to_str(tilt),
        "status": "skipped_dense_threshold",
        "shell_exits": witness.exit_count,
        "skip_reason": (
            f"state_count={state_count} exceeds dense_state_threshold={DENSE_STATE_THRESHOLD}"
        ),
    }


def _load_spectral_rows() -> dict[tuple[int, str], dict[str, Any]]:
    data = json.loads(SPECTRAL_GAPS_PATH.read_text(encoding="utf-8"))
    rows = data.get("payload", data)["rows"]
    return {
        (int(row["N"]), row["epsilon"]): {
            "gap": float(row["gap"]),
            "tau_rel": float(row["tau_rel"]),
            "mixing_time_bound": float(row["mixing_time_bound"]),
        }
        for row in rows
    }


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
