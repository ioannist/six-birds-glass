from fractions import Fraction

from sixbirds_glass.protocols.catalog import p_eq, p_kovacs, p_quench


def test_p_eq_constructor() -> None:
    schedule = p_eq(Fraction(1, 2), 10)

    assert len(schedule) == 1
    assert schedule[0].epsilon == Fraction(1, 2)
    assert schedule[0].steps == 10


def test_p_quench_constructor() -> None:
    schedule = p_quench(Fraction(7, 10), 12, Fraction(1, 10), 5)

    assert [(leg.epsilon, leg.steps) for leg in schedule] == [
        (Fraction(7, 10), 12),
        (Fraction(1, 10), 5),
    ]


def test_p_kovacs_constructor() -> None:
    schedule = p_kovacs(
        Fraction(7, 10),
        12,
        Fraction(1, 10),
        5,
        Fraction(2, 5),
        20,
    )

    assert [(leg.epsilon, leg.steps) for leg in schedule] == [
        (Fraction(7, 10), 12),
        (Fraction(1, 10), 5),
        (Fraction(2, 5), 20),
    ]
