"""Pressure certificates against analytic controls and a conditioning counterexample."""

import importlib.util
import json
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path

import pytest

from sixbirds_glass.extension.disintegration import conditional_pressure_bounds
from sixbirds_glass.extension.pressure import pressure_bounds
from sixbirds_glass.io.exp_bounds import exp_bounds
from sixbirds_glass.models.kernels import Kernel


def _decimal(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


@pytest.mark.parametrize("x", [Fraction(0), Fraction(3, 5), Fraction(-8, 5), Fraction(20, 7)])
def test_exp_intervals_enclose_independent_high_precision_evaluation(x: Fraction) -> None:
    lower, upper = exp_bounds(x)
    with localcontext() as context:
        context.prec = 100
        exact = _decimal(x).exp()
        assert _decimal(lower) <= exact <= _decimal(upper)
    assert upper - lower < Fraction(1, 10**27)


def test_limiting_pressure_bound_matches_independent_rank_one_formula() -> None:
    # Every row resets to Bernoulli(1/3); L is rank one, so its nonzero
    # eigenvalue is 2/3 + exp(s)/3 independently of the comparison algorithm.
    kernel = Kernel(
        N=1,
        state_count=2,
        rows={
            0: {0: Fraction(2, 3), 1: Fraction(1, 3)},
            1: {0: Fraction(2, 3), 1: Fraction(1, 3)},
        },
    )
    certificate = pressure_bounds(kernel, lambda state, _: state, 1, Fraction(1, 5))
    with localcontext() as context:
        context.prec = 100
        expected = (Decimal(2) / 3 + (Decimal(1) / 5).exp() / 3).ln()
        assert _decimal(certificate.pressure_lower) <= expected
        assert expected <= _decimal(certificate.pressure_upper)
    assert certificate.pressure_upper - certificate.pressure_lower < Fraction(1, 10**20)


def test_comparison_vector_must_be_positive_on_the_actual_carrier() -> None:
    kernel = Kernel(N=1, state_count=2, rows={0: {0: Fraction(1)}, 1: {1: Fraction(1)}})
    with pytest.raises(ValueError, match="strictly positive"):
        pressure_bounds(
            kernel, lambda state, _: state, 1, Fraction(0), vector=(Fraction(0), Fraction(1))
        )


def test_initial_conditioning_is_not_killing_at_fiber_exit() -> None:
    # Resampling erases the initial condition. Every true conditional profile
    # is zero at zero tilt; killing would instead keep a diagonal entry 1/2.
    kernel = Kernel(
        N=1,
        state_count=2,
        rows={
            0: {0: Fraction(1, 2), 1: Fraction(1, 2)},
            1: {0: Fraction(1, 2), 1: Fraction(1, 2)},
        },
    )
    base, strata, gap = conditional_pressure_bounds(
        kernel,
        {0: Fraction(1, 2), 1: Fraction(1, 2)},
        lambda state, _: state,
        lambda state, _: state,
        1,
        Fraction(0),
        2,
    )
    assert base == (0, 0) and set(strata.values()) == {(0, 0)} and gap == (0, 0)


def test_n8_certificate_replay_rejects_false_limiting_and_finite_gaps() -> None:
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location(
        "pressure_audit", root / "experiments/audit_gt6_pressure.py"
    )
    assert spec is not None and spec.loader is not None
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    certificate = json.loads((root / "math/gt6_pressure_certificate.json").read_text())
    audit.verify_certificate(certificate)
    for field in ("limit", "finite", "killed"):
        changed = deepcopy(certificate)
        if field == "limit":
            changed["conditional_infinite_time_gap"] = "1"
        elif field == "finite":
            changed["finite_time_conditional_contrast"][0]["jensen_gap_interval"][0] = "1"
        else:
            changed["killed_process_limiting_diagnostic"]["contrast_interval"][0] = "1"
        with pytest.raises(ValueError, match="exact source replay"):
            audit.verify_certificate(changed)
