# Paper claims ledger (rendered)

Generated from `paper/claims_ledger.json` by `experiments/check_claims_ledger.py
--stamp`; do not edit by hand. The JSON is the operative ledger.

Evidence manifest binding: `93e67a2deff7c660c75cfba7efe9fe5c659f984af9b89ec24f0d1c545b575a05`

## GT claims

### GT1 — Non-closure of the thermodynamic lens (East N=8, L_energy)

On the declared scope (East model, N=8, lens L_energy, tau ladder [1,2,4,8], epsilon grid 1/10..7/10, t_w=20), the closure deficit CD_tau of the aging protocol exceeds the constrained-East stationary-equilibrium baseline at every declared cell by at least the declared margin 3/2 (achieved minimum glassy-to-equilibrium CD ratio ~1.6392), and the audited delta table exceeds its declared margin 2 (achieved ratio 289/121). The structurally lumpable unconstrained control sits at exact rational CD = 0; constrained East equilibrium under L_energy is itself a nonzero stationary CD baseline (kinetic constraint, not aging), so equilibrium is NOT used as a zero control. Filed in F-II channel-status vocabulary: the P5 channel of the standard thermodynamic packaging is not active_projection as a closed packaging on this declared glassy scope. The GB2 consistency gate passes on this artifact.

- **Grade:** theorem_audited_class
- **Anchors (proposal §4):** foundations_I: D-IC-01, D-IC-02, T-IC-02, T-CL-01 (cor:closure-saturates); foundations_II: def:role-projection, def:channel-status (P5 channel not active_projection); foundations_III: T8, T6; foundations_IV: F10, F20(non-idem), F52; support: [B] Def 3.1, Props 3.2/3.5
- **Artifacts:**
  - `artifacts/gt1_cd_tables/east_n8_l_energy.json` `a0cea276116f05fcbb10844c527aac69d2027c70210a19db4753364d6c54d44e`
  - `artifacts/gt1_delta_tables/east_n8_l_energy.json` `29fbfc474de70a4a5c70f4664677df926e62c306bd52b786755aa23a379fefab`
- **Nonclaims:**
  - GT1 certificate is scoped to East N=8 and L_energy only; FA and L_panel are undone extensions.
  - The tau ladder is the declared finite ladder [1, 2, 4, 8], not the full combinatorial grid.
  - Constrained East equilibrium under L_energy is a nonzero stationary CD baseline; only the unconstrained lumpable control is exact-zero.
  - [B] benchmark-parity control is filed as skipped in this artifact because the paper-specific example chains were not ported in this remediation packet.
- **F-II §16 items:** A1, A2, A3, B1, B2, B5, D1, G1, H2
- **Paper section:** W-03

### GT2 — Kovacs witness theorem (memory as route residue, East N=10)

On the declared scope (East, N=10, kovacs_moment lens, declared epsilon grid and continuation catalog), one exact-rational split pair of preparation histories is exhibited that agrees on the current lens value while the futures differ (exact max-abs future gap > 0, exact rational arithmetic). Filed as P4 staged-dependence on the p1-witness template (F-II prop:causality-closure) - NOT a P3 route mismatch and NOT a directionality or irreversibility claim. The Phase-0 Kovacs hump search that located the witness window is filed separately as a pre-certificate control. The planned loop certificate was not built (see NEG.gt2_loop_certificate_not_built).

- **Grade:** theorem_audited_class
- **Anchors (proposal §4):** foundations_I: Def. 17, T-FOR-02 (witness language); foundations_II: prop:p1-witness template; prop:causality-closure (P4 routing); rem:p6-drive; foundations_III: T7, T12, T13, T5; foundations_IV: F2, F3, F7, F13a; support: [A] Defs 2.2-2.4, Thms 3.5-3.6 + Lean
- **Artifacts:**
  - `artifacts/gt2_witnesses/kovacs_moment.json` `321f9bffdbf1368ec764a8fcde97d569dd9f4292ee5a98a0b6f30ac9483ce7bf`
  - `artifacts/kovacs_hump_check/result.json` `9d2fcba8b060c58d73f68c13ac6cf4d8defde7ad5b133bc414be8166e1461189`
- **Nonclaims:**
  - filed as P4 staged dependence, not a directionality or irreversibility claim
  - Phase-0 Kovacs search output is a pre-certificate diagnostic, not a GT witness certificate.
  - The selected result freezes a later config but does not by itself prove a theorem-grade claim.
- **F-II §16 items:** A1, A2, A3, B1, B3, B4, B5, D1, G1, H2
- **Paper section:** W-04

### GT3 — Foreclosure of static order parameters (declared lens class)

On the declared scope (East, N=8, epsilon 1/2), all 512 definable predicates over the 9-element L_energy lens image agree on the exhibited standalone W_reflection witness pair (constructed for this sweep; not chained to the GT2.kovacs_moment certificate), while a distinguishing n_1-based readout separates it: a constructive witness that the distinguishing readout is not in Def(l_energy) - constructive exhibition, not generic counting. The field-facing sentence 'no static order parameter for glass' is licensed ONLY as the declared-class shadow of this theorem (F-II item E2), with class, catalog, and suppressed content named; it is never a scope-free impossibility.

- **Grade:** theorem_audited_class
- **Anchors (proposal §4):** foundations_I: Def. 17, lem:count-definable, T-FOR-01; foundations_II: def:threshold-attachment (channel stays below_threshold); foundations_III: T14; foundations_IV: F12, F46, F11; support: [A] Thms 3.3-3.4 + Lean uniqueness
- **Artifacts:**
  - `artifacts/gt3_foreclosure/lens_class_sweep.json` `25e78910189098978f58f5e083cd3553f42fd9eb2b94cc7818d0ed80f0f661a7`
- **Nonclaims:**
  - finite N=8 East foreclosure over Def(l_energy), not a continuum or all-lens claim
- **F-II §16 items:** A2, A3, C1, C2, E1, E2, G1, H1
- **Paper section:** W-05

### GT4 — Memory-regime triage over the declared benchmark family

Over the declared 9-member thermal benchmark family, the deterministic triage classification identifies kovacs_wheel as the sole coherent_candidate, and the five declared non-coherent regime controls (artifact_trap, dissipative, explicit_latent, flat, flattenable) are correctly killed or cleared, with protocol-trap discipline applied (raw vs cleared classifications both recorded). The triage is over the declared finite family only, not a shell-general theorem; the GB1 protocol-trap caveat remains a theorem-wrapper limitation.

- **Grade:** theorem_audited_class
- **Anchors (proposal §4):** foundations_I: T-AOT-01, T-AOT-02, T-ACC-01, cor:null-regime, D-PROT-02; foundations_II: prop:visibility, def:residual-scheme (vi)/(iii)/(viii); foundations_III: T23, CM1-CM12, TopDownChannelRecord+NC-TD; foundations_IV: F9, F49, F20 statuses; support: [A] six regimes + kill-tests
- **Artifacts:**
  - `artifacts/gt4_triage/regime_table.json` `160ed9c4bb65a8189f012fba1fb7e4a55fc17e323050437206c341c077b53619`
  - `artifacts/benchmark_suite/phase1_parity.json` `fade825187d851683d7f035f34e06b3c9ae0ded9b7b2b1afc69e6f5ab74b545d`
- **Nonclaims:**
  - GT4 triage is over the declared finite benchmark family, not a shell-general theorem.
  - The artifact promotes the Phase-1 benchmark-suite data; it does not change the underlying classification logic.
  - GB1 protocol-trap caveat remains a theorem-wrapper limitation; this table files the deterministic triage computation.
  - Phase 1 benchmark parity is a control suite, not a standalone GT4 triage certificate.
  - Dedicated GT4 regime-table promotion, if present, is filed in a separate artifact.
- **F-II §16 items:** A2, A3, B1, E1, E3, G1
- **Paper section:** W-05

### GT5 — Effective-dimension lower bound and buyback curve (East N=10)

On the declared scope (East, N=10, kovacs_moment interface, declared 2-history class), MaxFiber = 2 meets the nontriviality threshold (predictive quotient size 2 over current quotient size 1), and the buyback curve is published as a lift ledger: each added memory coordinate is a recorded, selected, non-unique lift. The shipped witness saturates at saturation_budget = 1: one added coordinate restores predictive sufficiency FOR THIS minimal two-history witness. This demonstrates the buyback mechanism and its ledger discipline; it is not a claim that one fictive-temperature-like scalar is insufficient in general.

- **Grade:** theorem_audited_class
- **Anchors (proposal §4):** foundations_I: D-IC-02 guardrail (nontriviality witness); foundations_II: prop:forgetting-lifts (each lift = added data, recorded); foundations_III: T5 (family separation); foundations_IV: F24 (8 cases); support: [A] MaxFiber; [B] Rand_B
- **Artifacts:**
  - `artifacts/gt5_dimension/max_fiber.json` `746b44e6c2f7f92364137a202f7306b6afc9e99c413fb4dd3a40d47bfd6f94c8`
  - `artifacts/gt5_dimension/buyback_curve.json` `3f3c56405847a079f48bae350b3b35e901a5731470bcb4a092bd7f682f075559`
- **Nonclaims:**
  - buyback saturation or nonsaturation is not a GB5 repair-impossibility certificate; GB5 requires a separate exhaustive repair-class sweep
  - the shipped Kovacs buyback curve is a minimal two-history witness with saturation_budget=1; it demonstrates buyback mechanics, not general single-scalar or TNM insufficiency
- **F-II §16 items:** A2, A3, C3, D1, D2, D4, G1
- **Paper section:** W-04

### GT6 — Strict-extension certificate for the audited glass shell

For the audited East glass shell (N=8, declared epsilon grid), the gate-table verdict is 'strict', with the filed basis quoted verbatim from the audit artifact: 'verdict: strict is established via F-III T19/T20 (non-factorization from GT2/GT3 witnesses). Paper [C]'s thm:strict-extension (the fuller completion-dynamics route requiring material P4<-P5 forcing) is NOT invoked: H4_forcing.material_forcing_count = 0 for this shell, filed as an honest negative sub-result, not as a satisfied hypothesis.' The knockout panel and the float64 pressure-closure diagnostic are filed alongside; H5 (macro-admissibility obstruction) cites the GT1 theorem-grade certificate. Strictness is shell-local and does not imply autonomous macro closure or drive.

- **Grade:** certificate_shell_local
- **Anchors (proposal §4):** foundations_I: T-CL-01 + anti-saturation remark; thm:meta-prim HL-META-1 case (iii); foundations_II: def:level-trichotomy, promotion records, claim grades; foundations_III: T11, T12, T19-T22, T20, T34, T24/T25 (no self-certification of the new layer); foundations_IV: F8, F24, F19, F20; support: [C] four theoremlets (full stack)
- **Anchor note:** The proposal-section-4 support cell reads '[C] four theoremlets (full stack)'; the shipped verdict is narrower: it rests on F-III T19/T20 (non-factorization) only, and paper [C]'s thm:strict-extension is not invoked (verdict_basis in artifacts/gt6_bridge/audit.json; remediation finding R-B). The paper must anchor GT6 to the narrowed basis, not the original support cell. Spectral gaps are cited as the shell-window calibration diagnostic only.
- **Artifacts:**
  - `artifacts/gt6_bridge/audit.json` `6453d0e36a5f43e0a3e7ed9f69f53e00a3c6cef7aa1ddea4019522d5670cab97`
  - `artifacts/gt6_bridge/strict_extension.json` `f5f9558e0ffa786ac8a28254e555d398eff572d2936aea89a889ea160cb7bed2`
  - `artifacts/gt6_bridge/knockouts.json` `7302945f1769aff3995cea782b6572bc5765c2c398db94088115addf0b28efeb`
  - `artifacts/gt6_bridge/pressure_closure.json` `ce66da2ec600565cd5fd869a5a3abdf10098dc0b52ecf2cf7f79eca5a06a146c`
  - `artifacts/spectral_gaps/east.json` `576de95a7de5e67c0cec532b7d1aaad310a52246330e04c4c810be21e833ae69`
- **Nonclaims:**
  - GT6 is scoped to the audited glass shell, not to all East or glassy regimes.
  - No shell-general strict-bridge theorem is claimed.
  - No broader external-class theorem is claimed beyond the frozen finite class.
  - Strictness does not imply autonomous macro closure.
  - Strictness does not imply drive; P6_drive requires the separate GB1 audit discipline.
  - The pressure gap is not a KL closure deficit unless an explicit bridge is supplied.
  - The pressure gap is not the strictness witness; GT2/GT3 provide the strictness witnesses.
  - The gap functional is a conditional disintegration on strata, not stratumwise root separation.
  - This is a model realization, not a universal strict-extension theory.
  - T1 is a packaged completion layer, not repeated application of one fixed idempotent completion.
  - Single bridge only; no stacked or glued promotions are claimed.
  - strict-extension inputs are shell-local and do not claim continuum or all-protocol closure
  - H5 and non-factorization are cited from prior artifacts, not recomputed here
  - Knockout rows are shell-local diagnostics, not shell-general strict-extension proofs.
  - P4-P6 rows are capability-loss degradations, not numeric re-simulation degradations.
  - Pressure closure is a float64 Fekete diagnostic, not an exact-rational certificate.
  - N=10 dense pressure rows may be skipped by declared threshold and are reported as such.
  - Spectral gaps are float64 diagnostics and not theorem-graded exact-rational certificates.
  - Mixing-time bounds are used for shell-window calibration only.
- **F-II §16 items:** A3, D1, D3, G1, G2, H1, H3
- **Paper section:** W-06

### GT7 — Aging constants are run-only: freeze-and-transfer protocol + scoreboard

The freeze-and-transfer protocol was executed in full with sha256 content-hash freezing (F1 readouts freeze: 6 readouts; F2 East reference; F3 pre-registration of 338 predictions - 42 interval, 2 order-relation, 294 declared no_prediction - committed before any target-family run; F4 FA and trap target runs; F5 mechanical scoring by the frozen scorer). The scoreboard is filed unedited: 8 pass, 14 fail, 294 no_prediction, 22 unobserved (338 cells). The claim is the run-only discipline plus this honest scoreboard: the aging readouts are run-only constants, not fitted scaling laws, and the prediction failures are first-class honest negatives (see NEG.gt7_transfer_failures).

- **Grade:** run_only_readout
- **Anchors (proposal §4):** foundations_I: T-FOR-01 + caveat remark; foundations_II: prop:empirical-bridge, prop:probability-closure; foundations_III: (none); foundations_IV: F42, F26, F44; support: Primer sections 5, 8
- **Artifacts:**
  - `artifacts/gt7_constants/east_reference.json` `4905b013624462549b9a4cdb18f51d0220f70be29976be461e5a8681978dcab8`
  - `artifacts/gt7_constants/fa_target.json` `f2c310018fbf57e4d5166ccbbcd616f32422fcb01ce382e1db3c9c31087348f3`
  - `artifacts/gt7_constants/trap_target.json` `671a28b4a4a9d812a1a6cb6e0083fc23ac01360c6ef5f6327b99de6560c153c2`
  - `artifacts/gt7_constants/gt7_transfer_scores.json` `37ac2b8f4bcb55cf1f2cf9f0518850a84039c3e51177d3000d0244b5ed6cc96e`
  - `registry/readouts.json` `ff1b5b85386fe90202276f4e3c09e0b4d3ee27b7cd836696376cecd4739afad4`
  - `registry/predictions_f5e2a3332a2191a2.json` `3afe026caa7491c1e8ba30e49cc4971f8156864ccbdff1cf1ccd3e95a83cf637`
  - `registry/gt7_observations.json` `105a4cfd5b17f92375ca7d260d7ada3bdb2dc2215425384fdb8f506b676e5578`
  - `experiments/score_transfer.py` `beb83ce759f656ae1b60fdecd22dc736fe682440eba338e279dab9199ad21b22`
- **Nonclaims:**
  - run-only readouts, not a fitted scaling law
  - East reference only; no transfer claim without a scored FA/trap target run and a pre-registered prediction.
  - FA target run only; scoring is deferred to the frozen transfer scorer.
  - memdim_profile and deficit_decay transfer are out of scope for this target artifact.
  - Trap target run only; scoring is deferred to the frozen transfer scorer.
  - Trap uses a declared depth observable, not East/FA spin-count energy.
  - transfer scoring is mechanical comparison against pre-registered predictions
  - score counts are not a fitted scaling law
- **F-II §16 items:** A1, A2, A3, E1, G1, H2
- **Paper section:** W-07

## GB bridges

### GB1 — Temperature-protocol-trap discipline (math demo)

GB1 records a pseudo-EPR identity plus a finite exact numerical check for the temperature-protocol-trap discipline, at recognition grade. The general theorem obligation is filed as open in the artifact payload and is not discharged; GT4's triage cites this caveat as a standing theorem-wrapper limitation.

- **Grade:** recognition — math demo; the closed general theorem remains an open obligation
- **Anchor note:** No proposal-section-4 row; specified in design/specs/10_new_math.md.
- **Artifacts:**
  - `artifacts/gb1_demo.json` `4173705a52c358bc74b51815929cb2a28c8f680b3421dafdb7633e97b051fa8e`
- **Disclosed in:** `design/specs/10_new_math.md`
- **Nonclaims:**
  - GB1 demo records a pseudo-EPR identity and finite numerical check, not a closed general theorem.
  - The open obligation remains filed in the payload and is not discharged by this artifact.
- **F-II §16 items:** G1, G2
- **Paper section:** W-05

### GB2 — Protocol-relative closure deficit (math demo)

GB2 records finite protocol-CD computations (East vs unconstrained, N=4, declared epsilon grid) with exactness reserved for the lumpability check; windowed and marginalized CD values are float64 diagnostics. Recognition-grade demo underpinning the GT1 machinery (GT1's artifact carries a passing GB2 consistency gate); not itself a GT certificate.

- **Grade:** recognition — math demo
- **Anchor note:** No proposal-section-4 row; specified in design/specs/10_new_math.md.
- **Artifacts:**
  - `artifacts/gb2_demo.json` `847f389464f9196f2315c05e3cef842efa94f201aad26f19b5dc4071e043f081`
- **Disclosed in:** `design/specs/10_new_math.md`
- **Nonclaims:**
  - GB2 demo records finite protocol-CD computations, not a GT claim certificate.
  - Windowed and marginalized CD values are float64 diagnostics; exactness is reserved for the lumpability check.
- **F-II §16 items:** G1
- **Paper section:** W-03

### GB9 — Lean-checked core and fidelity table

The vendored HolonomyMemory core plus the GlassWitness extension compile sorry-free on the pinned toolchain (leanprover/lean4:4.29.0). All 17 fidelity rows are disclosed in the canonical fidelity table using the five-value legend (11 verified, 3 narrowed/parametric, 1 typed mirror, 1 schema projection, 1 computational-evidence label), with per-theorem axiom audits. The glass instance is a typed structural mirror; no schema or trivial declaration is described as a verified proof, and CD computations are labeled deterministic computational evidence, not Lean theorems.

- **Grade:** recognition — fidelity is per-row; 'verified' rows are machine-checked Lean theorems
- **Anchor note:** No proposal-section-4 row; specified in design/specs/11_gb9_lean.md.
- **Artifacts:**
  - `artifacts/lean_fidelity_table.json` `014c387c154a27d21d86e0454c25fea4ddc7ac8ecd3e7d3ea116d6f068a296c1`
  - `lean/GlassWitness/Instance.lean` `8df214180a49c4bde6b73b456a2c34e7c32ddb4f33110f8e749a583144fa554b`
  - `lean/GlassWitness/ScopeBoundary.lean` `c70185334829fe8ad9f879a2288e90efe3d24700b8eeb5593f2de05341b62a51`
  - `lean/HolonomyMemory.lean` `ccfab89cd11646e81f9c3becb6d68c985a6008cbce859fefb7df4bfcc96602b6`
  - `lean/lean-toolchain` `e755dd42499cb1469c4acaf7503bda8009efe72bd992fe23570fd085ef46b0cb`
- **Disclosed in:** `design/specs/11_gb9_lean.md`
- **Nonclaims:**
  - The real Kovacs numeric split-pair witness is not encoded in Lean.
  - No non-vacuous PredictiveWitness, StrictRefinement, or LoopAsymmetry instance is claimed.
  - The GlassWitness instance is structural and index-based, not a real numeric package export.
- **F-II §16 items:** G1, G4
- **Paper section:** W-08

### GB10 — Empirical bridge records (kovacs_pvac, colloid_aging, spin_glass_memory)

Three empirical bridge records are filed with the full five-field bridge schema (substrate+observable, instrument with per-instrument visibility record, level map with formal-artifact hashes, threshold-witness relation, suppressed-structure nonclaims) and pass the bridge checker. Bridge-only: lab data is never presented as a realization of the formal description; measured Kovacs signatures are lab-grade witnesses via the bridge, full stop.

- **Grade:** recognition — bridge admissibility filings per F-II prop:empirical-bridge; the bridge schema has no claim_grade field
- **Anchor note:** No proposal-section-4 row; specified in design/specs/12_gb10_bridges.md.
- **Artifacts:**
  - `bridges/kovacs_pvac.json` `8015ce419a3a00e8a1b81217d0796ef53a6467db81cb774d0fa9711694087ab8`
  - `bridges/colloid_aging.json` `80bc17fe8faf4763130b74da1d7b969d1514f95969ed7fbce3c4224b5fe1c1c0`
  - `bridges/spin_glass_memory.json` `73cd3f732fbbd37b9480d0f42571d229a5afa0fc0134454e890367a21ca58439`
  - `experiments/check_bridges.py` `e1025a82d6ec9d19930f2c43a7c4d25974d93f01ae89b2955c85f8ca1174d04c`
- **Disclosed in:** `design/specs/12_gb10_bridges.md`
- **Nonclaims:**
  - No empirical-realization claim anywhere; bridges are admissibility filings only.
  - Visibility records are per instrument; no cross-instrument merge into an instrument-free statement.
- **F-II §16 items:** F1, F2, F3, G1
- **Paper section:** W-09

## Findings

### FINDING.trap_epsilon_invariance — Epsilon-invariance of the declared trap stationary distribution

The declared trap weight family multiplies every trap's base weight by a common per-epsilon scalar; since the stationary distribution satisfies pi_k proportional to 1/w_k and depends only on weight ratios, that scalar cancels exactly, so the stationary distribution is exactly epsilon-invariant (proved in exact Fraction arithmetic, regression-tested). This is known in substance in the trap-model literature (Bouchaud 1992; Monthus-Bouchaud 1996; Diezemann-Heuer 2011; Bertin-Bouchaud-Drouffe-Godreche 2003), where Arrhenius-form depth dependence avoids the cancellation. Filed as a cited design caveat on what the declared trap family can probe - NOT as a novel result.

- **Grade:** theorem_audited_class — exact lemma over the declared trap family; known in substance in the literature (cited), filed as a design caveat, not as novelty
- **Anchor note:** Proof and citations live in src/sixbirds_glass/models/trap.py (module docstring) and tests/test_models_trap.py; the declared weight family is frozen in the trap target artifact.
- **Artifacts:**
  - `artifacts/gt7_constants/trap_target.json` `671a28b4a4a9d812a1a6cb6e0083fc23ac01360c6ef5f6327b99de6560c153c2`
- **Disclosed in:** `src/sixbirds_glass/models/trap.py`, `tests/test_models_trap.py`, `design/specs/01_models.md`
- **Nonclaims:**
  - Not a novelty claim: the multiplicative-scalar cancellation is standard trap-model structure once stated; the contribution is stating and testing it for the declared family.
  - Says nothing about trap dynamics or aging trajectories; only the stationary distribution is epsilon-invariant.
- **F-II §16 items:** A2, G1
- **Paper section:** W-02

### FINDING.lean_collapse — Scope boundary: CurrentEventEquiv collapses to FuturePredictiveEquiv in RouteTransportCore

For EVERY instance of RouteTransportCore, the observe_push coherence field together with CurrentEventEquiv's universal quantification over events forces CurrentEventEquiv to imply FuturePredictiveEquiv (current_implies_future_GENERIC); consequently PredictiveWitness, StrictRefinement, and non-vacuous LoopAsymmetry cannot be instantiated in this formal core (predictiveWitness_impossible_GENERIC, strictRefinement_impossible_GENERIC; machine-checked, sorry-free). This is a genuine scope-boundary result about the formal core's expressiveness - stronger than paper [A]'s own declared scope boundary - and it is why the real Kovacs numeric witness remains exact-rational computational evidence outside Lean. Related formal territory: Kemeny-Snell lumpability (1960; Buchholz 1994) and Chu-space morphisms (Barr 1979; Pratt 1999; Parente 2024), cited in the source.

- **Grade:** theorem_audited_class — machine-checked in Lean (pinned toolchain, sorry-free, axioms audited in the fidelity table); a statement about the formal core, not about glass dynamics
- **Anchor note:** Filed in the fidelity table's scope_boundary_finding field with the three GENERIC theorem rows.
- **Artifacts:**
  - `lean/GlassWitness/ScopeBoundary.lean` `c70185334829fe8ad9f879a2288e90efe3d24700b8eeb5593f2de05341b62a51`
  - `artifacts/lean_fidelity_table.json` `014c387c154a27d21d86e0454c25fea4ddc7ac8ecd3e7d3ea116d6f068a296c1`
- **Disclosed in:** `design/reference/A_holonomy_memory.md`
- **Nonclaims:**
  - Not a claim that Kovacs memory is unformalizable; only that THIS core's coherence axioms foreclose non-vacuous witness instances.
  - Does not weaken the exact-rational computational witnesses; it explains why they are filed as computational evidence rather than Lean theorems.
- **F-II §16 items:** G1, G4
- **Paper section:** W-08

## Honest negatives

### NEG.material_forcing_absent — Material P4<-P5 forcing is absent for the audited shell

H4_forcing.material_forcing_count = 0 for the audited shell: paper [C]'s thm:strict-extension (the fuller completion-dynamics route) is therefore NOT invoked anywhere; the strict verdict rests on F-III T19/T20 alone. Filed as an honest negative sub-result, not as a satisfied hypothesis.

- **Grade:** certificate_shell_local — negative sub-result filed inside the GT6 shell-local certificate
- **Artifacts:**
  - `artifacts/gt6_bridge/strict_extension.json` `f5f9558e0ffa786ac8a28254e555d398eff572d2936aea89a889ea160cb7bed2`
  - `artifacts/gt6_bridge/audit.json` `6453d0e36a5f43e0a3e7ed9f69f53e00a3c6cef7aa1ddea4019522d5670cab97`
- **Disclosed in:** `design/specs/08_gt6_extension.md`
- **Nonclaims:**
  - Absence of material forcing in this shell is not evidence about other shells or protocols.
- **F-II §16 items:** D3, G1, G2
- **Paper section:** W-06

### NEG.gt7_transfer_failures — 14 pre-registered interval predictions failed; 22 cells unobserved

Of the 44 committed predictions (42 interval + 2 order-relation), 22 were scored against observed target cells: 8 passed and 14 failed; the other 22 targeted unobserved cells. All are filed unedited in the transfer scoreboard. The pattern is itself a filed fact: all 14 failures are FA-family interval predictions and all are one-sided high (observed value above the predicted upper bound), with 12 of 14 at the deeper mid-quench epsilon_mid = 2/5; all 22 unobserved cells are trap-family, where the exact hump search found no Kovacs hump in any of the 56 surface cells (uniform miss reason: does not start below equilibrium) - the dynamical corollary of FINDING.trap_epsilon_invariance. The failures are first-class results of the pre-registration protocol: the protocol is designed to be falsifiable, and it was.

- **Grade:** run_only_readout — negative outcomes inside the run-only GT7 filing
- **Artifacts:**
  - `artifacts/gt7_constants/gt7_transfer_scores.json` `37ac2b8f4bcb55cf1f2cf9f0518850a84039c3e51177d3000d0244b5ed6cc96e`
  - `artifacts/gt7_constants/trap_target.json` `671a28b4a4a9d812a1a6cb6e0083fc23ac01360c6ef5f6327b99de6560c153c2`
- **Disclosed in:** `paper/gap_register.md`
- **Nonclaims:**
  - Failure counts are not evidence against the run-only thesis; they are the run-only thesis operating as designed. No post-hoc reinterpretation of failed intervals is permitted.
- **F-II §16 items:** G1, H2
- **Paper section:** W-07

### NEG.gb5_repair_sweep_not_built — GB5 exhaustive repair-class sweep: not built

No exhaustive frozen-repair-class sweep exists, so no repair-impossibility certificate is claimed anywhere. Buyback saturation (GT5) is explicitly not a substitute: saturation of the shipped witness says nothing about the declared repair class.

- **Grade:** (none) — absent deliverable, disclosed as open
- **Artifacts:**
  - `artifacts/gt5_dimension/buyback_curve.json` `3f3c56405847a079f48bae350b3b35e901a5731470bcb4a092bd7f682f075559`
- **Disclosed in:** `design/specs/00_architecture.md`, `design/specs/07_gt5_dimension.md`
- **Nonclaims:**
  - 'No admissible repair exists' is never asserted at any grade.
- **F-II §16 items:** C1, C2
- **Paper section:** W-10

### NEG.gt2_loop_certificate_not_built — GT2 loop certificate: not built

The planned GT2 loop certificate (route-loop asymmetry companion to the split-pair witness) was not built; the Kovacs witness stands alone as P4 staged-dependence. Disclosed in the architecture spec and the GT2 spec.

- **Grade:** (none) — absent deliverable, disclosed as open
- **Artifacts:**
  - `artifacts/gt2_witnesses/kovacs_moment.json` `321f9bffdbf1368ec764a8fcde97d569dd9f4292ee5a98a0b6f30ac9483ce7bf`
- **Disclosed in:** `design/specs/00_architecture.md`, `design/specs/04_gt2_witnesses.md`
- **Nonclaims:**
  - No loop-asymmetry or P3 route-mismatch claim is made anywhere on GT2's behalf.
- **F-II §16 items:** B4
- **Paper section:** W-04

### NEG.gt1_b_parity_control_open — GT1 paper-[B] benchmark-parity control: open

The [B] example-chain benchmark-parity control for GT1 was not ported; the GT1 artifact files it as an explicitly skipped control with its reason. The GT1 certificate's declared scope does not depend on it; it remains an open control obligation.

- **Grade:** (none) — skipped control, filed inside the GT1 artifact
- **Artifacts:**
  - `artifacts/gt1_cd_tables/east_n8_l_energy.json` `a0cea276116f05fcbb10844c527aac69d2027c70210a19db4753364d6c54d44e`
- **Disclosed in:** `design/specs/03_gt1_nonclosure.md`
- **Nonclaims:**
  - No [B]-parity is claimed for GT1 until the control is actually run.
- **F-II §16 items:** A3
- **Paper section:** W-03

### NEG.lean_instance_structural — Lean glass instance is structural, not numeric

glassInstance is a typed, index-based structural mirror: the real Kovacs numeric split-pair witness is NOT encoded in Lean (doing so honestly was investigated and found impossible in this core - see FINDING.lean_collapse), and no non-vacuous PredictiveWitness, StrictRefinement, or LoopAsymmetry instance is claimed.

- **Grade:** recognition — scope disclosure inside the GB9 filing
- **Artifacts:**
  - `artifacts/lean_fidelity_table.json` `014c387c154a27d21d86e0454c25fea4ddc7ac8ecd3e7d3ea116d6f068a296c1`
  - `lean/GlassWitness/Instance.lean` `8df214180a49c4bde6b73b456a2c34e7c32ddb4f33110f8e749a583144fa554b`
- **Disclosed in:** `design/reference/A_holonomy_memory.md`
- **Nonclaims:**
  - The Lean track certifies the abstract core's theorems, not glass numerics.
- **F-II §16 items:** G1, G4
- **Paper section:** W-08

## Totals

| kind | rows |
|---|---|
| gt_claim | 7 |
| gb_bridge | 4 |
| finding | 2 |
| honest_negative | 6 |
| **total** | **19** |
