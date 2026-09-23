"""Build the GB2 protocol-relative closure-deficit demonstration artifact."""

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

from sixbirds_glass.io.config import config_hash  # noqa: E402
from sixbirds_glass.io.rational import rational_to_str  # noqa: E402
from sixbirds_glass.lenses.catalog import l_energy  # noqa: E402
from sixbirds_glass.models.east import build_east_kernel, east_stationary  # noqa: E402
from sixbirds_glass.models.unconstrained import (  # noqa: E402
    build_unconstrained_kernel,
    unconstrained_stationary,
)
from sixbirds_glass.pipeline.cd import closure_deficit_float  # noqa: E402
from sixbirds_glass.pipeline.protocol_cd import (  # noqa: E402
    ProtocolCell,
    protocol_relative_cd,
    protocol_relative_lumpability_check,
)
from sixbirds_glass.protocols.evolution import hold  # noqa: E402

OUTPUT_PATH = REPO_ROOT / "artifacts" / "gb2_demo.json"


def main(output_path: Path = OUTPUT_PATH) -> None:
    """Write the GB2 demo artifact."""

    artifact = build_artifact()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    non_lumpable = artifact["payload"]["non_lumpable_aging_catalog"]
    print(
        "gb2_demo "
        f"windowed_cd={non_lumpable['windowed_cd']:.15g} "
        f"marginalized_cd={non_lumpable['marginalized_cd']:.15g} "
        f"wrote={output_path}"
    )


def build_artifact() -> dict[str, Any]:
    """Return the GB2 demonstration payload."""

    consistency = _stationary_consistency()
    lumpable = _lumpable_catalog()
    non_lumpable = _non_lumpable_catalog()
    payload = {
        "artifact_status": "phase2_math_demo",
        "note": "GB2 protocol-CD demonstration artifact; not a GT-claim certificate.",
        "math_note": "math/gb2_protocol_cd.md",
        "stationary_consistency": consistency,
        "lumpable_multi_cell_catalog": lumpable,
        "non_lumpable_aging_catalog": non_lumpable,
    }
    return {
        "artifact_kind": "math_demo",
        "claim_id": "GB2.protocol_relative_closure_deficit.demo",
        "config_hash": config_hash(
            {
                "stationary_consistency": {
                    "N": consistency["N"],
                    "epsilon": consistency["epsilon"],
                    "tau": consistency["tau"],
                },
                "lumpable": {"N": lumpable["N"], "tau": lumpable["tau"]},
                "non_lumpable": {
                    "N": non_lumpable["N"],
                    "tau": non_lumpable["tau"],
                    "epsilon_hi": non_lumpable["epsilon_hi"],
                    "epsilon_lo": non_lumpable["epsilon_lo"],
                    "epsilon_mid": non_lumpable["epsilon_mid"],
                },
            }
        ),
        "code_version": _code_version(),
        "claim_grade": "recognition",
        "evidence_type": "float64_deterministic",
        "quantifier_domain": {
            "model_families": ["east", "unconstrained"],
            "N_values": [4],
            "epsilon_grid": ["1/10", "1/5", "2/5", "1/2", "7/10"],
            "lens_catalog_hash": config_hash({"lens": "L_energy"}),
            "protocol_catalog_hash": config_hash(
                {"protocols": ["stationary", "unconstrained_multi_cell", "aging_catalog"]}
            ),
        },
        "nonclaims": [
            "GB2 demo records finite protocol-CD computations, not a GT claim certificate.",
            (
                "Windowed and marginalized CD values are float64 diagnostics; "
                "exactness is reserved for the lumpability check."
            ),
        ],
        "payload": payload,
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


def _stationary_consistency() -> dict[str, Any]:
    N = 4
    epsilon = Fraction(1, 2)
    tau = 2
    kernel = build_east_kernel(N, epsilon)
    stationary = east_stationary(N, epsilon)
    catalog = (
        ProtocolCell(
            label="stationary",
            weight=Fraction(1),
            initial_distribution=stationary,
            kernels=(kernel, kernel),
        ),
    )
    protocol_cd = protocol_relative_cd(catalog, l_energy, N, tau, condition_on_r=True)
    stationary_cd = closure_deficit_float(N, kernel, stationary, tau, l_energy)
    return {
        "N": N,
        "epsilon": rational_to_str(epsilon),
        "tau": tau,
        "protocol_relative_cd": protocol_cd,
        "stationary_cd": stationary_cd,
        "absolute_difference": abs(protocol_cd - stationary_cd),
    }


def _lumpable_catalog() -> dict[str, Any]:
    N = 4
    tau = 2
    eps_a = Fraction(1, 5)
    eps_b = Fraction(1, 2)
    kernel_a = build_unconstrained_kernel(N, eps_a)
    kernel_b = build_unconstrained_kernel(N, eps_b)
    catalog = (
        ProtocolCell(
            label="unconstrained_a",
            weight=Fraction(1, 3),
            initial_distribution=unconstrained_stationary(N, eps_a),
            kernels=(kernel_a, kernel_a),
        ),
        ProtocolCell(
            label="unconstrained_b",
            weight=Fraction(2, 3),
            initial_distribution=unconstrained_stationary(N, eps_b),
            kernels=(kernel_b, kernel_a),
        ),
    )
    result = protocol_relative_lumpability_check(catalog, l_energy, N, tau)
    return {
        "N": N,
        "tau": tau,
        "epsilons": [rational_to_str(eps_a), rational_to_str(eps_b)],
        "is_lumpable": result.is_lumpable,
        "violation": None,
    }


def _non_lumpable_catalog() -> dict[str, Any]:
    N = 4
    tau = 2
    eps_hi = Fraction(7, 10)
    eps_lo = Fraction(1, 10)
    eps_mid = Fraction(2, 5)
    kernel_lo = build_east_kernel(N, eps_lo)
    kernel_mid = build_east_kernel(N, eps_mid)
    initial_hot = east_stationary(N, eps_hi)
    catalog = (
        ProtocolCell(
            label="age_1",
            weight=Fraction(1, 2),
            initial_distribution=hold(initial_hot, kernel_lo, 1),
            kernels=(kernel_mid, kernel_mid),
        ),
        ProtocolCell(
            label="age_2",
            weight=Fraction(1, 2),
            initial_distribution=hold(initial_hot, kernel_lo, 2),
            kernels=(kernel_lo, kernel_mid),
        ),
    )
    exact = protocol_relative_lumpability_check(catalog, l_energy, N, tau)
    windowed = protocol_relative_cd(catalog, l_energy, N, tau, condition_on_r=True)
    marginalized = protocol_relative_cd(catalog, l_energy, N, tau, condition_on_r=False)
    violation = exact.violation
    return {
        "N": N,
        "tau": tau,
        "epsilon_hi": rational_to_str(eps_hi),
        "epsilon_lo": rational_to_str(eps_lo),
        "epsilon_mid": rational_to_str(eps_mid),
        "is_lumpable": exact.is_lumpable,
        "violation": None
        if violation is None
        else {
            "source_fiber": violation.source_fiber,
            "target_fiber": violation.target_fiber,
            "left_state": violation.left_state,
            "right_state": violation.right_state,
            "left_probability": rational_to_str(violation.left_probability),
            "right_probability": rational_to_str(violation.right_probability),
        },
        "windowed_cd": windowed,
        "marginalized_cd": marginalized,
        "windowed_minus_marginalized": windowed - marginalized,
    }


if __name__ == "__main__":
    main()
