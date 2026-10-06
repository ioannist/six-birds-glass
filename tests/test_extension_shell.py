from pathlib import Path

import pytest

from sixbirds_glass.extension.shell import build_shell_witnesses, check_config_shell_membership
from sixbirds_glass.io.config import load_config

pytestmark = pytest.mark.slow


def test_real_n10_shell_witness_has_zero_exits() -> None:
    config = load_config(Path("configs/kovacs_hump_default.json"))

    membership = check_config_shell_membership(config)

    assert membership.exit_count == 0
    assert membership.in_shell


def test_both_frozen_shell_witnesses_have_zero_exits() -> None:
    witnesses = build_shell_witnesses(materialize_n8=False)

    assert len(witnesses) == 2
    assert {witness.N for witness in witnesses} == {8, 10}
    assert all(witness.exit_count == 0 for witness in witnesses)
