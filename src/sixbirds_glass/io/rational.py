"""Serialization helpers for exact rationals.

The certificate path uses ``fractions.Fraction`` only. String input is strict:
it must already be in canonical lowest terms with a positive denominator.
"""

from __future__ import annotations

import re
from fractions import Fraction

_RATIONAL_RE = re.compile(r"^-?[0-9]+/[1-9][0-9]*$")


def rational_to_str(f: Fraction) -> str:
    """Serialize a Fraction as canonical ``p/q`` with ``q > 0``.

    ``Fraction`` normalizes values at construction, so this function never
    emits a reducible fraction or a negative denominator. Integral values still
    render with ``/1`` to satisfy the config schema.
    """

    return f"{f.numerator}/{f.denominator}"


def str_to_rational(s: str) -> Fraction:
    """Parse a canonical rational string into a ``Fraction``.

    Raises:
        ValueError: If ``s`` is malformed, has a non-positive denominator, or is
            not in canonical lowest-terms form.
    """

    if not _RATIONAL_RE.fullmatch(s):
        raise ValueError(f"malformed rational {s!r}; expected canonical 'p/q' with denominator > 0")

    numerator_text, denominator_text = s.split("/", maxsplit=1)
    denominator = int(denominator_text)
    if denominator <= 0:
        raise ValueError(f"malformed rational {s!r}; denominator must be positive")

    value = Fraction(int(numerator_text), denominator)
    canonical = rational_to_str(value)
    if s != canonical:
        raise ValueError(f"non-canonical rational {s!r}; expected {canonical!r}")

    return value
