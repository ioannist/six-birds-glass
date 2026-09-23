"""Build the GT2 Kovacs loop certificate artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.io.config import config_hash, load_config_with_hash  # noqa: E402
from sixbirds_glass.io.rational import rational_to_str  # noqa: E402
from sixbirds_glass.pipeline.diagnostics import summarize  # noqa: E402
from sixbirds_glass.pipeline.kovacs_loop import (  # noqa: E402
    DEFAULT_LOOP_HOLD_STEPS,
    KovacsLoopCertificate,
    build_kovacs_loop_certificate,
    predictive_class_count,
)
from sixbirds_glass.pipeline.kovacs_witness import (  # noqa: E402
    build_kovacs_moment_witness_from_config,
)

CONFIG_PATH = REPO_ROOT / "configs" / "kovacs_hump_default.json"
OUTPUT_PATH = REPO_ROOT / "artifacts" / "gt2_witnesses" / "kovacs_loop.json"
P4_NONCLAIM = "filed as P4 staged dependence, not a directionality or irreversibility claim"


def main(
    output_path: Path = OUTPUT_PATH,
    *,
    config_path: Path = CONFIG_PATH,
    hold_steps: int = DEFAULT_LOOP_HOLD_STEPS,
) -> None:
    """Build, validate, and write the GT2 Kovacs loop artifact."""

    artifact = build_artifact(config_path=config_path, hold_steps=hold_steps)
    _validate_artifact(artifact)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    loop = artifact["payload"]["loop"]
    print(
        "kovacs_loop "
        f"theta_return={loop['schedule_word'][-1]['theta_return']} "
        f"loop_Q={loop['current_action']['score']} "
        f"loop_M={loop['predictive_action']['score']} "
        f"wrote={output_path}"
    )


def build_artifact(
    *, config_path: Path = CONFIG_PATH, hold_steps: int = DEFAULT_LOOP_HOLD_STEPS
) -> dict:
    config, cfg_hash = load_config_with_hash(config_path)
    witness = build_kovacs_moment_witness_from_config(config)
    certificate = build_kovacs_loop_certificate(witness, hold_steps=hold_steps)
    lens_catalog_hash = config_hash({"lens_id": "L_energy", "event_id": "w_E"})
    protocol_catalog_hash = config_hash(config["protocol"])
    return {
        "artifact_kind": "loop_certificate",
        "claim_id": "GT2.kovacs_loop.east_N10",
        "config_hash": cfg_hash,
        "config_path": str(config_path.resolve().relative_to(REPO_ROOT)),
        "code_version": _code_version(),
        "claim_grade": "theorem_audited_class",
        "evidence_type": "exact_rational",
        "quantifier_domain": {
            "model_families": ["east"],
            "N_values": [witness.N],
            "epsilon_grid": config["epsilon_grid"],
            "lens_catalog_hash": lens_catalog_hash,
            "protocol_catalog_hash": protocol_catalog_hash,
        },
        "nonclaims": [P4_NONCLAIM],
        "payload": _payload(certificate),
    }


def _payload(certificate: KovacsLoopCertificate) -> dict[str, Any]:
    if certificate.loop_score_current is None or certificate.loop_score_predictive is None:
        raise RuntimeError(
            "real Kovacs loop did not satisfy finite loop-action closure: "
            f"{certificate.loop_score_error}"
        )
    package = certificate.package
    diagnostics = summarize(package, "mid")
    predictive_total = predictive_class_count(package)
    predictive_moved = int(certificate.loop_score_predictive * predictive_total)
    return {
        "package_ref": "generated:kovacs_loop:east_N10:L_energy",
        "interface": "mid",
        "lens_id": "L_energy",
        "continuation_catalog_hash": config_hash(
            {"future_catalog": {"mid": [["probe_hold", "w_E"]], "probe": []}}
        ),
        "diagnostics": {
            "history_count": diagnostics.history_count,
            "current_quotient_size": diagnostics.current_quotient_size,
            "predictive_quotient_size": diagnostics.predictive_quotient_size,
            "max_fiber_size": diagnostics.max_fiber_size,
            "witness_count": diagnostics.witness_count,
            "exact_max_abs_future_gap_value": rational_to_str(diagnostics.exact_max_abs_future_gap),
            "loop_action_score_current_quotient": rational_to_str(certificate.loop_score_current),
            "loop_action_score_predictive_quotient": rational_to_str(
                certificate.loop_score_predictive
            ),
        },
        "loop": {
            "loop_id": "loop_kovacs",
            "schedule_word": [
                {"leg": "mid_hold", "steps": certificate.hold_steps},
                {
                    "leg": "sparse_panel_return",
                    "theta_return": rational_to_str(certificate.theta_return),
                    "return_steps": certificate.return_steps,
                },
            ],
            "current_action": {
                "classes_total": diagnostics.current_quotient_size,
                "classes_moved": 0,
                "score": rational_to_str(certificate.loop_score_current),
            },
            "predictive_action": {
                "classes_total": predictive_total,
                "classes_moved": predictive_moved,
                "score": rational_to_str(certificate.loop_score_predictive),
                "moved_classes": [{"class_id": "mu_K"}, {"class_id": "pi_eq"}],
            },
            "intertwining_exhibit": {
                "source_history": "mu_K",
                "image_history": "loop_image_of_mu_K",
                "current_class_fixed": True,
                "predictive_class_moved": True,
            },
        },
    }


def _validate_artifact(artifact: dict[str, Any]) -> None:
    Draft202012Validator(_schema("artifact_envelope.schema.json")).validate(artifact)
    Draft202012Validator(_schema("witness_certificate.schema.json")).validate(artifact["payload"])


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
