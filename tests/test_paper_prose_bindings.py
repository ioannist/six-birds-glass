"""Prose-to-artifact bindings added after the 2026-09-22 Eddy FIX-FIRST review.

Each test binds a sentence of the paper's plain-language glosses to the code or artifact it
paraphrases, so a future rewording cannot silently strengthen or misstate a claim. The science
controls (lumpability vs. packaging idempotence, the randomized-stop crossing) are exact.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path

from sixbirds_glass.lenses.catalog import l_energy
from sixbirds_glass.models.east import build_east_kernel, east_stationary
from sixbirds_glass.models.unconstrained import build_unconstrained_kernel
from sixbirds_glass.pipeline.cd import closure_deficit_float, is_exactly_lumpable
from sixbirds_glass.pipeline.packaging import (
    gibbs_prototype_rule,
    idempotence_defect,
    packaging_endomap,
)
from sixbirds_glass.triage import benchmarks

REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER = REPO_ROOT / "paper"
SECTIONS = PAPER / "sections"


def _tex(name: str) -> str:
    return (SECTIONS / name).read_text(encoding="utf-8")


def _all_prose() -> str:
    parts = [p.read_text(encoding="utf-8") for p in sorted(SECTIONS.glob("*.tex"))]
    parts.append((PAPER / "main.tex").read_text(encoding="utf-8"))
    parts.append((PAPER / "notation_and_terminology.md").read_text(encoding="utf-8"))
    return "\n".join(parts)


def _artifact(rel: str) -> dict:
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


def _figures():
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location(
        "build_figures_for_bindings", REPO_ROOT / "paper" / "figures" / "build_figures.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["build_figures_for_bindings"] = module
    spec.loader.exec_module(module)
    return module


# --- Finding 1: lumpability does not imply packaging idempotence --------------------------------


def test_lumpable_control_has_positive_idempotence_defect_exactly_2_over_9() -> None:
    N, epsilon, tau = 2, Fraction(1, 2), 1
    kernel = build_unconstrained_kernel(N, epsilon)
    assert is_exactly_lumpable(N, kernel, tau, l_energy)
    endomap = packaging_endomap(N, kernel, tau, l_energy, gibbs_prototype_rule(N, epsilon))
    assert idempotence_defect(endomap) == Fraction(2, 9)


def test_methods_prose_does_not_equate_closure_with_packaging_idempotence() -> None:
    methods = _tex("sec_02_architecture_methods.tex").lower()
    for phrase in ("would be idempotent", "persistent positivity is aging"):
        assert phrase not in methods, phrase
    assert "saturation diagnostic" in methods
    assert "exact defect $2/9$" in methods
    assert "in nats" in methods and "in bits" not in _all_prose().lower()


# --- Finding 8: closure deficits are computed with natural logarithms ---------------------------


def test_closure_deficit_code_uses_natural_log() -> None:
    for rel in ("src/sixbirds_glass/pipeline/cd.py", "src/sixbirds_glass/pipeline/protocol_cd.py"):
        source = (REPO_ROOT / rel).read_text(encoding="utf-8")
        assert "math.log(" in source and "log2" not in source, rel


# --- Finding 4: the Kovacs crossing is a randomized stop between bracketing steps ---------------


def test_kovacs_crossing_prose_binds_to_bracketing_trace_and_theta() -> None:
    selected = _artifact("artifacts/kovacs_hump_check/result.json")["payload"]["selected_result"]
    e_eq = Fraction(selected["e_eq"])
    trace = [Fraction(v) for v in selected["trace"]]
    t_k = selected["t_k"]
    assert t_k == 1
    assert trace[t_k] < e_eq < trace[t_k + 1], "crossing must be bracketed, not hit exactly"
    theta = (e_eq - trace[t_k + 1]) / (trace[t_k] - trace[t_k + 1])
    witness = _artifact("artifacts/gt2_witnesses/kovacs_moment.json")
    theta_star = Fraction(witness["payload"]["witness_pairs"][0]["tuning"]["theta_star"])
    assert theta == theta_star
    entry = witness["payload"]["witness_pairs"][0]["separating_entry"]
    assert entry["continuation_id"] == "probe_hold" and entry["event_id"] == "w_E"

    prose = _tex("sec_05_gt2_gt5.tex")
    assert "randomized stop" in prose
    assert "between\nsteps $1$ and $2$" in prose or "between steps $1$ and $2$" in prose
    assert "Only the mean energy is matched" in prose
    # Numbers quoted in prose must agree with the artifact to the printed precision.
    assert f"\\theta \\approx {float(theta):.4f}" in prose
    assert f"$\\approx {float(trace[t_k]):.3f}$" in prose
    assert f"$\\approx {float(trace[t_k + 1]):.3f}$" in prose
    assert f"$\\approx {float(Fraction(entry['abs_gap'])):.4f}$" in prose


# --- Finding 5: the GT5 coordinates are expectations of per-microstate quantities ---------------


def test_gt5_coordinate_prose_binds_to_expectation_of_index_semantics() -> None:
    payload = _artifact("artifacts/gt5_dimension/buyback_curve.json")["payload"]
    assert payload["resolved_coordinates"] == [["T_f"], ["D"], ["n_1"]]
    assert payload["saturation_budget"] == 1
    prose = _tex("sec_05_gt2_gt5.tex")
    assert "\\mathbb{E}_\\mu[\\,i^*(E(n))\\,]" in prose
    assert "not a temperature" in prose
    assert "not the\nTNM quantity itself" in prose or "not the TNM quantity itself" in prose
    intro = _tex("sec_01_introduction.tex")
    assert "TNM fictive temperature is one lawful choice" not in intro


# --- Finding 2: GT3's separator is a present structural coordinate; no overreach ----------------


def test_gt3_separator_is_present_state_readout_and_prose_does_not_overreach() -> None:
    payload = _artifact("artifacts/gt3_foreclosure/lens_class_sweep.json")["payload"]
    entry = payload["separating_entry"]
    assert entry["continuation_id"] == "identity_probe" and entry["event_id"] == "n_1"
    prose = _all_prose().lower()
    for phrase in (
        "must carry declared memory",
        "no description by present observables",
        "by gt3 they are not definable",
        "by gt3 they are non-definable",
    ):
        assert phrase not in prose, phrase
    assert "identity continuation" in _tex("sec_06_gt3_gt4.tex")


# --- Finding 3: no blanket exactness claims ----------------------------------------------------


def test_no_blanket_exactness_claims_in_prose() -> None:
    prose = _all_prose().lower()
    for phrase in (
        "every answer is an exact computation",
        "carry no numerical error",
        "carries no numerical error",
    ):
        assert phrase not in prose, phrase


# --- Finding 6: GT4 fixtures are schematic; the "honest" twins are constant resets --------------


def _is_constant_reset(kernel, target: int) -> bool:
    return all(dict(row) == {target: Fraction(1)} for row in kernel.rows.values())


def test_gt4_honest_fixtures_are_constant_resets_and_prose_says_so() -> None:
    for builder in (benchmarks.protocol_trap_honest, benchmarks.flattenable_completed):
        package = builder()
        (continuation,) = package.continuations[("mid", "out")]
        assert _is_constant_reset(continuation.kernel, benchmarks.STATE_LEFT), builder.__name__
    for builder in (benchmarks.protocol_trap_naive, benchmarks.flattenable_raw):
        package = builder()
        (continuation,) = package.continuations[("mid", "out")]
        assert not _is_constant_reset(continuation.kernel, benchmarks.STATE_LEFT), builder.__name__
    prose = _tex("sec_06_gt3_gt4.tex")
    assert "constant reset" in prose and "regime schemata" in prose
    for phrase in ("written into the state", "once the catalog is completed"):
        assert phrase not in prose, phrase


# --- Finding 7: T-AOT-02 is an entropy-production audit, not a memory theorem -------------------


def test_gb1_gloss_describes_arrow_of_time_audit_not_memory_exclusion() -> None:
    prose = _tex("sec_06_gt3_gt4.tex")
    assert "zero entropy production" in prose
    assert "theorem excluding this" not in prose
    assert "can appear\nto have memory" not in prose


# --- Finding 9: scoreboard caption counts come from the artifact --------------------------------


def test_scoreboard_caption_counts_match_artifact() -> None:
    cells = _artifact("artifacts/gt7_constants/gt7_transfer_scores.json")["payload"]["cells"]
    scored_interval = sum(
        1
        for c in cells
        if c["target_family"] == "fa1f"
        and c["prediction_type"] == "interval"
        and c["verdict"] in ("pass", "fail")
    )
    scored_order = sum(
        1
        for c in cells
        if c["target_family"] == "fa1f"
        and c["prediction_type"] == "order_relation"
        and c["verdict"] in ("pass", "fail")
    )
    assert scored_interval == 21 and scored_order == 1
    prose = _tex("sec_08_gt7.tex")
    assert f"the {scored_interval} scored FA interval cells" in prose
    assert f"{scored_interval + scored_order} were scored" in prose


# --- Restructure: claim coverage runs over main.tex's real input graph --------------------------


def test_main_tex_input_graph_matches_section_files_on_disk() -> None:
    main = (PAPER / "main.tex").read_text(encoding="utf-8")
    inputs = re.findall(r"^\\input\{sections/([^}]+)\}", main, flags=re.M)
    assert inputs, "main.tex must \\input its sections"
    on_disk = sorted(p.stem for p in SECTIONS.glob("*.tex"))
    assert sorted(inputs) == on_disk
    assert inputs == on_disk, "sections must be input in numeric order"


# --- Round 2, finding 1: CD = 0 is a positive-mass statement, not global lumpability ------------


def test_zero_support_cd_zero_but_kernel_not_lumpable_and_full_support_positive() -> None:
    N, epsilon, tau = 2, Fraction(1, 2), 1
    kernel = build_east_kernel(N, epsilon)
    assert not is_exactly_lumpable(N, kernel, tau, l_energy)
    point_mass = {0b01: Fraction(1)}
    assert closure_deficit_float(N, kernel, point_mass, tau, l_energy) == 0.0
    full_support = east_stationary(N, epsilon)
    assert all(weight > 0 for weight in full_support.values())
    assert closure_deficit_float(N, kernel, full_support, tau, l_energy) > 0.0
    methods = _tex("sec_02_architecture_methods.tex")
    assert "positive-mass" in methods and "full support" in methods


# --- Round 2, finding 2: a closed coarsening is not an order-parameter candidate ----------------


def test_constant_readout_is_closed_but_separates_nothing() -> None:
    N, epsilon, tau = 2, Fraction(1, 2), 1
    kernel = build_east_kernel(N, epsilon)

    def constant_lens(_state: int, _N: int) -> int:
        return 0

    assert is_exactly_lumpable(N, kernel, tau, constant_lens)
    payload = _artifact("artifacts/gt3_foreclosure/lens_class_sweep.json")["payload"]
    # The constant readout agrees on both saved witness distributions (it agrees on everything),
    # so it is a closed coarsening that separates nothing: not an order-parameter candidate.
    values_h = {constant_lens(int(k), N) for k in payload["energy_level_distribution_mu"]}
    values_hprime = {constant_lens(int(k), N) for k in payload["energy_level_distribution_h_prime"]}
    assert values_h == values_hprime == {0}
    assert payload["separating_entry"]["event_id"] == "n_1"
    intro = _tex("sec_01_introduction.tex")
    assert "separates two preparations whose futures differ" in intro
    assert "would make it closed" not in intro


# --- Round 2, findings 3-5: residual gloss guards -----------------------------------------------


def test_round2_residual_gloss_guards() -> None:
    prose = _all_prose().lower()
    for phrase in (
        "computed without approximation",
        "without approximation",
        "grid temperature whose",
        "near the crossing the chain equals equilibrium",
    ):
        assert phrase not in prose, phrase
    assert "index of the grid point" in _tex("sec_01_introduction.tex")


# --- Round 2, finding 6 + figures: annotated values come from the artifacts ---------------------


def test_figure_derived_values_match_artifacts() -> None:
    figures = _figures()
    hump = figures.collect_kovacs_hump()
    assert hump["hump_height"] == pytest_approx(max(hump["trace"]) - float(Fraction(hump["e_eq"])))
    ladder = figures.collect_gt1_cd_ladder()
    for glassy, equilibrium, ratio in zip(
        ladder["glassy_cd"], ladder["equilibrium_cd"], ladder["ratios"], strict=True
    ):
        assert ratio == pytest_approx(glassy / equilibrium)
        assert ratio >= float(Fraction(ladder["margin"]))
    buyback = figures.collect_buyback()
    gap = Fraction(
        _artifact("artifacts/gt2_witnesses/kovacs_moment.json")["payload"]["witness_pairs"][0][
            "separating_entry"
        ]["abs_gap"]
    )
    assert buyback["loss"][0] == pytest_approx(float(gap**2 / 2))
    assert buyback["loss"][1] == 0.0 and buyback["loss"][2] == 0.0
    caption = _tex("sec_05_gt2_gt5.tex")
    assert "(a-b)^2/2" in caption and f"$\\approx {buyback['loss'][0]:.4f}$" in caption
    board = figures.collect_transfer_scoreboard()
    for cell in board["fa_interval_cells"]:
        assert cell["hi"] > 0
        inside = cell["lo"] <= cell["observed"] <= cell["hi"]
        inside_normalized = cell["lo"] / cell["hi"] <= cell["observed"] / cell["hi"] <= 1.0
        assert inside == inside_normalized
        assert (cell["verdict"] == "pass") == inside


def pytest_approx(value: float, rel: float = 1e-9):
    import pytest

    return pytest.approx(value, rel=rel)
