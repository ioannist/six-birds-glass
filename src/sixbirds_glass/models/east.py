"""East kinetically constrained model kernels."""

from fractions import Fraction

from sixbirds_glass.models.kernels import (
    Kernel,
    build_heat_bath_kernel,
    energy,
    product_bernoulli_stationary,
    spin,
)


def east_constraint(config: int, site: int, N: int) -> bool:
    """East constraint ``C_i(n) = n_{i-1}`` with wall ``n_0 = 1``."""

    _validate_site(site, N)
    if site == 1:
        return True
    return spin(config, site - 1)


def east_constraint_periodic(config: int, site: int, N: int) -> bool:
    """Periodic East constraint, used only to demonstrate non-irreducibility."""

    _validate_site(site, N)
    left_site = N if site == 1 else site - 1
    return spin(config, left_site)


def build_east_kernel(N: int, epsilon: Fraction) -> Kernel:
    """Build the wall-boundary East heat-bath kernel."""

    c = epsilon / (Fraction(1) + epsilon)
    return build_heat_bath_kernel(N, lambda config, site: east_constraint(config, site, N), c)


def build_periodic_east_kernel(N: int, epsilon: Fraction) -> Kernel:
    """Build the periodic-boundary East kernel for the negative-control test."""

    c = epsilon / (Fraction(1) + epsilon)
    return build_heat_bath_kernel(
        N, lambda config, site: east_constraint_periodic(config, site, N), c
    )


def east_stationary(N: int, epsilon: Fraction) -> dict[int, Fraction]:
    """Return the exact East product-Bernoulli stationary distribution."""

    return product_bernoulli_stationary(N, epsilon)


def east_energy(config: int, N: int) -> int:
    """Return East energy ``E(n) = sum_i n_i``."""

    return energy(config, N)


def _validate_site(site: int, N: int) -> None:
    if not 1 <= site <= N:
        raise ValueError(f"site must be in 1..N; got site={site}, N={N}")
