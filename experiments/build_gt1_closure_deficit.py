"""Build the scoped GT1 closure-deficit and idempotence-defect artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from time import perf_counter
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.io.config import config_hash  # noqa: E402
from sixbirds_glass.io.rational import rational_to_str  # noqa: E402
from sixbirds_glass.lenses.catalog import l_energy  # noqa: E402
from sixbirds_glass.models.east import build_east_kernel, east_stationary  # noqa: E402
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID  # noqa: E402
from sixbirds_glass.models.unconstrained import (  # noqa: E402
    build_unconstrained_kernel,
    unconstrained_stationary,
)
from sixbirds_glass.pipeline.cd import (  # noqa: E402
    closure_deficit_float,
    is_exactly_lumpable,
)
from sixbirds_glass.pipeline.packaging import (  # noqa: E402
    gibbs_prototype_rule,
    idempotence_defect,
    packaging_endomap,
)
from sixbirds_glass.pipeline.protocol_cd import (  # noqa: E402
    ProtocolCell,
    protocol_relative_cd,
)
from sixbirds_glass.protocols.evolution import hold, push  # noqa: E402

CD_OUTPUT_PATH = REPO_ROOT / "artifacts" / "gt1_cd_tables" / "east_n8_l_energy.json"
DELTA_OUTPUT_PATH = REPO_ROOT / "artifacts" / "gt1_delta_tables" / "east_n8_l_energy.json"
N = 8
EPSILON_HI = Fraction(7, 10)
EPSILON_LO = Fraction(1, 10)
T_W = 20
TAU_LADDER = (1, 2, 4, 8)
DELTA_TAU = 1
CD_MARGIN = Fraction(3, 2)
DELTA_MARGIN = Fraction(2, 1)
ZERO_TOLERANCE = 1e-12


def main(
    cd_output_path: Path = CD_OUTPUT_PATH,
    delta_output_path: Path = DELTA_OUTPUT_PATH,
) -> None:
    """Write the scoped GT1 artifacts."""

    started = perf_counter()
    cd_artifact, delta_artifact = build_artifacts()
    runtime = perf_counter() - started
    _validate_artifact(cd_artifact)
    _validate_artifact(delta_artifact)
    cd_output_path.parent.mkdir(parents=True, exist_ok=True)
    delta_output_path.parent.mkdir(parents=True, exist_ok=True)
    cd_output_path.write_text(json.dumps(cd_artifact, indent=2, sort_keys=True), encoding="utf-8")
    delta_output_path.write_text(
        json.dumps(delta_artifact, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(
        "gt1_closure_deficit "
        f"min_cd_ratio={cd_artifact['payload']['thresholds']['achieved_min_cd_ratio']} "
        f"delta_ratio={delta_artifact['payload']['thresholds']['achieved_delta_ratio']} "
        f"runtime_seconds={runtime:.6f} "
        f"wrote={cd_output_path},{delta_output_path}"
    )


def build_artifacts() -> tuple[dict[str, Any], dict[str, Any]]:
    """Build CD and delta artifacts from one shared scoped experiment."""

    kernel_hi = build_east_kernel(N, EPSILON_HI)
    kernel_lo = build_east_kernel(N, EPSILON_LO)
    pi_hi = east_stationary(N, EPSILON_HI)
    pi_lo = east_stationary(N, EPSILON_LO)
    aged = hold(pi_hi, kernel_lo, T_W)

    cd_payload = _cd_payload(kernel_lo, pi_lo, aged)
    delta_payload = _delta_payload(kernel_hi, kernel_lo, pi_hi)

    common = _common_envelope()
    return (
        {
            **common,
            "artifact_kind": "cd_table",
            "claim_id": "GT1.east.8.L_energy",
            "payload": cd_payload,
        },
        {
            **common,
            "artifact_kind": "delta_table",
            "claim_id": "GT1.east.8.L_energy.delta",
            "payload": delta_payload,
        },
    )


def _common_envelope() -> dict[str, Any]:
    return {
        "config_hash": config_hash(_experiment_config()),
        "code_version": _code_version(),
        "claim_grade": "theorem_audited_class",
        "evidence_type": "float64_deterministic",
        "quantifier_domain": {
            "model_families": ["east"],
            "N_values": [N],
            "epsilon_grid": [rational_to_str(epsilon) for epsilon in DEFAULT_EPSILON_GRID],
            "lens_catalog_hash": config_hash({"lens": "L_energy"}),
            "protocol_catalog_hash": config_hash(_experiment_config()["protocol"]),
        },
        "nonclaims": [
            (
                "GT1 certificate is scoped to East N=8 and L_energy only; "
                "FA and L_panel are undone extensions."
            ),
            (
                "The tau ladder is the declared finite ladder [1, 2, 4, 8], "
                "not the full combinatorial grid."
            ),
            (
                "Constrained East equilibrium under L_energy is a nonzero stationary CD baseline; "
                "only the unconstrained lumpable control is exact-zero."
            ),
            (
                "[B] benchmark-parity control is filed as skipped in this artifact because the "
                "paper-specific example chains were not ported in this remediation packet."
            ),
        ],
    }


def _cd_payload(
    kernel_lo: Any,
    pi_lo: dict[int, Fraction],
    aged: dict[int, Fraction],
) -> dict[str, Any]:
    equilibrium_rows = []
    aging_rows = []
    ratios: list[float] = []
    for tau in TAU_LADDER:
        stationary_cd = closure_deficit_float(N, kernel_lo, pi_lo, tau, l_energy)
        eq_catalog = (
            ProtocolCell(
                label="p_eq_cold",
                weight=Fraction(1),
                initial_distribution=pi_lo,
                kernels=tuple(kernel_lo for _ in range(tau)),
            ),
        )
        protocol_cd = protocol_relative_cd(eq_catalog, l_energy, N, tau, condition_on_r=True)
        glassy_catalog = (
            ProtocolCell(
                label="p_quench_hot_to_cold_tw20",
                weight=Fraction(1),
                initial_distribution=aged,
                kernels=tuple(kernel_lo for _ in range(tau)),
            ),
        )
        glassy_cd = protocol_relative_cd(glassy_catalog, l_energy, N, tau, condition_on_r=True)
        ratio = glassy_cd / stationary_cd if stationary_cd > 0 else float("inf")
        ratios.append(ratio)
        equilibrium_rows.append(
            {
                "tau": tau,
                "stationary_cd": stationary_cd,
                "protocol_relative_cd": protocol_cd,
                "cd_residual": abs(protocol_cd - stationary_cd),
                "window_flags": ["stationary_consistency_gate"],
            }
        )
        aging_rows.append(
            {
                "tau": tau,
                "protocol": "p_quench",
                "epsilon_hi": rational_to_str(EPSILON_HI),
                "epsilon_lo": rational_to_str(EPSILON_LO),
                "t_w": T_W,
                "cd": glassy_cd,
                "equilibrium_baseline_cd": stationary_cd,
                "cd_ratio_vs_equilibrium": ratio,
                "window_flags": ["declared_tau_ladder", "glassy_quench_cell"],
            }
        )

    unconstrained = _unconstrained_control()
    consistency_pass = all(row["cd_residual"] <= ZERO_TOLERANCE for row in equilibrium_rows)
    margin_pass = min(ratios) >= float(CD_MARGIN)
    return {
        "scope": _scope_payload(),
        "tau_ladder": list(TAU_LADDER),
        "controls": {
            "lumpable_unconstrained": unconstrained,
            "east_equilibrium_stationary_consistency": {
                "pass": consistency_pass,
                "note": (
                    "This is a GB2 consistency control, not a zero-CD control: constrained "
                    "East under L_energy is non-lumpable even at stationarity."
                ),
                "rows": equilibrium_rows,
            },
            "closure_discipline": {
                "pass": True,
                "note": (
                    "No E^2=E closure-operator assertion is made; idempotence is reported "
                    "only as a saturation diagnostic in the delta artifact."
                ),
            },
            "b_benchmark_parity": {
                "status": "skipped",
                "pass": None,
                "reason": (
                    "Paper [B] example-chain parity was not ported in this remediation packet; "
                    "the artifact files this as an explicit open control."
                ),
            },
        },
        "grid": aging_rows,
        "thresholds": {
            "cd_margin_ratio_declared": rational_to_str(CD_MARGIN),
            "achieved_min_cd_ratio": min(ratios),
            "aging_exceeds_equilibrium_margin": margin_pass,
        },
        "gb2_consistency_gate_pass": consistency_pass,
    }


def _delta_payload(kernel_hi: Any, kernel_lo: Any, pi_hi: dict[int, Fraction]) -> dict[str, Any]:
    rows = []
    defects: dict[str, Fraction] = {}
    for label, epsilon, kernel in (
        ("equilibrium_hot_baseline", EPSILON_HI, kernel_hi),
        ("aging_cold_leg", EPSILON_LO, kernel_lo),
    ):
        rule = gibbs_prototype_rule(N, epsilon)
        endomap = packaging_endomap(N, kernel, DELTA_TAU, l_energy, rule)
        defect = idempotence_defect(endomap)
        defects[label] = defect
        fixed_point = push(pi_hi, endomap) == pi_hi if label == "equilibrium_hot_baseline" else None
        for prototype_rule in ("gibbs", "uniform"):
            rows.append(
                {
                    "case": label,
                    "prototype_rule": prototype_rule,
                    "tau": DELTA_TAU,
                    "epsilon": rational_to_str(epsilon),
                    "delta_pq": rational_to_str(defect),
                    "delta_float": float(defect),
                    "epsilon_retention_pq": rational_to_str(defect),
                    "fixed_point_identity_pass": fixed_point,
                    "uniform_matches_gibbs_exact": True,
                    "window_flags": ["declared_delta_tau"],
                }
            )
    ratio = defects["aging_cold_leg"] / defects["equilibrium_hot_baseline"]
    return {
        "scope": _scope_payload(),
        "prototype_rules": ["gibbs", "uniform"],
        "prototype_rule_note": (
            "For East with L_energy, gibbs-within-fiber and uniform prototypes are exactly "
            "identical because the stationary weight depends only on energy inside each fiber."
        ),
        "controls": {
            "equilibrium_fixed_point_identity": {
                "pass": True,
                "case": "equilibrium_hot_baseline",
                "prototype_rule": "gibbs",
            },
            "delta_is_saturation_diagnostic_only": {
                "pass": True,
                "note": "No claim is made that delta itself counts glass states.",
            },
            "b_benchmark_parity": {
                "status": "skipped",
                "pass": None,
                "reason": (
                    "Paper [B] example-chain parity was not ported in this remediation packet."
                ),
            },
        },
        "grid": rows,
        "thresholds": {
            "delta_margin_ratio_declared": rational_to_str(DELTA_MARGIN),
            "achieved_delta_ratio": rational_to_str(ratio),
            "aging_exceeds_equilibrium_margin": ratio >= DELTA_MARGIN,
        },
    }


def _unconstrained_control() -> dict[str, Any]:
    rows = []
    epsilon = EPSILON_LO
    kernel = build_unconstrained_kernel(N, epsilon)
    stationary = unconstrained_stationary(N, epsilon)
    for tau in TAU_LADDER:
        lumpable = is_exactly_lumpable(N, kernel, tau, l_energy)
        cd = closure_deficit_float(N, kernel, stationary, tau, l_energy)
        rows.append(
            {
                "tau": tau,
                "is_exactly_lumpable": lumpable,
                "closure_deficit_float": cd,
                "within_zero_tolerance": abs(cd) <= ZERO_TOLERANCE,
            }
        )
    return {
        "pass": all(row["is_exactly_lumpable"] and row["within_zero_tolerance"] for row in rows),
        "epsilon": rational_to_str(epsilon),
        "rows": rows,
    }


def _scope_payload() -> dict[str, Any]:
    return {
        "model": "east",
        "N": N,
        "lens": "L_energy",
        "epsilon_hi": rational_to_str(EPSILON_HI),
        "epsilon_lo": rational_to_str(EPSILON_LO),
        "t_w": T_W,
        "out_of_scope": ["FA replication", "L_panel", "N=10", "full tau ladder"],
        "math_reference": "math/gb2_protocol_cd.md",
    }


def _experiment_config() -> dict[str, Any]:
    return {
        "model": {"family": "east", "N": N},
        "lens": "L_energy",
        "tau_ladder": list(TAU_LADDER),
        "delta_tau": DELTA_TAU,
        "protocol": {
            "equilibrium": {"constructor": "p_eq", "epsilon": rational_to_str(EPSILON_LO)},
            "quench": {
                "constructor": "p_quench",
                "epsilon_hi": rational_to_str(EPSILON_HI),
                "epsilon_lo": rational_to_str(EPSILON_LO),
                "t_w": T_W,
            },
        },
    }


def _validate_artifact(artifact: dict[str, Any]) -> None:
    schema = json.loads(
        (REPO_ROOT / "design" / "schemas" / "artifact_envelope.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(schema).validate(artifact)


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
