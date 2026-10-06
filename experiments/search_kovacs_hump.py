"""Search a declared exact East Kovacs-hump grid."""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.io.config import config_hash  # noqa: E402
from sixbirds_glass.io.rational import rational_to_str  # noqa: E402
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID  # noqa: E402
from sixbirds_glass.pipeline.kovacs_hump import HumpResult, detect_kovacs_hump  # noqa: E402

N_VALUES = (6, 10)
T_W_VALUES = (5, 10, 20, 40)
TAU_PROBE_VALUES = (30, 60, 120)
EPSILON_LO = min(DEFAULT_EPSILON_GRID)
EPSILON_HI = max(DEFAULT_EPSILON_GRID)
EPSILON_MID = DEFAULT_EPSILON_GRID[len(DEFAULT_EPSILON_GRID) // 2]
RESULT_PATH = REPO_ROOT / "artifacts" / "kovacs_hump_check" / "result.json"
CONFIG_PATH = REPO_ROOT / "configs" / "kovacs_hump_default.json"


def run_search(
    *,
    n_values: Sequence[int] = N_VALUES,
    t_w_values: Sequence[int] = T_W_VALUES,
    tau_probe_values: Sequence[int] = TAU_PROBE_VALUES,
) -> tuple[HumpResult | None, list[HumpResult], HumpResult]:
    """Run the declared grid and return ``(first_found, all_results, closest)``."""

    results: list[HumpResult] = []
    preferred_found: HumpResult | None = None
    for N in n_values:
        for t_w in t_w_values:
            for tau_probe in tau_probe_values:
                result = detect_kovacs_hump(N, EPSILON_HI, EPSILON_LO, EPSILON_MID, t_w, tau_probe)
                results.append(result)
                if result.found and (preferred_found is None or result.N > preferred_found.N):
                    preferred_found = result

    return preferred_found, results, closest_result(results)


def closest_result(results: Sequence[HumpResult]) -> HumpResult:
    """Pick a deterministic closest miss for reporting/reproducibility."""

    if not results:
        raise ValueError("results must not be empty")
    crossed = [result for result in results if result.t_k is not None]
    candidates = crossed or list(results)
    return max(candidates, key=_result_score)


def main() -> None:
    found, results, closest = run_search()
    frozen = found if found is not None else closest
    _write_result(frozen, results, found is not None)
    if found is not None:
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_PATH.write_text(
            json.dumps(config_for_result(found), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        print(
            "FOUND "
            f"N={found.N} t_w={found.t_w} tau_probe={found.tau_probe} "
            f"t_K={found.t_k} t_peak={found.t_peak} "
            f"hump_height={rational_to_str(found.hump_height or Fraction(0))}"
        )
        print(f"wrote config to {CONFIG_PATH}")
    else:
        print("NO HUMP FOUND in declared grid")
        print(
            "closest "
            f"N={closest.N} t_w={closest.t_w} tau_probe={closest.tau_probe} "
            f"reason={closest.abort_reason or closest.miss_reason}"
        )
    print(f"wrote result to {RESULT_PATH}")
    print(_summary_table(results))


def config_for_result(result: HumpResult) -> dict[str, object]:
    """Return a model_config-shaped dict for a Kovacs result."""

    epsilon_grid = [rational_to_str(epsilon) for epsilon in DEFAULT_EPSILON_GRID]
    return {
        "config_version": 1,
        "run_label": "kovacs_hump_default",
        "model": {"family": "east", "N": result.N, "boundary": "wall_up"},
        "epsilon_grid": epsilon_grid,
        "lens": {"id": "L_energy"},
        "protocol": {
            "id": (
                "P_kovacs("
                f"epsilon_hi={rational_to_str(result.epsilon_hi)},"
                f"epsilon_lo={rational_to_str(result.epsilon_lo)},"
                f"epsilon_mid={rational_to_str(result.epsilon_mid)},"
                f"t_w={result.t_w},tau_probe={result.tau_probe})"
            ),
            "word": [
                {"epsilon": rational_to_str(result.epsilon_hi), "steps": result.tau_hot},
                {"epsilon": rational_to_str(result.epsilon_lo), "steps": result.t_w},
                {"epsilon": rational_to_str(result.epsilon_mid), "steps": result.tau_probe},
            ],
        },
        "arithmetic": {"mode": "exact_rational", "max_denominator_bits": 4096},
    }


def _write_result(result: HumpResult, all_results: Sequence[HumpResult], found: bool) -> None:
    RESULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "artifact_status": "phase0_exploratory_result",
        "found": found,
        "note": "Pre-certificate Kovacs search output; not an honesty-ledger-graded certificate.",
        "search_grid": {
            "N_values": list(N_VALUES),
            "t_w_values": list(T_W_VALUES),
            "tau_probe_values": list(TAU_PROBE_VALUES),
            "epsilon_hi": rational_to_str(EPSILON_HI),
            "epsilon_lo": rational_to_str(EPSILON_LO),
            "epsilon_mid": rational_to_str(EPSILON_MID),
        },
        "selected_result": result_payload(result),
        "results": [compact_result_payload(item) for item in all_results],
    }
    artifact = {
        "artifact_kind": "window_table",
        "claim_id": "P0.kovacs_hump_search.east",
        "config_hash": config_hash(payload["search_grid"]),
        "config_path": str(CONFIG_PATH.resolve().relative_to(REPO_ROOT)),
        "code_version": _code_version(),
        "claim_grade": "control",
        "evidence_type": "exact_rational",
        "quantifier_domain": {
            "model_families": ["east"],
            "N_values": list(N_VALUES),
            "epsilon_grid": [rational_to_str(epsilon) for epsilon in DEFAULT_EPSILON_GRID],
            "lens_catalog_hash": config_hash({"lens": "L_energy"}),
            "protocol_catalog_hash": config_hash(payload["search_grid"]),
        },
        "nonclaims": [
            (
                "Phase-0 Kovacs search output is a pre-certificate diagnostic, "
                "not a GT witness certificate."
            ),
            (
                "The selected result freezes a later config but does not by itself "
                "prove a theorem-grade claim."
            ),
        ],
        "payload": payload,
    }
    RESULT_PATH.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")


def result_payload(result: HumpResult) -> dict[str, object]:
    payload = compact_result_payload(result)
    payload["trace"] = [rational_to_str(value) for value in result.trace]
    payload["e_eq"] = rational_to_str(result.e_eq)
    return payload


def compact_result_payload(result: HumpResult) -> dict[str, object]:
    data = asdict(result)
    for key in ("epsilon_hi", "epsilon_lo", "epsilon_mid", "hump_height", "e_eq"):
        value = data[key]
        data[key] = None if value is None else rational_to_str(value)
    data.pop("trace")
    return data


def _result_score(result: HumpResult) -> tuple[int, Fraction, int]:
    if result.abort_reason is not None:
        return (0, Fraction(0), -result.tau_probe)
    height = result.hump_height or Fraction(0)
    crossed = 1 if result.t_k is not None else 0
    return (crossed, height, result.tau_probe)


def _summary_table(results: Sequence[HumpResult]) -> str:
    lines = ["N  t_w  tau_probe  status"]
    for result in results:
        status = "FOUND" if result.found else result.abort_reason or result.miss_reason or "miss"
        lines.append(f"{result.N:>1} {result.t_w:>4} {result.tau_probe:>10}  {status}")
    return "\n".join(lines)


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
