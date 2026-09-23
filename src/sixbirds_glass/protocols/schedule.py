"""Declared finite schedule words and autonomous phase lifts."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fractions import Fraction

from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.protocols.evolution import Distribution, Observable, expectation, hold, push

KernelBuilder = Callable[[Fraction], Kernel]


@dataclass(frozen=True)
class ScheduleLeg:
    """One schedule leg: run ``steps`` steps at epsilon."""

    epsilon: Fraction
    steps: int

    def __post_init__(self) -> None:
        if self.steps < 0:
            raise ValueError("schedule leg steps must be non-negative")


Schedule = Sequence[ScheduleLeg]


@dataclass(frozen=True)
class LiftedChain:
    """A phase-lifted autonomous chain over packed ``(config, phase)`` states."""

    N: int
    total_steps: int
    cyclic: bool
    kernel: Kernel


def evolve_schedule(
    distribution: Distribution,
    schedule: Schedule,
    kernel_builder: KernelBuilder,
) -> Distribution:
    """Apply every schedule leg in order."""

    result = distribution
    for leg in schedule:
        result = hold(result, kernel_builder(leg.epsilon), leg.steps)
    return result


def evolve_schedule_trace(
    distribution: Distribution,
    schedule: Schedule,
    kernel_builder: KernelBuilder,
    observable: Observable,
) -> list[Fraction]:
    """Return observable expectations after every single schedule step.

    Traced evolution intentionally uses sequential sparse pushes even for long
    legs. Dense powers skip intermediate distributions, so they are only valid
    for ``hold`` calls where no per-step trace is requested.
    """

    result = distribution
    trace: list[Fraction] = []
    for leg in schedule:
        kernel = kernel_builder(leg.epsilon)
        for _ in range(leg.steps):
            result = push(result, kernel)
            trace.append(expectation(result, observable))
    return trace


def lift_schedule(
    schedule: Schedule,
    kernel_builder: KernelBuilder,
    *,
    cyclic: bool = False,
) -> LiftedChain:
    """Build the autonomous phase-lifted kernel for a schedule.

    Lifted states are packed as ``config | (phase << N)``. Non-cyclic lifts use
    phases ``0..L``; the terminal phase ``L`` keeps phase fixed while applying
    the final leg's kernel. Cyclic lifts use phases ``0..L-1`` and wrap the
    final phase back to ``0``.
    """

    if not schedule:
        raise ValueError("schedule must contain at least one leg")

    total_steps = sum(leg.steps for leg in schedule)
    if cyclic and total_steps == 0:
        raise ValueError("cyclic schedule must have at least one step")

    active_epsilons = _active_epsilons(schedule)
    first_kernel = kernel_builder(schedule[0].epsilon)
    N = first_kernel.N
    kernels = {schedule[0].epsilon: first_kernel}
    for leg in schedule[1:]:
        kernels.setdefault(leg.epsilon, kernel_builder(leg.epsilon))

    phase_count = total_steps if cyclic else total_steps + 1
    lifted_state_count = first_kernel.state_count * phase_count
    rows: dict[int, dict[int, Fraction]] = {}

    for phase in range(phase_count):
        active_kernel = _kernel_for_phase(
            phase=phase,
            total_steps=total_steps,
            cyclic=cyclic,
            active_epsilons=active_epsilons,
            final_epsilon=schedule[-1].epsilon,
            kernels=kernels,
        )
        next_phase = _next_phase(phase, total_steps=total_steps, cyclic=cyclic)
        for config in range(first_kernel.state_count):
            lifted_source = lift_state(config, phase, N)
            lifted_row: dict[int, Fraction] = {}
            for target_config, probability in active_kernel.rows[config].items():
                lifted_target = lift_state(target_config, next_phase, N)
                lifted_row[lifted_target] = probability
            rows[lifted_source] = lifted_row

    return LiftedChain(
        N=N,
        total_steps=total_steps,
        cyclic=cyclic,
        kernel=Kernel(N=N, state_count=lifted_state_count, rows=rows),
    )


def lift_state(config: int, phase: int, N: int) -> int:
    """Pack ``(config, phase)`` as ``config | (phase << N)``."""

    return config | (phase << N)


def unlift(lifted_state: int, N: int) -> tuple[int, int]:
    """Unpack ``config | (phase << N)`` into ``(config, phase)``."""

    config_mask = (1 << N) - 1
    return lifted_state & config_mask, lifted_state >> N


def _active_epsilons(schedule: Schedule) -> list[Fraction]:
    epsilons: list[Fraction] = []
    for leg in schedule:
        epsilons.extend(leg.epsilon for _ in range(leg.steps))
    return epsilons


def _kernel_for_phase(
    *,
    phase: int,
    total_steps: int,
    cyclic: bool,
    active_epsilons: Sequence[Fraction],
    final_epsilon: Fraction,
    kernels: dict[Fraction, Kernel],
) -> Kernel:
    if not cyclic and phase == total_steps:
        return kernels[final_epsilon]
    return kernels[active_epsilons[phase]]


def _next_phase(phase: int, *, total_steps: int, cyclic: bool) -> int:
    if cyclic:
        return (phase + 1) % total_steps
    if phase == total_steps:
        return total_steps
    return phase + 1
