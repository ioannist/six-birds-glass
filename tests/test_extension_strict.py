from fractions import Fraction
from pathlib import Path

import pytest

from sixbirds_glass.extension.strict import (
    artifact_sha256,
    build_h5_citation,
    build_nonfactorization_citations,
    nonfactorization_rate,
    run_forcing_comparison,
    run_saturation,
)
from sixbirds_glass.io.config import load_config
from sixbirds_glass.io.rational import str_to_rational
from sixbirds_glass.lenses.catalog import l_energy
from sixbirds_glass.models.east import build_east_kernel
from sixbirds_glass.pipeline.packaging import gibbs_prototype_rule

pytestmark = pytest.mark.slow


def test_saturation_reaches_fixed_strata_on_n8_shell_witness() -> None:
    config = load_config(Path("configs/gt6_shell_witness_n8.json"))
    N, _epsilon_lo, epsilon_mid, _epsilon_hi = _strict_params(config)

    result = run_saturation(
        N,
        build_east_kernel(N, epsilon_mid),
        1,
        l_energy,
        gibbs_prototype_rule(N, epsilon_mid),
    )

    assert result.saturated
    assert result.iterations_to_saturation <= 10
    assert result.strata_count == N + 1


def test_conditioned_annealing_forcing_comparison_runs() -> None:
    config = load_config(Path("configs/gt6_shell_witness_n8.json"))
    N, epsilon_lo, epsilon_mid, epsilon_hi = _strict_params(config)

    result = run_forcing_comparison(
        N,
        epsilon_lo,
        epsilon_hi,
        epsilon_mid,
        1,
        l_energy,
        gibbs_prototype_rule(N, epsilon_mid),
    )

    assert result.with_conditioning.saturated
    assert result.without_conditioning.saturated
    assert result.material_forcing_count >= 0


def test_h5_and_nonfactorization_citations_resolve_existing_artifacts() -> None:
    h5 = build_h5_citation(Path("artifacts/gt1_cd_tables/east_n8_l_energy.json"))
    citations = build_nonfactorization_citations(
        Path("artifacts/gt2_witnesses/kovacs_moment.json"),
        Path("artifacts/gt3_foreclosure/lens_class_sweep.json"),
    )

    assert h5.artifact_path.is_file()
    assert "gt1_cd_tables" in h5.artifact_path.as_posix()
    assert h5.sha256 == artifact_sha256(h5.artifact_path)
    assert all(citation.artifact_path.is_file() for citation in citations)
    assert all(citation.sha256 == artifact_sha256(citation.artifact_path) for citation in citations)
    assert nonfactorization_rate(citations) == 1


def _strict_params(config: dict) -> tuple[int, Fraction, Fraction, Fraction]:
    word = config["protocol"]["word"]
    return (
        int(config["model"]["N"]),
        str_to_rational(word[1]["epsilon"]),
        str_to_rational(word[2]["epsilon"]),
        str_to_rational(word[0]["epsilon"]),
    )
