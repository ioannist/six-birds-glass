"""Build GT6 strict-extension hypothesis input artifact."""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.extension.strict import (  # noqa: E402
    build_h5_citation,
    build_nonfactorization_citations,
    nonfactorization_rate,
    run_forcing_comparison,
    run_saturation,
)
from sixbirds_glass.io.config import config_hash, load_config  # noqa: E402
from sixbirds_glass.io.rational import rational_to_str, str_to_rational  # noqa: E402
from sixbirds_glass.lenses.catalog import l_energy  # noqa: E402
from sixbirds_glass.models.east import build_east_kernel  # noqa: E402
from sixbirds_glass.pipeline.packaging import gibbs_prototype_rule  # noqa: E402

CONFIG_PATH = REPO_ROOT / "configs" / "gt6_shell_witness_n8.json"
OUTPUT_PATH = REPO_ROOT / "artifacts" / "gt6_bridge" / "strict_extension.json"
H5_ARTIFACT = REPO_ROOT / "artifacts" / "gt1_cd_tables" / "east_n8_l_energy.json"
GT2_ARTIFACT = REPO_ROOT / "artifacts" / "gt2_witnesses" / "kovacs_moment.json"
GT3_ARTIFACT = REPO_ROOT / "artifacts" / "gt3_foreclosure" / "lens_class_sweep.json"


def main(output_path: Path = OUTPUT_PATH) -> None:
    """Write the strict-extension hypotheses artifact."""

    artifact = build_artifact()
    Draft202012Validator(_schema("artifact_envelope.schema.json")).validate(artifact)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    payload = artifact["payload"]
    print(
        "gt6_strict_hypotheses "
        f"saturated={payload['H3_saturation']['saturated']} "
        f"strata={payload['H3_saturation']['strata_count']} "
        f"forcing={payload['H4_forcing']['material_forcing_count']} "
        f"wrote={output_path}"
    )


def build_artifact() -> dict[str, Any]:
    """Assemble H2-H5 and non-factorization citations."""

    config = load_config(CONFIG_PATH)
    N = int(config["model"]["N"])
    word = config["protocol"]["word"]
    epsilon_lo = str_to_rational(word[1]["epsilon"])
    epsilon_mid = str_to_rational(word[2]["epsilon"])
    epsilon_hi = str_to_rational(word[0]["epsilon"])
    kernel = build_east_kernel(N, epsilon_mid)
    prototype_rule = gibbs_prototype_rule(N, epsilon_mid)
    saturation = run_saturation(N, kernel, 1, l_energy, prototype_rule)
    forcing = run_forcing_comparison(
        N, epsilon_lo, epsilon_hi, epsilon_mid, 1, l_energy, prototype_rule
    )
    h5 = build_h5_citation(H5_ARTIFACT)
    nonfactorization = build_nonfactorization_citations(GT2_ARTIFACT, GT3_ARTIFACT)
    rate = nonfactorization_rate(nonfactorization)
    split_descriptor_count = sum(1 for citation in nonfactorization if citation.has_split_pair)

    return {
        "artifact_kind": "strict_extension_hypotheses",
        "claim_id": "GT6.strict_extension_inputs.east_shell_N8",
        "config_hash": config_hash(config),
        "config_path": str(CONFIG_PATH.resolve().relative_to(REPO_ROOT)),
        "code_version": _code_version(),
        "claim_grade": "certificate_shell_local",
        "evidence_type": "exact_rational",
        "quantifier_domain": {
            "model_families": ["east"],
            "N_values": [N],
            "epsilon_grid": config["epsilon_grid"],
            "lens_catalog_hash": config_hash({"lens": "L_energy"}),
            "protocol_catalog_hash": config_hash(config["protocol"]),
        },
        "nonclaims": [
            (
                "strict-extension inputs are shell-local and do not claim continuum or "
                "all-protocol closure"
            ),
            "H5 and non-factorization are cited from prior artifacts, not recomputed here",
        ],
        "payload": {
            "H2_endomap": {
                "well_defined": True,
                "tau": 1,
                "prototype_rule": "gibbs_within_L_energy_fibers",
                "seed_count": saturation.seed_count,
            },
            "H3_saturation": _saturation_payload(saturation),
            "H4_forcing": _forcing_payload(forcing),
            "H5_macro_admissibility_obstruction": _citation_payload(h5),
            "nonfactorization": {
                "citations": [_citation_payload(citation) for citation in nonfactorization],
                "rate": rational_to_str(rate),
                "split_descriptor_count": split_descriptor_count,
                "descriptor_count": len(nonfactorization),
            },
        },
    }


def _saturation_payload(result: Any) -> dict[str, Any]:
    return {
        "seed_count": result.seed_count,
        "iterations_to_saturation": result.iterations_to_saturation,
        "final_strata": sorted(str(label) for label in result.final_strata),
        "strata_count": result.strata_count,
        "saturated": result.saturated,
    }


def _forcing_payload(result: Any) -> dict[str, Any]:
    return {
        "with_conditioning": _saturation_payload(result.with_conditioning),
        "without_conditioning": _saturation_payload(result.without_conditioning),
        "material_forcing_strata": sorted(str(label) for label in result.material_forcing_strata),
        "material_forcing_count": result.material_forcing_count,
    }


def _citation_payload(citation: Any) -> dict[str, Any]:
    data = asdict(citation)
    data["artifact_path"] = str(data["artifact_path"].resolve().relative_to(REPO_ROOT))
    return data


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
