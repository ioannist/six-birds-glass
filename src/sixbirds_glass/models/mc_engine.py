"""Float64 Monte Carlo diagnostics for sampled East/FA trajectories.

This module intentionally leaves the certificate path: it approximates the
exact discrete-time dynamics by pseudorandom direct simulation, using float64
readouts and frozen seeds. Do not use this module for theorem-graded
certificates. It is only for ``run_only_readout`` /
``evidence_type: monte_carlo_frozen_seeds`` artifacts.
"""

from __future__ import annotations

from collections.abc import Callable
from fractions import Fraction
from typing import Literal, cast

import numpy as np

from sixbirds_glass.models.east import (
    build_east_kernel,
    east_energy,
    east_stationary,
)
from sixbirds_glass.models.fa import build_fa_kernel, fa_energy, fa_stationary
from sixbirds_glass.protocols.evolution import Distribution, expectation, push

Family = Literal["east", "fa"]


def east_constraint_batch(configs: np.ndarray, sites: np.ndarray, N: int) -> np.ndarray:
    """Vectorized East constraint with wall ``n_0 = 1``."""

    configs = _as_uint32_configs(configs)
    sites = _as_site_array(sites, configs.shape[0], N)
    constrained = sites == 1
    other = ~constrained
    if np.any(other):
        shifts = sites[other] - 2
        constrained[other] = ((configs[other] >> shifts) & np.uint32(1)) == np.uint32(1)
    return cast(np.ndarray, constrained)


def fa_constraint_batch(configs: np.ndarray, sites: np.ndarray, N: int) -> np.ndarray:
    """Vectorized FA-1f constraint with wall ``n_0 = 1`` and ``n_{N+1} = 0``."""

    configs = _as_uint32_configs(configs)
    sites = _as_site_array(sites, configs.shape[0], N)
    constrained = sites == 1

    left = sites > 1
    if np.any(left):
        left_shifts = sites[left] - 2
        constrained[left] |= ((configs[left] >> left_shifts) & np.uint32(1)) == np.uint32(1)

    right = sites < N
    if np.any(right):
        right_shifts = sites[right]
        constrained[right] |= ((configs[right] >> right_shifts) & np.uint32(1)) == np.uint32(1)

    return cast(np.ndarray, constrained)


def simulate_trajectories(
    family: Family,
    N: int,
    epsilon: Fraction,
    initial_configs: np.ndarray,
    steps: int,
    seed: int,
    *,
    record_every: int = 1,
) -> np.ndarray:
    """Sample independent discrete-time trajectories from the East or FA chain."""

    if steps < 0:
        raise ValueError("steps must be non-negative")
    if record_every < 1:
        raise ValueError("record_every must be positive")
    configs = _as_uint32_configs(initial_configs).copy()
    n_traj = configs.shape[0]
    c = float(epsilon / (Fraction(1) + epsilon))
    rng = np.random.default_rng(seed)

    records = [configs.copy()]
    for step in range(1, steps + 1):
        sites = rng.integers(1, N + 1, size=n_traj, dtype=np.int64)
        constrained = _constraint_batch(family, configs, sites, N)
        up = rng.random(n_traj) < c
        masks = np.left_shift(np.uint32(1), (sites - 1).astype(np.uint32))
        up_configs = configs | masks
        down_configs = configs & ~masks
        resampled = np.where(up, up_configs, down_configs).astype(np.uint32)
        configs = np.where(constrained, resampled, configs).astype(np.uint32)
        if step % record_every == 0:
            records.append(configs.copy())

    return np.stack(records, axis=0)


def ensemble_energy_trace(trajectory_configs: np.ndarray, N: int) -> np.ndarray:
    """Return the ensemble-mean popcount trace for recorded configurations."""

    configs = np.asarray(trajectory_configs, dtype=np.uint32)
    if configs.ndim != 2:
        raise ValueError("trajectory_configs must have shape (n_recorded, n_traj)")
    return cast(
        np.ndarray,
        _popcount_uint32(configs & np.uint32((1 << N) - 1)).mean(axis=1, dtype=np.float64),
    )


def seed_block_bands(
    trajectory_configs: np.ndarray,
    N: int,
    *,
    n_blocks: int = 10,
) -> tuple[np.ndarray, np.ndarray]:
    """Return block mean energy trace and standard-error half-width trace."""

    configs = np.asarray(trajectory_configs, dtype=np.uint32)
    if configs.ndim != 2:
        raise ValueError("trajectory_configs must have shape (n_recorded, n_traj)")
    if n_blocks < 2:
        raise ValueError("n_blocks must be at least 2 for a ddof=1 standard error")
    n_traj = configs.shape[1]
    if n_traj % n_blocks != 0:
        raise ValueError("n_traj must be evenly divisible by n_blocks")

    block_size = n_traj // n_blocks
    block_traces = []
    for block in range(n_blocks):
        start = block * block_size
        stop = start + block_size
        block_traces.append(ensemble_energy_trace(configs[:, start:stop], N))
    block_means = np.stack(block_traces, axis=0)
    mean_trace = block_means.mean(axis=0, dtype=np.float64)
    band = block_means.std(axis=0, ddof=1) / np.sqrt(float(n_blocks))
    return mean_trace, band


def cross_validate_at_n10(
    family: Family,
    epsilon_hi: Fraction,
    epsilon_lo: Fraction,
    t_w: int,
    n_traj: int,
    seed: int,
    *,
    n_blocks: int = 10,
    tolerance_bandwidths: float = 3.0,
) -> dict[str, object]:
    """Compare N=10 MC quench traces to exact rational evolution."""

    if t_w < 0:
        raise ValueError("t_w must be non-negative")
    if n_traj < 1:
        raise ValueError("n_traj must be positive")

    N = 10
    exact_trace = _exact_quench_energy_trace(family, N, epsilon_hi, epsilon_lo, t_w)
    rng = np.random.default_rng(seed)
    initial = _sample_stationary_configs(family, N, epsilon_hi, n_traj, rng)
    trajectories = simulate_trajectories(family, N, epsilon_lo, initial, t_w, seed + 1)
    mc_mean, mc_band = seed_block_bands(trajectories, N, n_blocks=n_blocks)

    rows: list[dict[str, int | float | bool]] = []
    all_within = True
    for step, exact_value in enumerate(exact_trace):
        difference = abs(float(exact_value) - float(mc_mean[step]))
        tolerance = tolerance_bandwidths * float(mc_band[step])
        within = difference <= tolerance
        all_within = all_within and within
        rows.append(
            {
                "step": step,
                "exact": float(exact_value),
                "mc_mean": float(mc_mean[step]),
                "mc_band": float(mc_band[step]),
                "within_tolerance": bool(within),
            }
        )

    return {
        "pass": bool(all_within),
        "family": family,
        "N": N,
        "epsilon_hi": f"{epsilon_hi.numerator}/{epsilon_hi.denominator}",
        "epsilon_lo": f"{epsilon_lo.numerator}/{epsilon_lo.denominator}",
        "t_w": t_w,
        "n_traj": n_traj,
        "seed": seed,
        "n_blocks": n_blocks,
        "tolerance_bandwidths": float(tolerance_bandwidths),
        "rows": rows,
    }


def _constraint_batch(family: Family, configs: np.ndarray, sites: np.ndarray, N: int) -> np.ndarray:
    if family == "east":
        return east_constraint_batch(configs, sites, N)
    if family == "fa":
        return fa_constraint_batch(configs, sites, N)
    raise ValueError(f"unknown family: {family}")


def _exact_quench_energy_trace(
    family: Family,
    N: int,
    epsilon_hi: Fraction,
    epsilon_lo: Fraction,
    steps: int,
) -> list[Fraction]:
    if family == "east":
        distribution = east_stationary(N, epsilon_hi)
        kernel = build_east_kernel(N, epsilon_lo)
    elif family == "fa":
        distribution = fa_stationary(N, epsilon_hi)
        kernel = build_fa_kernel(N, epsilon_lo)
    else:
        raise ValueError(f"unknown family: {family}")

    observable = _energy_observable(family, N)
    trace = [expectation(distribution, observable)]
    for _ in range(steps):
        distribution = push(distribution, kernel)
        trace.append(expectation(distribution, observable))
    return trace


def _energy_observable(family: Family, N: int) -> Callable[[int], int]:
    if family == "east":

        def east_observable(state: int) -> int:
            return east_energy(state, N)

        return east_observable
    if family == "fa":

        def fa_observable(state: int) -> int:
            return fa_energy(state, N)

        return fa_observable
    raise ValueError(f"unknown family: {family}")


def _sample_stationary_configs(
    family: Family,
    N: int,
    epsilon: Fraction,
    n_traj: int,
    rng: np.random.Generator,
) -> np.ndarray:
    stationary: Distribution
    if family == "east":
        stationary = east_stationary(N, epsilon)
    elif family == "fa":
        stationary = fa_stationary(N, epsilon)
    else:
        raise ValueError(f"unknown family: {family}")

    state_count = 1 << N
    weights = np.array([float(stationary[state]) for state in range(state_count)], dtype=np.float64)
    return rng.choice(state_count, size=n_traj, p=weights).astype(np.uint32)


def _as_uint32_configs(configs: np.ndarray) -> np.ndarray:
    array = np.asarray(configs, dtype=np.uint32)
    if array.ndim != 1:
        raise ValueError("configs must be a 1-D array")
    return array


def _as_site_array(sites: np.ndarray, n_traj: int, N: int) -> np.ndarray:
    site_array = np.asarray(sites, dtype=np.int64)
    if site_array.shape != (n_traj,):
        raise ValueError("sites must have shape matching configs")
    if np.any((site_array < 1) | (site_array > N)):
        raise ValueError("sites must lie in 1..N")
    return site_array


def _popcount_uint32(values: np.ndarray) -> np.ndarray:
    x0: np.ndarray = np.asarray(values, dtype=np.uint32)
    x1: np.ndarray = x0 - ((x0 >> np.uint32(1)) & np.uint32(0x55555555))
    x2: np.ndarray = (x1 & np.uint32(0x33333333)) + ((x1 >> np.uint32(2)) & np.uint32(0x33333333))
    x3: np.ndarray = (x2 + (x2 >> np.uint32(4))) & np.uint32(0x0F0F0F0F)
    x4: np.ndarray = (x3 * np.uint32(0x01010101)) >> np.uint32(24)
    return x4.astype(np.uint8)
