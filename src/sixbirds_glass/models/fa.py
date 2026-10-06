"""Fredrickson-Andersen FA-1f kinetically constrained model kernels."""

from fractions import Fraction

from sixbirds_glass.models.kernels import (
    Kernel,
    build_heat_bath_kernel,
    energy,
    product_bernoulli_stationary,
    spin,
)


def fa_constraint(config: int, site: int, N: int) -> bool:
    """FA-1f constraint with wall ``n_0 = 1`` and right boundary ``n_{N+1} = 0``."""

    _validate_site(site, N)
    left_up = True if site == 1 else spin(config, site - 1)
    right_up = False if site == N else spin(config, site + 1)
    return left_up or right_up


def build_fa_kernel(N: int, epsilon: Fraction) -> Kernel:
    """Build the wall-boundary FA-1f heat-bath kernel."""

    c = epsilon / (Fraction(1) + epsilon)
    return build_heat_bath_kernel(N, lambda config, site: fa_constraint(config, site, N), c)


def fa_stationary(N: int, epsilon: Fraction) -> dict[int, Fraction]:
    """Return the exact FA-1f product-Bernoulli stationary distribution."""

    return product_bernoulli_stationary(N, epsilon)


def fa_energy(config: int, N: int) -> int:
    """Return FA energy ``E(n) = sum_i n_i``."""

    return energy(config, N)


def _validate_site(site: int, N: int) -> None:
    if not 1 <= site <= N:
        raise ValueError(f"site must be in 1..N; got site={site}, N={N}")
