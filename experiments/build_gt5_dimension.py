"""Build GT5 MaxFiber and buyback-curve artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.io.config import config_hash, load_config_with_hash  # noqa: E402
from sixbirds_glass.io.rational import rational_to_str, str_to_rational  # noqa: E402
from sixbirds_glass.pipeline.diagnostics import summarize  # noqa: E402
from sixbirds_glass.pipeline.dimension import (  # noqa: E402
    BuybackCurveResult,
    buyback_curve,
    declared_scalar_pool,
    fiber_histogram,
    max_fiber_size,
)
from sixbirds_glass.pipeline.kovacs_witness import (  # noqa: E402
    KovacsMomentWitness,
    build_kovacs_moment_witness_from_config,
)

CONFIG_PATH = REPO_ROOT / "configs" / "kovacs_hump_default.json"
OUTPUT_DIR = REPO_ROOT / "artifacts" / "gt5_dimension"
GB5_NONCLAIM = (
    "buyback saturation or nonsaturation is not a GB5 repair-impossibility certificate; "
    "GB5 requires a separate exhaustive repair-class sweep"
)
SINGLE_SCALAR_NONCLAIM = (
    "the shipped Kovacs buyback curve is a minimal two-history witness with saturation_budget=1; "
    "it demonstrates buyback mechanics, not general single-scalar or TNM insufficiency"
)


def main(output_dir: Path = OUTPUT_DIR, *, config_path: Path = CONFIG_PATH) -> None:
    """Build, validate, and write both GT5 dimension artifacts."""

    max_fiber_artifact, buyback_artifact = build_artifacts(config_path=config_path)
    _validate_artifact(max_fiber_artifact)
    _validate_artifact(buyback_artifact)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "max_fiber.json").write_text(
        json.dumps(max_fiber_artifact, indent=2, sort_keys=True), encoding="utf-8"
    )
    (output_dir / "buyback_curve.json").write_text(
        json.dumps(buyback_artifact, indent=2, sort_keys=True), encoding="utf-8"
    )
    payload = buyback_artifact["payload"]
    print(
        "gt5_dimension "
        f"max_fiber={max_fiber_artifact['payload']['max_fiber_size']} "
        f"envelope={payload['envelope']} "
        f"saturation_budget={payload['saturation_budget']} "
        f"wrote={output_dir}"
    )


def build_artifacts(*, config_path: Path = CONFIG_PATH) -> tuple[dict[str, Any], dict[str, Any]]:
    config, cfg_hash = load_config_with_hash(config_path)
    witness = build_kovacs_moment_witness_from_config(config)
    epsilon_grid = tuple(str_to_rational(value) for value in config["epsilon_grid"])
    pool = declared_scalar_pool(witness.N, epsilon_grid)
    curve = buyback_curve(
        witness.mu_k,
        witness.pi_eq,
        witness.N,
        witness.future_value_mu_k,
        witness.future_value_pi_eq,
        pool,
        max_budget=2,
    )
    common = _common_envelope_fields(config, cfg_hash, witness)
    max_fiber_artifact = {
        **common,
        "artifact_kind": "max_fiber",
        "claim_id": "GT5.max_fiber.kovacs_moment.east_N10",
        "payload": _max_fiber_payload(witness),
    }
    buyback_artifact = {
        **common,
        "artifact_kind": "buyback_curve",
        "claim_id": "GT5.buyback_curve.kovacs_moment.east_N10",
        "nonclaims": [GB5_NONCLAIM, SINGLE_SCALAR_NONCLAIM],
        "payload": _buyback_payload(curve),
    }
    return (max_fiber_artifact, buyback_artifact)


def _common_envelope_fields(
    config: dict[str, Any], cfg_hash: str, witness: KovacsMomentWitness
) -> dict[str, Any]:
    return {
        "config_hash": cfg_hash,
        "config_path": str(CONFIG_PATH.resolve().relative_to(REPO_ROOT)),
        "code_version": _code_version(),
        "claim_grade": "theorem_audited_class",
        "evidence_type": "exact_rational",
        "quantifier_domain": {
            "model_families": ["east"],
            "N_values": [witness.N],
            "epsilon_grid": config["epsilon_grid"],
            "lens_catalog_hash": config_hash({"lens": "L_energy", "scalars": ["T_f", "D", "n_1"]}),
            "protocol_catalog_hash": config_hash(config["protocol"]),
        },
        "nonclaims": [GB5_NONCLAIM],
    }


def _max_fiber_payload(witness: KovacsMomentWitness) -> dict[str, Any]:
    histogram = fiber_histogram(witness.package, "mid")
    summary = summarize(witness.package, "mid")
    return {
        "package_ref": "generated:kovacs_moment:east_N10:L_energy",
        "interface": "mid",
        "history_count": summary.history_count,
        "current_quotient_size": summary.current_quotient_size,
        "predictive_quotient_size": summary.predictive_quotient_size,
        "max_fiber_size": summary.max_fiber_size,
        "fiber_histogram": {
            _signature_key(signature): count for signature, count in histogram.items()
        },
        "nontriviality_threshold_met": max_fiber_size(witness.package, "mid") >= 2,
    }


def _buyback_payload(curve: BuybackCurveResult) -> dict[str, Any]:
    return {
        "raw_by_budget": {
            str(budget): [
                {
                    "coordinates": list(row["coordinates"]),
                    "loss": rational_to_str(row["loss"]),
                    "resolved": row["resolved"],
                }
                for row in rows
            ]
            for budget, rows in curve.raw_by_budget.items()
        },
        "envelope": {str(budget): rational_to_str(loss) for budget, loss in curve.envelope.items()},
        "saturation_budget": curve.saturation_budget,
        "resolved_coordinates": _resolved_coordinates(curve),
    }


def _resolved_coordinates(curve: BuybackCurveResult) -> list[list[str]]:
    if curve.saturation_budget is None:
        return []
    return [
        list(row["coordinates"])
        for row in curve.raw_by_budget[curve.saturation_budget]
        if row["loss"] == 0
    ]


def _signature_key(signature: tuple[Fraction, ...]) -> str:
    return "|".join(rational_to_str(value) for value in signature)


def _validate_artifact(artifact: dict[str, Any]) -> None:
    Draft202012Validator(_schema("artifact_envelope.schema.json")).validate(artifact)


def _schema(filename: str) -> dict[str, Any]:
    schema_path = REPO_ROOT / "design" / "schemas" / filename
    with schema_path.open(encoding="utf-8") as schema_file:
        data = json.load(schema_file)
    if not isinstance(data, dict):
        raise TypeError(f"{schema_path} did not contain a JSON object")
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
