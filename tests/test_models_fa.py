from fractions import Fraction

import pytest

from sixbirds_glass.models.fa import build_fa_kernel, fa_stationary
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID
from sixbirds_glass.models.kernels import Kernel, strongly_connected

DETAIL_N_VALUES = (4, 6, 8, pytest.param(10, marks=pytest.mark.slow))
CONNECTIVITY_N_VALUES = (4, 6, 8, pytest.param(10, marks=pytest.mark.slow))


@pytest.mark.parametrize("epsilon", DEFAULT_EPSILON_GRID)
@pytest.mark.parametrize("N", DETAIL_N_VALUES)
def test_fa_detailed_balance_exact(N: int, epsilon: Fraction) -> None:
    kernel = build_fa_kernel(N, epsilon)
    stationary = fa_stationary(N, epsilon)

    assert_detailed_balance(kernel, stationary)


@pytest.mark.parametrize("epsilon", DEFAULT_EPSILON_GRID)
@pytest.mark.parametrize("N", DETAIL_N_VALUES)
def test_fa_row_sums_are_exactly_one(N: int, epsilon: Fraction) -> None:
    kernel = build_fa_kernel(N, epsilon)

    for state in range(kernel.state_count):
        assert kernel.row_sum(state) == Fraction(1)


@pytest.mark.parametrize("N", CONNECTIVITY_N_VALUES)
def test_fa_wall_boundary_is_irreducible(N: int) -> None:
    assert strongly_connected(build_fa_kernel(N, Fraction(1, 2)))


def assert_detailed_balance(kernel: Kernel, stationary: dict[int, Fraction]) -> None:
    for source, row in kernel.rows.items():
        for target, probability in row.items():
            reverse = kernel.rows[target].get(source, Fraction(0))
            assert stationary[source] * probability == stationary[target] * reverse
