# 08 — GT6: Strict-Extension Certificate (+ GB6 Shell, GB8 Filing)

**Claim (GT6).** The predictive-structure layer T₁ (persistent packaged strata of M — "glass states" as fictive-structure records) receives a shell-local `strict` promotion verdict via F-III's generic promotion-gate classifier (T19 `PromotionGateSoundness` + T20 `StrictPromotionImpliesNonfactorization`), anchored in GT2/GT3 non-factorization witnesses. This is distinct from paper [C]'s specific `thm:strict-extension` completion-dynamics theorem, whose fuller route additionally requires material P4←P5 forcing; H2-H5 are filed as supporting diagnostics toward that fuller obligation narrative, and H4 may honestly be zero without changing the F-III T20 verdict basis.

**Primary references (this spec deliberately defers):** `../reference/C_cantor_shell.md` §9 is the complete GT6/GB6 checklist — shell declaration, six-primitive knockout mapping, Fekete-functional assessment, hypothesis-by-hypothesis discharge table, Obligation-4 gap spec, rejected route. `../reference/foundations_III.md` is the complete filing machinery: §6 (17-field bridge record, 8 gates, classifier priority, T19–T22), §4 (seven status families), §8 (AdmDomain), §§10–15 (model realizations → the GT6 filing checklist in §15). `../reference/code_randomness_cantor.md` maps [C]'s scripts to clone. This spec adds only the glass-specific decisions and the build plan.

**Grade.** Certificate-grade, shell-local, [C]-style non-claims. Single bridge T₀→T₁ only (F-III 10.7: no stacking-composition theorem exists).

---

## 1. Decisions fixed by this spec (the implementer does not re-decide)

1. **Fekete functional: route (a), relaxation-decay/transfer-operator growth**, per [C] digest §9.3's assessment (submultiplicative by construction on the finite class; Furstenberg–Kesten setting). Route (b) (integrated response) is the documented reserve; do not build it unless (a)'s shell-uniform positivity constant fails empirically.
   - Concrete a_n: Φ_n(s) = sup over shell witnesses x of the weighted transfer-operator matrix element implementing the declared relaxation function of the lens observable at horizon n, with tilt s on the declared rational grid. Per-protocol-block subadditivity with bounded-error boundary terms (constants recorded as shell hypotheses; their empirical values go in the margins columns).
2. **T₀** = the declared lens Π_std + the closed growth theory P_{T₀}(s) from (1). **T₁** = T₀ ⊕ persistent packaged strata of M: the fixed-point records of E_{τ,f} iteration labeled by their M-class content ("fictive-structure records").
3. **Strata construction:** run E_{τ,f} to saturation (H3); a stratum = a saturated prototype family stable over the declared window; its label = the predictive-class decomposition of its support. Persistence = survives the declared horizon set of GT4(d).
4. **P4←P5 forcing (H4) protocol:** the declared *conditioned annealing* family — protocols whose next leg is a declared function of the current measured panel (e.g. "hold until binned ⟨E⟩ enters cell c, then step ε"). These are legitimate declared continuations (finite lookahead on the lens, kernel form: block-diagonal switch on Σ), and they realize "packaged records feed back into the lens" exactly as real glass processing does. Count material forcing events = strata that exist only because a conditioned protocol is in the catalog (knockout comparison: catalog with vs without the conditioned family).
5. **Thresholds** (declare before running, [C]-style): knockout degradation thresholds (glass analogues of [C]'s 50%/70% rules — set after Phase-0 calibration runs on the *controls*, frozen before witness runs); Δ gap threshold (e.g. 1e-3 in the float64 reporting scale, with the exact-rational version where feasible); saturation = zero new strata for 2 consecutive iterations.

## 2. Build plan

1. **GB6 shell** (`extension/shell.py` + configs): shell membership predicate (glassy window: declared ε window + GB4 τ-window + non-equilibration criterion), ≥ 2 frozen witnesses (East N=8, N=10 recommended), exit counter (must be 0), non-claims register. Clone [C]'s report/ledger/checker stack (`validate_metadata.py` pattern).
2. **Knockout panel** (`extension/knockouts.py`): the six-primitive table from [C] digest §9.2 (P1 kernel, P2 kinetic constraint, P3 schedule, P4 lens selection, P5 packaging E_{τ,f}, P6 audit ledger). Knockouts re-run the actual simulation with the mechanism disabled and score degradations against the frozen thresholds — parity with [C]'s pilot (`run_continuous_kernel_pilot.py` re-simulates knockouts; borrow its pattern, and the row schema of the rule-based classification audit, per the corrected note in `../reference/code_randomness_cantor.md` §7). Distinct degradation signature per primitive; full-loop nondegeneracy row.
3. **Pressure closure** (`extension/pressure.py`): compute the normalized log-envelope ladder (1/n)·log Φ_n over the declared n ladder; Fekete gap = max successive difference beyond the declared n_min; publish the `tbl:pressure-closure-support` clone (Witness | size | Shell exits = 0 | Fekete gap | growth bound | margins).
4. **Strict-extension hypotheses** (`extension/strict.py`): H1 ← (3); H2 endomap report (clone `run_packaging_completion_endomap.py` semantics onto the glass E_{τ,f}); H3 saturation panel; H4 forcing counts per (1.4); H5 ← **GT1 artifact hashes** (CD > 0 = macro-admissibility obstruction via [B] `prop:cd-zero`); non-factorization ← **GT2 witness certificate hashes** (constructive; report also the non-factorization *rate* over T₀-descriptor classes for the [C] table clone).
5. **Conditional disintegration** (`extension/disintegration.py`): Δ_{T₀→T₁}(s) = P_{T₀}(s) − Σ_strata w_Σ P_Σ(s) per [C] digest §9.5; certify Δ ≥ threshold on all audited panels. **Rejected-route guard:** no per-stratum autonomy claims — strata are fiber averages; the artifact carries this as a mandatory nonclaim.
6. **GB8 filing** (`extension/filing.py`): produce the F-III records:
   - `AdmDomain` record for the KCM host (𝖧_prob) — all 19 components + 12 exclusion checks per F-III digest §AdmDomain.
   - The 17-field expanded bridge record B for T₀→T₁.
   - **Gate table — NINE gates, not eight** (an earlier draft of this doc omitted the ninth; corrected
     per `foundations_III.md` §15 section C): G_suff; **G_desc = `not_required`** — G_desc is required
     only when the bridge claims macro closure / descended dynamics *on the target*, and the glass
     bridge makes no such claim (the whole point of GT1 is that descent through Π_std fails; a required
     G_desc fed by δ₁^split(Π_std, F) ≠ ∅ would route the classifier to `failed_descent` and destroy the
     `strict` verdict). File the companion nonclaim "no autonomous macro law on T₁ is claimed"; GT1's
     CD > 0 enters as H5 evidence only. Do not conflate δ₁^split (descent defect, T7) with Δ_fact
     (strictness witness, T13) — they feed different gates. G_stab (required — strata are fixed points
     of E: δ_stab = ∅ at declared tolerance), G_ctrl, G_nosmuggle (six violation kinds checked; esp. (3)
     simulation-as-theorem and (5) P3-witness-as-P6_drive), G_vis, G_audit, G_strict (filed as the
     F-III T19/T20 `strict_pass`, fed by Δ_fact ≠ ∅ from GT2/GT3 non-factorization witnesses, not as a
     discharge of paper [C]'s `thm:strict-extension` when H4 forcing is zero), and
     **`G_locglob = not_required`** (shell-bound filing; single bridge
     only per §10.7 — no stacked or glued promotions claimed). This mirrors the T34 Cantor precedent
     (`foundations_III.md` §10.3/§15C), whose gate table also files G_desc and G_locglob `not_required`.
     The checker must validate the gate-table NAME SET is exactly these nine — no missing, extra, or
     duplicate gates — not merely that the gates present happen to pass.
   - Status assignments per the seven status families; TopDownChannelRecord + NC-TD for the P5 macro-to-micro channel (prototype selection is the declared downward channel).
   - Nonclaim register: the six shell-local non-claims of [C] digest §7.2 plus the ten T34-style filing nonclaims of `foundations_III.md` §10.3, both adapted to glass.
   - **Residual balance-law check (F-II `rem:recognition-open` item (a)):** scan the filing's residual features for a finite balance law irreducible to the six roles (candidate residuals: any conserved/ledgered quantity of the aging dynamics not filed under P1–P6); record the outcome. If found: declare the no-seventh-role ceiling, re-grade affected claims to recognition grade, report separately (proposal §6).
   - `artifacts/gt6_bridge/audit.json` + `experiments/check_gt6_filing.py` (checker: schema validity, gate-evidence presence, hash resolution, nonclaim completeness, classifier verdict reproduction — the verdict must be *recomputed* by the checker from the gate records, per F-III "an acceptance verdict is never informal").

## 3. Discharge order (forced, [C] §6)

Lawfulness (knockouts) → base closure (pressure) → H2 endomap → H3 saturation → H4 forcing (diagnostic, may be zero) → H5 obstruction (GT1 import) → non-factorization (GT2 import) → verdict `strict` via F-III T20 (not via paper [C] `thm:strict-extension` when H4 = 0; T20 then forces the explicit witness pair in the filing — assert it is present) → disintegration gap → filing + checker.

## 4. Acceptance criteria

1. Knockout table: six distinct material degradations by re-simulation, thresholds frozen pre-run, full-loop nondegeneracy green.
2. Pressure table: Fekete gap within declared bound, shell exits = 0 on all witnesses, margins positive.
3. All five hypotheses discharged with named artifacts; H5/non-factorization rows cite GT1/GT2 hashes.
4. Δ ≥ threshold on all audited panels; rejected-route nonclaim present.
5. `check_gt6_filing.py` passes: gate table complete, classifier verdict `strict` recomputed from gate records, T22-template parallel documented (the filing mirrors Toy22's structure), no-stacking respected (exactly one bridge).
