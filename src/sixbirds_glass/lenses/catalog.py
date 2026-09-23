"""Declared current-observable lenses for East/FA bitmask states."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from fractions import Fraction

from sixbirds_glass.models.kernels import energy, spin

EquilibriumMeanEnergy = Callable[[Fraction, int], Fraction]


def l_energy(config: int, N: int) -> int:
    """Return the energy lens ``E(n)``."""

    return energy(config, N)


def l_energy_phase(config: int, N: int, phase: int) -> tuple[int, int]:
    """Return ``(E(n), phase)`` with phase supplied by a later protocol layer."""

    return (l_energy(config, N), phase)


def l_panel_bond_count(config: int, N: int) -> int:
    """Return the interior adjacency count ``D(n)``.

    The wall bond ``n_0 * n_1`` is excluded because the fixed wall ``n_0 = 1``
    would add a non-reflection-invariant ``n_1`` term.
    """

    return sum(1 for site in range(1, N) if spin(config, site) and spin(config, site + 1))


def l_panel(config: int, N: int) -> tuple[int, int, int]:
    """Return the declared rich panel ``(E(n), n_1, D(n))``."""

    return (l_energy(config, N), int(spin(config, 1)), l_panel_bond_count(config, N))


def l_panel_reflection_invariant(config: int, N: int) -> tuple[int, int]:
    """Return the reflection-invariant sub-panel ``(E(n), D(n))``."""

    return (l_energy(config, N), l_panel_bond_count(config, N))


def reflect(config: int, N: int) -> int:
    """Reflect a bitmask state by ``rho(n)_i = n_{N+1-i}``."""

    reflected = 0
    for site in range(1, N + 1):
        if spin(config, site):
            reflected |= 1 << (N - site)
    return reflected


def fictive_temperature_index(
    target_energy: Fraction | int,
    N: int,
    grid: Sequence[Fraction],
    *,
    equilibrium_mean_energy: EquilibriumMeanEnergy,
) -> int:
    """Return the grid index whose equilibrium mean energy is closest.

    Distances are exact absolute ``Fraction`` values. If multiple grid entries
    tie for the minimum distance, the smallest index in the supplied grid
    sequence wins. This tie-break is by caller-declared grid order, not by
    numeric epsilon order. Callers must pass an ascending grid for this to
    realize the documented "ties broken low" convention.
    """

    if not grid:
        raise ValueError("grid must contain at least one epsilon")

    target = Fraction(target_energy)
    best_index = 0
    best_distance = abs(equilibrium_mean_energy(grid[0], N) - target)

    for index, epsilon in enumerate(grid[1:], start=1):
        distance = abs(equilibrium_mean_energy(epsilon, N) - target)
        if distance < best_distance:
            best_index = index
            best_distance = distance

    return best_index


def l_tf(
    config: int,
    N: int,
    grid: Sequence[Fraction],
    *,
    equilibrium_mean_energy: EquilibriumMeanEnergy,
) -> tuple[int, int]:
    """Return ``(E(n), T_f index)`` for the declared epsilon grid."""

    current_energy = l_energy(config, N)
    return (
        current_energy,
        fictive_temperature_index(
            current_energy, N, grid, equilibrium_mean_energy=equilibrium_mean_energy
        ),
    )
