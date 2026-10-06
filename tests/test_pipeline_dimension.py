from fractions import Fraction
from pathlib import Path

import pytest

from sixbirds_glass.io.config import load_config
from sixbirds_glass.io.rational import str_to_rational
from sixbirds_glass.pipeline.dimension import (
    buyback_curve,
    declared_scalar_pool,
    fiber_histogram,
    max_fiber_size,
    two_point_squared_error,
)
from sixbirds_glass.pipeline.kovacs_witness import (
    KovacsMomentWitness,
    build_kovacs_moment_witness_from_config,
)
from sixbirds_glass.pipeline.quotients import current_quotient, predictive_quotient

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def frozen_witness() -> KovacsMomentWitness:
    config = load_config(Path("configs/kovacs_hump_default.json"))
    return build_kovacs_moment_witness_from_config(config)


def test_real_kovacs_witness_max_fiber_is_two(frozen_witness: KovacsMomentWitness) -> None:
    histogram = fiber_histogram(frozen_witness.package, "mid")
    current = current_quotient(frozen_witness.package, "mid")
    predictive = predictive_quotient(frozen_witness.package, "mid")

    assert max_fiber_size(frozen_witness.package, "mid") == 2
    assert sorted(histogram.values()) == [2]
    assert sum(histogram.values()) == len(predictive) == 2
    assert len(current) == 1


def test_two_point_squared_error_formula() -> None:
    assert two_point_squared_error(Fraction(3), Fraction(5), same_group=False) == Fraction(0)
    assert two_point_squared_error(Fraction(3), Fraction(5), same_group=True) == Fraction(2)


def test_real_kovacs_buyback_curve_is_bruteforce_consistent(
    frozen_witness: KovacsMomentWitness,
) -> None:
    config = load_config(Path("configs/kovacs_hump_default.json"))
    epsilon_grid = tuple(str_to_rational(value) for value in config["epsilon_grid"])
    pool = declared_scalar_pool(frozen_witness.N, epsilon_grid)

    curve = buyback_curve(
        frozen_witness.mu_k,
        frozen_witness.pi_eq,
        frozen_witness.N,
        frozen_witness.future_value_mu_k,
        frozen_witness.future_value_pi_eq,
        pool,
        max_budget=2,
    )

    assert curve.envelope[0] > 0
    assert all(
        curve.envelope[budget] <= curve.envelope[budget - 1]
        for budget in range(1, len(curve.envelope))
    )
    for budget, rows in curve.raw_by_budget.items():
        raw_min = min(row["loss"] for row in rows)
        expected = (
            raw_min
            if budget == 0
            else min(raw_min, *(curve.envelope[previous] for previous in range(budget)))
        )
        assert curve.envelope[budget] == expected
    if curve.saturation_budget is not None:
        assert curve.envelope[curve.saturation_budget] == 0
