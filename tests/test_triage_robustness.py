from fractions import Fraction

from sixbirds_glass.triage import robustness


def test_cleared_robustness_predicates_meet_threshold() -> None:
    checks = (
        robustness.flat_control_cleared(),
        robustness.protocol_trap_honest_cleared(),
        robustness.flattenable_completed_cleared(),
        robustness.latent_memory_refined_cleared(),
        robustness.dissipative_memory_end_cleared(),
    )

    assert all(fraction >= robustness.CLEARED_THRESHOLD for fraction in checks)
    assert all(fraction == Fraction(1) for fraction in checks)


def test_persistence_robustness_predicates_meet_threshold() -> None:
    checks = (
        robustness.protocol_trap_naive_persists(),
        robustness.flattenable_raw_persists(),
        robustness.latent_memory_base_persists(),
        robustness.dissipative_memory_persists(),
        robustness.kovacs_wheel_persists(),
    )

    assert all(fraction >= robustness.PERSISTENCE_THRESHOLD for fraction in checks)
    assert all(fraction == Fraction(1) for fraction in checks)
