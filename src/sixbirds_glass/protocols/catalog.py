"""Named finite schedule-word constructors."""

from fractions import Fraction

from sixbirds_glass.protocols.schedule import ScheduleLeg

ScheduleWord = tuple[ScheduleLeg, ...]


def p_eq(epsilon: Fraction, steps: int) -> ScheduleWord:
    """Equilibrium hold word ``P_eq(epsilon)``."""

    return (ScheduleLeg(epsilon=epsilon, steps=steps),)


def p_quench(epsilon_hi: Fraction, tau_mix: int, epsilon_lo: Fraction, t_w: int) -> ScheduleWord:
    """Quench word: hot equilibration leg followed by cold aging leg."""

    return (
        ScheduleLeg(epsilon=epsilon_hi, steps=tau_mix),
        ScheduleLeg(epsilon=epsilon_lo, steps=t_w),
    )


def p_kovacs(
    epsilon_hi: Fraction,
    tau_hot: int,
    epsilon_lo: Fraction,
    t_w: int,
    epsilon_mid: Fraction,
    tau_probe: int,
) -> ScheduleWord:
    """Kovacs schedule word: hot, cold aging, then intermediate probe."""

    return (
        ScheduleLeg(epsilon=epsilon_hi, steps=tau_hot),
        ScheduleLeg(epsilon=epsilon_lo, steps=t_w),
        ScheduleLeg(epsilon=epsilon_mid, steps=tau_probe),
    )
