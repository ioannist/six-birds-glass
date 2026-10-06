"""Declared finite schedule words and autonomous phase lifts."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fractions import Fraction

from sixbirds_glass.models.kernels import Kernel, validate_kernel_rows
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
    base_state_count: int

    def pack(self, state: int, phase: int) -> int:
        """Pack a base state using this chain's actual finite carrier."""
        if phase >= self.total_steps + (not self.cyclic):
            raise ValueError("phase is outside the lifted carrier")
        return lift_state(state, phase, self.N, state_count=self.base_state_count)

    def unpack(self, state: int) -> tuple[int, int]:
        """Unpack and check membership in the lifted carrier."""
        if not 0 <= state < self.kernel.state_count:
            raise ValueError("state is outside the lifted carrier")
        return unlift(state, self.N, state_count=self.base_state_count)


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

    Lifted states are packed as ``config + phase * base_state_count``. This
    agrees with bit packing for spin carriers, and also supports trap carriers.
    Non-cyclic lifts use
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
        if leg.epsilon not in kernels:
            kernels[leg.epsilon] = kernel_builder(leg.epsilon)
    for kernel in kernels.values():
        validate_kernel_rows(kernel)
        if kernel.N != N or kernel.state_count != first_kernel.state_count:
            raise ValueError("every schedule kernel must use the same finite carrier")

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
            lifted_source = lift_state(config, phase, N, state_count=first_kernel.state_count)
            lifted_row: dict[int, Fraction] = {}
            for target_config, probability in active_kernel.rows[config].items():
                lifted_target = lift_state(
                    target_config, next_phase, N, state_count=first_kernel.state_count
                )
                lifted_row[lifted_target] = probability
            rows[lifted_source] = lifted_row

    return LiftedChain(
        N=N,
        total_steps=total_steps,
        cyclic=cyclic,
        kernel=Kernel(N=N, state_count=lifted_state_count, rows=rows),
        base_state_count=first_kernel.state_count,
    )


def lift_state(config: int, phase: int, N: int, *, state_count: int | None = None) -> int:
    """Pack a finite state and phase; the default carrier is ``2**N``."""

    size = (1 << N) if state_count is None else state_count
    if size < 1 or not 0 <= config < size or phase < 0:
        raise ValueError("invalid base state, phase, or carrier")
    return config + phase * size


def unlift(lifted_state: int, N: int, *, state_count: int | None = None) -> tuple[int, int]:
    """Unpack a finite state and phase; the default carrier is ``2**N``."""

    size = (1 << N) if state_count is None else state_count
    if size < 1 or lifted_state < 0:
        raise ValueError("invalid lifted state or carrier")
    phase, config = divmod(lifted_state, size)
    return config, phase


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
