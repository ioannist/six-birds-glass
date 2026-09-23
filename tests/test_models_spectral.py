import math
from fractions import Fraction

import pytest

from sixbirds_glass.models.east import build_east_kernel
from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.models.spectral import (
    mixing_time_bound,
    spectral_gap,
    spectral_gap_table_row,
)


@pytest.mark.parametrize(("N", "epsilon"), [(4, Fraction(1, 2)), (6, Fraction(1, 5))])
def test_spectral_gap_is_valid_for_east(N: int, epsilon: Fraction) -> None:
    gap = spectral_gap(build_east_kernel(N, epsilon))

    assert 0 < gap <= 1


def test_spectral_gap_excludes_leading_eigenvalue_by_modulus() -> None:
    kernel = Kernel(
        N=1,
        state_count=2,
        rows={
            0: {0: Fraction(1, 2), 1: Fraction(1, 2)},
            1: {0: Fraction(1, 2), 1: Fraction(1, 2)},
        },
    )

    assert spectral_gap(kernel) == pytest.approx(1.0)


def test_mixing_time_bound_positive_and_infinite_guard() -> None:
    assert mixing_time_bound(0.25) > 0
    assert math.isinf(mixing_time_bound(0.0))
    assert math.isinf(mixing_time_bound(-0.1))


def test_spectral_gap_table_row_shape() -> None:
    row = spectral_gap_table_row(4, Fraction(1, 2))

    assert set(row) == {"N", "epsilon", "gap", "tau_rel", "mixing_time_bound"}
    assert row["N"] == 4
    assert row["epsilon"] == "1/2"
    assert isinstance(row["gap"], float)


def test_spectral_gap_table_row_matches_generic_gap_on_small_east_kernel() -> None:
    epsilon = Fraction(1, 2)
    row = spectral_gap_table_row(4, epsilon)
    generic_gap = spectral_gap(build_east_kernel(4, epsilon))

    assert row["gap"] == pytest.approx(generic_gap)
