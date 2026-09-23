from fractions import Fraction

from sixbirds_glass.extension.pressure import (
    fekete_gap,
    phi_n,
    pressure_ladder,
    tilted_transfer_matrix,
    verify_subadditivity,
)
from sixbirds_glass.lenses.catalog import l_energy
from sixbirds_glass.models.east import build_east_kernel


def test_untilted_pressure_phi_is_one_for_row_stochastic_kernel() -> None:
    N = 4
    kernel = build_east_kernel(N, Fraction(2, 5))
    matrix = tilted_transfer_matrix(kernel, l_energy, N, 0.0)

    for n in range(1, 6):
        assert abs(phi_n(matrix, n) - 1.0) < 1e-12


def test_subadditivity_verified_for_tilted_transfer_matrix() -> None:
    N = 4
    kernel = build_east_kernel(N, Fraction(2, 5))
    matrix = tilted_transfer_matrix(kernel, l_energy, N, 0.2)

    checks = verify_subadditivity(matrix, ((1, 1), (1, 2), (2, 3)))

    assert all(check.passed for check in checks)


def test_pressure_ladder_and_fekete_gap_are_reported() -> None:
    N = 4
    kernel = build_east_kernel(N, Fraction(2, 5))

    ladder = pressure_ladder(kernel, l_energy, N, 0.2, range(1, 6))
    gap = fekete_gap(ladder, n_min=2)

    assert set(ladder) == {1, 2, 3, 4, 5}
    assert gap >= 0.0
