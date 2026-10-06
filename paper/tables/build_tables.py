"""Deterministic LaTeX table-fragment builder for the Phase 5 paper.

Every table is sourced ONLY from paths listed in ``SOURCE_ARTIFACTS`` below, which must all
appear in ``paper/evidence_manifest.json``. Two tables are design-pack mandates
(design/specs/00_architecture.md's Phase 5 gate): the Lean fidelity table and the nonclaims
ledger, both printed IN FULL, not summarized.

Usage:
    python paper/tables/build_tables.py            # write .tex fragments
    python paper/tables/build_tables.py --check     # exit nonzero if any fragment is stale
"""

from __future__ import annotations

import json
import math
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent / "out"

SOURCE_ARTIFACTS = (
    "artifacts/gt1_cd_tables/east_n8_l_energy.json",
    "artifacts/gt3_foreclosure/lens_class_sweep.json",
    "artifacts/gt4_triage/regime_table.json",
    "artifacts/gt6_bridge/audit.json",
    "artifacts/gt6_bridge/knockouts.json",
    "artifacts/lean_fidelity_table.json",
)

SOURCE_PAPER_FILES = ("paper/claims_ledger.json",)


def _load(path: str) -> dict[str, Any]:
    if path not in SOURCE_ARTIFACTS:
        raise ValueError(f"table builder may only read declared SOURCE_ARTIFACTS, got {path!r}")
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _load_paper_file(path: str) -> dict[str, Any]:
    if path not in SOURCE_PAPER_FILES:
        raise ValueError(f"table builder may only read declared SOURCE_PAPER_FILES, got {path!r}")
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def _escape(text: Any) -> str:
    if text is None:
        return "--"
    text = str(text)
    return (
        text.replace("\\", r"\textbackslash{}")
        .replace("_", r"\_")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("#", r"\#")
    )


def _breakable(text: Any) -> str:
    """Escape an identifier and let LaTeX break it after underscores, dots and slashes."""
    escaped = _escape(text)
    for mark in (r"\_", ".", "/"):
        escaped = escaped.replace(mark, mark + r"\allowbreak{}")
    return escaped


def _longtable(
    caption: str, label: str, columns: str, header: list[str], rows: list[list[str]]
) -> str:
    lines = [
        r"\begin{longtable}{" + columns + "}",
        rf"\caption{{{caption}}}\label{{{label}}} \\",
        r"\toprule",
        " & ".join(header) + r" \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        " & ".join(header) + r" \\",
        r"\midrule",
        r"\endhead",
        r"\bottomrule",
        r"\endfoot",
    ]
    for row in rows:
        lines.append(" & ".join(row) + r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{longtable}")
    return "\n".join(lines) + "\n"


def build_gt1_margins() -> str:
    payload = _load("artifacts/gt1_cd_tables/east_n8_l_energy.json")["payload"]
    grid = sorted(payload["grid"], key=lambda row: row["tau"])
    rows = [
        [
            str(row["tau"]),
            f"{row['cd']:.6f}",
            f"{row['equilibrium_baseline_cd']:.6f}",
            f"{row['cd_ratio_vs_equilibrium']:.4f}",
            _floor4(Fraction(row["cd_ratio_certified_interval"][0])),
        ]
        for row in grid
    ]
    thresholds = payload["thresholds"]
    rows.append(
        [
            r"\textbf{margin}",
            "--",
            "--",
            f"declared {thresholds['cd_margin_ratio_declared']}",
            r"$\geq$ " + _floor4(Fraction(thresholds["achieved_min_cd_ratio_certified_lower"])),
        ]
    )
    return _longtable(
        "GT1 closure deficit (nats) of the aging protocol against the constrained-equilibrium "
        "baseline (East $N=8$, energy readout). Deficits are shown as floats; the last column is "
        "a rigorous lower bound on the ratio from exact probabilities and rational logarithm "
        "enclosures, rounded down",
        "tab:gt1-margins",
        "rrrrr",
        [
            r"$\tau$",
            r"$\mathrm{CD}_\tau$ (aging)",
            r"$\mathrm{CD}_\tau$ (equilibrium)",
            "ratio",
            "certified ratio",
        ],
        rows,
    )


def _floor4(value: Fraction) -> str:
    """Round a positive rational down to four decimals, so the printed bound stays valid."""
    scaled = math.floor(value * 10_000)
    return f"{scaled // 10_000}.{scaled % 10_000:04d}"


def build_gt3_foreclosure() -> str:
    payload = _load("artifacts/gt3_foreclosure/lens_class_sweep.json")["payload"]
    rows = [
        ["N", str(payload["N"])],
        ["epsilon", _escape(payload["epsilon"])],
        ["lens", _escape(payload["lens_id"])],
        ["total predicates", str(payload["total_predicates"])],
        ["agreeing predicates", str(payload["agreeing_predicates"])],
        ["lens image size", str(payload["lens_image_size"])],
        ["all agree", str(payload["all_agree"])],
        ["separating event", _escape(payload["separating_entry"]["event_id"])],
        ["witness provenance", _escape(payload["witness_provenance"])],
        ["T-FOR-02 statement", _escape(payload["t_for_02_statement"])],
    ]
    return _longtable(
        "GT3 foreclosure sweep summary (East N=8, $\\epsilon=1/2$)",
        "tab:gt3-foreclosure",
        "lp{9cm}",
        ["field", "value"],
        rows,
    )


def build_gt4_regime_triage() -> str:
    summary = _load("artifacts/gt4_triage/regime_table.json")["payload"]["summary"]
    rows = [
        [
            "coherent candidate",
            _breakable(summary["coherent_candidate"]),
            _breakable(summary["coherent_candidate_regime"]),
            "--",
            "--",
        ]
    ]
    for regime, record in sorted(summary["noncoherent_regime_controls"].items()):
        raw_class = record.get("raw_regime", record.get("regime"))
        rows.append(
            [
                _breakable(regime),
                _breakable(record["raw"]),
                _breakable(raw_class),
                _breakable(record.get("cleared", "(pure control)")),
                _breakable(record.get("cleared_regime", "--")),
            ]
        )
    return _longtable(
        "GT4 regime triage over the declared benchmark family: each fixture and the class the "
        "deterministic triage assigns to it, before (raw) and after (cleared) the declared repair",
        "tab:gt4-regime-triage",
        r">{\raggedright\arraybackslash}p{2.4cm}>{\raggedright\arraybackslash}p{3.3cm}>{\raggedright\arraybackslash}p{2.4cm}>{\raggedright\arraybackslash}p{3.5cm}>{\raggedright\arraybackslash}p{2.2cm}",
        ["control", "raw fixture", "raw class", "cleared fixture", "cleared class"],
        rows,
    )


def build_gt6_gate_table() -> str:
    gate_table = _load("artifacts/gt6_bridge/audit.json")["payload"]["gate_table"]
    rows = [
        [
            _escape(g["gate"]),
            "yes" if g["required"] else "no",
            _escape(g["status"]),
            _escape(g["evidence"]),
        ]
        for g in gate_table
    ]
    return _longtable(
        "GT6 gate table of the original strict-extension filing, as filed in the audit artifact",
        "tab:gt6-gate-table",
        "lllp{6.5cm}",
        ["gate", "required", "status", "evidence"],
        rows,
    )


def build_gt6_knockouts() -> str:
    knockouts = _load("artifacts/gt6_bridge/knockouts.json")["payload"]["knockouts"]
    rows = [
        [_escape(k["primitive"]), _escape(k["kind"]), str(k["degraded"]), _escape(k["threshold"])]
        for k in knockouts
    ]
    return _longtable(
        "GT6 knockout panel (P1--P3 numeric ablations; P4--P6 capability-loss rows)",
        "tab:gt6-knockouts",
        "lllp{6.5cm}",
        ["primitive", "kind", "degraded", "threshold"],
        rows,
    )


def build_lean_fidelity_full() -> str:
    """Design-pack mandate: printed in full, all rows, verbatim fidelity labels."""
    rows_data = _load("artifacts/lean_fidelity_table.json")["payload"]["rows"]
    rows = [
        [
            _breakable(
                Path(row["lean_file"]).relative_to("lean").with_suffix("").as_posix()
                if row["lean_file"] is not None
                else "(exact Python)"
            ),
            _breakable(row["lean_name"])
            if row["lean_name"] is not None
            else _escape(row["paper_or_project_claim"]),
            _escape(row["fidelity"]),
        ]
        for row in rows_data
    ]
    return _longtable(
        "Lean fidelity table, every row. Rows with no Lean encoding are labeled by the claim "
        "they document instead of a Lean identifier",
        "tab:lean-fidelity-full",
        r">{\raggedright\arraybackslash}p{3.6cm}>{\raggedright\arraybackslash}p{8.4cm}p{2.9cm}",
        ["module", "Lean name / documented claim", "fidelity"],
        rows,
    )


def build_nonclaims_full() -> str:
    """Design-pack mandate: the nonclaims ledger printed in full, one row per (claim, nonclaim)."""
    ledger = _load_paper_file("paper/claims_ledger.json")
    rows = []
    for row in ledger["rows"]:
        for nonclaim in row["nonclaims"]:
            rows.append([_breakable(row["row_id"]), _escape(nonclaim)])
    return _longtable(
        "Full nonclaims ledger: every nonclaim of every ledger row, unabridged",
        "tab:nonclaims-full",
        r">{\raggedright\arraybackslash}p{3.6cm}p{11.6cm}",
        ["claim", "nonclaim"],
        rows,
    )


TABLES = {
    "tab_gt1_margins.tex": build_gt1_margins,
    "tab_gt3_foreclosure.tex": build_gt3_foreclosure,
    "tab_gt4_regime_triage.tex": build_gt4_regime_triage,
    "tab_gt6_gate_table.tex": build_gt6_gate_table,
    "tab_gt6_knockouts.tex": build_gt6_knockouts,
    "tab_lean_fidelity_full.tex": build_lean_fidelity_full,
    "tab_nonclaims_full.tex": build_nonclaims_full,
}


def build_all() -> dict[str, str]:
    return {name: build() for name, build in TABLES.items()}


def write_all() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in build_all().items():
        (OUT_DIR / name).write_text(content, encoding="utf-8")
    print(f"wrote {len(TABLES)} table fragments to {OUT_DIR.relative_to(REPO_ROOT)}")


def check_fresh() -> list[str]:
    stale = []
    for name, content in build_all().items():
        path = OUT_DIR / name
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            stale.append(name)
    return stale


def main() -> int:
    if "--check" in sys.argv[1:]:
        stale = check_fresh()
        if stale:
            for name in stale:
                print(f"STALE: {name}")
            return 1
        print(f"PASS tables ({len(TABLES)} fragments fresh)")
        return 0
    write_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
