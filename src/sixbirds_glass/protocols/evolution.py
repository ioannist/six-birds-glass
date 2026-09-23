"""Exact rational distribution evolution."""

from __future__ import annotations

from collections.abc import Callable
from fractions import Fraction

from sixbirds_glass.models.kernels import Kernel

Distribution = dict[int, Fraction]
Observable = Callable[[int], Fraction | int]

DENSE_POWER_THRESHOLD = 32


def dirac(state: int) -> Distribution:
    """Return the point mass at ``state``."""

    return {state: Fraction(1)}


def push(distribution: Distribution, kernel: Kernel) -> Distribution:
    """Push a sparse distribution forward by one exact kernel step."""

    result: Distribution = {}
    for source, mass in distribution.items():
        if mass == 0:
            continue
        for target, probability in kernel.rows[source].items():
            value = mass * probability
            if value != 0:
                result[target] = result.get(target, Fraction(0)) + value
    return _drop_zeros(result)


def hold(distribution: Distribution, kernel: Kernel, steps: int) -> Distribution:
    """Apply ``steps`` repetitions of ``kernel`` to ``distribution``.

    Sequential sparse pushes are cheap for short holds. For longer holds,
    ``steps > DENSE_POWER_THRESHOLD``, we use dense exact exponentiation by
    squaring; the threshold is a performance heuristic, not a semantic constant.
    """

    if steps < 0:
        raise ValueError("steps must be non-negative")
    if steps == 0:
        return _drop_zeros(dict(distribution))
    if steps <= DENSE_POWER_THRESHOLD:
        result = dict(distribution)
        for _ in range(steps):
            result = push(result, kernel)
        return result
    return _hold_dense_power(distribution, kernel, steps)


def max_denominator_bits(distribution: Distribution) -> int:
    """Return the largest denominator bit length in a distribution."""

    if not distribution:
        return 0
    return max(value.denominator.bit_length() for value in distribution.values())


def expectation(distribution: Distribution, observable: Observable) -> Fraction:
    """Return the exact expectation of an observable under a distribution."""

    return sum(
        (mass * Fraction(observable(state)) for state, mass in distribution.items()),
        start=Fraction(0),
    )


def _hold_dense_power(distribution: Distribution, kernel: Kernel, steps: int) -> Distribution:
    matrix = kernel.to_dense()
    vector = [distribution.get(state, Fraction(0)) for state in range(kernel.state_count)]

    exponent = steps
    power = matrix
    while exponent:
        if exponent & 1:
            vector = _dense_vector_matrix_multiply(vector, power)
        exponent >>= 1
        if exponent:
            power = _dense_matrix_multiply(power, power)

    return {state: probability for state, probability in enumerate(vector) if probability != 0}


def _dense_vector_matrix_multiply(
    vector: list[Fraction], matrix: list[list[Fraction]]
) -> list[Fraction]:
    size = len(vector)
    result = [Fraction(0) for _ in range(size)]
    for source, mass in enumerate(vector):
        if mass == 0:
            continue
        row = matrix[source]
        for target, probability in enumerate(row):
            if probability != 0:
                result[target] += mass * probability
    return result


def _dense_matrix_multiply(
    left: list[list[Fraction]], right: list[list[Fraction]]
) -> list[list[Fraction]]:
    size = len(left)
    result = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    for row_index, left_row in enumerate(left):
        result_row = result[row_index]
        for middle, left_value in enumerate(left_row):
            if left_value == 0:
                continue
            right_row = right[middle]
            for column, right_value in enumerate(right_row):
                if right_value != 0:
                    result_row[column] += left_value * right_value
    return result


def _drop_zeros(distribution: Distribution) -> Distribution:
    return {state: mass for state, mass in distribution.items() if mass != 0}
