from fractions import Fraction

import pytest

from sixbirds_glass.models.east import build_east_kernel
from sixbirds_glass.protocols.evolution import (
    dirac,
    expectation,
    hold,
    max_denominator_bits,
    push,
)


def test_push_dirac_matches_kernel_row_exactly() -> None:
    kernel = build_east_kernel(6, Fraction(1, 2))

    assert push(dirac(0), kernel) == kernel.rows[0]


@pytest.mark.slow
def test_hold_dense_power_agrees_with_sequential_pushes() -> None:
    kernel = build_east_kernel(6, Fraction(1, 2))
    distribution = {0: Fraction(1, 3), 7: Fraction(2, 3)}

    dense_power_result = hold(distribution, kernel, 40)
    sequential_result = distribution
    for _ in range(40):
        sequential_result = push(sequential_result, kernel)

    assert dense_power_result == sequential_result


def test_hold_preserves_probability_mass_exactly() -> None:
    kernel = build_east_kernel(6, Fraction(3, 10))
    distribution = hold({0: Fraction(1, 2), 63: Fraction(1, 2)}, kernel, 17)

    assert sum(distribution.values(), start=Fraction(0)) == Fraction(1)
    assert max_denominator_bits(distribution) > 0


def test_expectation_is_exact() -> None:
    distribution = {0: Fraction(1, 4), 3: Fraction(3, 4)}

    assert expectation(distribution, lambda state: state) == Fraction(9, 4)
