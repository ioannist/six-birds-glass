"""Unconstrained heat-bath control kernels."""

from fractions import Fraction

from sixbirds_glass.models.kernels import (
    Kernel,
    build_heat_bath_kernel,
    product_bernoulli_stationary,
)


def build_unconstrained_kernel(N: int, epsilon: Fraction) -> Kernel:
    """Build the independent per-site heat-bath control kernel."""

    c = epsilon / (Fraction(1) + epsilon)
    return build_heat_bath_kernel(N, lambda _config, _site: True, c)


def unconstrained_stationary(N: int, epsilon: Fraction) -> dict[int, Fraction]:
    """Return the exact product-Bernoulli stationary distribution."""

    return product_bernoulli_stationary(N, epsilon)
