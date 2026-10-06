import math

from sixbirds_glass.pipeline.protocol_trap import (
    FloatKernel,
    candidate_measure,
    epr,
    gibbs_measure,
    heat_bath_resample_kernel,
    kl_divergence,
    lifted_kernel,
    mixed_square_affinity_from_energy,
    mixed_square_affinity_from_kernel,
    path_kl_enumerate,
    pseudo_epr_boundary_term,
    stationary_distribution,
)


def test_common_temperature_recovers_zero_boundary_and_zero_stationary_epr() -> None:
    energies = demo_energies()
    temperatures = {0: 2.0, 1: 2.0}
    pis = {
        phase: gibbs_measure(energies, temperature) for phase, temperature in temperatures.items()
    }
    S, s = reversible_clock()
    alpha = 1.0 / 3.0
    Ks = {phase: heat_bath_resample_kernel(pi) for phase, pi in pis.items()}
    lifted = lifted_kernel(Ks, S, alpha)

    assert pseudo_epr_boundary_term(pis, s, S, alpha) < 1e-14
    assert epr(lifted, stationary_distribution(lifted)) < 1e-14


def test_pseudo_epr_boundary_term_matches_independent_formula() -> None:
    energies = demo_energies()
    temperatures = {0: 3.0, 1: 1.0}
    pis = {
        phase: gibbs_measure(energies, temperature) for phase, temperature in temperatures.items()
    }
    S, s = reversible_clock()
    alpha = 1.0 / 3.0
    independent = alpha * sum(
        s[phase] * S.rows[phase][target] * kl_divergence(pis[phase], pis[target])
        for phase in pis
        for target in pis
        if phase != target
    )

    assert math.isclose(
        pseudo_epr_boundary_term(pis, s, S, alpha), independent, rel_tol=0.0, abs_tol=1e-15
    )


def test_three_state_hot_cold_demo_respects_conjectured_bound() -> None:
    energies = demo_energies()
    temperatures = {0: 3.0, 1: 1.0}
    pis = {
        phase: gibbs_measure(energies, temperature) for phase, temperature in temperatures.items()
    }
    S, s = reversible_clock()
    alpha = 1.0 / 3.0
    Ks = {phase: heat_bath_resample_kernel(pi) for phase, pi in pis.items()}
    lifted = lifted_kernel(Ks, S, alpha)
    stationary = stationary_distribution(lifted)
    bound_rate = pseudo_epr_boundary_term(pis, s, S, alpha)

    assert epr(lifted, candidate_measure(pis, s)) == pytest_approx(bound_rate)
    assert epr(lifted, stationary) > 0.0
    for horizon in (1, 2, 3):
        sigma = path_kl_enumerate(lifted, stationary, horizon)
        assert sigma <= horizon * bound_rate + 1e-12


def test_mixed_square_affinity_matches_kernel_log_ratio_audit() -> None:
    energies = demo_energies()
    temperatures = {0: 3.0, 1: 1.0}
    pis = {
        phase: gibbs_measure(energies, temperature) for phase, temperature in temperatures.items()
    }
    S, _s = reversible_clock()
    alpha = 1.0 / 3.0
    Ks = {phase: heat_bath_resample_kernel(pi) for phase, pi in pis.items()}
    lifted = lifted_kernel(Ks, S, alpha)

    energy_affinity = mixed_square_affinity_from_energy(
        energies, state=0, target_state=1, temperature=temperatures, phase=0, target_phase=1
    )
    kernel_affinity = mixed_square_affinity_from_kernel(
        lifted, state=0, target_state=1, phase=0, target_phase=1, state_count_x=3
    )

    assert math.isclose(kernel_affinity, energy_affinity, rel_tol=0.0, abs_tol=1e-14)


def demo_energies() -> dict[int, float]:
    return {0: 0.0, 1: 1.0, 2: 2.0}


def reversible_clock() -> tuple[FloatKernel, dict[int, float]]:
    return (
        FloatKernel(
            state_count=2,
            rows={
                0: {0: 0.8, 1: 0.2},
                1: {0: 0.2, 1: 0.8},
            },
        ),
        {0: 0.5, 1: 0.5},
    )


def pytest_approx(value: float):
    import pytest

    return pytest.approx(value, rel=0.0, abs=1e-14)
