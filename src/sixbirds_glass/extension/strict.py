"""GT6 strict-extension hypothesis inputs H2-H5."""

from __future__ import annotations

import hashlib
from collections.abc import Hashable
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from sixbirds_glass.lenses.catalog import l_energy
from sixbirds_glass.models.east import build_east_kernel
from sixbirds_glass.models.kernels import Kernel
from sixbirds_glass.pipeline.packaging import (
    Lens,
    PrototypeRule,
    coarse_grain,
    fiber_partition,
    packaging_endomap,
)
from sixbirds_glass.protocols.evolution import Distribution, push


@dataclass(frozen=True)
class StrataSaturationResult:
    """H2/H3 saturated reachable-strata report."""

    seed_count: int
    iterations_to_saturation: int
    final_strata: frozenset[Hashable]
    strata_count: int
    saturated: bool


@dataclass(frozen=True)
class ConditionedAnnealingResult:
    """H4 with/without conditioned-annealing comparison."""

    with_conditioning: StrataSaturationResult
    without_conditioning: StrataSaturationResult
    material_forcing_strata: frozenset[Hashable]
    material_forcing_count: int


@dataclass(frozen=True)
class H5Citation:
    """Resolved citation for the macro-admissibility obstruction."""

    artifact_path: Path
    sha256: str
    summary: str


@dataclass(frozen=True)
class NonFactorizationCitation:
    """Resolved citation for a constructive non-factorization witness."""

    artifact_path: Path
    sha256: str
    summary: str
    t0_descriptor: str
    has_split_pair: bool


def run_saturation(
    N: int,
    kernel: Kernel,
    tau: int,
    lens: Lens,
    prototype_rule: PrototypeRule,
    *,
    round_cap: int = 10,
) -> StrataSaturationResult:
    """Run packaging strata support to a two-empty-round saturation criterion."""

    if round_cap < 1:
        raise ValueError("round_cap must be positive")
    fibers = fiber_partition(N, lens)
    endomap = packaging_endomap(N, kernel, tau, lens, prototype_rule)
    states_by_seed = {label: prototype_rule(label, states) for label, states in fibers.items()}
    reached: set[Hashable] = set()
    empty_rounds = 0
    iterations = 0
    current = dict(states_by_seed)

    for iteration in range(1, round_cap + 1):
        iterations = iteration
        next_distributions: dict[Hashable, Distribution] = {}
        round_reached: set[Hashable] = set()
        for label, distribution in current.items():
            evolved = push(distribution, endomap)
            next_distributions[label] = evolved
            macro = coarse_grain(evolved, fibers)
            round_reached.update(macro_label for macro_label, mass in macro.items() if mass != 0)
        new_labels = round_reached - reached
        reached.update(round_reached)
        empty_rounds = empty_rounds + 1 if not new_labels else 0
        current = next_distributions
        if empty_rounds >= 2:
            return StrataSaturationResult(
                seed_count=len(states_by_seed),
                iterations_to_saturation=iterations,
                final_strata=frozenset(reached),
                strata_count=len(reached),
                saturated=True,
            )

    return StrataSaturationResult(
        seed_count=len(states_by_seed),
        iterations_to_saturation=iterations,
        final_strata=frozenset(reached),
        strata_count=len(reached),
        saturated=False,
    )


def run_forcing_comparison(
    N: int,
    epsilon_lo: Fraction,
    epsilon_hi: Fraction,
    epsilon_mid: Fraction,
    tau: int,
    lens: Lens,
    prototype_rule: PrototypeRule,
    *,
    round_cap: int = 10,
) -> ConditionedAnnealingResult:
    """Compare conditioned annealing against an unconditioned hold catalog."""

    conditioned = _conditioned_energy_kernel(N, epsilon_lo, epsilon_hi)
    unconditioned = build_east_kernel(N, epsilon_mid)
    with_conditioning = run_saturation(
        N, conditioned, tau, lens, prototype_rule, round_cap=round_cap
    )
    without_conditioning = run_saturation(
        N, unconditioned, tau, lens, prototype_rule, round_cap=round_cap
    )
    material = with_conditioning.final_strata - without_conditioning.final_strata
    return ConditionedAnnealingResult(
        with_conditioning=with_conditioning,
        without_conditioning=without_conditioning,
        material_forcing_strata=frozenset(material),
        material_forcing_count=len(material),
    )


def build_h5_citation(
    artifact_path: Path = Path("artifacts/gt1_cd_tables/east_n8_l_energy.json"),
) -> H5Citation:
    """Resolve the GT1/H5 macro-admissibility obstruction citation."""

    return H5Citation(
        artifact_path=artifact_path,
        sha256=artifact_sha256(artifact_path),
        summary=(
            "GT1 closure-deficit certificate records constrained East under L_energy with "
            "positive CD against the declared equilibrium baseline."
        ),
    )


def build_nonfactorization_citations(
    kovacs_path: Path = Path("artifacts/gt2_witnesses/kovacs_moment.json"),
    reflection_path: Path = Path("artifacts/gt3_foreclosure/lens_class_sweep.json"),
) -> tuple[NonFactorizationCitation, ...]:
    """Resolve constructive non-factorization witness citations."""

    return (
        NonFactorizationCitation(
            artifact_path=kovacs_path,
            sha256=artifact_sha256(kovacs_path),
            summary="GT2 Kovacs-moment witness: same current energy readout, separated future.",
            t0_descriptor="L_energy.mean=20/7",
            has_split_pair=True,
        ),
        NonFactorizationCitation(
            artifact_path=reflection_path,
            sha256=artifact_sha256(reflection_path),
            summary=(
                "GT3 reflection witness: same full L_energy distribution over Def(l_energy), "
                "separated by n_1 readout."
            ),
            t0_descriptor="L_energy.full_distribution.N8.reflection_pair",
            has_split_pair=True,
        ),
    )


def nonfactorization_rate(citations: tuple[NonFactorizationCitation, ...]) -> Fraction:
    """Return split-pair rate over cited T0 descriptor classes."""

    if not citations:
        return Fraction(0)
    split_count = sum(1 for citation in citations if citation.has_split_pair)
    return Fraction(split_count, len(citations))


def artifact_sha256(path: Path) -> str:
    """Return the sha256 hash of an artifact file's bytes."""

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _conditioned_energy_kernel(N: int, epsilon_lo: Fraction, epsilon_hi: Fraction) -> Kernel:
    lo_kernel = build_east_kernel(N, epsilon_lo)
    hi_kernel = build_east_kernel(N, epsilon_hi)
    threshold = Fraction(N, 2)
    rows = {}
    for state in range(1 << N):
        source_energy = l_energy(state, N)
        rows[state] = (
            dict(lo_kernel.rows[state])
            if Fraction(source_energy) <= threshold
            else dict(hi_kernel.rows[state])
        )
    return Kernel(N=N, state_count=1 << N, rows=rows)
