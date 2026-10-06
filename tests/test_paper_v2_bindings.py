"""Prose-to-evidence bindings for the v2 paper (fact review, 2026-10-03).

Each test ties a sentence of the paper to the artifact, certificate or code it summarizes, so a
rewording cannot silently strengthen or misstate it.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path

import pytest

from sixbirds_glass.models.east import build_east_kernel
from sixbirds_glass.pipeline.quotients import comparison_map
from sixbirds_glass.triage import benchmarks

REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER = REPO_ROOT / "paper"
SECTIONS = PAPER / "sections"


def _tex(name: str) -> str:
    return (SECTIONS / name).read_text(encoding="utf-8")


def _flat(text: str) -> str:
    return " ".join(text.split())


def _floats(values: list[str]) -> list[float]:
    return [float(Fraction(value)) for value in values]


def _json(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


# --- comparison map exists only under verified refinement ---------------------------------------


def test_comparison_map_requires_refinement_and_prose_says_so() -> None:
    left, right = benchmarks.STATE_LEFT, benchmarks.STATE_RIGHT
    out_event = benchmarks._left_state_event("out_left", left, right)
    package = benchmarks._two_state_package(
        state_left=left,
        state_right=right,
        mid_event=benchmarks._left_state_event("now_left", left, right),
        to_out=benchmarks._constant_continuation("to_out", "mid", "out", benchmarks.SMALL_N, left),
        out_event=out_event,
    )
    with pytest.raises(ValueError, match="does not refine"):
        comparison_map(package, "mid")
    methods = _flat(_tex("sec_02_architecture_methods.tex"))
    assert "This refinement is a premise, not automatic" in methods
    assert "always a comparison map" not in methods
    notation = (PAPER / "notation_and_terminology.md").read_text(encoding="utf-8")
    assert "always exists" not in notation


# --- support-relative zero CD is not weak lumpability --------------------------------------------


def _energy_path_probability(kernel, start: int, energies: tuple[int, ...]) -> Fraction:
    weights = {start: Fraction(1)}
    for target in energies:
        nxt: dict[int, Fraction] = {}
        for state, mass in weights.items():
            for succ, prob in kernel.rows[state].items():
                if bin(succ).count("1") == target:
                    nxt[succ] = nxt.get(succ, Fraction(0)) + mass * prob
        weights = nxt
    return sum(weights.values(), Fraction(0))


def test_point_mass_energy_process_is_not_markov_and_prose_keeps_weak_lumpability_apart() -> None:
    # East N=2, epsilon=1/2, start 01 (energy 1): CD = 0 at the first step, yet the energy
    # process is not Markov, so support-relative closure is not weak lumpability.
    kernel = build_east_kernel(2, Fraction(1, 2))
    start = 0b01

    def cond(prefix: tuple[int, ...]) -> Fraction:
        return _energy_path_probability(kernel, start, (*prefix, 0)) / _energy_path_probability(
            kernel, start, prefix
        )

    assert cond((0, 1)) == Fraction(1, 3)
    assert cond((2, 1)) == Fraction(1, 6)
    methods = _flat(_tex("sec_02_architecture_methods.tex"))
    assert "does not by itself establish weak lumpability" in methods


# --- GB1 zero-asymmetry gloss carries its stationary hypothesis ---------------------------------


def test_gb1_zero_asymmetry_gloss_is_stationary_and_counterexamples_are_bound() -> None:
    prose = _flat(_tex("sec_06_gt3_gt4.tex"))
    assert "initialized at its stationary product law" in prose
    assert "does not cover arbitrary initial laws" in prose
    note = (REPO_ROOT / "math" / "gb1_temperature_trap.md").read_text(encoding="utf-8")
    assert "log(3)/6" in note and "9.5 * 10^-8" in note
    assert "9.5\\times10^{-8}" in prose


# --- GT4 rendered table shows classifications ---------------------------------------------------


def test_gt4_table_cells_are_classifications_from_the_artifact() -> None:
    summary = _json("artifacts/gt4_triage/regime_table.json")["payload"]["summary"]
    table = (PAPER / "tables" / "out" / "tab_gt4_regime_triage.tex").read_text(encoding="utf-8")
    plain = table.replace("\\allowbreak{}", "").replace("\\_", "_")
    rows = {line.split(" & ")[0]: line.rstrip(" \\").split(" & ") for line in plain.splitlines()}
    trap = summary["noncoherent_regime_controls"]["artifact_trap"]
    assert rows["artifact_trap"][2] == trap["raw_regime"] == "artifact_trap"
    assert rows["artifact_trap"][4] == trap["cleared_regime"] == "flat"
    assert rows["coherent candidate"][2] == summary["coherent_candidate_regime"]
    for regime, record in summary["noncoherent_regime_controls"].items():
        assert rows[regime][2] == record.get("raw_regime", record.get("regime"))


# --- GT7 dependency and chronology --------------------------------------------------------------


def test_gt7_rescaling_dependency_and_chronology_are_stated_honestly() -> None:
    predictions = _json("registry/predictions_f5e2a3332a2191a2.json")
    maps = {entry["map_id"] for entry in predictions["rescaling_maps"]}
    assert "spectral_gap_ratio_fa" in maps
    models = _flat(_tex("sec_03_models_pipeline.tex"))
    assert "nothing about FA is used" not in models.lower()
    assert "spectral gaps enter the declared interval-rescaling rule" in models
    assert "do not independently certify that order" in models
    gt7 = _flat(_tex("sec_08_gt7.tex"))
    assert "do not, by themselves, certify the chronological order" in gt7
    narrative = _flat((PAPER / "narrative.md").read_text(encoding="utf-8"))
    assert "frozen before target runs" not in narrative
    assert "planned per-stage commits were not made" in gt7
    assert "commits" in _json("registry/readouts.json")["freeze_note"]


# --- GT3 already matches the full energy law ----------------------------------------------------


def test_gt3_pair_has_equal_full_energy_law_and_prose_says_so() -> None:
    payload = _json("artifacts/gt3_foreclosure/lens_class_sweep.json")["payload"]
    assert payload["energy_level_distribution_mu"] == payload["energy_level_distribution_h_prime"]
    assert payload["separating_entry"]["continuation_id"] == "identity_probe"
    gt3 = _flat(_tex("sec_06_gt3_gt4.tex"))
    assert "the two histories have the same complete energy distribution" in gt3
    gt6 = _flat(_tex("sec_07_gt6.tex"))
    assert "GT3 already matches the complete energy distribution" in gt6


# --- GT6 construction and numbers ---------------------------------------------------------------


def test_gt6_prose_binds_to_full_energy_certificate() -> None:
    w = _json("math/gt6_energy_mixture_witness.json")
    construction = w["construction"]
    assert construction["rank"] == 9 and w["scope"]["stop_times"] == list(range(10))
    plus = [Fraction(x) for x in construction["positive_stopping_weights"]]
    minus = [Fraction(x) for x in construction["negative_stopping_weights"]]
    assert all((p > 0) == (t % 2 == 1) for t, p in enumerate(plus))
    assert all((m > 0) == (t % 2 == 0) for t, m in enumerate(minus))
    assert sum(plus) == sum(minus) == 1
    current = w["object_maps"]["pi0"]
    assert len(current["h_plus"]) == 9 and current["h_plus"] == current["h_minus"]
    gaps = {int(t): Fraction(v["absolute_gap"]) for t, v in w["future_energy"].items()}
    assert sorted(gaps) == list(range(1, 22)) and all(g > 0 for g in gaps.values())
    assert all(Fraction(g) == 0 for g in w["unconstrained_probe_ablation"]["future_gaps"].values())
    d = min(gaps.values())
    assert min(gaps, key=gaps.get) == 1
    radius = Fraction(w["finite_window_persistence"]["source_tv_perturbation_radius_for_half_gap"])
    assert radius == d / 32
    assert w["energy_predicate_sweep"]["agreeing_predicates"] == 512
    assert Fraction(w["energy_scalar_buyback"]["coordinate_differences"]["T_f"]) == 0
    prose = _flat(_tex("sec_07_gt6.tex"))
    assert f"$\\approx {float(d) * 1e10:.2f}\\times 10^{{-10}}$" in prose
    assert f"$\\approx {float(max(gaps.values())) * 1e9:.2f}\\times 10^{{-9}}$" in prose
    assert "the ten vectors have rank $9$" in prose
    assert "odd stopping times" in prose and "at most $d/32$" in prose


def test_gt6_pressure_prose_is_outward_of_certified_intervals() -> None:
    cert = _json("math/gt6_pressure_certificate.json")
    lo = Fraction(cert["limiting_pressure"]["pressure_lower"])
    hi = Fraction(cert["limiting_pressure"]["pressure_upper"])
    prose = _flat(_tex("sec_07_gt6.tex"))
    match = re.search(r"\[(\d\.\d+),\\, (\d\.\d+)\]", prose)
    assert match is not None
    assert Fraction(match.group(1)) <= lo and Fraction(match.group(2)) >= hi
    assert cert["conditional_infinite_time_gap"] == "0"
    assert cert["finite_margin"] == "1/1000"
    killed = cert["killed_process_limiting_diagnostic"]
    assert Fraction(killed["certified_margin"]) == Fraction(1, 2)
    assert Fraction(killed["contrast_interval"][0]) > Fraction(1, 2)
    assert killed["is_initial_law_conditioning"] is False
    assert "$1/1000$ for every horizon $n = 1, \\ldots, 8$" in prose
    assert "not initial-law conditioning" in prose


# --- counts quoted in prose and memo ------------------------------------------------------------


def test_lean_counts_and_memo_counts_match_sources() -> None:
    fidelity = _json("artifacts/lean_fidelity_table.json")["payload"]
    rows = fidelity["rows"]
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["fidelity"]] = counts.get(row["fidelity"], 0) + 1
    lean = _flat(_tex("sec_09_gb9_lean.tex"))
    assert f"All ${fidelity['theorem_count']}$ theorems" in lean
    assert f"${len(rows)}$-row fidelity" in lean
    assert f"${counts['verified']}$ \\emph{{verified}}" in lean
    assert f"${counts['narrowed / parametric']}$ \\emph{{narrowed/parametric}}" in lean
    ledger = _json("paper/claims_ledger.json")
    nonclaims = sum(len(row["nonclaims"]) for row in ledger["rows"])
    gaps = (PAPER / "gap_register.md").read_text(encoding="utf-8").count("\n### GAP-")
    memo = _flat((PAPER / "narrative.md").read_text(encoding="utf-8"))
    assert f"({nonclaims} entries)" in memo
    words = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
    words += ("ten", "eleven", "twelve")
    assert f"{words[gaps]} items" in memo
    collapse = next(r for r in ledger["rows"] if r["row_id"] == "FINDING.lean_collapse")
    generic = [r for r in rows if (r["lean_name"] or "").endswith("_GENERIC")]
    assert len(generic) == 5 and "five GENERIC theorem rows" in collapse["anchor_note"]


# --- GT4 fixture sizes (review round 2) ----------------------------------------------------------


def test_gt4_fixture_sizes_match_prose() -> None:
    builders = (
        benchmarks.protocol_trap_naive,
        benchmarks.protocol_trap_honest,
        benchmarks.flattenable_raw,
        benchmarks.flattenable_completed,
        benchmarks.flat_control,
        benchmarks.latent_memory_base,
        benchmarks.latent_memory_refined,
        benchmarks.dissipative_memory,
    )
    for builder in builders:
        package = builder()
        assert len(package.interfaces) in (2, 3), builder.__name__
        sizes = {c.kernel.state_count for cs in package.continuations.values() for c in cs}
        assert sizes == {16}, builder.__name__
    flat = benchmarks.flat_control()
    assert all(len(h.distribution) == 16 for hs in flat.histories.values() for h in hs)
    prose = _flat(_tex("sec_06_gt3_gt4.tex"))
    assert "16-state $N=4$ carrier and two or three interfaces" in prose
    assert "two or three microstates" not in prose


# --- GT6 figure series come straight from the certificate (review round 2) -----------------------


def test_gt6_figure_series_bind_to_certificate() -> None:
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location(
        "build_figures_v2_bindings", PAPER / "figures" / "build_figures.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_figures_v2_bindings"] = module
    spec.loader.exec_module(module)
    series = module.collect_gt6_energy_witness()
    w = _json("math/gt6_energy_mixture_witness.json")
    construction = w["construction"]
    assert series["stop_times"] == w["scope"]["stop_times"]
    current = w["object_maps"]["pi0"]
    assert series["weights_plus"] == _floats(construction["positive_stopping_weights"])
    assert series["weights_minus"] == _floats(construction["negative_stopping_weights"])
    assert series["current_plus"] == _floats(current["h_plus"])
    assert series["current_minus"] == _floats(current["h_minus"])
    assert series["current_laws_equal"] is True
    assert series["horizons"] == list(range(1, 22))
    assert series["gaps"] == [
        float(Fraction(w["future_energy"][str(t)]["absolute_gap"])) for t in range(1, 22)
    ]
    assert series["ablation_gaps_all_zero"] is True
