"""Build the GT3 energy-lens foreclosure sweep artifact."""

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

from sixbirds_glass.io.config import config_hash  # noqa: E402
from sixbirds_glass.io.rational import rational_to_str  # noqa: E402
from sixbirds_glass.models.east import build_east_kernel  # noqa: E402
from sixbirds_glass.models.kernels import Kernel, energy, spin  # noqa: E402
from sixbirds_glass.pipeline.foreclosure import foreclosure_sweep  # noqa: E402
from sixbirds_glass.pipeline.package import (  # noqa: E402
    Continuation,
    Event,
    History,
    RouteTransportPackage,
)
from sixbirds_glass.pipeline.reflection_witness import (  # noqa: E402
    energy_level_distribution,
    reflect_distribution,
    verify_reflection_energy_invariance,
)
from sixbirds_glass.pipeline.signatures import current_signature, future_signature  # noqa: E402
from sixbirds_glass.protocols.evolution import Distribution, dirac, expectation, hold  # noqa: E402

OUTPUT_PATH = REPO_ROOT / "artifacts" / "gt3_foreclosure" / "lens_class_sweep.json"
DEFAULT_N = 8
DEFAULT_EPSILON = Fraction(1, 2)
DEFAULT_PREP_STEPS = 3
T_FOR_02_STATEMENT = (
    "the distinguishing readout (n_1-based) is not in Def(l_energy); constructive witness "
    "exhibited, not generic counting"
)
WITNESS_PROVENANCE = (
    "standalone W_reflection witness constructed for this sweep; not chained to the "
    "GT2.kovacs_moment certificate (a separate witness family per "
    "design/specs/04_gt2_witnesses.md §4)."
)


def main(output_path: Path = OUTPUT_PATH) -> None:
    """Build, validate, and write the GT3 foreclosure sweep artifact."""

    artifact = build_artifact()
    _validate_artifact(artifact)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True), encoding="utf-8")
    payload = artifact["payload"]
    print(
        "gt3_foreclosure "
        f"predicates={payload['agreeing_predicates']}/{payload['total_predicates']} "
        f"gap={payload['separating_entry']['abs_gap']} "
        f"wrote={output_path}"
    )


def build_artifact() -> dict[str, Any]:
    config = {
        "model": {"family": "east", "N": DEFAULT_N},
        "epsilon": rational_to_str(DEFAULT_EPSILON),
        "prep": {"initial": "dirac_0", "steps": DEFAULT_PREP_STEPS},
        "lens": "L_energy",
        "future_event": "n_1",
    }
    mu = build_real_reflection_seed(DEFAULT_N, DEFAULT_EPSILON, DEFAULT_PREP_STEPS)
    h_prime = reflect_distribution(mu, DEFAULT_N)
    package = build_reflection_witness_package(DEFAULT_N, mu, h_prime)
    payload = build_payload(DEFAULT_N, DEFAULT_EPSILON, DEFAULT_PREP_STEPS, mu, h_prime, package)
    return {
        "artifact_kind": "foreclosure_sweep",
        "claim_id": "GT3.energy_lens_sweep.east_N8",
        "config_hash": config_hash(config),
        "code_version": _code_version(),
        "claim_grade": "theorem_audited_class",
        "evidence_type": "exact_rational",
        "quantifier_domain": {
            "model_families": ["east"],
            "N_values": [DEFAULT_N],
            "epsilon_grid": [rational_to_str(DEFAULT_EPSILON)],
            "lens_catalog_hash": config_hash(
                {"lens": "L_energy", "image": list(range(DEFAULT_N + 1))}
            ),
            "protocol_catalog_hash": config_hash(
                {"prep": "dirac_0", "steps": DEFAULT_PREP_STEPS, "future": "identity"}
            ),
        },
        "nonclaims": [
            "finite N=8 East foreclosure over Def(l_energy), not a continuum or all-lens claim"
        ],
        "payload": payload,
    }


def build_real_reflection_seed(N: int, epsilon: Fraction, steps: int) -> Distribution:
    """Return a real East-evolved asymmetric seed distribution."""

    return hold(dirac(0), build_east_kernel(N, epsilon), steps)


def build_reflection_witness_package(
    N: int, mu: Distribution, h_prime: Distribution
) -> RouteTransportPackage:
    """Build the two-history package used to compute the separating future entry."""

    state_count = 1 << N
    return RouteTransportPackage(
        interfaces=("mid", "probe"),
        projections={"mid": lambda state: state, "probe": lambda state: state},
        histories={
            "mid": (
                History("mu", "mid", mu),
                History("h_reflect", "mid", h_prime),
            ),
            "probe": (),
        },
        continuations={
            ("mid", "probe"): (
                Continuation("identity_probe", "mid", "probe", _identity_kernel(N, state_count)),
            )
        },
        events={
            "mid": tuple(_energy_indicator_event(N, level) for level in range(N + 1)),
            "probe": (_n1_event(N),),
        },
        identity={
            "mid": Continuation("id_mid", "mid", "mid", _identity_kernel(N, state_count)),
            "probe": Continuation("id_probe", "probe", "probe", _identity_kernel(N, state_count)),
        },
        future_catalog={"mid": (("identity_probe", "n_1"),), "probe": ()},
    )


def build_payload(
    N: int,
    epsilon: Fraction,
    prep_steps: int,
    mu: Distribution,
    h_prime: Distribution,
    package: RouteTransportPackage,
) -> dict[str, Any]:
    """Return the foreclosure payload after exact checks."""

    if not verify_reflection_energy_invariance(mu, N):
        raise ValueError("reflected witness failed energy-level invariance")
    asym_left = expectation(mu, lambda state: int(spin(state, 1)))
    asym_right = expectation(mu, lambda state: int(spin(state, N)))
    if asym_left == asym_right:
        raise ValueError("real evolved witness is reflection-symmetric in n_1/n_N")

    sweep = foreclosure_sweep(mu, h_prime, N)
    if not sweep.all_agree:
        raise ValueError(f"foreclosure sweep found disagreement: {sweep.first_disagreement}")

    mu_history = package.history_by_label("mid", "mu")
    reflected_history = package.history_by_label("mid", "h_reflect")
    current_mu = current_signature(package, mu_history)
    current_reflected = current_signature(package, reflected_history)
    if current_mu != current_reflected:
        raise ValueError("full energy current signatures differ")
    future_mu = future_signature(package, mu_history)
    future_reflected = future_signature(package, reflected_history)
    gap = abs(future_mu[0] - future_reflected[0])
    if gap == 0:
        raise ValueError("n_1 separating future entry is zero")

    return {
        "N": N,
        "epsilon": rational_to_str(epsilon),
        "prep_steps": prep_steps,
        "lens_id": "L_energy",
        "witness_provenance": WITNESS_PROVENANCE,
        "lens_image_size": N + 1,
        "total_predicates": sweep.total_predicates,
        "agreeing_predicates": sweep.agreeing_predicates,
        "all_agree": sweep.all_agree,
        "first_disagreement": None,
        "energy_level_distribution_mu": _rational_dict(energy_level_distribution(mu, N)),
        "energy_level_distribution_h_prime": _rational_dict(energy_level_distribution(h_prime, N)),
        "asymmetry_check": {
            "event_left": "n_1",
            "event_right": "n_N",
            "value_left": rational_to_str(asym_left),
            "value_right": rational_to_str(asym_right),
            "abs_gap": rational_to_str(abs(asym_left - asym_right)),
        },
        "witness_pair": {
            "h_id": "mu",
            "hprime_id": "h_reflect",
            "current_signature": [
                {"energy": level, "value": rational_to_str(value)}
                for level, value in enumerate(current_mu)
            ],
        },
        "separating_entry": {
            "continuation_id": "identity_probe",
            "event_id": "n_1",
            "value_h": rational_to_str(future_mu[0]),
            "value_hprime": rational_to_str(future_reflected[0]),
            "abs_gap": rational_to_str(gap),
        },
        "t_for_02_statement": T_FOR_02_STATEMENT,
    }


def _energy_indicator_event(N: int, level: int) -> Event:
    return Event(
        f"energy_{level}",
        {state: Fraction(int(energy(state, N) == level)) for state in range(1 << N)},
    )


def _n1_event(N: int) -> Event:
    return Event("n_1", {state: Fraction(int(spin(state, 1))) for state in range(1 << N)})


def _identity_kernel(N: int, state_count: int) -> Kernel:
    return Kernel(
        N=N,
        state_count=state_count,
        rows={state: {state: Fraction(1)} for state in range(state_count)},
    )


def _rational_dict(values: dict[int, Fraction]) -> dict[str, str]:
    return {str(key): rational_to_str(value) for key, value in values.items()}


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
