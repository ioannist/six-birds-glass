"""Exact sparse heat-bath kernels for finite spin models.

States are indexed by integer bitmask. Site numbers are 1-indexed in the
physics convention: bit ``site - 1`` is spin ``n_site``. Boundary conditions are
handled by each model's constraint predicate.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction

ConstraintPredicate = Callable[[int, int], bool]
SparseRows = dict[int, dict[int, Fraction]]


@dataclass(frozen=True)
class Kernel:
    """Sparse row-stochastic kernel over bitmask-indexed states."""

    N: int
    state_count: int
    rows: SparseRows

    def row_sum(self, state: int) -> Fraction:
        """Return the exact sum of one sparse row."""

        return sum(self.rows[state].values(), start=Fraction(0))

    def to_dense(self) -> list[list[Fraction]]:
        """Return a dense Fraction matrix, suitable for small test sizes."""

        return [
            [self.rows[state].get(target, Fraction(0)) for target in range(self.state_count)]
            for state in range(self.state_count)
        ]


def validate_kernel_rows(kernel: Kernel, *, label: str = "kernel") -> None:
    """Validate a declared exact row-stochastic kernel.

    This is certificate-path validation: every row must be present, every
    probability must be a ``Fraction``, every target must be in range, and every
    row must sum exactly to one.
    """

    for state in range(kernel.state_count):
        if state not in kernel.rows:
            raise ValueError(f"{label} lacks row for state {state}")
        row = kernel.rows[state]
        for target, probability in row.items():
            if target < 0 or target >= kernel.state_count:
                raise ValueError(f"{label} row {state} has out-of-range target {target}")
            if not isinstance(probability, Fraction):
                raise ValueError(
                    f"{label} row {state} has non-Fraction entry to target "
                    f"{target}: {probability!r}"
                )
            if probability < 0:
                raise ValueError(
                    f"{label} row {state} has negative entry to target {target}: {probability}"
                )
        row_total = sum(row.values(), start=Fraction(0))
        if row_total != Fraction(1):
            raise ValueError(f"{label} row {state} must sum to 1")


def build_heat_bath_kernel(N: int, constraint: ConstraintPredicate, c: Fraction) -> Kernel:
    """Build the random-scan heat-bath kernel for a model constraint.

    At each step a site is selected uniformly from ``1..N``. If its constraint
    is false the state holds. If true, the selected spin is resampled to 1 with
    probability ``c`` and to 0 with probability ``1 - c``.
    """

    if N < 1:
        raise ValueError("N must be positive")
    if not (Fraction(0) <= c <= Fraction(1)):
        raise ValueError("up-probability c must lie in [0, 1]")

    state_count = 1 << N
    site_weight = Fraction(1, N)
    rows: SparseRows = {}

    for config in range(state_count):
        row: dict[int, Fraction] = {}
        for site in range(1, N + 1):
            if not constraint(config, site):
                _add_entry(row, config, site_weight)
                continue

            mask = 1 << (site - 1)
            up_config = config | mask
            down_config = config & ~mask
            _add_entry(row, up_config, site_weight * c)
            _add_entry(row, down_config, site_weight * (Fraction(1) - c))
        rows[config] = row

    return Kernel(N=N, state_count=state_count, rows=rows)


def strongly_connected(kernel: Kernel) -> bool:
    """Return whether nonzero off-diagonal transitions form one directed SCC."""

    if kernel.state_count == 0:
        return True

    forward = _adjacency(kernel, reverse=False)
    reverse = _adjacency(kernel, reverse=True)
    start = 0
    return (
        len(_reachable(start, forward)) == kernel.state_count
        and len(_reachable(start, reverse)) == kernel.state_count
    )


def spin(config: int, site: int) -> bool:
    """Return spin ``n_site`` from a bitmask config, with 1-indexed sites."""

    if site < 1:
        raise ValueError("site must be 1-indexed")
    return bool(config & (1 << (site - 1)))


def energy(config: int, N: int) -> int:
    """Return ``sum_i n_i`` over the first ``N`` bits."""

    return (config & ((1 << N) - 1)).bit_count()


def product_bernoulli_stationary(N: int, epsilon: Fraction) -> dict[int, Fraction]:
    """Return ``pi_epsilon(n) = epsilon^E(n) / (1 + epsilon)^N``."""

    if epsilon <= 0:
        raise ValueError("epsilon must be positive")

    denominator = (Fraction(1) + epsilon) ** N
    return {config: (epsilon ** energy(config, N)) / denominator for config in range(1 << N)}


def _add_entry(row: dict[int, Fraction], target: int, value: Fraction) -> None:
    if value == 0:
        return
    row[target] = row.get(target, Fraction(0)) + value


def _adjacency(kernel: Kernel, *, reverse: bool) -> dict[int, list[int]]:
    adjacency: dict[int, list[int]] = {state: [] for state in range(kernel.state_count)}
    for source, row in kernel.rows.items():
        for target, probability in row.items():
            if source == target or probability == 0:
                continue
            if reverse:
                adjacency[target].append(source)
            else:
                adjacency[source].append(target)
    return adjacency


def _reachable(start: int, adjacency: dict[int, list[int]]) -> set[int]:
    seen = {start}
    stack = [start]
    while stack:
        source = stack.pop()
        for target in adjacency[source]:
            if target not in seen:
                seen.add(target)
                stack.append(target)
    return seen
