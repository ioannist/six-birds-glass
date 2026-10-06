from copy import deepcopy
from fractions import Fraction

import pytest

from sixbirds_glass.extension.shell import check_config_shell_membership, n8_shell_witness_config
from sixbirds_glass.models.spectral import mixing_time_bound


@pytest.mark.parametrize(("field", "value"), [("family", "fa"), ("boundary", "periodic")])
def test_shell_rejects_unsupported_dynamics(field: str, value: str) -> None:
    config = deepcopy(n8_shell_witness_config())
    config["model"][field] = value
    with pytest.raises(ValueError, match="wall-up East"):
        check_config_shell_membership(config)


def test_shell_rejects_undeclared_measurement_and_invalid_thresholds() -> None:
    config = deepcopy(n8_shell_witness_config())
    config["lens"]["id"] = "L_identity"
    with pytest.raises(ValueError, match="energy-lens"):
        check_config_shell_membership(config)
    with pytest.raises(ValueError, match="divisor"):
        check_config_shell_membership(n8_shell_witness_config(), lower_divisor=0)
    with pytest.raises(ValueError, match="tolerance"):
        check_config_shell_membership(
            n8_shell_witness_config(), non_equilibration_tolerance=Fraction(-1)
        )


@pytest.mark.parametrize("gap", [float("nan"), float("inf"), 1.1])
def test_spectral_proxy_rejects_invalid_gap(gap: float) -> None:
    with pytest.raises(ValueError):
        mixing_time_bound(gap)


@pytest.mark.parametrize(
    ("section", "field", "value"),
    [
        ("protocol", "cyclic", True),
        ("protocol", "initial_distribution", "explicit"),
        ("arithmetic", "mode", "float64_sweep"),
    ],
)
def test_exact_builders_reject_protocol_options_they_do_not_execute(
    section: str, field: str, value: object
) -> None:
    from sixbirds_glass.pipeline.kovacs_witness import build_kovacs_moment_witness_from_config
    from sixbirds_glass.pipeline.reproducibility import rebuild_hump_result_from_config

    config = deepcopy(n8_shell_witness_config())
    config[section][field] = value
    for builder in (
        check_config_shell_membership,
        build_kovacs_moment_witness_from_config,
        rebuild_hump_result_from_config,
    ):
        with pytest.raises(ValueError, match=r"requires|require"):
            builder(config)
