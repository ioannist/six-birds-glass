"""Build the GT6 glass strict-bridge filing."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.extension.disintegration import (  # noqa: E402
    disintegration_gap,
    stratum_conditioned_pressure,
)
from sixbirds_glass.extension.filing import (  # noqa: E402
    AdmDomainRecord,
    BridgeRecord,
    build_gate_table,
    default_exclusion_checks,
    gate_table_to_payload,
    recompute_verdict,
)
from sixbirds_glass.extension.pressure import pressure_ladder  # noqa: E402
from sixbirds_glass.extension.strict import artifact_sha256  # noqa: E402
from sixbirds_glass.io.config import config_hash, load_config  # noqa: E402
from sixbirds_glass.io.rational import rational_to_str, str_to_rational  # noqa: E402
from sixbirds_glass.lenses.catalog import l_energy  # noqa: E402
from sixbirds_glass.models.east import build_east_kernel, east_stationary  # noqa: E402
from sixbirds_glass.pipeline.packaging import coarse_grain, fiber_partition  # noqa: E402

CONFIG_PATH = REPO_ROOT / "configs" / "gt6_shell_witness_n8.json"
OUTPUT_PATH = REPO_ROOT / "artifacts" / "gt6_bridge" / "audit.json"
DISINTEGRATION_TILT = Fraction(1, 5)
DISINTEGRATION_THRESHOLD = 1e-3
N_VALUES = tuple(range(1, 9))
VERDICT_BASIS = (
    "verdict: strict is established via F-III T19/T20 (non-factorization from "
    "GT2/GT3 witnesses). Paper [C]'s thm:strict-extension (the fuller "
    "completion-dynamics route requiring material P4<-P5 forcing) is NOT "
    "invoked: H4_forcing.material_forcing_count = 0 for this shell, filed as "
    "an honest negative sub-result, not as a satisfied hypothesis."
)

TEN_NONCLAIMS = (
    "GT6 is scoped to the audited glass shell, not to all East or glassy regimes.",
    "No shell-general strict-bridge theorem is claimed.",
    "No broader external-class theorem is claimed beyond the frozen finite class.",
    "Strictness does not imply autonomous macro closure.",
    "Strictness does not imply drive; P6_drive requires the separate GB1 audit discipline.",
    "The pressure gap is not a KL closure deficit unless an explicit bridge is supplied.",
    "The pressure gap is not the strictness witness; GT2/GT3 provide the strictness witnesses.",
    (
        "The gap functional is a conditional disintegration on strata, not stratumwise "
        "root separation."
    ),
    "This is a model realization, not a universal strict-extension theory.",
    (
        "T1 is a packaged completion layer, not repeated application of one fixed "
        "idempotent completion."
    ),
    "Single bridge only; no stacked or glued promotions are claimed.",
)

CITED_ARTIFACTS = (
    "artifacts/gt6_bridge/knockouts.json",
    "artifacts/gt6_bridge/pressure_closure.json",
    "artifacts/gt6_bridge/strict_extension.json",
    "artifacts/gt1_cd_tables/east_n8_l_energy.json",
    "artifacts/gt2_witnesses/kovacs_moment.json",
    "artifacts/gt3_foreclosure/lens_class_sweep.json",
    "artifacts/gt5_dimension/max_fiber.json",
)


def main(output_path: Path = OUTPUT_PATH) -> None:
    """Write the GT6 filing artifact."""

    artifact = build_artifact()
    Draft202012Validator(_schema("artifact_envelope.schema.json")).validate(artifact)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    print(
        "gt6_filing "
        f"verdict={artifact['payload']['verdict']} "
        f"gap={artifact['payload']['disintegration']['gap']} "
        f"wrote={output_path}"
    )


def build_artifact() -> dict[str, Any]:
    """Assemble the GT6 filing."""

    config = load_config(CONFIG_PATH)
    N = int(config["model"]["N"])
    epsilon_mid = str_to_rational(config["protocol"]["word"][2]["epsilon"])
    disintegration = _compute_disintegration(N, epsilon_mid)
    gate_table = build_gate_table()
    verdict = recompute_verdict(gate_table)
    citations = _citation_records()
    adm_domain = _adm_domain_record()
    bridge = BridgeRecord(
        id="B_glass_T0_to_T1",
        T0="T0:L_energy_pressure",
        T1="T1:packaged_predictive_strata",
        carrier_S={
            "shell": "GB6:GlassShell_aud",
            "histories": ["kovacs_N8", "kovacs_N10"],
            "protocol_catalog": "declared Kovacs shell configs",
        },
        O0={"codomain": "current-panel L_energy values"},
        O1={"codomain": "packaged stratum labels / predictive quotient classes"},
        pi0={"map": "finite map from shell histories to L_energy current panel"},
        pi1={"map": "finite map from shell histories to predictive quotient / strata labels"},
        L={"lens": "L_energy", "interface": "mid", "level": "Str"},
        V={"visibility": "artifact hashes, gate table, nonclaims, and shell witnesses"},
        Theta={
            "disintegration_threshold": {"type": "Θ_le_eps", "value": DISINTEGRATION_THRESHOLD},
            "saturation_empty_rounds": {"type": "exact", "value": 2},
            "shell_exit_count": {"type": "exact", "value": 0},
        },
        A={"audit_artifact": "artifacts/gt6_bridge/audit.json", "checker": "check_gt6_filing.py"},
        delta={
            "delta_fact": "GT2/GT3 constructive witnesses cited",
            "delta_nosmuggle": "all six no-smuggling checks filed pass",
            "delta_sat": "empty because P3-04 saturated=True",
            "delta_stab": "empty because P3-04 saturated=True",
            "delta_forcing": "0 material forcing strata in P3-04",
            "delta_1_split_if_claimed": "not_claimed because G_desc=not_required",
            "delta_macro": "GT1 closure-deficit CD>0 citation",
            "delta_press_analogue": str(disintegration["gap"]),
        },
        GateResults=gate_table_to_payload(gate_table),
        N=TEN_NONCLAIMS,
        HostTag="H_prob",
        lambda_prom={"profile": "shell_local_strict_promotion", "single_bridge": True},
    )
    return {
        "artifact_kind": "audit",
        "claim_id": "GT6.strict_bridge.glass_shell",
        "config_hash": config_hash(config),
        "config_path": str(CONFIG_PATH.resolve().relative_to(REPO_ROOT)),
        "code_version": _code_version(),
        "claim_grade": "certificate_shell_local",
        "evidence_type": "float64_deterministic",
        "verdict_basis": VERDICT_BASIS,
        "quantifier_domain": {
            "model_families": ["east"],
            "N_values": [N],
            "epsilon_grid": config["epsilon_grid"],
            "lens_catalog_hash": config_hash({"lens": "L_energy"}),
            "protocol_catalog_hash": config_hash(config["protocol"]),
        },
        "nonclaims": list(TEN_NONCLAIMS),
        "payload": {
            "realization_object": {
                "id": "GlassShell_aud",
                "components": ["S_aud", "T0", "T1", "pi0", "pi1", "F", "Delta", "A", "N"],
            },
            "adm_domain": asdict(adm_domain),
            "bridge_records": [_bridge_payload(bridge)],
            "gate_table": gate_table_to_payload(gate_table),
            "verdict": verdict,
            "disintegration": disintegration,
            "citations": citations,
        },
    }


def _compute_disintegration(N: int, epsilon_mid: Fraction) -> dict[str, Any]:
    kernel = build_east_kernel(N, epsilon_mid)
    stationary = east_stationary(N, epsilon_mid)
    fibers = fiber_partition(N, l_energy)
    weights = coarse_grain(stationary, fibers)
    s = float(DISINTEGRATION_TILT)
    base_ladder = pressure_ladder(kernel, l_energy, N, s, N_VALUES)
    P_T0 = base_ladder[max(base_ladder)]
    stratum_pressures = {
        label: stratum_conditioned_pressure(kernel, l_energy, N, s, frozenset(states), N_VALUES)
        for label, states in fibers.items()
    }
    gap = disintegration_gap(P_T0, stratum_pressures, weights)
    return {
        "tilt": rational_to_str(DISINTEGRATION_TILT),
        "threshold": DISINTEGRATION_THRESHOLD,
        "P_T0": P_T0,
        "stratum_pressures": {str(label): value for label, value in stratum_pressures.items()},
        "stratum_weights": {str(label): rational_to_str(value) for label, value in weights.items()},
        "gap": gap,
        "passes_threshold": gap >= DISINTEGRATION_THRESHOLD,
        "rejected_route_nonclaim": (
            "no per-stratum thermodynamic autonomy claim; strata are fiber averages"
        ),
    }


def _adm_domain_record() -> AdmDomainRecord:
    artifacts = tuple(CITED_ARTIFACTS)
    return AdmDomainRecord(
        primitives=("P1", "P2", "P3", "P4", "P5", "P6"),
        levels=("Beh", "Ver", "Str"),
        host=("H_prob",),
        content=artifacts,
        instrument=("East exact-rational simulation", "pytest suite", "GT6 checker"),
        packages=("RouteTransportPackage", "packaging_endomap", "pressure_ladder"),
        witnesses=("GT2.kovacs_moment", "GT3.reflection_foreclosure"),
        updates=(
            "P1 kernel",
            "P2 constraint",
            "P3 schedule",
            "P4 lens",
            "P5 packaging",
            "P6 audit",
        ),
        defects=("delta_fact", "delta_sat", "delta_forcing", "delta_macro", "delta_press"),
        judgments=("strict_promotion",),
        status=("certificate_shell_local",),
        gates=(
            "G_suff",
            "G_desc",
            "G_stab",
            "G_ctrl",
            "G_nosmuggle",
            "G_vis",
            "G_audit",
            "G_strict",
            "G_locglob",
        ),
        dependencies=artifacts,
        audit=("artifacts/gt6_bridge/audit.json", "experiments/check_gt6_filing.py"),
        source=("design/specs/08_gt6_extension.md", "design/reference/foundations_III.md"),
        visibility=("visible_artifact_hashes", "visible_nonclaims", "visible_gate_table"),
        nonclaims=TEN_NONCLAIMS,
        realization="GlassShell_aud",
        exclusion_checks=default_exclusion_checks(),
        notes=(
            "empty finite families are filed as typed empty records where no glass content exists",
        ),
    )


def _bridge_payload(bridge: BridgeRecord) -> dict[str, Any]:
    return asdict(bridge)


def _citation_records() -> list[dict[str, str]]:
    records = []
    for relative in CITED_ARTIFACTS:
        path = REPO_ROOT / relative
        records.append({"artifact_path": relative, "sha256": artifact_sha256(path)})
    return records


def _schema(filename: str) -> dict[str, Any]:
    path = REPO_ROOT / "design" / "schemas" / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"{path} did not contain a JSON object")
    return data


def _code_version() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip()


if __name__ == "__main__":
    main()
