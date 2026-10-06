from collections import defaultdict
from fractions import Fraction

import pytest

from sixbirds_glass.models.east import build_east_kernel, east_energy, east_stationary
from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.models.trap import build_trap_kernel
from sixbirds_glass.protocols.catalog import p_eq
from sixbirds_glass.protocols.evolution import dirac, expectation, hold
from sixbirds_glass.protocols.schedule import (
    ScheduleLeg,
    evolve_schedule,
    evolve_schedule_trace,
    lift_schedule,
    lift_state,
    unlift,
)


def test_evolve_schedule_trace_matches_plain_evolution_at_final_boundary() -> None:
    N = 6
    schedule = (
        ScheduleLeg(Fraction(1, 2), 3),
        ScheduleLeg(Fraction(1, 5), 2),
    )

    def kernel_builder(epsilon: Fraction) -> Kernel:
        return build_east_kernel(N, epsilon)

    def observable(state: int) -> int:
        return east_energy(state, N)

    trace = evolve_schedule_trace(dirac(0), schedule, kernel_builder, observable)
    final_distribution = evolve_schedule(dirac(0), schedule, kernel_builder)

    assert len(trace) == 5
    assert trace[-1] == expectation(final_distribution, observable)


@pytest.mark.slow
def test_east_stationary_distribution_is_exact_fixed_point_under_p_eq() -> None:
    N = 6
    epsilon = Fraction(1, 2)
    stationary = east_stationary(N, epsilon)

    evolved = evolve_schedule(
        stationary,
        p_eq(epsilon, 50),
        lambda leg_epsilon: build_east_kernel(N, leg_epsilon),
    )

    assert evolved == stationary


def test_noncyclic_lifted_chain_matches_plain_schedule_marginal() -> None:
    N = 4
    initial_config = 3
    schedule = (
        ScheduleLeg(Fraction(1, 2), 2),
        ScheduleLeg(Fraction(1, 5), 4),
    )

    def kernel_builder(epsilon: Fraction) -> Kernel:
        return build_east_kernel(N, epsilon)

    lifted = lift_schedule(schedule, kernel_builder, cyclic=False)

    assert_all_rows_sum_to_one(lifted.kernel)

    lifted_final = hold(dirac(lift_state(initial_config, 0, N)), lifted.kernel, 6)
    marginal = config_marginal(lifted_final, N)
    plain_final = evolve_schedule(dirac(initial_config), schedule, kernel_builder)

    assert {phase for state in lifted_final for _, phase in [unlift(state, N)]} == {6}
    assert marginal == plain_final


def test_cyclic_lifted_chain_wraps_phase_and_is_row_stochastic() -> None:
    N = 4
    schedule = (ScheduleLeg(Fraction(1, 2), 3),)
    lifted = lift_schedule(schedule, lambda epsilon: build_east_kernel(N, epsilon), cyclic=True)

    assert_all_rows_sum_to_one(lifted.kernel)

    final_distribution = hold(dirac(lift_state(0, 0, N)), lifted.kernel, 3)
    assert {phase for state in final_distribution for _, phase in [unlift(state, N)]} == {0}


@pytest.mark.parametrize("cyclic", [False, True])
def test_generic_trap_lift_uses_actual_carrier_and_matches_schedule(cyclic: bool) -> None:
    weights = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 5))
    schedule = (ScheduleLeg(Fraction(1, 2), 2), ScheduleLeg(Fraction(1, 5), 3))

    def builder(epsilon: Fraction) -> Kernel:
        return build_trap_kernel(weights, tuple(epsilon * w for w in weights))

    lifted = lift_schedule(schedule, builder, cyclic=cyclic)
    assert lifted.base_state_count == 3
    assert set(lifted.kernel.rows) == set(range(lifted.kernel.state_count))
    assert_all_rows_sum_to_one(lifted.kernel)
    final = hold(dirac(lifted.pack(2, 0)), lifted.kernel, 5)
    marginal: defaultdict[int, Fraction] = defaultdict(Fraction)
    for state, mass in final.items():
        config, phase = lifted.unpack(state)
        assert phase == (0 if cyclic else 5)
        marginal[config] += mass
    assert dict(marginal) == evolve_schedule(dirac(2), schedule, builder)
    with pytest.raises(ValueError, match="outside"):
        lifted.pack(0, 5 if cyclic else 6)


def test_schedule_lift_rejects_temperature_dependent_carrier_changes() -> None:
    schedule = (ScheduleLeg(Fraction(1, 2), 1), ScheduleLeg(Fraction(1, 5), 1))
    with pytest.raises(ValueError, match="same finite carrier"):
        lift_schedule(
            schedule, lambda epsilon: build_east_kernel(2 if epsilon == 1 / 2 else 3, epsilon)
        )


def assert_all_rows_sum_to_one(kernel: Kernel) -> None:
    for state in range(kernel.state_count):
        assert kernel.row_sum(state) == Fraction(1)


def config_marginal(distribution: dict[int, Fraction], N: int) -> dict[int, Fraction]:
    marginal: defaultdict[int, Fraction] = defaultdict(Fraction)
    for lifted_state, mass in distribution.items():
        config, _phase = unlift(lifted_state, N)
        marginal[config] += mass
    return {config: mass for config, mass in marginal.items() if mass != 0}
