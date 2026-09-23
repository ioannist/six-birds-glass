from fractions import Fraction

import pytest

from sixbirds_glass.io.rational import rational_to_str, str_to_rational


@pytest.mark.parametrize(
    ("value", "text"),
    [
        (Fraction(0, 1), "0/1"),
        (Fraction(2, 4), "1/2"),
        (Fraction(-2, 4), "-1/2"),
        (Fraction(7, 1), "7/1"),
        (Fraction(123456789, 987654321), "13717421/109739369"),
    ],
)
def test_rational_to_str_is_canonical(value: Fraction, text: str) -> None:
    assert rational_to_str(value) == text
    assert str_to_rational(text) == value


@pytest.mark.parametrize(
    "text",
    [
        "2/4",
        "-2/4",
        "1/0",
        "1/-2",
        "abc",
        "1",
        "1.0/2",
        " 1/2",
        "1/2 ",
    ],
)
def test_str_to_rational_rejects_malformed_or_noncanonical(text: str) -> None:
    with pytest.raises(ValueError):
        str_to_rational(text)
