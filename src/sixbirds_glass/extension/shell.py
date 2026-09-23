"""GB6 shell declaration and membership checks for GT6."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any

from sixbirds_glass.io.config import load_config
from sixbirds_glass.io.rational import rational_to_str, str_to_rational
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID
from sixbirds_glass.pipeline.kovacs_hump import detect_kovacs_hump

REPO_ROOT = Path(__file__).resolve().parents[3]
SPECTRAL_GAPS_PATH = REPO_ROOT / "artifacts" / "spectral_gaps" / "east.json"
KOVACS_N10_CONFIG_PATH = REPO_ROOT / "configs" / "kovacs_hump_default.json"
KOVACS_N8_CONFIG_PATH = REPO_ROOT / "configs" / "gt6_shell_witness_n8.json"

TAU_ALPHA_LOWER_DIVISOR = 100_000
NON_EQUILIBRATION_TOLERANCE = Fraction(0)


@dataclass(frozen=True)
class ShellCheckpointResult:
    """One declared shell-membership check."""

    label: str
    passed: bool
    notes: str


@dataclass(frozen=True)
class ShellMembershipResult:
    """GB6 shell-membership result with an explicit exit counter."""

    checkpoints: tuple[ShellCheckpointResult, ...]
    exit_count: int

    @property
    def in_shell(self) -> bool:
        """Return whether every declared checkpoint passed."""

        return self.exit_count == 0


@dataclass(frozen=True)
class ShellWitness:
    """Frozen shell witness declaration."""

    label: str
    config_path: Path
    N: int
    membership: ShellMembershipResult
    exit_count: int


def n8_shell_witness_config() -> dict[str, Any]:
    """Return the frozen East N=8 shell witness config found by the declared grid search."""

    epsilon_grid = [rational_to_str(epsilon) for epsilon in DEFAULT_EPSILON_GRID]
    return {
        "config_version": 1,
        "run_label": "gt6_shell_witness_n8",
        "model": {"family": "east", "N": 8, "boundary": "wall_up"},
        "epsilon_grid": epsilon_grid,
        "lens": {"id": "L_energy"},
        "protocol": {
            "id": "P_kovacs(epsilon_hi=7/10,epsilon_lo=1/10,epsilon_mid=2/5,t_w=20,tau_probe=30)",
            "word": [
                {"epsilon": "7/10", "steps": 0},
                {"epsilon": "1/10", "steps": 20},
                {"epsilon": "2/5", "steps": 30},
            ],
        },
        "arithmetic": {"mode": "exact_rational", "max_denominator_bits": 4096},
    }


def write_n8_shell_witness_config(path: Path = KOVACS_N8_CONFIG_PATH) -> None:
    """Freeze the N=8 witness config if the caller wants the file materialized."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(n8_shell_witness_config(), indent=2, sort_keys=True), encoding="utf-8"
    )


def check_config_shell_membership(
    config: dict[str, Any],
    *,
    spectral_gaps_path: Path = SPECTRAL_GAPS_PATH,
    lower_divisor: int = TAU_ALPHA_LOWER_DIVISOR,
    non_equilibration_tolerance: Fraction = NON_EQUILIBRATION_TOLERANCE,
) -> ShellMembershipResult:
    """Check the frozen GB6 shell predicate for one Kovacs config."""

    spectral_gaps = load_spectral_gap_table(spectral_gaps_path)
    checkpoints: list[ShellCheckpointResult] = []
    N = int(config["model"]["N"])
    word = config["protocol"]["word"]
    declared_grid = {str_to_rational(value) for value in config["epsilon_grid"]}
    default_grid = set(DEFAULT_EPSILON_GRID)

    schedule_epsilons = [str_to_rational(leg["epsilon"]) for leg in word]
    in_default_grid = all(epsilon in default_grid for epsilon in schedule_epsilons)
    in_config_grid = all(epsilon in declared_grid for epsilon in schedule_epsilons)
    checkpoints.append(
        ShellCheckpointResult(
            label="epsilon_grid",
            passed=in_default_grid and in_config_grid,
            notes="every schedule epsilon lies in DEFAULT_EPSILON_GRID and the config grid",
        )
    )

    for index, leg in enumerate(word):
        epsilon = str_to_rational(leg["epsilon"])
        steps = int(leg["steps"])
        if steps == 0:
            checkpoints.append(
                ShellCheckpointResult(
                    label=f"tau_window_leg_{index}",
                    passed=True,
                    notes="zero-step preparation leg is exempt from hold-window checks",
                )
            )
            continue
        tau_alpha = spectral_gaps[(N, epsilon)]
        lower = Fraction(tau_alpha, lower_divisor)
        passed = lower < steps < tau_alpha
        checkpoints.append(
            ShellCheckpointResult(
                label=f"tau_window_leg_{index}",
                passed=passed,
                notes=(
                    f"steps={steps}, lower=tau_alpha/{lower_divisor}={rational_to_str(lower)}, "
                    f"tau_alpha={tau_alpha}"
                ),
            )
        )

    epsilon_hi = schedule_epsilons[0]
    epsilon_lo = schedule_epsilons[1]
    epsilon_mid = schedule_epsilons[2]
    t_w = int(word[1]["steps"])
    tau_probe = int(word[2]["steps"])
    result = detect_kovacs_hump(N, epsilon_hi, epsilon_lo, epsilon_mid, t_w, tau_probe)
    gap = abs(result.trace[0] - result.e_eq) if result.trace else Fraction(0)
    checkpoints.append(
        ShellCheckpointResult(
            label="non_equilibration_at_measurement",
            passed=bool(result.trace) and gap > non_equilibration_tolerance,
            notes=(
                f"|E_start_probe - E_eq|={rational_to_str(gap)}, "
                f"tolerance={rational_to_str(non_equilibration_tolerance)}"
            ),
        )
    )
    checkpoints.append(
        ShellCheckpointResult(
            label="kovacs_hump_witness",
            passed=result.found,
            notes=(
                f"found={result.found}, t_K={result.t_k}, t_peak={result.t_peak}, "
                f"reason={result.miss_reason or result.abort_reason}"
            ),
        )
    )
    exit_count = sum(1 for checkpoint in checkpoints if not checkpoint.passed)
    return ShellMembershipResult(checkpoints=tuple(checkpoints), exit_count=exit_count)


def build_shell_witnesses(
    *,
    n10_config_path: Path = KOVACS_N10_CONFIG_PATH,
    n8_config_path: Path = KOVACS_N8_CONFIG_PATH,
    materialize_n8: bool = True,
) -> tuple[ShellWitness, ...]:
    """Build/check the two frozen GB6 shell witnesses."""

    if materialize_n8:
        write_n8_shell_witness_config(n8_config_path)
    declarations = (
        ("kovacs_N10", n10_config_path),
        ("kovacs_N8", n8_config_path),
    )
    witnesses: list[ShellWitness] = []
    for label, path in declarations:
        config = load_config(path)
        membership = check_config_shell_membership(config)
        N = int(config["model"]["N"])
        witnesses.append(
            ShellWitness(
                label=label,
                config_path=path,
                N=N,
                membership=membership,
                exit_count=membership.exit_count,
            )
        )
    return tuple(witnesses)


def load_spectral_gap_table(path: Path = SPECTRAL_GAPS_PATH) -> dict[tuple[int, Fraction], int]:
    """Load ``tau_alpha = ceil(mixing_time_bound)`` from the spectral diagnostics table."""

    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("payload", data)["rows"]
    return {
        (int(row["N"]), str_to_rational(row["epsilon"])): math.ceil(float(row["mixing_time_bound"]))
        for row in rows
    }
