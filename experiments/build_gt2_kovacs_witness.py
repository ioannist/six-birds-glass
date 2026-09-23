"""Build the GT2 Kovacs-moment witness certificate artifact."""

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
from sixbirds_glass.pipeline.diagnostics import (  # noqa: E402
    exact_max_abs_future_gap,
    max_fiber_size,
    summarize,
    witness_count,
)
from sixbirds_glass.pipeline.kovacs_witness import (  # noqa: E402
    DEFAULT_PROBE_STEPS,
    KovacsMomentWitness,
    build_kovacs_moment_witness_from_config,
)
from sixbirds_glass.pipeline.signatures import current_signature  # noqa: E402

CONFIG_PATH = REPO_ROOT / "configs" / "kovacs_hump_default.json"
OUTPUT_PATH = REPO_ROOT / "artifacts" / "gt2_witnesses" / "kovacs_moment.json"
P4_NONCLAIM = "filed as P4 staged dependence, not a directionality or irreversibility claim"


def main(
    output_path: Path = OUTPUT_PATH,
    *,
    config_path: Path = CONFIG_PATH,
    probe_steps: int = DEFAULT_PROBE_STEPS,
) -> None:
    """Build, validate, and write the GT2 Kovacs witness artifact."""

    artifact = build_artifact(config_path=config_path, probe_steps=probe_steps)
    _validate_artifact(artifact)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")

    witness = build_kovacs_moment_witness_from_config(
        load_config_with_hash(config_path)[0], probe_steps=probe_steps
    )
    print(
        "kovacs_moment "
        f"theta={rational_to_str(witness.theta)} "
        f"gap={rational_to_str(witness.separating_gap)} "
        f"wrote={output_path}"
    )


def build_artifact(
    *, config_path: Path = CONFIG_PATH, probe_steps: int = DEFAULT_PROBE_STEPS
) -> dict:
    config, cfg_hash = load_config_with_hash(config_path)
    witness = build_kovacs_moment_witness_from_config(config, probe_steps=probe_steps)
    continuation_catalog_hash = _continuation_catalog_hash()
    lens_catalog_hash = config_hash({"lens_id": "L_energy", "event_id": "w_E"})
    protocol_catalog_hash = config_hash(config["protocol"])
    return {
        "artifact_kind": "witness_certificate",
        "claim_id": "GT2.kovacs_moment.east_N10",
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
        "payload": _payload(witness, continuation_catalog_hash),
    }


def _payload(witness: KovacsMomentWitness, continuation_catalog_hash: str) -> dict[str, Any]:
    package = witness.package
    diagnostics = summarize(package, "mid")
    summary = {
        "history_count": diagnostics.history_count,
        "current_quotient_size": diagnostics.current_quotient_size,
        "predictive_quotient_size": diagnostics.predictive_quotient_size,
        "max_fiber_size": max_fiber_size(package, "mid"),
        "witness_count": witness_count(package, "mid"),
        "exact_max_abs_future_gap_value": rational_to_str(exact_max_abs_future_gap(package, "mid")),
    }
    mu_history = package.history_by_label("mid", "mu_K")
    current_value = current_signature(package, mu_history)[0]
    return {
        "package_ref": "generated:kovacs_moment:east_N10:L_energy",
        "interface": "mid",
        "lens_id": "L_energy",
        "continuation_catalog_hash": continuation_catalog_hash,
        "witness_pairs": [
            {
                "h_id": "mu_K",
                "hprime_id": "pi_eq",
                "family": "W_kovacs_moment",
                "s0_equal_entries": [{"event_id": "w_E", "value": rational_to_str(current_value)}],
                "separating_entry": {
                    "continuation_id": "probe_hold",
                    "event_id": "w_E",
                    "value_h": rational_to_str(witness.future_value_mu_k),
                    "value_hprime": rational_to_str(witness.future_value_pi_eq),
                    "abs_gap": rational_to_str(witness.separating_gap),
                },
                "tuning": {"theta_star": rational_to_str(witness.theta)},
            }
        ],
        "diagnostics": summary,
    }


def _continuation_catalog_hash() -> str:
    return config_hash({"future_catalog": {"mid": [["probe_hold", "w_E"]], "probe": []}})


def _validate_artifact(artifact: dict[str, Any]) -> None:
    envelope_schema = _schema("artifact_envelope.schema.json")
    witness_schema = _schema("witness_certificate.schema.json")
    Draft202012Validator(envelope_schema).validate(artifact)
    Draft202012Validator(witness_schema).validate(artifact["payload"])


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
