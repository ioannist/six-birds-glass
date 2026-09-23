"""Protocol-trap EPR helpers for the GB1 finite demonstration."""

from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import product

FloatMeasure = dict[int, float]
FloatRows = dict[int, dict[int, float]]


@dataclass(frozen=True)
class FloatKernel:
    """Small finite Markov kernel with float probabilities."""

    state_count: int
    rows: FloatRows


def gibbs_measure(energies: dict[int, float], temperature: float) -> FloatMeasure:
    """Return the finite Gibbs law proportional to ``exp(-E/T)``."""

    if temperature <= 0:
        raise ValueError("temperature must be positive")
    weights = {state: math.exp(-energy / temperature) for state, energy in energies.items()}
    total = sum(weights.values())
    return {state: weight / total for state, weight in weights.items()}


def heat_bath_resample_kernel(pi: FloatMeasure) -> FloatKernel:
    """Return the full-resampling heat-bath kernel reversible to ``pi``."""

    state_count = len(pi)
    return FloatKernel(
        state_count=state_count, rows={state: dict(pi) for state in range(state_count)}
    )


def kl_divergence(p: FloatMeasure, q: FloatMeasure) -> float:
    """Return ``KL(p || q)`` with natural logarithms."""

    value = 0.0
    for state, probability in p.items():
        if probability <= 0.0:
            continue
        q_probability = q.get(state, 0.0)
        if q_probability <= 0.0:
            return math.inf
        value += probability * (math.log(probability) - math.log(q_probability))
    return value


def epr(kernel: FloatKernel, measure: FloatMeasure) -> float:
    """Return the directed edge-flux entropy-production functional."""

    value = 0.0
    for source, row in kernel.rows.items():
        source_mass = measure.get(source, 0.0)
        if source_mass <= 0.0:
            continue
        for target, probability in row.items():
            forward = source_mass * probability
            if forward <= 0.0:
                continue
            reverse = measure.get(target, 0.0) * kernel.rows[target].get(source, 0.0)
            if reverse <= 0.0:
                return math.inf
            value += forward * (math.log(forward) - math.log(reverse))
    return value


def pseudo_epr_boundary_term(
    pis: dict[int, FloatMeasure],
    s: FloatMeasure,
    S: FloatKernel,
    alpha: float,
) -> float:
    """Return ``alpha * (clock EPR + phase-switch KL boundary term)``."""

    boundary = 0.0
    for phase, row in S.rows.items():
        for target_phase, probability in row.items():
            if phase == target_phase or probability <= 0.0:
                continue
            boundary += s[phase] * probability * kl_divergence(pis[phase], pis[target_phase])
    return alpha * (epr(S, s) + boundary)


def lifted_kernel(Ks: dict[int, FloatKernel], S: FloatKernel, alpha: float) -> FloatKernel:
    """Build the random-scan lifted kernel on ``X x Phi``."""

    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must lie in (0, 1)")
    phases = tuple(sorted(Ks))
    state_count_x = next(iter(Ks.values())).state_count
    lifted_state_count = state_count_x * len(phases)
    rows: FloatRows = {}
    for phase in phases:
        for state in range(state_count_x):
            source = pack_state(state, phase, state_count_x)
            row: dict[int, float] = {}
            for target_phase, clock_probability in S.rows[phase].items():
                target = pack_state(state, target_phase, state_count_x)
                row[target] = row.get(target, 0.0) + alpha * clock_probability
            for target_state, state_probability in Ks[phase].rows[state].items():
                target = pack_state(target_state, phase, state_count_x)
                row[target] = row.get(target, 0.0) + (1.0 - alpha) * state_probability
            rows[source] = row
    return FloatKernel(state_count=lifted_state_count, rows=rows)


def stationary_distribution(
    kernel: FloatKernel, *, tolerance: float = 1e-14, max_steps: int = 100_000
) -> FloatMeasure:
    """Compute the stationary law by power iteration."""

    distribution = {state: 1.0 / kernel.state_count for state in range(kernel.state_count)}
    for _step in range(max_steps):
        next_distribution = _push(distribution, kernel)
        delta = sum(
            abs(next_distribution[state] - distribution[state])
            for state in range(kernel.state_count)
        )
        distribution = next_distribution
        if delta < tolerance:
            return distribution
    raise RuntimeError("stationary power iteration did not converge")


def path_kl_enumerate(kernel: FloatKernel, initial: FloatMeasure, horizon: int) -> float:
    """Exhaustively compute path-space KL against time reversal for small horizons."""

    if horizon < 1:
        raise ValueError("horizon must be positive")
    value = 0.0
    for path in product(range(kernel.state_count), repeat=horizon + 1):
        forward = initial.get(path[0], 0.0)
        reverse = initial.get(path[-1], 0.0)
        for index in range(horizon):
            forward *= kernel.rows[path[index]].get(path[index + 1], 0.0)
            reverse *= kernel.rows[path[index + 1]].get(path[index], 0.0)
        if forward <= 0.0:
            continue
        if reverse <= 0.0:
            return math.inf
        value += forward * (math.log(forward) - math.log(reverse))
    return value


def pack_state(state: int, phase: int, state_count_x: int) -> int:
    """Pack ``(state, phase)`` into one integer."""

    return state + phase * state_count_x


def unpack_state(lifted_state: int, state_count_x: int) -> tuple[int, int]:
    """Unpack one lifted integer state into ``(state, phase)``."""

    return lifted_state % state_count_x, lifted_state // state_count_x


def candidate_measure(pis: dict[int, FloatMeasure], s: FloatMeasure) -> FloatMeasure:
    """Return ``hat_mu(x, phi) = pi_phi(x) * s(phi)``."""

    state_count_x = len(next(iter(pis.values())))
    return {
        pack_state(state, phase, state_count_x): s[phase] * probability
        for phase, pi in pis.items()
        for state, probability in pi.items()
    }


def mixed_square_affinity_from_energy(
    energies: dict[int, float],
    state: int,
    target_state: int,
    temperature: dict[int, float],
    phase: int,
    target_phase: int,
) -> float:
    """Return ``Delta E * (1/T_phase - 1/T_target_phase)``."""

    delta_e = energies[target_state] - energies[state]
    return delta_e * (1.0 / temperature[phase] - 1.0 / temperature[target_phase])


def mixed_square_affinity_from_kernel(
    kernel: FloatKernel,
    *,
    state: int,
    target_state: int,
    phase: int,
    target_phase: int,
    state_count_x: int,
) -> float:
    """Compute the same mixed-square affinity by summing log transition ratios."""

    cycle = (
        pack_state(state, phase, state_count_x),
        pack_state(state, target_phase, state_count_x),
        pack_state(target_state, target_phase, state_count_x),
        pack_state(target_state, phase, state_count_x),
    )
    value = 0.0
    for source, target in zip(cycle, (*cycle[1:], cycle[0]), strict=True):
        forward = kernel.rows[source][target]
        reverse = kernel.rows[target][source]
        value += math.log(forward) - math.log(reverse)
    return value


def _push(distribution: FloatMeasure, kernel: FloatKernel) -> FloatMeasure:
    result = {state: 0.0 for state in range(kernel.state_count)}
    for source, mass in distribution.items():
        if mass == 0.0:
            continue
        for target, probability in kernel.rows[source].items():
            result[target] += mass * probability
    return result
