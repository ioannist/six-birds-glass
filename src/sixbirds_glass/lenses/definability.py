"""Combinatorial utilities for lens-definable predicates."""

from collections.abc import Hashable, Iterable


def definable_predicate_count(image_size: int) -> int:
    """Return ``|Def(f)| = 2^|im f|`` for a finite lens image."""

    if image_size < 0:
        raise ValueError("image_size must be non-negative")
    return 1 << image_size


def lens_image_size(values: Iterable[Hashable]) -> int:
    """Return the number of distinct lens outputs in an iterable."""

    return len(set(values))
