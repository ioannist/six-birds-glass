from fractions import Fraction
from pathlib import Path

import pytest

from sixbirds_glass.io.config import load_config
from sixbirds_glass.models.east import east_energy
from sixbirds_glass.pipeline.diagnostics import max_fiber_size, witness_count
from sixbirds_glass.pipeline.kovacs_witness import (
    KovacsMomentWitness,
    build_kovacs_moment_history,
    build_kovacs_moment_witness_from_config,
    solve_randomized_stop_theta,
)
from sixbirds_glass.pipeline.signatures import current_signature, future_signature
from sixbirds_glass.protocols.evolution import expectation

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def frozen_witness() -> KovacsMomentWitness:
    config = load_config(Path("configs/kovacs_hump_default.json"))
    return build_kovacs_moment_witness_from_config(config)


def test_randomized_stop_theta_solve_and_bracketing_guard() -> None:
    assert solve_randomized_stop_theta(Fraction(3, 2), Fraction(5, 2), Fraction(2)) == Fraction(
        1, 2
    )

    with pytest.raises(ValueError, match="not bracketed"):
        solve_randomized_stop_theta(Fraction(3, 2), Fraction(5, 2), Fraction(3))


def test_real_kovacs_moment_history_hits_equilibrium_energy_exactly(
    frozen_witness: KovacsMomentWitness,
) -> None:
    rebuilt = build_kovacs_moment_history(
        frozen_witness.mu_t, frozen_witness.mu_t_plus_1, frozen_witness.theta
    )

    assert rebuilt == frozen_witness.mu_k
    assert sum(frozen_witness.mu_k.values(), start=Fraction(0)) == Fraction(1)
    assert (
        expectation(frozen_witness.mu_k, lambda state: east_energy(state, frozen_witness.N))
        == frozen_witness.e_eq
    )


def test_kovacs_witness_package_has_equal_current_and_separating_future(
    frozen_witness: KovacsMomentWitness,
) -> None:
    package = frozen_witness.package
    mu_history = package.history_by_label("mid", "mu_K")
    pi_history = package.history_by_label("mid", "pi_eq")

    assert current_signature(package, mu_history) == current_signature(package, pi_history)
    mu_future = future_signature(package, mu_history)
    pi_future = future_signature(package, pi_history)
    assert mu_future != pi_future
    assert abs(mu_future[0] - pi_future[0]) == frozen_witness.separating_gap
    assert frozen_witness.separating_gap > 0


def test_kovacs_witness_diagnostics(frozen_witness: KovacsMomentWitness) -> None:
    package = frozen_witness.package

    assert witness_count(package, "mid") == 1
    assert max_fiber_size(package, "mid") == 2
