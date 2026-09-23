"""Exact Kovacs-hump trace detection for the East model."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from functools import cache

from sixbirds_glass.models.east import build_east_kernel, east_energy, east_stationary
from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.protocols.evolution import (
    Distribution,
    expectation,
    max_denominator_bits,
    push,
)

DEFAULT_DENOMINATOR_BIT_CAP = 4096


@dataclass(frozen=True)
class HumpResult:
    """Self-describing result of one exact Kovacs-hump check."""

    found: bool
    t_k: int | None
    t_peak: int | None
    hump_height: Fraction | None
    trace: list[Fraction]
    e_eq: Fraction
    N: int
    epsilon_hi: Fraction
    epsilon_lo: Fraction
    epsilon_mid: Fraction
    tau_hot: int
    t_w: int
    tau_probe: int
    abort_reason: str | None = None
    miss_reason: str | None = None


@dataclass(frozen=True)
class HumpTraceWithDistributions:
    """Kovacs-hump result with every mid-leg distribution retained."""

    result: HumpResult
    distributions: list[Distribution]


@dataclass(frozen=True)
class HumpAnalysis:
    """Pure trace-level hump analysis result."""

    found: bool
    t_k: int | None
    t_peak: int | None
    hump_height: Fraction | None
    miss_reason: str | None = None
    trace: list[Fraction] | None = None
    e_eq: Fraction | None = None
    abort_reason: str | None = None


def analyze_hump_trace(values: list[Fraction], e_eq: Fraction) -> HumpAnalysis:
    """Apply the exact crossing/overshoot/return hump definition to a trace."""

    if len(values) < 2:
        return HumpAnalysis(False, None, None, None, "trace has fewer than two values")
    if values[0] >= e_eq:
        return HumpAnalysis(False, None, None, None, "does not start below equilibrium")

    deviations = [value - e_eq for value in values]
    t_k = _first_crossing_index(deviations)
    if t_k is None:
        return HumpAnalysis(False, None, None, None, "no crossing")

    side = _post_crossing_side(deviations, t_k)
    if side is None:
        return HumpAnalysis(False, t_k, None, None, "no nonzero post-crossing side")
    if side < 0:
        return HumpAnalysis(False, t_k, None, None, "post-crossing side is not above equilibrium")

    magnitudes = [(t, side * deviations[t]) for t in range(t_k + 1, len(values))]
    hump_height = max(magnitude for _t, magnitude in magnitudes)
    peak_times = [t for t, magnitude in magnitudes if magnitude == hump_height]
    qualifying_peaks = [t for t in peak_times if t > t_k + 1]
    if not qualifying_peaks:
        return HumpAnalysis(False, t_k, None, hump_height, "crossed but never overshot")

    if magnitudes[-1][1] >= hump_height:
        return HumpAnalysis(False, t_k, qualifying_peaks[0], hump_height, "no return from peak")

    return HumpAnalysis(True, t_k, qualifying_peaks[0], hump_height)


def detect_kovacs_hump(
    N: int,
    epsilon_hi: Fraction,
    epsilon_lo: Fraction,
    epsilon_mid: Fraction,
    t_w: int,
    tau_probe: int,
    *,
    denominator_bit_cap: int = DEFAULT_DENOMINATOR_BIT_CAP,
) -> HumpResult:
    """Run the exact East Kovacs trace and detect a qualifying hump."""

    analysis = run_kovacs_trace_exact(
        lambda epsilon: _cached_east_kernel(N, epsilon),
        lambda epsilon: _cached_east_stationary(N, epsilon),
        lambda state: east_energy(state, N),
        epsilon_hi,
        epsilon_lo,
        epsilon_mid,
        t_w,
        tau_probe,
        denominator_bit_cap=denominator_bit_cap,
    )
    if analysis.abort_reason is not None:
        return _aborted_result(
            N,
            epsilon_hi,
            epsilon_lo,
            epsilon_mid,
            t_w,
            tau_probe,
            analysis.trace or [],
            analysis.abort_reason,
        )
    return HumpResult(
        found=analysis.found,
        t_k=analysis.t_k,
        t_peak=analysis.t_peak,
        hump_height=analysis.hump_height,
        trace=analysis.trace or [],
        e_eq=analysis.e_eq or Fraction(0),
        N=N,
        epsilon_hi=epsilon_hi,
        epsilon_lo=epsilon_lo,
        epsilon_mid=epsilon_mid,
        tau_hot=0,
        t_w=t_w,
        tau_probe=tau_probe,
        miss_reason=analysis.miss_reason,
    )


def run_kovacs_trace_exact(
    kernel_builder: Callable[[Fraction], Kernel],
    stationary_fn: Callable[[Fraction], Distribution],
    energy_fn: Callable[[int], Fraction | int],
    epsilon_hi: Fraction,
    epsilon_lo: Fraction,
    epsilon_mid: Fraction,
    t_w: int,
    tau_probe: int,
    *,
    denominator_bit_cap: int = DEFAULT_DENOMINATOR_BIT_CAP,
) -> HumpAnalysis:
    """Run a generic exact Kovacs trace and analyze its hump signature."""

    distribution = stationary_fn(epsilon_hi)
    kernel_lo = kernel_builder(epsilon_lo)
    for step in range(1, t_w + 1):
        distribution = push(distribution, kernel_lo)
        abort_reason = _denominator_abort_reason(distribution, denominator_bit_cap, "quench", step)
        if abort_reason is not None:
            return HumpAnalysis(
                False,
                None,
                None,
                None,
                trace=[],
                e_eq=_generic_expectation(stationary_fn(epsilon_mid), energy_fn),
                abort_reason=abort_reason,
            )

    e_eq = _generic_expectation(stationary_fn(epsilon_mid), energy_fn)
    trace = [_generic_expectation(distribution, energy_fn)]
    kernel_mid = kernel_builder(epsilon_mid)
    for step in range(1, tau_probe + 1):
        distribution = push(distribution, kernel_mid)
        abort_reason = _denominator_abort_reason(distribution, denominator_bit_cap, "probe", step)
        if abort_reason is not None:
            return HumpAnalysis(
                False,
                None,
                None,
                None,
                trace=trace,
                e_eq=e_eq,
                abort_reason=abort_reason,
            )
        trace.append(_generic_expectation(distribution, energy_fn))

    analysis = analyze_hump_trace(trace, e_eq)
    return HumpAnalysis(
        analysis.found,
        analysis.t_k,
        analysis.t_peak,
        analysis.hump_height,
        analysis.miss_reason,
        trace=trace,
        e_eq=e_eq,
    )


def detect_kovacs_hump_with_distributions(
    N: int,
    epsilon_hi: Fraction,
    epsilon_lo: Fraction,
    epsilon_mid: Fraction,
    t_w: int,
    tau_probe: int,
    *,
    denominator_bit_cap: int = DEFAULT_DENOMINATOR_BIT_CAP,
) -> HumpTraceWithDistributions:
    """Run the exact East Kovacs trace and retain mid-leg distributions.

    The returned ``distributions`` list is aligned with ``result.trace``:
    index ``0`` is the distribution at the up-jump before any ``epsilon_mid``
    step, and index ``t`` for ``t >= 1`` is after ``t`` mid-leg steps.
    """

    distribution = _cached_east_stationary(N, epsilon_hi)
    kernel_lo = _cached_east_kernel(N, epsilon_lo)
    for step in range(1, t_w + 1):
        distribution = push(distribution, kernel_lo)
        abort_reason = _denominator_abort_reason(distribution, denominator_bit_cap, "quench", step)
        if abort_reason is not None:
            result = _aborted_result(
                N, epsilon_hi, epsilon_lo, epsilon_mid, t_w, tau_probe, [], abort_reason
            )
            return HumpTraceWithDistributions(result=result, distributions=[])

    e_eq = _equilibrium_energy(N, epsilon_mid)
    trace = [_energy_expectation(distribution, N)]
    distributions = [dict(distribution)]

    kernel_mid = _cached_east_kernel(N, epsilon_mid)
    for step in range(1, tau_probe + 1):
        distribution = push(distribution, kernel_mid)
        abort_reason = _denominator_abort_reason(distribution, denominator_bit_cap, "probe", step)
        if abort_reason is not None:
            result = _aborted_result(
                N, epsilon_hi, epsilon_lo, epsilon_mid, t_w, tau_probe, trace, abort_reason
            )
            return HumpTraceWithDistributions(result=result, distributions=distributions)
        trace.append(_energy_expectation(distribution, N))
        distributions.append(dict(distribution))

    analysis = analyze_hump_trace(trace, e_eq)
    result = HumpResult(
        found=analysis.found,
        t_k=analysis.t_k,
        t_peak=analysis.t_peak,
        hump_height=analysis.hump_height,
        trace=trace,
        e_eq=e_eq,
        N=N,
        epsilon_hi=epsilon_hi,
        epsilon_lo=epsilon_lo,
        epsilon_mid=epsilon_mid,
        tau_hot=0,
        t_w=t_w,
        tau_probe=tau_probe,
        miss_reason=analysis.miss_reason,
    )
    return HumpTraceWithDistributions(result=result, distributions=distributions)


def _first_crossing_index(deviations: list[Fraction]) -> int | None:
    for index in range(len(deviations) - 1):
        if deviations[index] == 0:
            return index
        if deviations[index] * deviations[index + 1] < 0:
            return index
    return None


def _post_crossing_side(deviations: list[Fraction], t_k: int) -> int | None:
    for value in deviations[t_k + 1 :]:
        if value > 0:
            return 1
        if value < 0:
            return -1
    return None


def _equilibrium_energy(N: int, epsilon: Fraction) -> Fraction:
    return _energy_expectation(_cached_east_stationary(N, epsilon), N)


def _energy_expectation(distribution: Distribution, N: int) -> Fraction:
    return expectation(distribution, lambda state: east_energy(state, N))


def _generic_expectation(
    distribution: Distribution, energy_fn: Callable[[int], Fraction | int]
) -> Fraction:
    return expectation(distribution, energy_fn)


@cache
def _cached_east_kernel(N: int, epsilon: Fraction) -> Kernel:
    return build_east_kernel(N, epsilon)


@cache
def _cached_east_stationary(N: int, epsilon: Fraction) -> Distribution:
    return east_stationary(N, epsilon)


def _denominator_abort_reason(
    distribution: Distribution, cap: int, leg_name: str, step: int
) -> str | None:
    observed = max_denominator_bits(distribution)
    if observed > cap:
        return f"max_denominator_bits={observed} exceeded cap={cap} during {leg_name} step {step}"
    return None


def _aborted_result(
    N: int,
    epsilon_hi: Fraction,
    epsilon_lo: Fraction,
    epsilon_mid: Fraction,
    t_w: int,
    tau_probe: int,
    trace: list[Fraction],
    abort_reason: str,
) -> HumpResult:
    return HumpResult(
        found=False,
        t_k=None,
        t_peak=None,
        hump_height=None,
        trace=trace,
        e_eq=_equilibrium_energy(N, epsilon_mid),
        N=N,
        epsilon_hi=epsilon_hi,
        epsilon_lo=epsilon_lo,
        epsilon_mid=epsilon_mid,
        tau_hot=0,
        t_w=t_w,
        tau_probe=tau_probe,
        abort_reason=abort_reason,
    )
