# 06 — GT4: Memory Triage (Six-Regime Kill-Test Panel)

**Claim (GT4).** The glass memory candidate is **coherent**: it survives (a) honest protocol internalization, (b) admissible completion on fixed support, (c) currentization by declared lens refinements (TNM-type T_f panels), (d) transport persistence over declared horizons; while constructed controls instantiate all five non-coherent regimes (flat / artifact_trap / flattenable / explicit_latent / dissipative) and are correctly killed.

**Anchors.** [A] §§5–6 six-regime taxonomy, statuses, robustness predicates with 0.95/0.80 thresholds (`../reference/A_holonomy_memory.md` §§11–13); F-I `thm:protocol_trap` (T-AOT-02) + D-PROT-02 + C-ACC-01 + clock-audit remark, `thm:dpi_path` (T-AOT-01 "No Fake Arrows"), T-ACC-01 + `cor:null-regime` (`../reference/foundations_I.md`); F-III T23 + countermodels CM1–CM12, esp. CM2 and CM5 (`../reference/foundations_III.md`); F-IV F9, F49.

**Critical caveat (GB1).** F-I's protocol-trap theorem hypothesis (ii) needs all phase kernels reversible w.r.t. a **common** π; Kovacs kernels K_ε are reversible w.r.t. different Gibbs π_ε. The temperature-protocol trap theorem is **new mathematics** (spec `10_new_math.md` §GB1). Until it is proved, GT4(a) ships at conditional grade with the protocol-trap discipline cited as an explicit open obligation (proposal Phase-2 fallback). The triage *computations* below do not wait for GB1 — only the theorem-grade wrapper of (a) does.

---

## 1. The candidate and the regime taxonomy

Candidate: the `kovacs_wheel` package (spec 02 §4.2–4.3). Target: regime `coherent_candidate` per [A]'s classification rules ([A] digest §12): witness ≥ 1, fiber ≥ 2, gap > 0, loop scores (0, >0), and — via GB5 — repairs *certified failed* rather than `skipped` (the glass upgrade over [A]).

The five control regimes are the thermal benchmark family of spec 02 §6. Build controls so that each is *minimal*: small N (4–6), one mechanism each, notes in `docs/results/<benchmark>.md` mirroring [A]'s note structure.

## 2. The four survival tests on the candidate

**(a) Honest protocol internalization.** Pair the candidate with its naive variant (`protocol_trap_naive`: schedule bookkeeping external). Required outcome: the naive variant's *extra* residue (if any) disappears on the honest side, while the honest candidate's residue **persists** — i.e. the candidate is not a protocol-trap artifact. Discipline: clock audit (never read structure off a stroboscopic fit; the honest package is autonomous by construction, spec 01 §7.2). Affinity audit alongside: compute the path-reversal KL Σ_T and cycle affinities (T-ACC-01 exact formulas, F-I digest §§6–7; borrow code from `six-birds-protocol-trap` per `../reference/primer_and_protocol_trap.md` §§2.5–2.6) for the candidate's loop. Expected: the Kovacs loop *does* carry schedule-induced affinity terms (different Gibbs measures) — GB1's bound classifies how much asymmetry is lawful without drive; the artifact reports Σ_T, the affinity table, and the GB1 status (proved bound vs open obligation).

**(b) Admissible completion on fixed support.** Apply the declared completions (symmetrized thermal catalogs) to the candidate: residue must persist (contrast: `flattenable_raw` control, where completion kills it). Same-support check (`support_fixation_status`) must be non-failing for every pair comparison, else the comparison is void.

**(c) Currentization by declared refinements.** The GB5 sweep restricted to T_f-type refinements (spec 05 §3): `currentization_status` never `passed` on the candidate; the `latent_memory_base` control shows the machinery detects success. This is the certified insufficiency of single-scalar fictive-temperature descriptions at the triage level (GT5 quantifies it).

**(d) Transport persistence over declared horizons.** Declare probe horizons H = {short, mid, long} (from `spectral_gaps.json`: within the GB4 window, and beyond it). Compute the transported quotients at interfaces `probe_h`: the candidate's predictive split must persist for h within the declared window (contrast: `dissipative_memory` control, where the split dies at `end`). Report the **persistence profile** — the h-indexed witness count / fiber table. The claim is horizon-relative ("not merely dissipative on the claimed timescale"), never absolute persistence.

## 3. Kill-tests on the controls

Each control must be *killed by the right test and only that test* — this is what makes the panel diagnostic rather than decorative:

| Control | Killed by | Statuses that must fire |
|---|---|---|
| `flat_control` | nothing to kill (all diagnostics 0) | flat |
| `protocol_trap_naive` | test (a) | honest counterpart flat; same-support ok |
| `flattenable_raw` | test (b) | `flattening_status: passed` |
| `latent_memory_base` | test (c) | `currentization_status: passed` |
| `dissipative_memory` | test (d) | split at `mid`, merged at `end`, class map C0↦C0, C1↦C0 |
| `kovacs_wheel` | none | all four survived; loop asymmetry present |

Cross-fire check: run *all four tests on every control* and assert the off-diagonal outcomes (e.g. completion does not kill the latent-memory control; currentization does not kill the dissipative control). The full 6×4 outcome matrix is the headline GT4 artifact.

## 4. Countermodel imports (F-III CM templates)

Instantiate at least: **CM2** ("active holonomy, no drive") as a thermal control — loop asymmetry present with null affinity audit (null-regime relaxation per `cor:null-regime`) — this is the control that keeps GT2's loop claim honest against "it's just driven"; **CM5** ("refinement worsens closure") — a declared refinement that *increases* CD — guarding the GB5 sweep against the assumption that refinements monotonically help (also [B]'s Appendix-A anti-monotonicity caution, see `../reference/B_cast_a_stone.md`). File both as additional rows of the outcome matrix with their F-III CM numbers.

## 5. Robustness layer

Per spec 02 §7: perturbation bundles, 20 trials, predicates `kovacs_persists` (0.80), `flat_cleared`/`honest_trap_cleared` (0.95), `completed_collapsed`/`explicit_latent_*`/`dissipative_persists` (0.80). Survival fractions recorded per benchmark; interpretation discipline verbatim from [A]: robustness does not upgrade the candidate's grade.

## 6. Artifacts and acceptance

- `artifacts/gt4_triage/regime_table.json` — the 6×4 (+CM rows) outcome matrix with statuses, affinity audit table, persistence profiles, robustness fractions; envelope with GB1 status flag.
- Acceptance: (1) every control lands in its designated regime and is killed only by its designated test; (2) candidate survives all four tests with statuses recorded; (3) CM2/CM5 rows present; (4) affinity audit computed with exact rationals and filed with GB1 status; (5) robustness thresholds met; (6) F-IV F9 check: no unstatused residual — every non-zero diagnostic in the table carries a status or a filed open obligation.
