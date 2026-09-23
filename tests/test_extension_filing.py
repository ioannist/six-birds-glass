from sixbirds_glass.extension.filing import (
    GateRecord,
    GateTable,
    build_gate_table,
    recompute_verdict,
)


def test_recompute_verdict_depends_on_gate_inputs() -> None:
    good = build_gate_table()
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
