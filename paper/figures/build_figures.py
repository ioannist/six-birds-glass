"""Deterministic figure builder for the Phase 5 paper.

Every figure is sourced ONLY from paths listed in ``SOURCE_ARTIFACTS`` below, which must all
appear in ``paper/evidence_manifest.json``. The numeric series each figure plots are produced by
pure ``collect_*`` functions with no timestamps, randomness, or filesystem side effects, so they
can be (and are, in ``tests/test_paper_figures_tables.py``) rebuilt twice and compared for
determinism. Rendering to PDF uses matplotlib's Agg backend with figure metadata stripped, since
matplotlib does not otherwise guarantee byte-identical PDF output across runs.

Usage:
    python paper/figures/build_figures.py
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

REPO_ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = Path(__file__).resolve().parent / "out"

SOURCE_ARTIFACTS = (
    "artifacts/kovacs_hump_check/result.json",
    "artifacts/gt1_cd_tables/east_n8_l_energy.json",
    "artifacts/gt7_constants/east_reference.json",
    "artifacts/spectral_gaps/east.json",
    "artifacts/gt5_dimension/buyback_curve.json",
    "artifacts/gt7_constants/gt7_transfer_scores.json",
)

_NO_METADATA = {"Creator": None, "Producer": None, "CreationDate": None}

BLUE = "#0072B2"
ORANGE = "#D55E00"
GREEN = "#009E73"
GRAY = "#707070"
STYLE = {
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.labelsize": 10,
    "axes.titlesize": 11,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.linewidth": 0.7,
    "lines.linewidth": 1.8,
    "pdf.fonttype": 42,
}


def _load(path: str) -> dict[str, Any]:
    if path not in SOURCE_ARTIFACTS:
        raise ValueError(f"figure builder may only read declared SOURCE_ARTIFACTS, got {path!r}")
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def collect_kovacs_hump() -> dict[str, Any]:
    result = _load("artifacts/kovacs_hump_check/result.json")["payload"]["selected_result"]
    trace = [float(Fraction(value)) for value in result["trace"]]
    return {
        "trace": trace,
        "t_k": result["t_k"],
        "t_peak": result["t_peak"],
        "N": result["N"],
        "epsilon_lo": result["epsilon_lo"],
        "epsilon_hi": result["epsilon_hi"],
        "epsilon_mid": result["epsilon_mid"],
        "e_eq": result["e_eq"],
        "hump_height": float(Fraction(result["hump_height"])),
    }


def collect_gt1_cd_ladder() -> dict[str, Any]:
    payload = _load("artifacts/gt1_cd_tables/east_n8_l_energy.json")["payload"]
    grid = sorted(payload["grid"], key=lambda row: row["tau"])
    lumpable = {
        row["tau"]: row["closure_deficit_float"]
        for row in payload["controls"]["lumpable_unconstrained"]["rows"]
    }
    return {
        "tau": [row["tau"] for row in grid],
        "glassy_cd": [row["cd"] for row in grid],
        "equilibrium_cd": [row["equilibrium_baseline_cd"] for row in grid],
        "lumpable_cd": [lumpable[row["tau"]] for row in grid],
        "ratios": [row["cd_ratio_vs_equilibrium"] for row in grid],
        "margin": payload["thresholds"]["cd_margin_ratio_declared"],
    }


def collect_deficit_decay() -> dict[str, Any]:
    decay = _load("artifacts/gt7_constants/east_reference.json")["payload"]["deficit_decay"]
    tau_ladder = decay["tau_ladder"]
    cd_values = decay["cd_values"]
    return {"tau": tau_ladder, "cd": [cd_values[str(tau)] for tau in tau_ladder]}


def collect_spectral_gaps() -> dict[str, Any]:
    rows = _load("artifacts/spectral_gaps/east.json")["payload"]["rows"]
    by_n: dict[int, list[tuple[float, float]]] = {}
    for row in rows:
        by_n.setdefault(row["N"], []).append((float(Fraction(row["epsilon"])), row["gap"]))
    series = {}
    for n_value, points in sorted(by_n.items()):
        points.sort()
        series[n_value] = {
            "epsilon": [point[0] for point in points],
            "gap": [point[1] for point in points],
        }
    return series


def collect_buyback() -> dict[str, Any]:
    payload = _load("artifacts/gt5_dimension/buyback_curve.json")["payload"]
    budgets = sorted(int(budget) for budget in payload["raw_by_budget"])
    resolved_counts = [
        sum(1 for row in payload["raw_by_budget"][str(budget)] if row["resolved"])
        for budget in budgets
    ]
    total_counts = [len(payload["raw_by_budget"][str(budget)]) for budget in budgets]
    return {
        "budget": budgets,
        "resolved": resolved_counts,
        "total": total_counts,
        "saturation_budget": payload["saturation_budget"],
        "loss": [float(Fraction(payload["envelope"][str(b)])) for b in budgets],
        "coordinate_sets": [
            [row["coordinates"] for row in payload["raw_by_budget"][str(b)]] for b in budgets
        ],
    }


def collect_transfer_scoreboard() -> dict[str, Any]:
    payload = _load("artifacts/gt7_constants/gt7_transfer_scores.json")["payload"]
    aggregate = payload["aggregate"]
    fa_cells = [
        cell
        for cell in payload["cells"]
        if cell["target_family"] == "fa1f" and cell["prediction_type"] == "interval"
    ]
    fa_cells.sort(key=lambda cell: cell["cell_id"])
    points = []
    for cell in fa_cells:
        lo, hi = (
            float(Fraction(part.strip())) for part in cell["predicted"].strip("[]").split(",")
        )
        points.append(
            {
                "cell_id": cell["cell_id"],
                "lo": lo,
                "hi": hi,
                "observed": float(cell["observed"]),
                "verdict": cell["verdict"],
            }
        )
    return {"aggregate": aggregate, "fa_interval_cells": points}


def _canvas(height: float = 3.5) -> tuple[Any, Any]:
    return plt.subplots(figsize=(5, height), layout="constrained")


def _save(fig: Any, path: Path) -> None:
    for ax in fig.axes:
        ax.set_axisbelow(True)
        ax.grid(axis="y", color="#E6E6E6", linewidth=0.5)
    fig.savefig(path, metadata=_NO_METADATA)
    plt.close(fig)


def _tau_axis(ax: Any, tau: list[int]) -> None:
    ax.set_xscale("log", base=2)
    ax.set_xticks(tau, [str(t) for t in tau])
    ax.set_xlabel(r"Prediction horizon $\tau$ (steps)")
    ax.margins(x=0.12)


def render_kovacs_hump(data: dict[str, Any], path: Path) -> None:
    fig, ax = _canvas(3.8)
    steps = list(range(len(data["trace"])))
    eq = float(Fraction(data["e_eq"]))
    peak = data["t_peak"]
    ax.plot(steps, data["trace"], color=BLUE)
    ax.axhline(eq, color=GRAY, linestyle="--", linewidth=1)
    ax.text(steps[-1], eq - 0.018, f"Equilibrium = {data['e_eq']}", ha="right", va="top")
    ax.scatter([peak], [data["trace"][peak]], color=ORANGE, zorder=4)
    ax.annotate(
        f"Peak at step {peak}",
        (peak, data["trace"][peak]),
        xytext=(0, 12),
        textcoords="offset points",
        ha="center",
        color=ORANGE,
    )
    height_x = peak + (steps[-1] - peak) * 0.68
    ax.annotate(
        "",
        (height_x, eq + data["hump_height"]),
        (height_x, eq),
        arrowprops={"arrowstyle": "<->", "color": ORANGE, "lw": 1.2},
    )
    ax.text(
        height_x - 2,
        eq + data["hump_height"] / 2,
        f"Hump height\n{data['hump_height']:.3f}",
        ha="right",
        va="center",
    )
    ax.set(
        xlabel="Steps after second temperature jump",
        ylabel=r"Mean energy $\langle E\rangle$",
        title=f"East, $N={data['N']}$: crossing and overshoot",
    )
    ax.set_ylim(min(data["trace"]) - 0.035, max(data["trace"]) + 0.08)
    # Show the sampled bracket without suggesting an exact hit at an integer step.
    inset = ax.inset_axes([0.24, 0.30, 0.28, 0.26])
    k = data["t_k"]
    inset.plot([k, k + 1], data["trace"][k : k + 2], "o-", color=BLUE, markersize=4)
    inset.axhline(eq, color=GRAY, linestyle="--", linewidth=0.8)
    inset.set_xticks([k, k + 1])
    inset.set_title("Crossing bracket", fontsize=8)
    inset.tick_params(labelsize=8)
    inset.margins(x=0.3, y=0.25)
    _save(fig, path)


def render_gt1_cd_ladder(data: dict[str, Any], path: Path) -> None:
    fig, ax = _canvas(3.8)
    ax.plot(data["tau"], data["glassy_cd"], "o-", color=ORANGE, label="Aging")
    ax.plot(data["tau"], data["equilibrium_cd"], "s-", color=BLUE, label="Constrained equilibrium")
    ax.plot(data["tau"], data["lumpable_cd"], "^--", color=GRAY, label="Unconstrained control")
    for tau, cd, ratio in zip(data["tau"], data["glassy_cd"], data["ratios"], strict=True):
        ax.annotate(
            f"{ratio:.2f}" + r"$\times$",
            (tau, cd),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            color=ORANGE,
            fontsize=9,
        )
    _tau_axis(ax, data["tau"])
    ax.set_ylabel("Closure deficit (nats)")
    ax.set_title(f"Aging / equilibrium ratios; declared margin {data['margin']}")
    ax.set_ylim(-0.003, max(data["glassy_cd"]) * 1.75)
    ax.legend(frameon=False, loc="upper left")
    _save(fig, path)


def render_deficit_decay(data: dict[str, Any], path: Path) -> None:
    fig, ax = _canvas(3.3)
    ax.plot(data["tau"], data["cd"], "o-", color=BLUE)
    _tau_axis(ax, data["tau"])
    ax.set_ylabel("Closure deficit (nats)")
    ax.set_title("East reference: float64 readout")
    ax.set_ylim(bottom=0)
    _save(fig, path)


def render_spectral_gaps(data: dict[str, Any], path: Path) -> None:
    fig, ax = _canvas()
    colors, markers = [BLUE, ORANGE, GREEN, GRAY], ["o", "s", "^", "D"]
    for index, (n_value, series) in enumerate(sorted(data.items())):
        ax.plot(
            series["epsilon"],
            series["gap"],
            marker=markers[index % len(markers)],
            color=colors[index % len(colors)],
            label=f"$N={n_value}$",
        )
    ax.set_yscale("log")
    ax.set_xticks(sorted({eps for series in data.values() for eps in series["epsilon"]}))
    ax.set_xlabel(r"Temperature parameter $\epsilon$")
    ax.set_ylabel("Spectral gap")
    ax.set_title("East: float64 spectral diagnostic")
    ax.legend(frameon=False, ncol=len(data), loc="lower right")
    _save(fig, path)


def render_buyback(data: dict[str, Any], path: Path) -> None:
    fig, ax = _canvas()
    ax.plot(data["budget"], data["loss"], "o-", color=BLUE, markersize=7)
    for b, loss, resolved, total, sets in zip(
        data["budget"],
        data["loss"],
        data["resolved"],
        data["total"],
        data["coordinate_sets"],
        strict=True,
    ):
        coordinates = "\n".join(" + ".join(f"${c}$" for c in group) for group in sets if group)
        label = f"{resolved}/{total} resolved\n" + (coordinates or "Pair unresolved")
        ax.annotate(
            label,
            (b, loss),
            xytext=(0, 14),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )
    ax.set_xticks(data["budget"])
    ax.set(
        xlabel="Added-coordinate budget",
        ylabel="Unresolved predictive loss",
        title=f"Saturates at budget {data['saturation_budget']}",
    )
    ax.set_xlim(min(data["budget"]) - 0.4, max(data["budget"]) + 0.4)
    ax.set_ylim(-max(data["loss"]) * 0.08, max(data["loss"]) * 1.65)
    _save(fig, path)


def render_transfer_scoreboard(data: dict[str, Any], path: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(8, 4), layout="constrained", gridspec_kw={"width_ratios": [1, 2.6]}
    )
    aggregate = data["aggregate"]
    labels = ["pass", "fail", "no_prediction", "unobserved"]
    counts = [aggregate[f"n_{label}"] for label in labels]
    bars = ax1.barh(labels, counts, color=[BLUE, ORANGE, "#BBBBBB", GRAY])
    ax1.bar_label(bars, padding=4, fontsize=10)
    ax1.set_yticks(range(len(labels)), ["Pass", "Fail", "No prediction", "Unobserved"])
    ax1.invert_yaxis()
    ax1.set_xscale("log")
    ax1.set_xlim(1, max(counts) * 2.5)
    ax1.set_xlabel("Cell count (log scale)")
    ax1.set_title(f"(a) All {aggregate['total']} cells", loc="left")
    # Upper-bound scaling preserves interval membership across unlike readout units.
    cells = sorted(data["fa_interval_cells"], key=lambda c: (c["observed"] / c["hi"], c["cell_id"]))
    xs = list(range(len(cells)))
    for x, cell in zip(xs, cells, strict=True):
        color = BLUE if cell["verdict"] == "pass" else ORANGE
        ax2.plot([x, x], [cell["lo"] / cell["hi"], 1], color=color, linewidth=3, alpha=0.65)
        ax2.plot(x, cell["observed"] / cell["hi"], marker="x", color=color, markersize=6)
    ax2.axhline(1, color=GRAY, linestyle="--", linewidth=0.8)
    ax2.set_xticks(
        xs,
        [
            {"t_K": "$t_K$", "t_peak": "$t_p$", "hump_height": "$h$"}[c["cell_id"].split(":")[1]]
            for c in cells
        ],
        fontsize=8,
    )
    ax2.set_xlabel(
        "FA cells, sorted by observed / upper bound\n$t_K$: crossing; $t_p$: peak; $h$: height"
    )
    ax2.set_ylabel("Value / predicted upper bound")
    ax2.set_title(f"(b) {len(cells)} FA intervals", loc="left")
    ax2.set_ylim(bottom=0)
    ax2.legend(
        handles=[
            Line2D([], [], color=BLUE, marker="x", label="Pass"),
            Line2D([], [], color=ORANGE, marker="x", label="Fail"),
        ],
        frameon=False,
        loc="upper left",
    )
    _save(fig, path)


FIGURES = (
    ("fig_gt2_kovacs_hump.pdf", collect_kovacs_hump, render_kovacs_hump),
    ("fig_gt1_cd_ladder.pdf", collect_gt1_cd_ladder, render_gt1_cd_ladder),
    ("fig_gt7_deficit_decay.pdf", collect_deficit_decay, render_deficit_decay),
    ("fig_spectral_gaps.pdf", collect_spectral_gaps, render_spectral_gaps),
    ("fig_gt5_buyback.pdf", collect_buyback, render_buyback),
    ("fig_gt7_transfer_scoreboard.pdf", collect_transfer_scoreboard, render_transfer_scoreboard),
)


def build_all_series() -> dict[str, Any]:
    """Pure data collection for every figure; the function exercised by determinism tests."""

    return {name: collect() for name, collect, _ in FIGURES}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with plt.rc_context(STYLE):
        for name, collect, render in FIGURES:
            render(collect(), OUT_DIR / name)
    print(f"wrote {len(FIGURES)} figures to {OUT_DIR.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
