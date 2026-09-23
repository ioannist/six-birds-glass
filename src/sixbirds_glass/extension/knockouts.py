"""Six-primitive knockout panel for the GB6 glass shell."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any, Literal

from sixbirds_glass.io.rational import str_to_rational
from sixbirds_glass.lenses.catalog import l_energy
from sixbirds_glass.models.east import build_east_kernel, east_energy, east_stationary
from sixbirds_glass.models.unconstrained import build_unconstrained_kernel
from sixbirds_glass.pipeline.cd import lumpability_check_exact
from sixbirds_glass.pipeline.dimension import buyback_curve, declared_scalar_pool
from sixbirds_glass.pipeline.kovacs_hump import analyze_hump_trace, detect_kovacs_hump
from sixbirds_glass.pipeline.kovacs_witness import build_kovacs_moment_witness_from_config
from sixbirds_glass.pipeline.packaging import (
    gibbs_prototype_rule,
    idempotence_defect,
    packaging_endomap,
)
from sixbirds_glass.pipeline.protocol_trap import (
    FloatKernel,
    gibbs_measure,
    heat_bath_resample_kernel,
    lifted_kernel,
    mixed_square_affinity_from_energy,
    mixed_square_affinity_from_kernel,
)
from sixbirds_glass.protocols.evolution import Distribution, expectation, push

KnockoutKind = Literal["numeric", "capability_loss"]


@dataclass(frozen=True)
class KnockoutResult:
    """One primitive knockout row."""

    primitive: str
    kind: KnockoutKind
    baseline_value: Any
    knockout_value: Any
    degraded: bool
    threshold: Any | None
    notes: str


def knockout_p1(config: dict[str, Any]) -> KnockoutResult:
    """P1 knockout: identity kernel collapses relaxation activity."""

    N, epsilon_hi, epsilon_lo, epsilon_mid, t_w, tau_probe = _params(config)
    baseline = detect_kovacs_hump(N, epsilon_hi, epsilon_lo, epsilon_mid, t_w, tau_probe)
    identity_trace = _identity_mid_trace(N, epsilon_hi, baseline.e_eq, t_w, tau_probe)
    identity_variation = max(identity_trace) - min(identity_trace)
    baseline_variation = max(baseline.trace) - min(baseline.trace)
    analysis = analyze_hump_trace(identity_trace, baseline.e_eq)
    return KnockoutResult(
        primitive="P1",
        kind="numeric",
        baseline_value={
            "trace_variation": baseline_variation,
            "hump_found": baseline.found,
        },
        knockout_value={
            "trace_variation": identity_variation,
            "hump_found": analysis.found,
            "miss_reason": analysis.miss_reason,
        },
        degraded=baseline_variation > 0 and identity_variation == 0 and not analysis.found,
        threshold="identity trace variation must be exactly 0",
        notes="operator rewrite disabled by replacing every run kernel with the identity kernel",
    )


def knockout_p2(config: dict[str, Any]) -> KnockoutResult:
    """P2 knockout: unconstrained kernel restores exact energy lumpability."""

    N, _epsilon_hi, _epsilon_lo, epsilon_mid, _t_w, _tau_probe = _params(config)
    east = lumpability_check_exact(N, build_east_kernel(N, epsilon_mid), 1, l_energy)
    unconstrained = lumpability_check_exact(
        N, build_unconstrained_kernel(N, epsilon_mid), 1, l_energy
    )
    return KnockoutResult(
        primitive="P2",
        kind="numeric",
        baseline_value={"east_exactly_lumpable": east.is_lumpable},
        knockout_value={"unconstrained_exactly_lumpable": unconstrained.is_lumpable},
        degraded=(not east.is_lumpable) and unconstrained.is_lumpable,
        threshold="unconstrained control must be exactly lumpable under L_energy",
        notes="admissibility gating disabled by replacing East constraints with C_i == 1",
    )


def knockout_p3(config: dict[str, Any]) -> KnockoutResult:
    """P3 knockout: constant-temperature hold removes the Kovacs schedule variation."""

    N, epsilon_hi, epsilon_lo, epsilon_mid, t_w, tau_probe = _params(config)
    baseline = detect_kovacs_hump(N, epsilon_hi, epsilon_lo, epsilon_mid, t_w, tau_probe)
    constant_trace = _constant_mid_hold_trace(N, epsilon_hi, epsilon_mid, t_w + tau_probe)
    analysis = analyze_hump_trace(constant_trace, baseline.e_eq)
    return KnockoutResult(
        primitive="P3",
        kind="numeric",
        baseline_value={"hump_found": baseline.found},
        knockout_value={"hump_found": analysis.found, "miss_reason": analysis.miss_reason},
        degraded=baseline.found and not analysis.found,
        threshold="constant-epsilon replacement must fail the hump detector",
        notes=(
            "protocol/timescale adaptation disabled by replacing the schedule with one "
            "constant hold"
        ),
    )


def knockout_p4(config: dict[str, Any]) -> KnockoutResult:
    """P4 knockout: empty scalar pool makes buyback saturation unreachable."""

    witness = build_kovacs_moment_witness_from_config(config)
    epsilon_grid = tuple(str_to_rational(value) for value in config["epsilon_grid"])
    full_pool = declared_scalar_pool(witness.N, epsilon_grid)
    empty_curve = buyback_curve(
        witness.mu_k,
        witness.pi_eq,
        witness.N,
        witness.future_value_mu_k,
        witness.future_value_pi_eq,
        {},
        max_budget=2,
    )
    return KnockoutResult(
        primitive="P4",
        kind="capability_loss",
        baseline_value={"scalar_pool": tuple(full_pool)},
        knockout_value={
            "scalar_pool": (),
            "raw_budgets": tuple(empty_curve.raw_by_budget),
            "saturation_budget": empty_curve.saturation_budget,
        },
        degraded=bool(full_pool) and empty_curve.saturation_budget is None,
        threshold=None,
        notes="lens-selection/refinement catalog disabled by declaring an empty scalar pool",
    )


def knockout_p5(config: dict[str, Any]) -> KnockoutResult:
    """P5 knockout: packaging diagnostic becomes structurally unavailable."""

    N, _epsilon_hi, _epsilon_lo, epsilon_mid, _t_w, _tau_probe = _params(config)
    diagnostic_N = min(N, 8)
    kernel = build_east_kernel(diagnostic_N, epsilon_mid)
    endomap = packaging_endomap(
        diagnostic_N, kernel, 1, l_energy, gibbs_prototype_rule(diagnostic_N, epsilon_mid)
    )
    defect = idempotence_defect(endomap)
    baseline_value = {
        "delta_tau_f": defect,
        "diagnostic_N": diagnostic_N,
    }
    knockout_value = None
    return KnockoutResult(
        primitive="P5",
        kind="capability_loss",
        baseline_value=baseline_value,
        knockout_value=knockout_value,
        degraded=knockout_value is None and baseline_value["delta_tau_f"] is not None,
        threshold=None,
        notes=(
            "packaging/completion disabled; E_{tau,f}, delta_{tau,f}, and T1 strata are undefined"
        ),
    )


def knockout_p6(_config: dict[str, Any]) -> KnockoutResult:
    """P6 knockout: affinity/EPR audit accounting becomes unavailable."""

    affinity = _protocol_trap_affinity_audit()
    return KnockoutResult(
        primitive="P6",
        kind="capability_loss",
        baseline_value={"mixed_square_affinity": affinity},
        knockout_value=None,
        degraded=affinity != 0.0,
        threshold=None,
        notes="budget/ledger audit disabled; P6_drive classification is unavailable",
    )


def run_knockout_panel(config: dict[str, Any]) -> list[KnockoutResult]:
    """Run the six declared primitive knockouts."""

    return [
        knockout_p1(config),
        knockout_p2(config),
        knockout_p3(config),
        knockout_p4(config),
        knockout_p5(config),
        knockout_p6(config),
    ]


def full_loop_nondegeneracy(config: dict[str, Any]) -> dict[str, Any]:
    """Return the un-knocked-out baseline activity for all six axes."""

    rows = {row.primitive: row for row in run_knockout_panel(config)}
    _N, epsilon_hi, epsilon_lo, epsilon_mid, t_w, tau_probe = _params(config)
    schedule_epsilons = {epsilon_hi, epsilon_lo, epsilon_mid}
    return {
        "real_kernel_activity": rows["P1"].baseline_value["trace_variation"] > 0,
        "real_constraint_activity": rows["P2"].baseline_value["east_exactly_lumpable"] is False,
        "real_schedule_variation": len(schedule_epsilons) > 1 and t_w > 0 and tau_probe > 0,
        "nonempty_scalar_pool": bool(rows["P4"].baseline_value["scalar_pool"]),
        "packaging_diagnostic_available": rows["P5"].baseline_value["delta_tau_f"] >= 0,
        "affinity_audit_available": rows["P6"].baseline_value["mixed_square_affinity"] != 0.0,
    }


def _params(config: dict[str, Any]) -> tuple[int, Fraction, Fraction, Fraction, int, int]:
    word = config["protocol"]["word"]
    return (
        int(config["model"]["N"]),
        str_to_rational(word[0]["epsilon"]),
        str_to_rational(word[1]["epsilon"]),
        str_to_rational(word[2]["epsilon"]),
        int(word[1]["steps"]),
        int(word[2]["steps"]),
    )


def _identity_mid_trace(
    N: int, epsilon_hi: Fraction, e_eq: Fraction, _t_w: int, tau_probe: int
) -> list[Fraction]:
    distribution = east_stationary(N, epsilon_hi)
    value = _energy_expectation(distribution, N)
    return [value for _step in range(tau_probe + 1)] or [e_eq]


def _constant_mid_hold_trace(
    N: int, epsilon_hi: Fraction, epsilon_mid: Fraction, total_steps: int
) -> list[Fraction]:
    distribution = east_stationary(N, epsilon_hi)
    kernel = build_east_kernel(N, epsilon_mid)
    trace = [_energy_expectation(distribution, N)]
    for _step in range(total_steps):
        distribution = push(distribution, kernel)
        trace.append(_energy_expectation(distribution, N))
    return trace


def _energy_expectation(distribution: Distribution, N: int) -> Fraction:
    return expectation(distribution, lambda state: east_energy(state, N))


def _protocol_trap_affinity_audit() -> float:
    energies = {0: 0.0, 1: 1.0, 2: 2.0}
    temperatures = {0: 3.0, 1: 1.0}
    pis = {
        phase: gibbs_measure(energies, temperature) for phase, temperature in temperatures.items()
    }
    clock = FloatKernel(
        state_count=2,
        rows={
            0: {0: 0.8, 1: 0.2},
            1: {0: 0.2, 1: 0.8},
        },
    )
    alpha = 1.0 / 3.0
    kernels = {phase: heat_bath_resample_kernel(pi) for phase, pi in pis.items()}
    lifted = lifted_kernel(kernels, clock, alpha)
    energy_affinity = mixed_square_affinity_from_energy(
        energies, state=0, target_state=1, temperature=temperatures, phase=0, target_phase=1
    )
    kernel_affinity = mixed_square_affinity_from_kernel(
        lifted, state=0, target_state=1, phase=0, target_phase=1, state_count_x=3
    )
    if abs(energy_affinity - kernel_affinity) > 1e-14:
        raise ValueError("P6 affinity audit mismatch between energy and kernel routes")
    return kernel_affinity
