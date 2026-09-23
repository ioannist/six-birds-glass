"""Exact Kovacs-moment witness construction."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import cache
from typing import Any

from sixbirds_glass.io.rational import str_to_rational
from sixbirds_glass.models.east import build_east_kernel, east_energy, east_stationary
from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.pipeline.kovacs_hump import (
    detect_kovacs_hump_with_distributions,
)
from sixbirds_glass.pipeline.package import Continuation, Event, History, RouteTransportPackage
from sixbirds_glass.pipeline.signatures import current_signature, future_signature
from sixbirds_glass.protocols.evolution import Distribution, dirac, expectation, hold

DEFAULT_PROBE_STEPS = 5


@dataclass(frozen=True)
class KovacsMomentWitness:
    """Computed exact data for the Kovacs-moment witness pair."""

    N: int
    epsilon_hi: Fraction
    epsilon_lo: Fraction
    epsilon_mid: Fraction
    t_w: int
    tau_probe: int
    t_k: int
    theta: Fraction
    mu_t: Distribution
    mu_t_plus_1: Distribution
    mu_k: Distribution
    pi_eq: Distribution
    e_eq: Fraction
    probe_steps: int
    package: RouteTransportPackage
    current_value: Fraction
    future_value_mu_k: Fraction
    future_value_pi_eq: Fraction
    separating_gap: Fraction


def solve_randomized_stop_theta(
    value_at_t: Fraction, value_at_t_plus_1: Fraction, target: Fraction
) -> Fraction:
    """Solve ``theta*a + (1-theta)*b = target`` exactly under bracketing."""

    low = min(value_at_t, value_at_t_plus_1)
    high = max(value_at_t, value_at_t_plus_1)
    if target < low or target > high or value_at_t == value_at_t_plus_1:
        raise ValueError(
            "target is not bracketed by randomized-stop endpoints: "
            f"value_at_t={value_at_t}, value_at_t_plus_1={value_at_t_plus_1}, "
            f"target={target}"
        )
    theta = (target - value_at_t_plus_1) / (value_at_t - value_at_t_plus_1)
    if not Fraction(0) <= theta <= Fraction(1):
        raise ValueError(f"solved theta={theta} is outside [0, 1]")
    return theta


def build_kovacs_moment_history(
    mu_t: Distribution, mu_t_plus_1: Distribution, theta: Fraction
) -> Distribution:
    """Return ``theta*mu_t + (1-theta)*mu_t_plus_1`` as an exact distribution."""

    if not Fraction(0) <= theta <= Fraction(1):
        raise ValueError(f"theta must lie in [0, 1]; got {theta}")
    result: Distribution = {}
    for state in set(mu_t) | set(mu_t_plus_1):
        value = theta * mu_t.get(state, Fraction(0)) + (Fraction(1) - theta) * mu_t_plus_1.get(
            state, Fraction(0)
        )
        if value != 0:
            result[state] = value
    total = sum(result.values(), start=Fraction(0))
    if total != Fraction(1):
        raise ValueError(f"Kovacs moment history must sum to 1; got {total}")
    if any(value < 0 for value in result.values()):
        raise ValueError("Kovacs moment history has a negative entry")
    return result


def build_kovacs_witness_package(
    N: int,
    epsilon_mid: Fraction,
    mu_k: Distribution,
    pi_eq: Distribution,
    *,
    probe_steps: int = DEFAULT_PROBE_STEPS,
) -> RouteTransportPackage:
    """Assemble the two-history Kovacs-moment witness package."""

    state_count = 1 << N
    return RouteTransportPackage(
        interfaces=("mid", "probe"),
        projections={"mid": lambda state: state, "probe": lambda state: state},
        histories={
            "mid": (
                History("mu_K", "mid", mu_k),
                History("pi_eq", "mid", pi_eq),
            ),
            "probe": (),
        },
        continuations={
            ("mid", "probe"): (
                Continuation(
                    "probe_hold",
                    "mid",
                    "probe",
                    _powered_east_kernel(N, epsilon_mid, probe_steps),
                ),
            )
        },
        events={
            "mid": (_energy_event(N),),
            "probe": (_energy_event(N),),
        },
        identity={
            "mid": Continuation("id_mid", "mid", "mid", _identity_kernel(N, state_count)),
            "probe": Continuation("id_probe", "probe", "probe", _identity_kernel(N, state_count)),
        },
        future_catalog={"mid": (("probe_hold", "w_E"),), "probe": ()},
    )


def build_kovacs_moment_witness_from_config(
    config: dict[str, Any], *, probe_steps: int = DEFAULT_PROBE_STEPS
) -> KovacsMomentWitness:
    """Reconstruct the frozen Kovacs run and build the exact witness package."""

    N, epsilon_hi, epsilon_lo, epsilon_mid, t_w, tau_probe = _kovacs_params_from_config(config)
    return build_kovacs_moment_witness(
        N, epsilon_hi, epsilon_lo, epsilon_mid, t_w, tau_probe, probe_steps=probe_steps
    )


@cache
def build_kovacs_moment_witness(
    N: int,
    epsilon_hi: Fraction,
    epsilon_lo: Fraction,
    epsilon_mid: Fraction,
    t_w: int,
    tau_probe: int,
    *,
    probe_steps: int = DEFAULT_PROBE_STEPS,
) -> KovacsMomentWitness:
    """Build and cache the exact Kovacs-moment witness for hashable run parameters."""

    trace = detect_kovacs_hump_with_distributions(
        N, epsilon_hi, epsilon_lo, epsilon_mid, t_w, tau_probe
    )
    result = trace.result
    if not result.found or result.t_k is None:
        raise ValueError(f"frozen Kovacs run did not produce a crossing hump: {result!r}")

    t_k = result.t_k
    if t_k + 1 >= len(trace.distributions):
        raise ValueError("Kovacs crossing does not have a t_K+1 distribution")
    mu_t = trace.distributions[t_k]
    mu_t_plus_1 = trace.distributions[t_k + 1]
    value_at_t = result.trace[t_k]
    value_at_t_plus_1 = result.trace[t_k + 1]
    theta = solve_randomized_stop_theta(value_at_t, value_at_t_plus_1, result.e_eq)
    mu_k = build_kovacs_moment_history(mu_t, mu_t_plus_1, theta)
    current_value = _energy_expectation(mu_k, N)
    if current_value != result.e_eq:
        raise ValueError(f"tuned Kovacs history has energy {current_value}, expected {result.e_eq}")

    pi_eq = east_stationary(N, epsilon_mid)
    package = build_kovacs_witness_package(N, epsilon_mid, mu_k, pi_eq, probe_steps=probe_steps)
    mu_history = package.history_by_label("mid", "mu_K")
    pi_history = package.history_by_label("mid", "pi_eq")
    mu_current = current_signature(package, mu_history)
    pi_current = current_signature(package, pi_history)
    if mu_current != pi_current:
        raise ValueError(f"current signatures differ: {mu_current!r} != {pi_current!r}")
    mu_future = future_signature(package, mu_history)
    pi_future = future_signature(package, pi_history)
    if mu_future == pi_future:
        raise ValueError("Kovacs witness future signatures did not separate")

    gap = abs(mu_future[0] - pi_future[0])
    return KovacsMomentWitness(
        N=N,
        epsilon_hi=epsilon_hi,
        epsilon_lo=epsilon_lo,
        epsilon_mid=epsilon_mid,
        t_w=t_w,
        tau_probe=tau_probe,
        t_k=t_k,
        theta=theta,
        mu_t=mu_t,
        mu_t_plus_1=mu_t_plus_1,
        mu_k=mu_k,
        pi_eq=pi_eq,
        e_eq=result.e_eq,
        probe_steps=probe_steps,
        package=package,
        current_value=mu_current[0],
        future_value_mu_k=mu_future[0],
        future_value_pi_eq=pi_future[0],
        separating_gap=gap,
    )


def _kovacs_params_from_config(
    config: dict[str, Any],
) -> tuple[int, Fraction, Fraction, Fraction, int, int]:
    model = config["model"]
    protocol = config["protocol"]
    word = protocol["word"]
    N = int(model["N"])
    epsilon_hi = str_to_rational(word[0]["epsilon"])
    epsilon_lo = str_to_rational(word[1]["epsilon"])
    epsilon_mid = str_to_rational(word[2]["epsilon"])
    t_w = int(word[1]["steps"])
    tau_probe = int(word[2]["steps"])
    return (N, epsilon_hi, epsilon_lo, epsilon_mid, t_w, tau_probe)


def _energy_event(N: int) -> Event:
    return Event("w_E", {state: Fraction(east_energy(state, N)) for state in range(1 << N)})


def _energy_expectation(distribution: Distribution, N: int) -> Fraction:
    return expectation(distribution, lambda state: east_energy(state, N))


def _powered_east_kernel(N: int, epsilon: Fraction, steps: int) -> Kernel:
    if steps < 1:
        raise ValueError("probe_steps must be at least 1")
    base = build_east_kernel(N, epsilon)
    state_count = 1 << N
    return Kernel(
        N=N,
        state_count=state_count,
        rows={state: hold(dirac(state), base, steps) for state in range(state_count)},
    )


def _identity_kernel(N: int, state_count: int) -> Kernel:
    return Kernel(
        N=N,
        state_count=state_count,
        rows={state: {state: Fraction(1)} for state in range(state_count)},
    )
