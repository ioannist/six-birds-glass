from fractions import Fraction

import numpy as np
import pytest

from sixbirds_glass.models.east import east_constraint
from sixbirds_glass.models.fa import fa_constraint
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID
from sixbirds_glass.models.mc_engine import (
    cross_validate_at_n10,
    east_constraint_batch,
    ensemble_energy_trace,
    fa_constraint_batch,
    seed_block_bands,
    simulate_trajectories,
)


def test_mc_engine_smoke_reproducible_shape_and_energy_trace() -> None:
    initial = np.zeros(200, dtype=np.uint32)

    first = simulate_trajectories("east", 4, Fraction(1, 2), initial, 5, 123)
    second = simulate_trajectories("east", 4, Fraction(1, 2), initial, 5, 123)
    trace = ensemble_energy_trace(first, 4)

    np.testing.assert_array_equal(first, second)
    assert first.shape == (6, 200)
    assert trace.shape == (6,)
    assert np.all((0.0 <= trace) & (trace <= 4.0))


@pytest.mark.slow
@pytest.mark.parametrize("N", [4, 8, 10])
def test_vectorized_constraints_agree_with_scalar_constraints(N: int) -> None:
    rng = np.random.default_rng(202407)
    configs = rng.integers(0, 1 << N, size=500, dtype=np.uint32)
    sites = rng.integers(1, N + 1, size=500, dtype=np.int64)

    east_batch = east_constraint_batch(configs, sites, N)
    fa_batch = fa_constraint_batch(configs, sites, N)

    for config, site, east_value, fa_value in zip(
        configs, sites, east_batch, fa_batch, strict=True
    ):
        assert bool(east_value) == east_constraint(int(config), int(site), N)
        assert bool(fa_value) == fa_constraint(int(config), int(site), N)


@pytest.mark.slow
@pytest.mark.parametrize("family", ["east", "fa"])
def test_unconstrained_wall_site_empirical_frequency_matches_heat_bath(family: str) -> None:
    epsilon = Fraction(1, 2)
    c = float(epsilon / (Fraction(1) + epsilon))
    initial = np.zeros(20_000, dtype=np.uint32)

    trajectories = simulate_trajectories(family, 1, epsilon, initial, 1, 456)
    up_frequency = float((trajectories[-1] & np.uint32(1)).mean())

    assert abs(up_frequency - c) < 0.02


@pytest.mark.slow
def test_seed_block_bands_requires_even_blocks() -> None:
    trajectories = np.zeros((3, 21), dtype=np.uint32)

    with pytest.raises(ValueError, match="evenly divisible"):
        seed_block_bands(trajectories, 4, n_blocks=10)


@pytest.mark.slow
@pytest.mark.parametrize(
    ("family", "epsilon_hi", "epsilon_lo", "seed"),
    [
        ("east", DEFAULT_EPSILON_GRID[-1], DEFAULT_EPSILON_GRID[0], 1001),
        ("east", DEFAULT_EPSILON_GRID[-2], DEFAULT_EPSILON_GRID[1], 1002),
        ("fa", DEFAULT_EPSILON_GRID[-1], DEFAULT_EPSILON_GRID[0], 1003),
        ("fa", DEFAULT_EPSILON_GRID[-2], DEFAULT_EPSILON_GRID[1], 1004),
    ],
)
def test_cross_validate_at_n10_passes_for_both_families(
    family: str,
    epsilon_hi: Fraction,
    epsilon_lo: Fraction,
    seed: int,
) -> None:
    result = cross_validate_at_n10(
        family,
        epsilon_hi,
        epsilon_lo,
        t_w=8,
        n_traj=5_000,
        seed=seed,
    )

    assert result["pass"] is True
    assert len(result["rows"]) == 9


@pytest.mark.slow
def test_cross_validate_at_n10_negative_control_can_fail() -> None:
    result = cross_validate_at_n10(
        "east",
        DEFAULT_EPSILON_GRID[-1],
        DEFAULT_EPSILON_GRID[0],
        t_w=8,
        n_traj=1_000,
        seed=999,
        tolerance_bandwidths=0.01,
    )

    assert result["pass"] is False
    assert any(not row["within_tolerance"] for row in result["rows"])


@pytest.mark.parametrize("N", [0, 33])
def test_mc_rejects_carrier_outside_uint32(N: int) -> None:
    with pytest.raises(ValueError, match="1 <= N <= 32"):
        simulate_trajectories("east", N, Fraction(1, 2), np.array([0]), 0, 1)


@pytest.mark.parametrize("configs", [np.array([1 << 32]), np.array([-1]), np.array([0.5])])
def test_mc_rejects_states_before_casting(configs: np.ndarray) -> None:
    with pytest.raises(ValueError, match=r"carrier|integers"):
        simulate_trajectories("east", 4, Fraction(1, 2), configs, 0, 1)
    with pytest.raises(ValueError, match=r"carrier|integers"):
        ensemble_energy_trace(configs.reshape(1, -1), 4)


def test_mc_uint32_boundary_preserves_all_bits() -> None:
    initial = np.array([(1 << 32) - 1], dtype=np.uint64)
    trajectories = simulate_trajectories("east", 32, Fraction(1, 2), initial, 0, 1)
    assert trajectories[0, 0] == (1 << 32) - 1
    assert ensemble_energy_trace(trajectories, 32)[0] == 32.0


@pytest.mark.parametrize("epsilon", [Fraction(0), Fraction(-1, 2)])
def test_mc_rejects_invalid_heat_bath(epsilon: Fraction) -> None:
    with pytest.raises(ValueError, match="positive Fraction"):
        simulate_trajectories("east", 4, epsilon, np.array([0]), 1, 1)


def test_mc_rejects_empty_ensemble_and_noninteger_sites() -> None:
    with pytest.raises(ValueError, match="at least one trajectory"):
        simulate_trajectories("east", 4, Fraction(1, 2), np.array([], dtype=int), 1, 1)
    with pytest.raises(ValueError, match="nonempty"):
        seed_block_bands(np.empty((2, 0), dtype=np.uint32), 4)
    with pytest.raises(ValueError, match="sites must contain integers"):
        east_constraint_batch(np.array([0]), np.array([1.5]), 4)
