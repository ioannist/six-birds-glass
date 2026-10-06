"""Declared finite epsilon grids for exact certificate runs."""

from fractions import Fraction

DEFAULT_EPSILON_GRID: tuple[Fraction, ...] = (
    Fraction(1, 10),
    Fraction(1, 5),
    Fraction(3, 10),
    Fraction(2, 5),
    Fraction(1, 2),
    Fraction(3, 5),
    Fraction(7, 10),
)
