"""Compute the East spectral-gap diagnostic table."""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Sequence
from fractions import Fraction
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.io.config import config_hash  # noqa: E402
from sixbirds_glass.io.rational import rational_to_str  # noqa: E402
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID  # noqa: E402
from sixbirds_glass.models.spectral import spectral_gap_table_row  # noqa: E402

DEFAULT_N_VALUES = (6, 8, 10)
DEFAULT_OUTPUT_PATH = REPO_ROOT / "artifacts" / "spectral_gaps" / "east.json"


def compute_rows(
    *,
    n_values: Sequence[int] = DEFAULT_N_VALUES,
    epsilon_grid: Sequence[Fraction] = DEFAULT_EPSILON_GRID,
) -> list[dict[str, int | str | float]]:
    """Compute all East spectral-gap rows for the requested finite grid."""

    return [spectral_gap_table_row(N, epsilon) for N in n_values for epsilon in epsilon_grid]


def main(
    output_path: Path = DEFAULT_OUTPUT_PATH,
    *,
    n_values: Sequence[int] = DEFAULT_N_VALUES,
    epsilon_grid: Sequence[Fraction] = DEFAULT_EPSILON_GRID,
) -> None:
    """Write the East spectral-gap table and print a compact summary."""

    rows = compute_rows(n_values=n_values, epsilon_grid=epsilon_grid)
    payload = {
        "artifact_status": "phase0_diagnostic",
        "model": "east",
        "note": (
            "Pre-certificate spectral diagnostic table; not an honesty-ledger-graded certificate."
        ),
        "rows": rows,
    }
    output = {
        "artifact_kind": "spectral_gap_table",
        "claim_id": "P0.spectral_gaps.east",
        "config_hash": config_hash(
            {
                "n_values": list(n_values),
                "epsilon_grid": [rational_to_str(epsilon) for epsilon in epsilon_grid],
            }
        ),
        "code_version": _code_version(),
        "claim_grade": "control",
        "evidence_type": "float64_deterministic",
        "quantifier_domain": {
            "model_families": ["east"],
            "N_values": list(n_values),
            "epsilon_grid": [rational_to_str(epsilon) for epsilon in epsilon_grid],
            "lens_catalog_hash": config_hash({"lens": "L_energy"}),
            "protocol_catalog_hash": config_hash({"kernel": "east_constant_epsilon"}),
        },
        "nonclaims": [
            (
                "Spectral gaps are float64 diagnostics and not theorem-graded "
                "exact-rational certificates."
            ),
            "Mixing-time bounds are used for shell-window calibration only.",
        ],
        "payload": payload,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")

    print("N  epsilon  gap           tau_rel")
    for row in rows:
        print(f"{row['N']:>2} {row['epsilon']:>8} {row['gap']:.10g} {row['tau_rel']:.10g}")
    print(f"wrote {len(rows)} rows to {output_path}")


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
