"""Constructive foreclosure sweep over energy-lens definable predicates."""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from sixbirds_glass.lenses.catalog import l_energy
from sixbirds_glass.protocols.evolution import Distribution


@dataclass(frozen=True)
class ForeclosureSweepResult:
    """Exhaustive predicate-agreement result for a fixed energy lens."""

    total_predicates: int
    agreeing_predicates: int
    all_agree: bool
    first_disagreement: frozenset[int] | None


def enumerate_energy_predicates(N: int) -> list[frozenset[int]]:
    """Enumerate every boolean predicate on energy levels ``{0, ..., N}``."""

    return [
        frozenset(energy for energy in range(N + 1) if mask & (1 << energy))
        for mask in range(1 << (N + 1))
    ]


def predicate_expectation(
    distribution: Distribution, N: int, predicate: frozenset[int]
) -> Fraction:
    """Return ``Pr[E(state) in predicate]`` exactly."""

    return sum(
        (mass for state, mass in distribution.items() if l_energy(state, N) in predicate),
        start=Fraction(0),
    )


def foreclosure_sweep(mu: Distribution, h_prime: Distribution, N: int) -> ForeclosureSweepResult:
    """Brute-force all ``Def(l_energy)`` predicates and count exact agreements."""

    predicates = enumerate_energy_predicates(N)
    agreeing = 0
    first_disagreement: frozenset[int] | None = None
    for predicate in predicates:
        if predicate_expectation(mu, N, predicate) == predicate_expectation(h_prime, N, predicate):
            agreeing += 1
            continue
        if first_disagreement is None:
            first_disagreement = predicate
    return ForeclosureSweepResult(
        total_predicates=len(predicates),
        agreeing_predicates=agreeing,
        all_agree=agreeing == len(predicates),
        first_disagreement=first_disagreement,
    )
