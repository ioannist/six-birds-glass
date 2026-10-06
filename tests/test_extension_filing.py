import pytest

from sixbirds_glass.extension.filing import (
    GateRecord,
    GateTable,
    build_gate_table,
    gate_table_from_payload,
    recompute_verdict,
)


def test_recompute_verdict_depends_on_gate_inputs() -> None:
    assert recompute_verdict(build_gate_table()) == "failed"
    good = build_gate_table(
        {
            gate: True
            for gate in (
                "G_suff",
                "G_stab",
                "G_ctrl",
                "G_nosmuggle",
                "G_vis",
                "G_audit",
                "G_strict",
            )
        }
    )
    assert recompute_verdict(good) == "strict"

    bad = GateTable(
        gates=tuple(
            GateRecord(record.gate, "not_strict", record.required, record.evidence)
            if record.gate == "G_strict"
            else record
            for record in good.gates
        )
    )

    assert recompute_verdict(bad) != "strict"


def test_required_flag_is_not_a_truthy_string() -> None:
    with pytest.raises(ValueError, match="invalid types"):
        gate_table_from_payload(
            [{"gate": "G_stab", "status": "pass", "required": "false", "evidence": "fake"}]
        )


def test_mandatory_stability_gate_cannot_be_disabled() -> None:
    table = build_gate_table()
    changed = GateTable(
        tuple(
            GateRecord(row.gate, "not_required", False, row.evidence)
            if row.gate == "G_stab"
            else row
            for row in table.gates
        )
    )
    assert recompute_verdict(changed) == "failed"
