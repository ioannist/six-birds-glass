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
