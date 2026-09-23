from fractions import Fraction

import pytest

from sixbirds_glass.lenses.catalog import l_energy
from sixbirds_glass.models.east import build_east_kernel, east_stationary
from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.models.unconstrained import (
    build_unconstrained_kernel,
    unconstrained_stationary,
)
from sixbirds_glass.pipeline.cd import closure_deficit_float
from sixbirds_glass.pipeline.protocol_cd import (
    ProtocolCell,
    protocol_relative_cd,
    protocol_relative_lumpability_check,
)
from sixbirds_glass.protocols.evolution import hold


def test_protocol_cd_reduces_to_stationary_cd_for_single_constant_protocol() -> None:
    N = 4
    epsilon = Fraction(1, 2)
    tau = 2
    kernel = build_east_kernel(N, epsilon)
    stationary = east_stationary(N, epsilon)
    catalog = (
        ProtocolCell(
            label="stationary",
            weight=Fraction(1),
            initial_distribution=stationary,
            kernels=(kernel, kernel),
        ),
    )

    protocol_cd = protocol_relative_cd(catalog, l_energy, N, tau, condition_on_r=True)
    stationary_cd = closure_deficit_float(N, kernel, stationary, tau, l_energy)

    assert abs(protocol_cd - stationary_cd) < 1e-12


def test_protocol_lumpability_exact_zero_for_unconstrained_multi_cell_catalog() -> None:
    N = 4
    tau = 2
    eps_a = Fraction(1, 5)
    eps_b = Fraction(1, 2)
    kernel_a = build_unconstrained_kernel(N, eps_a)
    kernel_b = build_unconstrained_kernel(N, eps_b)
    catalog = (
        ProtocolCell(
            label="unconstrained_a",
            weight=Fraction(1, 3),
            initial_distribution=unconstrained_stationary(N, eps_a),
            kernels=(kernel_a, kernel_a),
        ),
        ProtocolCell(
            label="unconstrained_b",
            weight=Fraction(2, 3),
            initial_distribution=unconstrained_stationary(N, eps_b),
            kernels=(kernel_b, kernel_a),
        ),
    )

    result = protocol_relative_lumpability_check(catalog, l_energy, N, tau)

    assert result.is_lumpable
    assert result.violation is None


def test_protocol_cd_detects_non_lumpable_constrained_aging_catalog() -> None:
    N = 4
    tau = 2
    eps_hi = Fraction(7, 10)
    eps_lo = Fraction(1, 10)
    eps_mid = Fraction(2, 5)
    kernel_lo = build_east_kernel(N, eps_lo)
    kernel_mid = build_east_kernel(N, eps_mid)
    initial_hot = east_stationary(N, eps_hi)
    catalog = (
        ProtocolCell(
            label="age_1",
            weight=Fraction(1, 2),
            initial_distribution=hold(initial_hot, kernel_lo, 1),
            kernels=(kernel_mid, kernel_mid),
        ),
        ProtocolCell(
            label="age_2",
            weight=Fraction(1, 2),
            initial_distribution=hold(initial_hot, kernel_lo, 2),
            kernels=(kernel_lo, kernel_mid),
        ),
    )

    exact = protocol_relative_lumpability_check(catalog, l_energy, N, tau)
    windowed = protocol_relative_cd(catalog, l_energy, N, tau, condition_on_r=True)
    marginalized = protocol_relative_cd(catalog, l_energy, N, tau, condition_on_r=False)

    assert not exact.is_lumpable
    assert exact.violation is not None
    assert windowed > 0.0
    assert marginalized > 0.0
    assert windowed != marginalized


def test_protocol_cell_rejects_non_fraction_kernel_entry() -> None:
    kernel = Kernel(
        N=1,
        state_count=2,
        rows={0: {0: 1.0}, 1: {1: Fraction(1)}},  # type: ignore[dict-item]
    )

    with pytest.raises(ValueError, match="non-Fraction entry"):
        protocol_relative_lumpability_check(_single_kernel_catalog(kernel), l_energy, 1, 1)


def test_protocol_cell_rejects_bad_kernel_row_sum() -> None:
    kernel = Kernel(
        N=1,
        state_count=2,
        rows={0: {0: Fraction(2)}, 1: {1: Fraction(1)}},
    )

    with pytest.raises(ValueError, match="row 0 must sum to 1"):
        protocol_relative_lumpability_check(_single_kernel_catalog(kernel), l_energy, 1, 1)


def test_protocol_cell_rejects_negative_kernel_entry() -> None:
    kernel = Kernel(
        N=1,
        state_count=2,
        rows={0: {0: Fraction(2), 1: Fraction(-1)}, 1: {1: Fraction(1)}},
    )

    with pytest.raises(ValueError, match="negative entry"):
        protocol_relative_lumpability_check(_single_kernel_catalog(kernel), l_energy, 1, 1)


def test_protocol_cell_rejects_missing_kernel_row() -> None:
    kernel = Kernel(N=1, state_count=2, rows={0: {0: Fraction(1)}})

    with pytest.raises(ValueError, match="lacks row for state 1"):
        protocol_relative_lumpability_check(_single_kernel_catalog(kernel), l_energy, 1, 1)


def test_protocol_cell_rejects_out_of_range_kernel_target() -> None:
    kernel = Kernel(
        N=1,
        state_count=2,
        rows={0: {2: Fraction(1)}, 1: {1: Fraction(1)}},
    )

    with pytest.raises(ValueError, match="out-of-range target 2"):
        protocol_relative_lumpability_check(_single_kernel_catalog(kernel), l_energy, 1, 1)


def _single_kernel_catalog(kernel: Kernel) -> tuple[ProtocolCell, ...]:
    return (
        ProtocolCell(
            label="bad_kernel",
            weight=Fraction(1),
            initial_distribution={0: Fraction(1)},
            kernels=(kernel,),
        ),
    )
