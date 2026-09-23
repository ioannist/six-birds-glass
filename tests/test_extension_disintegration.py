from fractions import Fraction

from sixbirds_glass.extension.disintegration import (
    disintegration_gap,
    stratum_conditioned_pressure,
)
from sixbirds_glass.extension.pressure import pressure_ladder
from sixbirds_glass.lenses.catalog import l_energy
from sixbirds_glass.models.east import build_east_kernel, east_stationary
from sixbirds_glass.pipeline.packaging import coarse_grain, fiber_partition


def test_disintegration_gap_computes_for_small_east_case() -> None:
    N = 4
    epsilon = Fraction(2, 5)
    s = 0.2
    n_values = range(1, 5)
    kernel = build_east_kernel(N, epsilon)
    fibers = fiber_partition(N, l_energy)
    stationary = east_stationary(N, epsilon)
    weights = coarse_grain(stationary, fibers)
    base = pressure_ladder(kernel, l_energy, N, s, n_values)
    stratum_pressures = {
        label: stratum_conditioned_pressure(kernel, l_energy, N, s, frozenset(states), n_values)
        for label, states in fibers.items()
    }

    gap = disintegration_gap(base[max(base)], stratum_pressures, weights)

    assert isinstance(gap, float)
