"""Exact stationary laws and rigorous EPR enclosures for small GB1 kernels."""

from fractions import Fraction

from sixbirds_glass.io.log_bounds import log_bounds
from sixbirds_glass.models.kernels import Kernel, strongly_connected, validate_kernel_rows
from sixbirds_glass.protocols.evolution import Distribution, push


def stationary_measure_exact(kernel: Kernel) -> Distribution:
    """Solve mu K=mu, sum(mu)=1 by exact elimination on an irreducible kernel."""

    validate_kernel_rows(kernel)
    if not strongly_connected(kernel):
        raise ValueError("exact stationary solver requires an irreducible kernel")
    n = kernel.state_count
    matrix = [
        [
            kernel.rows[source].get(target, Fraction(0)) - int(source == target)
            for source in range(n)
        ]
        + [Fraction(0)]
        for target in range(n - 1)
    ]
    matrix.append([Fraction(1) for _ in range(n + 1)])
    for column in range(n):
        pivot = next(row for row in range(column, n) if matrix[row][column] != 0)
        matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
        divisor = matrix[column][column]
        matrix[column] = [entry / divisor for entry in matrix[column]]
        for row in range(n):
            if row == column:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                left - factor * right
                for left, right in zip(matrix[row], matrix[column], strict=True)
            ]
    stationary = {state: matrix[state][-1] for state in range(n)}
    if any(mass <= 0 for mass in stationary.values()) or push(stationary, kernel) != stationary:
        raise ArithmeticError("exact stationary solution failed verification")
    return stationary


def epr_bounds(
    kernel: Kernel, measure: Distribution, *, terms: int = 32
) -> tuple[Fraction, Fraction]:
    """Enclose the directed edge-flux functional, including nonstationary measures.

    The finite-valued interface requires strictly positive reference masses and
    bidirected positive edge support. A one-way positive edge has infinite EPR.
    """

    validate_kernel_rows(kernel)
    if set(measure) != set(range(kernel.state_count)) or any(m <= 0 for m in measure.values()):
        raise ValueError("EPR enclosure requires a full-support probability measure")
    if sum(measure.values(), Fraction(0)) != 1:
        raise ValueError("measure must sum to one")
    lower, upper = Fraction(0), Fraction(0)
    for source, row in kernel.rows.items():
        for target, probability in row.items():
            if probability == 0:
                continue
            forward = measure[source] * probability
            reverse = measure[target] * kernel.rows[target].get(source, Fraction(0))
            if reverse == 0:
                raise ValueError("one-way support gives infinite EPR")
            lo, hi = log_bounds(forward / reverse, terms=terms)
            lower += forward * lo
            upper += forward * hi
    return lower, upper
