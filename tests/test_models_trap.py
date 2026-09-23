from fractions import Fraction

import pytest

from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID
from sixbirds_glass.models.kernels import Kernel, strongly_connected
from sixbirds_glass.models.trap import (
    DEFAULT_TRAP_BASE_WEIGHTS,
    build_trap_kernel,
    declared_trap_weights_by_epsilon,
    trap_band,
    trap_depth_observable,
    trap_stationary,
)


def test_trap_detailed_balance_exact_on_declared_grid() -> None:
    weights_by_epsilon = declared_trap_weights_by_epsilon(DEFAULT_EPSILON_GRID)

    for escape_weights in weights_by_epsilon.values():
        kernel = build_trap_kernel(DEFAULT_TRAP_BASE_WEIGHTS, escape_weights)
        stationary = trap_stationary(escape_weights)
        assert_detailed_balance(kernel, stationary)


def test_trap_row_sums_are_exactly_one_on_declared_grid() -> None:
    weights_by_epsilon = declared_trap_weights_by_epsilon(DEFAULT_EPSILON_GRID)

    for escape_weights in weights_by_epsilon.values():
        kernel = build_trap_kernel(DEFAULT_TRAP_BASE_WEIGHTS, escape_weights)
        for state in range(kernel.state_count):
            assert kernel.row_sum(state) == Fraction(1)


def test_trap_kernel_is_irreducible_on_declared_grid() -> None:
    weights_by_epsilon = declared_trap_weights_by_epsilon(DEFAULT_EPSILON_GRID)

    for escape_weights in weights_by_epsilon.values():
        assert strongly_connected(build_trap_kernel(DEFAULT_TRAP_BASE_WEIGHTS, escape_weights))


def test_trap_band_has_two_element_image() -> None:
    image = {
        trap_band(trap, DEFAULT_TRAP_BASE_WEIGHTS) for trap in range(len(DEFAULT_TRAP_BASE_WEIGHTS))
    }

    assert image == {"shallow", "deep"}


def test_trap_declared_weights_are_colder_is_stickier() -> None:
    weights_by_epsilon = declared_trap_weights_by_epsilon(DEFAULT_EPSILON_GRID)
    cold_weights = weights_by_epsilon[DEFAULT_EPSILON_GRID[0]]
    hot_weights = weights_by_epsilon[DEFAULT_EPSILON_GRID[-1]]

    assert all(cold <= hot for cold, hot in zip(cold_weights, hot_weights, strict=True))
    assert any(cold < hot for cold, hot in zip(cold_weights, hot_weights, strict=True))


def test_trap_stationary_distribution_is_epsilon_invariant() -> None:
    weights_by_epsilon = declared_trap_weights_by_epsilon(DEFAULT_EPSILON_GRID)

    # Each grid point multiplies all base weights by one scalar. Since
    # pi_k is proportional to 1 / w_k, that scalar cancels exactly.
    cold_stationary = trap_stationary(weights_by_epsilon[DEFAULT_EPSILON_GRID[0]])
    hot_stationary = trap_stationary(weights_by_epsilon[DEFAULT_EPSILON_GRID[-1]])

    assert cold_stationary == hot_stationary


def test_trap_depth_observable_known_values() -> None:
    assert trap_depth_observable(0, DEFAULT_TRAP_BASE_WEIGHTS) == Fraction(2)
    assert trap_depth_observable(7, DEFAULT_TRAP_BASE_WEIGHTS) == Fraction(50)


def test_trap_depth_observable_rejects_out_of_range_trap() -> None:
    with pytest.raises(ValueError, match="out of range"):
        trap_depth_observable(len(DEFAULT_TRAP_BASE_WEIGHTS), DEFAULT_TRAP_BASE_WEIGHTS)


def assert_detailed_balance(kernel: Kernel, stationary: dict[int, Fraction]) -> None:
    for source, row in kernel.rows.items():
        for target, probability in row.items():
            reverse = kernel.rows[target].get(source, Fraction(0))
            assert stationary[source] * probability == stationary[target] * reverse
