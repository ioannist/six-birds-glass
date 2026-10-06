from collections import defaultdict
from fractions import Fraction

from sixbirds_glass.models.east import build_east_kernel, east_energy
from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.models.unconstrained import build_unconstrained_kernel


def test_unconstrained_kernel_is_exactly_lumpable_by_energy() -> None:
    N = 6
    kernel = build_unconstrained_kernel(N, Fraction(1, 2))
    fibers = energy_fibers(N)

    for states in fibers.values():
        first_row = fiber_transition_row(kernel, states[0], N)
        for state in states[1:]:
            assert fiber_transition_row(kernel, state, N) == first_row


def test_constrained_east_kernel_is_not_lumpable_by_energy() -> None:
    N = 6
    kernel = build_east_kernel(N, Fraction(1, 2))
    fibers = energy_fibers(N)

    assert has_lumpability_counterexample(kernel, fibers, N)


def energy_fibers(N: int) -> dict[int, list[int]]:
    fibers: dict[int, list[int]] = defaultdict(list)
    for state in range(1 << N):
        fibers[east_energy(state, N)].append(state)
    return dict(fibers)


def fiber_transition_row(kernel: Kernel, state: int, N: int) -> tuple[Fraction, ...]:
    totals = [Fraction(0) for _ in range(N + 1)]
    for target, probability in kernel.rows[state].items():
        totals[east_energy(target, N)] += probability
    return tuple(totals)


def has_lumpability_counterexample(kernel: Kernel, fibers: dict[int, list[int]], N: int) -> bool:
    for states in fibers.values():
        seen: set[tuple[Fraction, ...]] = set()
        for state in states:
            row = fiber_transition_row(kernel, state, N)
            if seen and row not in seen:
                return True
            seen.add(row)
    return False
