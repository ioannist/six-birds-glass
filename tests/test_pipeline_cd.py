from fractions import Fraction

import pytest

from sixbirds_glass.lenses.catalog import l_energy
from sixbirds_glass.models.east import build_east_kernel, east_stationary
from sixbirds_glass.models.unconstrained import (
    build_unconstrained_kernel,
    unconstrained_stationary,
)
from sixbirds_glass.pipeline.cd import (
    closure_deficit_float,
    is_exactly_lumpable,
    lumpability_check_exact,
)
from sixbirds_glass.pipeline.packaging import fiber_partition
from sixbirds_glass.protocols.evolution import dirac, hold

pytestmark = pytest.mark.slow


def test_unconstrained_energy_lens_is_exactly_lumpable_for_tau_ladder() -> None:
    N = 6
    kernel = build_unconstrained_kernel(N, Fraction(1, 2))

    for tau in (1, 2, 4):
        assert is_exactly_lumpable(N, kernel, tau, l_energy)


def test_constrained_east_energy_lens_is_not_exactly_lumpable_with_violation_detail() -> None:
    N = 6
    kernel = build_east_kernel(N, Fraction(1, 2))

    for tau in (1, 2, 4):
        result = lumpability_check_exact(N, kernel, tau, l_energy)

        assert not result.is_lumpable
        assert result.violation is not None
        violation = result.violation
        assert l_energy(violation.left_state, N) == l_energy(violation.right_state, N)
        assert violation.left_probability != violation.right_probability

        fibers = fiber_partition(N, l_energy)
        target_states = fibers[violation.target_fiber]
        left = hold(dirac(violation.left_state), kernel, tau)
        right = hold(dirac(violation.right_state), kernel, tau)
        assert (
            sum((left.get(state, Fraction(0)) for state in target_states), start=Fraction(0))
            == violation.left_probability
        )
        assert (
            sum((right.get(state, Fraction(0)) for state in target_states), start=Fraction(0))
            == violation.right_probability
        )


def test_numeric_closure_deficit_is_zero_on_unconstrained_control() -> None:
    N = 6

    for tau, epsilon in ((1, Fraction(1, 2)), (4, Fraction(1, 5))):
        kernel = build_unconstrained_kernel(N, epsilon)
        stationary = unconstrained_stationary(N, epsilon)
        cd = closure_deficit_float(N, kernel, stationary, tau, l_energy)
        assert abs(cd) < 1e-12


def test_numeric_closure_deficit_is_positive_on_constrained_east() -> None:
    N = 6

    for tau, epsilon in ((1, Fraction(1, 2)), (2, Fraction(1, 5))):
        kernel = build_east_kernel(N, epsilon)
        stationary = east_stationary(N, epsilon)
        cd = closure_deficit_float(N, kernel, stationary, tau, l_energy)
        assert cd > 0.0


def test_exact_and_numeric_closure_checks_agree_in_direction_for_east() -> None:
    N = 6
    epsilon = Fraction(1, 2)
    tau = 2
    kernel = build_east_kernel(N, epsilon)

    assert not is_exactly_lumpable(N, kernel, tau, l_energy)
    assert closure_deficit_float(N, kernel, east_stationary(N, epsilon), tau, l_energy) > 0.0
