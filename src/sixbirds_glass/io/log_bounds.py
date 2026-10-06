"""Rigorous rational enclosures of natural logarithms for finite certificates."""

from fractions import Fraction


def log_bounds(value: Fraction, *, terms: int = 32) -> tuple[Fraction, Fraction]:
    """Enclose log(value) using range reduction and the positive atanh series.

    For 1 <= r <= 2, t=(r-1)/(r+1) lies in [0,1/3]. The first ``terms``
    terms of 2*sum t^(2j+1)/(2j+1) give a lower bound. The remaining sum is
    at most 2*t^(2*terms+1)/((2*terms+1)*(1-t*t)). All operations are exact.
    Outward rounding to a common denominator 2**100 keeps subsequent finite
    sums small; it enlarges the certified interval by at most 2**-100 per end.
    """

    if not isinstance(value, Fraction) or value <= 0:
        raise ValueError("logarithm input must be a positive Fraction")
    if terms < 1:
        raise ValueError("terms must be positive")
    if value < 1:
        lower, upper = log_bounds(1 / value, terms=terms)
        return -upper, -lower
    exponent = 0
    reduced = value
    while reduced > 2:
        reduced /= 2
        exponent += 1
    lower, upper = _reduced_bounds(reduced, terms)
    if exponent:
        log2_lower, log2_upper = _reduced_bounds(Fraction(2), terms)
        lower += exponent * log2_lower
        upper += exponent * log2_upper
    scale = 1 << 100
    scaled_lower = lower * scale
    scaled_upper = upper * scale
    return (
        Fraction(scaled_lower.numerator // scaled_lower.denominator, scale),
        Fraction(-(-scaled_upper.numerator // scaled_upper.denominator), scale),
    )


def _reduced_bounds(value: Fraction, terms: int) -> tuple[Fraction, Fraction]:
    t = (value - 1) / (value + 1)
    power = t
    lower = Fraction(0)
    for j in range(terms):
        lower += 2 * power / (2 * j + 1)
        power *= t * t
    tail = 2 * power / ((2 * terms + 1) * (1 - t * t))
    return lower, lower + tail
