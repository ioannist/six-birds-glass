"""Rigorous rational enclosures of exponentials for transfer certificates."""

from fractions import Fraction


def exp_bounds(value: Fraction, *, terms: int = 32) -> tuple[Fraction, Fraction]:
    """Enclose exp(value) using a positive Taylor series and range reduction.

    For 0 <= r <= 1, after degree m the tail is bounded by its first
    omitted term divided by 1-r/(m+2). Doubling the argument squares the
    positive interval. Outward dyadic rounding at every square keeps the
    certificate small. Negative arguments use reciprocal bounds.
    """
    if not isinstance(value, Fraction) or terms < 1:
        raise ValueError("exponential requires a Fraction and positive term count")
    if value < 0:
        lo, hi = exp_bounds(-value, terms=terms)
        return _round(Fraction(1) / hi, Fraction(1) / lo)
    if value == 0:
        return Fraction(1), Fraction(1)
    reduced, squares = value, 0
    while reduced > 1:
        reduced /= 2
        squares += 1
    term = lower = Fraction(1)
    for degree in range(1, terms + 1):
        term *= reduced / degree
        lower += term
    first_omitted = term * reduced / (terms + 1)
    upper = lower + first_omitted / (1 - reduced / (terms + 2))
    lo, hi = _round(lower, upper)
    for _ in range(squares):
        lo, hi = _round(lo * lo, hi * hi)
    return lo, hi


def _round(lower: Fraction, upper: Fraction) -> tuple[Fraction, Fraction]:
    scale = 1 << 100
    lo, hi = lower * scale, upper * scale
    return Fraction(lo.numerator // lo.denominator, scale), Fraction(
        -(-hi.numerator // hi.denominator), scale
    )
