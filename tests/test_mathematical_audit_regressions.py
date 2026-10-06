"""Counterexamples to unchecked mathematical premises in the original implementation."""

from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction

import pytest

from sixbirds_glass.io.log_bounds import log_bounds
from sixbirds_glass.lenses.catalog import l_energy
from sixbirds_glass.models.kernels import Kernel, validate_kernel_rows
from sixbirds_glass.models.unconstrained import build_unconstrained_kernel
from sixbirds_glass.pipeline.loops import find_history_by_distribution, loop_action_score
from sixbirds_glass.pipeline.package import Continuation, Event, History, RouteTransportPackage
from sixbirds_glass.pipeline.packaging import (
    idempotence_defect,
    packaging_endomap,
    retention_error,
    uniform_prototype_rule,
)
from sixbirds_glass.pipeline.protocol_cd import ProtocolCell, protocol_relative_cd
from sixbirds_glass.pipeline.protocol_trap_exact import epr_bounds, stationary_measure_exact
from sixbirds_glass.triage.statuses import support_labels


def test_loop_must_preserve_equivalence_for_every_representative() -> None:
    """0 and 1 agree now; the purported loop fixes 0 but sends 1 to visible 2."""

    identity = Kernel(1, 3, {state: {state: Fraction(1)} for state in range(3)})
    loop = Continuation(
        "bad_loop",
        "mid",
        "mid",
        Kernel(1, 3, {0: {0: Fraction(1)}, 1: {2: Fraction(1)}, 2: {2: Fraction(1)}}),
    )
    package = RouteTransportPackage(
        interfaces=("mid",),
        projections={"mid": lambda state: int(state == 2)},
        histories={"mid": tuple(History(str(s), "mid", {s: Fraction(1)}) for s in range(3))},
        continuations={("mid", "mid"): (loop,)},
        events={"mid": (Event("visible", {1: Fraction(1)}),)},
        identity={"mid": Continuation("id", "mid", "mid", identity)},
        future_catalog={"mid": (("id", "visible"),)},
    )
    for kind in ("current", "predictive"):
        with pytest.raises(ValueError, match="does not descend"):
            loop_action_score(package, "mid", (loop,), quotient_kind=kind)


def test_idempotence_does_not_identify_retention_error() -> None:
    """A one-spin resampling kernel is idempotent but leaves its prototypes."""

    kernel = build_unconstrained_kernel(1, Fraction(1, 2))
    rule = uniform_prototype_rule()
    assert idempotence_defect(packaging_endomap(1, kernel, 1, l_energy, rule)) == 0
    assert retention_error(1, kernel, 1, l_energy, rule) == Fraction(2, 3)


def test_kernel_cannot_hide_a_source_outside_its_carrier() -> None:
    kernel = Kernel(1, 1, {0: {0: Fraction(1)}, 1: {0: Fraction(1)}})
    with pytest.raises(ValueError, match="out-of-range source"):
        validate_kernel_rows(kernel)


def test_empty_kernel_is_not_a_probability_kernel() -> None:
    with pytest.raises(ValueError, match="positive state_count"):
        validate_kernel_rows(Kernel(1, 0, {}))


def test_protocol_cannot_hide_out_of_range_mass() -> None:
    kernel = build_unconstrained_kernel(1, Fraction(1, 2))
    catalog = (ProtocolCell("bad", Fraction(1), {2: Fraction(1)}, (kernel,)),)
    with pytest.raises(ValueError, match="out-of-range state"):
        protocol_relative_cd(catalog, l_energy, 1, 1, condition_on_r=True)


def test_protocol_conditioning_labels_cannot_be_silently_split() -> None:
    kernel = build_unconstrained_kernel(1, Fraction(1, 2))
    catalog = tuple(
        ProtocolCell("same_R", Fraction(1, 2), {state: Fraction(1)}, (kernel,))
        for state in range(2)
    )
    with pytest.raises(ValueError, match="unique conditioning"):
        protocol_relative_cd(catalog, l_energy, 1, 1, condition_on_r=True)


def _one_interface_package() -> RouteTransportPackage:
    identity = Kernel(1, 2, {s: {s: Fraction(1)} for s in range(2)})
    return RouteTransportPackage(
        interfaces=("i",),
        projections={"i": lambda s: s},
        histories={"i": (History("h", "i", {0: Fraction(1)}),)},
        continuations={},
        events={"i": (Event("one", {1: Fraction(1)}),)},
        identity={"i": Continuation("id", "i", "i", identity)},
        future_catalog={"i": ()},
    )


def test_declared_identity_must_act_as_identity() -> None:
    package = _one_interface_package()
    flip = Kernel(1, 2, {0: {1: Fraction(1)}, 1: {0: Fraction(1)}})
    with pytest.raises(ValueError, match="does not fix"):
        replace(package, identity={"i": Continuation("id", "i", "i", flip)})


def test_package_history_must_live_in_its_interface_carrier() -> None:
    package = _one_interface_package()
    with pytest.raises(ValueError, match="out-of-range state"):
        replace(package, histories={"i": (History("bad", "i", {2: Fraction(1)}),)})


def test_duplicate_continuation_name_is_rejected_even_when_unused() -> None:
    package = _one_interface_package()
    with pytest.raises(ValueError, match="duplicate continuation"):
        replace(package, continuations={("i", "i"): (package.identity["i"],)})


def test_zero_entries_do_not_change_probability_support_or_history_identity() -> None:
    package = _one_interface_package()
    package = replace(
        package, histories={"i": (History("h", "i", {0: Fraction(1), 1: Fraction(0)}),)}
    )
    assert support_labels(package, "i") == frozenset({0})
    assert find_history_by_distribution(package, "i", {0: Fraction(1)}).label == "h"


@pytest.mark.parametrize("value", [Fraction(1), Fraction(2), Fraction(60), Fraction(4, 25)])
def test_rational_log_enclosures_contain_independent_high_precision_value(value: Fraction) -> None:
    lo, hi = log_bounds(value)
    with localcontext() as context:
        context.prec = 100
        actual = (Decimal(value.numerator) / Decimal(value.denominator)).ln()
        assert Decimal(lo.numerator) / Decimal(lo.denominator) <= actual
        assert actual <= Decimal(hi.numerator) / Decimal(hi.denominator)
    assert hi - lo < Fraction(1, 10**27)


def test_zero_stationary_budget_does_not_bound_transient_path_reversal() -> None:
    kernel = Kernel(
        1, 2, {0: {0: Fraction(2, 3), 1: Fraction(1, 3)}, 1: {0: Fraction(1, 3), 1: Fraction(2, 3)}}
    )
    stationary = stationary_measure_exact(kernel)
    assert stationary == {0: Fraction(1, 2), 1: Fraction(1, 2)}
    assert epr_bounds(kernel, stationary) == (0, 0)
    transient = {0: Fraction(3, 4), 1: Fraction(1, 4)}
    lower, _upper = epr_bounds(kernel, transient)
    assert lower > Fraction(1, 10)


def test_temperature_pseudo_bound_counterexample_is_certified_with_exact_intervals() -> None:
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[1] / "experiments/audit_gb1_stationary_bound.py"
    spec = importlib.util.spec_from_file_location("audit_gb1_stationary_bound", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    certificate = module.build_certificate()
    assert certificate["stationarity_verified_exact"]
    assert certificate["violation_certified_positive"]
    assert Fraction(certificate["violation_lower_bound"]) > Fraction(95, 10**9)
    assert certificate["repaired_budget"]["verified_on_example"]


@pytest.mark.parametrize("state", [0.0, True])
def test_kernel_rejects_aliases_of_integer_states(state: object) -> None:
    kernel = Kernel(1, 1, {state: {0: Fraction(1)}})
    with pytest.raises(ValueError, match="source states must be integers"):
        validate_kernel_rows(kernel)


@pytest.mark.parametrize("steps", [0, 1, 33])
def test_evolution_cannot_discard_mass_outside_carrier(steps: int) -> None:
    from sixbirds_glass.protocols.evolution import hold

    kernel = build_unconstrained_kernel(1, Fraction(1, 2))
    with pytest.raises(ValueError, match="declared carrier"):
        hold({2: Fraction(1)}, kernel, steps)


def test_stationary_cd_cannot_accept_a_transient_preparation() -> None:
    from sixbirds_glass.pipeline.cd import closure_deficit_float

    kernel = build_unconstrained_kernel(1, Fraction(1, 2))
    with pytest.raises(ValueError, match="invariant initial law"):
        closure_deficit_float(1, kernel, {0: Fraction(1)}, 1, l_energy)
