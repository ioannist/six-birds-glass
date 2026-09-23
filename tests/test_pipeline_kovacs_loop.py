from fractions import Fraction
from pathlib import Path

import pytest

from sixbirds_glass.io.config import load_config
from sixbirds_glass.pipeline.kovacs_loop import (
    KovacsLoopCertificate,
    build_constant_temperature_control_package,
    build_kovacs_loop_certificate,
)
from sixbirds_glass.pipeline.kovacs_witness import (
    KovacsMomentWitness,
    build_kovacs_moment_witness_from_config,
)
from sixbirds_glass.pipeline.loops import loop_action_score
from sixbirds_glass.pipeline.package import push_history
from sixbirds_glass.pipeline.signatures import current_signature

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def frozen_witness() -> KovacsMomentWitness:
    config = load_config(Path("configs/kovacs_hump_default.json"))
    return build_kovacs_moment_witness_from_config(config)


@pytest.fixture(scope="module")
def loop_certificate(frozen_witness: KovacsMomentWitness) -> KovacsLoopCertificate:
    return build_kovacs_loop_certificate(frozen_witness)


def test_tuned_loop_returns_current_panel_exactly(
    loop_certificate: KovacsLoopCertificate,
) -> None:
    package = loop_certificate.package
    mu_history = package.history_by_label("mid", "mu_K")
    image_history = next(
        history
        for history in package.histories["mid"]
        if history.distribution == loop_certificate.loop_image
    )
    loop = package.continuation_by_label("mid", "loop_kovacs")

    assert push_history(mu_history, loop) == image_history.distribution
    assert current_signature(package, mu_history) == current_signature(package, image_history)
    assert Fraction(0) <= loop_certificate.theta_return <= Fraction(1)
    assert loop_certificate.return_steps == 2


def test_real_east_kovacs_loop_score_closure_is_not_certified(
    loop_certificate: KovacsLoopCertificate,
) -> None:
    assert loop_certificate.closure_closed is False
    assert loop_certificate.closure_rounds == 6
    assert loop_certificate.closure_history_count == 14
    assert loop_certificate.loop_score_current is None
    assert loop_certificate.loop_score_predictive is None
    assert loop_certificate.loop_score_error is not None
    assert "did not stabilize" in loop_certificate.loop_score_error


def test_constant_temperature_control_loop_scores_zero(
    frozen_witness: KovacsMomentWitness,
) -> None:
    control = build_constant_temperature_control_package(
        frozen_witness.N, frozen_witness.epsilon_mid, frozen_witness.pi_eq
    )
    loop = control.continuation_by_label("mid", "loop_const_temp")

    assert loop_action_score(control, "mid", (loop,), quotient_kind="current") == Fraction(0)
    assert loop_action_score(control, "mid", (loop,), quotient_kind="predictive") == Fraction(0)
