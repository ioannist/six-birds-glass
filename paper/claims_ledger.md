# Paper claims ledger (rendered)

Generated from `paper/claims_ledger.json` by `experiments/check_claims_ledger.py
--stamp`; do not edit by hand. The JSON is the operative ledger.

Evidence manifest binding: `56b7e2ec46338d1aada4e6302532b2986e245053745ebb56f2b677fbc4bb2b1c`

## GT claims

### GT1 — Non-closure of the thermodynamic lens (East N=8, L_energy)

On the declared scope (East model, N=8, lens L_energy, tau ladder [1,2,4,8], quench epsilon 7/10 -> 1/10 with t_w=20), the closure deficit CD_tau of the aging protocol exceeds the constrained-East stationary-equilibrium baseline at every declared horizon by at least the declared margin 3/2 (certified lower bound on the minimum ratio ~1.6392, at tau=8). Every inequality is certified in exact arithmetic: joint and conditional probabilities are exact rationals and each logarithm is enclosed by outward-rounded rational bounds, so the printed floats are illustrative only. The one-step idempotence defect of the packaging map is 1225/1936 for the cold (epsilon=1/10) quench kernel against 1225/4624 for the hot (epsilon=7/10) equilibrium kernel, an exact ratio 289/121 above the declared margin 2; the distinct prototype-retention errors (10/11 and 10/17) bound these defects. The structurally lumpable unconstrained control sits at exact rational CD = 0; constrained East equilibrium under L_energy is itself a nonzero stationary CD baseline (kinetic constraint, not aging), so equilibrium is NOT used as a zero control. Filed in F-II channel-status vocabulary: the P5 channel of the standard thermodynamic packaging is not active_projection as a closed packaging on this declared glassy scope. The GB2 consistency gate passes on this artifact.

- **Grade:** theorem_audited_class
- **Anchors (proposal §4):** foundations_I: D-IC-01, D-IC-02, T-IC-02, T-CL-01 (cor:closure-saturates); foundations_II: def:role-projection, def:channel-status (P5 channel not active_projection); foundations_III: T8, T6; foundations_IV: F10, F20(non-idem), F52; support: [B] Def 3.1, Props 3.2/3.5
- **Artifacts:**
  - `artifacts/gt1_cd_tables/east_n8_l_energy.json` `287c64d67c666ebac399a10b237a8738183e25f41de1406d18153549dbbeadab`
  - `artifacts/gt1_delta_tables/east_n8_l_energy.json` `299261b597fc0e3846c3fb8faf757001825c909fb2565a0d31947e2747c5ca73`
- **Nonclaims:**
  - GT1 certificate is scoped to East N=8, L_energy and the declared quench cell only; FA, L_panel and N=10 are undone extensions.
  - The tau ladder is the declared finite ladder [1, 2, 4, 8], not the full combinatorial grid.
  - Constrained East equilibrium under L_energy is a nonzero stationary CD baseline; only the unconstrained lumpable control is exact-zero.
  - The idempotence defect is a saturation diagnostic, not a closure criterion, and is distinct from the prototype-retention error.
  - [B] benchmark-parity control is filed as skipped in this artifact because the paper-specific example chains were not ported.
- **F-II §16 items:** A1, A2, A3, B1, B2, B5, D1, G1, H2
- **Paper section:** W-03

### GT2 — Kovacs witness theorem (memory as route residue, East N=10)

On the declared scope (East, N=10, kovacs_moment lens, declared epsilon grid and continuation catalog), one exact-rational split pair of preparation histories is exhibited that agrees on the current lens value (mean energy 20/7) while the futures differ (exact max-abs future gap > 0 on the five-step hold, exact rational arithmetic). Filed as P4 staged-dependence on the p1-witness template (F-II prop:causality-closure) - NOT a P3 route mismatch and NOT a directionality or irreversibility claim. The exported rational lookup table of this witness is checked in Lean in the corrected declared-event core (strict refinement, nonfactorization, insufficiency of the current mean); the preparation, tuning and East evolution that produce the table are exact Python evidence. The Phase-0 Kovacs hump search that located the witness window is filed separately as a pre-certificate control. No loop certificate is filed (see NEG.gt2_loop_certificate_not_built).

- **Grade:** theorem_audited_class
- **Anchors (proposal §4):** foundations_I: Def. 17, T-FOR-02 (witness language); foundations_II: prop:p1-witness template; prop:causality-closure (P4 routing); rem:p6-drive; foundations_III: T7, T12, T13, T5; foundations_IV: F2, F3, F7, F13a; support: [A] Defs 2.2-2.4, Thms 3.5-3.6 + Lean
- **Artifacts:**
  - `artifacts/gt2_witnesses/kovacs_moment.json` `321f9bffdbf1368ec764a8fcde97d569dd9f4292ee5a98a0b6f30ac9483ce7bf`
  - `artifacts/kovacs_hump_check/result.json` `9d2fcba8b060c58d73f68c13ac6cf4d8defde7ad5b133bc414be8166e1461189`
  - `lean/GlassWitness/NumericN10.lean` `5cd5de8216545b5aaa6afc6f0bf5ae24582e386dfe5d36b1a06285f321d69d6e`
- **Nonclaims:**
  - filed as P4 staged dependence, not a directionality or irreversibility claim
  - Only the mean energy is matched at the crossing; the full energy laws of the two histories differ.
  - Lean checks the exported rational table and its logical consequences, not the East kernel evolution that produced it.
  - Phase-0 Kovacs search output is a pre-certificate diagnostic, not a GT witness certificate.
  - The selected result freezes a later config but does not by itself prove a theorem-grade claim.
- **F-II §16 items:** A1, A2, A3, B1, B3, B4, B5, D1, G1, H2
- **Paper section:** W-04

### GT3 — Foreclosure of static order parameters (declared lens class)

On the declared scope (East, N=8, epsilon 1/2), all 512 definable predicates over the 9-element L_energy lens image agree on the exhibited standalone W_reflection witness pair (constructed for this sweep; not chained to the GT2.kovacs_moment certificate), while a distinguishing n_1-based readout separates it under the identity continuation (exact gap 169/1536): a constructive witness that the distinguishing readout is not in Def(l_energy) - constructive exhibition, not generic counting. The field-facing sentence 'no static order parameter for glass' is licensed ONLY as the declared-class shadow of this theorem (F-II item E2), with class, catalog, and suppressed content named; it is never a scope-free impossibility. The two histories have identical complete energy laws, so every descriptor computed from the energy law agrees on them; GT6 supplies the same full-law match for two preparations of an aging run, separated by the East dynamics.

- **Grade:** theorem_audited_class
- **Anchors (proposal §4):** foundations_I: Def. 17, lem:count-definable, T-FOR-01; foundations_II: def:threshold-attachment (channel stays below_threshold); foundations_III: T14; foundations_IV: F12, F46, F11; support: [A] Thms 3.3-3.4 + Lean uniqueness
- **Artifacts:**
  - `artifacts/gt3_foreclosure/lens_class_sweep.json` `25e78910189098978f58f5e083cd3553f42fd9eb2b94cc7818d0ed80f0f661a7`
- **Nonclaims:**
  - finite N=8 East foreclosure over Def(l_energy), not a continuum or all-lens claim
- **F-II §16 items:** A2, A3, C1, C2, E1, E2, G1, H1
- **Paper section:** W-05

### GT4 — Memory-regime triage over the declared benchmark family

Over the declared 9-member benchmark family of small structural (bit-carrier) packages, the deterministic exact triage classification identifies kovacs_wheel as the sole coherent_candidate, and the five declared non-coherent regime controls (artifact_trap, dissipative, explicit_latent, flat, flattenable) are correctly killed or cleared, with protocol-trap discipline applied (raw vs cleared classifications both recorded). The cleared protocol-trap twin exposes the toy clock label in the current readout while preserving every future; the completed flattenable twin averages the declared two-state orbit on the same support. The triage is over the declared finite family only, not a shell-general theorem; the GB1 protocol-trap caveat remains a theorem-wrapper limitation.

- **Grade:** theorem_audited_class
- **Anchors (proposal §4):** foundations_I: T-AOT-01, T-AOT-02, T-ACC-01, cor:null-regime, D-PROT-02; foundations_II: prop:visibility, def:residual-scheme (vi)/(iii)/(viii); foundations_III: T23, CM1-CM12, TopDownChannelRecord+NC-TD; foundations_IV: F9, F49, F20 statuses; support: [A] six regimes + kill-tests
- **Artifacts:**
  - `artifacts/gt4_triage/regime_table.json` `b9ff2b977e8e947c9138d4d60a4c9588fa8dbfacd6dc902a97249978d40fd6d5`
  - `artifacts/benchmark_suite/phase1_parity.json` `22da4c06b075c66f57f8a55c058df15744dcb6f75d107deef3a8de42388bf07f`
- **Nonclaims:**
  - GT4 triage is over the declared finite benchmark family, not a shell-general theorem.
  - The fixtures are structural toys; they do not certify a thermal Kovacs coherence theorem or an exhaustive repair-class sweep.
  - Robustness fractions cover the three declared structural perturbations; they are not probabilistic confidence guarantees.
  - GB1 protocol-trap caveat remains a theorem-wrapper limitation; this table files the deterministic triage computation.
  - Phase 1 benchmark parity is a control suite, not a standalone GT4 triage certificate.
- **F-II §16 items:** A2, A3, B1, E1, E3, G1
- **Paper section:** W-05

### GT5 — Effective-dimension lower bound and buyback curve (East N=10)

On the declared scope (East, N=10, kovacs_moment interface, declared 2-history class), MaxFiber = 2 meets the nontriviality threshold (predictive quotient size 2 over current quotient size 1), and the buyback curve is published as a lift ledger: each added memory coordinate is a recorded, selected, non-unique lift. The loss is the in-carrier sum of the two unit-weight squared errors under group-mean prediction. The shipped witness saturates at saturation_budget = 1: each of the three declared scalars (T_f, D, n_1) restores predictive sufficiency FOR THIS minimal two-history witness. On the GT6 full-energy-law pair the energy-derived T_f difference is exactly 0, while D or n_1 alone still resolves the pair at budget 1. This demonstrates the buyback mechanism and its ledger discipline; it is not a claim that one fictive-temperature-like scalar is insufficient in general.

- **Grade:** theorem_audited_class
- **Anchors (proposal §4):** foundations_I: D-IC-02 guardrail (nontriviality witness); foundations_II: prop:forgetting-lifts (each lift = added data, recorded); foundations_III: T5 (family separation); foundations_IV: F24 (8 cases); support: [A] MaxFiber; [B] Rand_B
- **Artifacts:**
  - `artifacts/gt5_dimension/max_fiber.json` `da6ecf8908baf0a2d65e677113882e4ec7e9fbc359d7c96e269e0c16f798de84`
  - `artifacts/gt5_dimension/buyback_curve.json` `5a52aef79c46179740f51304a896ff2f2c5ff635930d00bc77fca3dfdf7c3a37`
  - `math/gt6_energy_mixture_witness.json` `e2b43fdc8a52dd555b71247adb120739dbd017c80743e3bdfa290caecbc8350b`
- **Nonclaims:**
  - buyback saturation or nonsaturation is not a GB5 repair-impossibility certificate; GB5 requires a separate exhaustive repair-class sweep
  - the shipped Kovacs buyback curve is a minimal two-history witness with saturation_budget=1; it demonstrates buyback mechanics, not general single-scalar or TNM insufficiency
  - Loss is exact in-carrier sum squared error; no held-out generalization claim.
  - MaxFiber=2 does not lower-bound the number of real-valued coordinates needed to resolve memory in general.
- **F-II §16 items:** A2, A3, C3, D1, D2, D4, G1
- **Paper section:** W-04

### GT6 — Predictive layer strictly extends the full current energy law (audited N=8 shell)

On the audited East shell (N=8, wall-up, equilibrium at epsilon 7/10, 20 quench steps at 1/10, then epsilon 2/5), two lawful randomized-stopping preparations h_+ and h_- (convex mixtures of stopping times 0..9 chosen from a null vector of the ten current energy-law columns only) have identical full current energy laws, exactly, while their future mean energies differ at every horizon tau = 1..21 (exact rational gaps, the smallest ~1.49e-10). By F-III T12/T13 the predictive object map therefore does not factor through the complete current energy law: object-map verdict strict. Consequently all 512 energy predicates and every descriptor computed from the current energy law (including the energy-derived T_f) fail future sufficiency on this pair. Replacing only the probe kernel by the unconstrained heat bath makes every future gap exactly 0. The exported tables are checked in Lean (EnergyN8); preparation and evolution are exact Python. The original strict-extension filing verdict is failed (see NEG.gt6_original_filing_failed); paper [C]'s thm:strict-extension is NOT invoked, and T19/T20 are not used to supply missing gates.

- **Grade:** certificate_shell_local
- **Anchors (proposal §4):** foundations_I: T-CL-01 + anti-saturation remark; thm:meta-prim HL-META-1 case (iii); foundations_II: def:level-trichotomy, promotion records, claim grades; foundations_III: T11, T12, T19-T22, T20, T34, T24/T25 (no self-certification of the new layer); foundations_IV: F8, F24, F19, F20; support: [C] four theoremlets (full stack)
- **Anchor note:** The proposal-section-4 support cell reads '[C] four theoremlets (full stack)'; the shipped result is narrower: object-map strictness via F-III T12/T13 on the full-energy-law split pair, with the original filing verdict failed (G_stab) and paper [C]'s thm:strict-extension not invoked (verdict_basis in artifacts/gt6_bridge/audit.json). Spectral gaps are cited as the shell-window calibration diagnostic only.
- **Artifacts:**
  - `artifacts/gt6_bridge/audit.json` `f90170ec0bd98b32a6c910a855ba92599bfd7ad8fa5fa930c08a04ddcb7ee82e`
  - `math/gt6_energy_mixture_witness.json` `e2b43fdc8a52dd555b71247adb120739dbd017c80743e3bdfa290caecbc8350b`
  - `artifacts/gt6_bridge/strict_extension.json` `83603ae6bd44b85dcee00a82ab0583a20c6944efc065d0fe91d0df5b5ed3cfe5`
  - `lean/GlassWitness/EnergyN8.lean` `f242addad9b0a4766585059d7d35233844908cb16f4d91ce661c79cad26b5f47`
  - `artifacts/spectral_gaps/east.json` `576de95a7de5e67c0cec532b7d1aaad310a52246330e04c4c810be21e833ae69`
- **Nonclaims:**
  - GT6 is scoped to the audited glass shell, not to all East or glassy regimes.
  - No shell-general strict-bridge theorem is claimed.
  - The two sources are independent random stopping mixtures, an explicit carrier extension.
  - Finite-window separation at horizons 1..21 does not imply multiple exact packaging fixed points, all-time persistence, or a large-N statement.
  - The tiny separating gap does not establish experimental detectability.
  - Strictness does not imply autonomous macro closure.
  - Strictness does not imply drive; P6_drive requires the separate GB1 audit discipline.
  - The pressure gap is not the strictness witness; the actual N8 energy-law split is.
  - This is a model realization, not a universal strict-extension theory.
  - Single bridge only; no stacked or glued promotions are claimed.
  - Spectral gaps and the legacy mixing-time field are window-calibration diagnostics, not proved total-variation bounds.
- **F-II §16 items:** A3, D1, D3, G1, G2, H1, H3
- **Paper section:** W-06

### GT7 — Aging constants are run-only: freeze-and-transfer protocol + scoreboard

The freeze-and-transfer protocol was executed with sha256 content-hash freezing (F1 readouts freeze: 6 readouts; F2 East reference; F3 pre-registration of 338 predictions - 42 interval, 2 order-relation, 294 declared no_prediction - whose registry pins the hashes of the frozen readouts, the East reference and the scoring script; F4 FA and trap target runs; F5 mechanical scoring by the frozen scorer). Scored transfer covers the three Kovacs-hump readouts (t_K, t_peak, hump height); interval rescaling uses target-kernel spectral calibration, not target hump outcomes. The scoreboard is filed unedited: 8 pass, 14 fail, 294 no_prediction, 22 unobserved (338 cells). The content hashes certify which bytes were frozen and scored; they do not by themselves certify the chronological order of the stages, and the registry's own freeze note records that the planned per-stage commits were not made. The claim is the run-only discipline plus this honest scoreboard: the aging readouts are run-only constants, not fitted scaling laws, and the prediction failures are first-class honest negatives (see NEG.gt7_transfer_failures).

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
  - 'Run-only' is a procedural grade; no per-readout same-current, different-readout nonfactorization witness is claimed for the GT7 readouts.
  - Hash integrity establishes the frozen bytes, not chronological preregistration.
  - memdim_profile and deficit_decay transfer are out of scope; scored transfer covers hump readouts only.
  - Trap uses a declared depth observable, not East/FA spin-count energy.
  - transfer scoring is mechanical comparison against pre-registered predictions
  - score counts are not a fitted scaling law
- **F-II §16 items:** A1, A2, A3, E1, G1, H2
- **Paper section:** W-07

## GB bridges

### GB1 — Temperature-protocol-trap discipline (math demo)

GB1 records, at recognition grade, the temperature-protocol version of the protocol-trap audit. The candidate-measure pseudo-EPR identity holds. The uncorrected candidate-measure expression is NOT a general stationary upper bound: an exact rational three-state counterexample with a reversible clock and common energy function exceeds it by more than 9.5e-8, with certified logarithm enclosures. A corrected stationary budget, adding an explicit Dobrushin-contraction residual osc(b) k TV(hat_mu P, hat_mu)/(1-D_k), is proved in the proof note; it recovers the published zero-EPR conclusion for a common Gibbs law and a reversible clock. No bound of this form holds for arbitrary initial laws (transient counterexample). The shipped three-state demonstration is a float64 numerical check. GT4's triage cites GB1 as a standing theorem-wrapper limitation.

- **Grade:** recognition — math demo plus proof note; the uncorrected candidate bound is refuted and a corrected stationary budget is proved, while no transient bound is claimed
- **Anchor note:** No proposal-section-4 row; specified in design/specs/10_new_math.md.
- **Artifacts:**
  - `artifacts/gb1_demo.json` `4173705a52c358bc74b51815929cb2a28c8f680b3421dafdb7633e97b051fa8e`
  - `math/gb1_temperature_trap.md` `92e093b33e6c7917ef0b2b981fd5c705f06c739104d9d4e77e1644e4893dfc3f`
  - `math/gb1_stationary_counterexample.json` `f2d3786ef57ab6b1ea6b4f85b0c10b154b4e9a3544c9eb37d26850d4d3a4e7d3`
- **Disclosed in:** `design/specs/10_new_math.md`
- **Nonclaims:**
  - GB1 is a recognition-grade demonstration and proof note, not a GT certificate.
  - The corrected budget is stationary only; no transient or arbitrary-initial-law bound is claimed.
  - The three-state demonstration in the artifact is float64, not exact.
  - The artifact payload records the general inequality as an open obligation; the counterexample certificate refutes its uncorrected stationary form and the proof note proves the corrected stationary budget.
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

Three Lean developments compile sorry-free on the pinned toolchain (leanprover/lean4:4.29.0): the vendored legacy HolonomyMemory core, the corrected DeclaredMemory core (adapted from the upstream route-transport development by namespace renaming only), and this project's GlassWitness extension. All 96 live theorems carry per-theorem axiom reports matching the stored audit, with no axioms beyond propext, Classical.choice and Quot.sound and no native_decide, sorry or custom axiom. The 97-row fidelity table (96 theorems plus one computational-evidence row) uses the five-value legend: 70 verified, 25 narrowed/parametric (finite rational lookup witnesses and their generic constructors), 1 schema projection, 1 computational evidence only (full East preparation, stopping-mixture construction and evolution, which remain exact Python). No schema or trivial declaration is described as a verified proof, and CD computations are not Lean theorems.

- **Grade:** recognition — fidelity is per-row; 'verified' rows are machine-checked Lean theorems
- **Anchor note:** No proposal-section-4 row; specified in design/specs/11_gb9_lean.md.
- **Artifacts:**
  - `artifacts/lean_fidelity_table.json` `712fa267299cef1fce505d5b88bb7689edac6f3cadbcdc932e371592a24ce78a`
  - `math/lean_axiom_audit.json` `af318aeced5c67701e621e0051464e2f1bb5e083f85fb2de58cf8f607e8b2288`
  - `math/declared_memory_provenance.json` `cbae838e71b7c48004a656a84d5c6c1ee527172a85d4f9ad007df69e8fa3cefe`
  - `lean/GlassWitness/Instance.lean` `8df214180a49c4bde6b73b456a2c34e7c32ddb4f33110f8e749a583144fa554b`
  - `lean/GlassWitness/ScopeBoundary.lean` `b29d612b26eddaa25183177e66a480e4b317ebd3e7794e16f1776a1e8ac08e11`
  - `lean/HolonomyMemory.lean` `ccfab89cd11646e81f9c3becb6d68c985a6008cbce859fefb7df4bfcc96602b6`
  - `lean/DeclaredMemory.lean` `1267cdb123fd0cc1750cd4e92f1bd09f85fa6c28791e4c2e38e17cd549bac3a4`
  - `lean/lean-toolchain` `e755dd42499cb1469c4acaf7503bda8009efe72bd992fe23570fd085ef46b0cb`
- **Disclosed in:** `design/specs/11_gb9_lean.md`
- **Nonclaims:**
  - Full East kernel evolution, preparation and tuning are exact Python evidence, not Lean computations.
  - Lean's numeric strictness concerns the exported finite observation tables.
  - No shell-general, asymptotic or packaging-fixed-point theorem is mechanized.
  - The legacy glassInstance remains a structural index-based instance.
- **F-II §16 items:** G1, G4
- **Paper section:** W-08

### GB10 — Empirical bridge records (kovacs_pvac, colloid_aging, spin_glass_memory)

Three empirical bridge records are filed with the full five-field bridge schema (substrate+observable, instrument with per-instrument visibility record, level map with formal-artifact hashes, threshold-witness relation, suppressed-structure nonclaims) and pass the bridge checker. Several numeric thresholds and source-precision fields are explicitly marked pending source verification. Bridge-only: lab data is never presented as a realization of the formal description; a measured Kovacs signature that meets a completed threshold would be a lab-grade witness via the bridge, full stop.

- **Grade:** recognition — bridge admissibility filings per F-II prop:empirical-bridge; the bridge schema has no claim_grade field
- **Anchor note:** No proposal-section-4 row; specified in design/specs/12_gb10_bridges.md.
- **Artifacts:**
  - `bridges/kovacs_pvac.json` `df5b7a28ad725d67ba52a2206e35b5592f7cf474ada13e33dc521b51f212828a`
  - `bridges/colloid_aging.json` `80bc17fe8faf4763130b74da1d7b969d1514f95969ed7fbce3c4224b5fe1c1c0`
  - `bridges/spin_glass_memory.json` `a89a4a849a3cc0e956fc3ec583e133a6fab5f1404034429ea327499f378b2b33`
  - `experiments/check_bridges.py` `e1025a82d6ec9d19930f2c43a7c4d25974d93f01ae89b2955c85f8ca1174d04c`
- **Disclosed in:** `design/specs/12_gb10_bridges.md`
- **Nonclaims:**
  - No empirical-realization claim anywhere; bridges are admissibility filings only.
  - Visibility records are per instrument; no cross-instrument merge into an instrument-free statement.
  - Fields marked pending_source are not verified thresholds.
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
  - Not a trap-literature no-go theorem: Arrhenius-form trap families can show Kovacs memory.
- **F-II §16 items:** A2, G1
- **Paper section:** W-02

### FINDING.lean_collapse — Scope boundary: CurrentEventEquiv collapses to FuturePredictiveEquiv in RouteTransportCore

For EVERY instance of the legacy RouteTransportCore, the observe_push coherence field together with CurrentEventEquiv's universal quantification over events forces CurrentEventEquiv to imply FuturePredictiveEquiv (current_implies_future_GENERIC); consequently the predictive-to-current map is injective and PredictiveWitness, StrictRefinement and LoopAsymmetry cannot be instantiated in that core (predictiveWitness_impossible_GENERIC, strictRefinement_impossible_GENERIC, predictiveToCurrent_injective_GENERIC, loopAsymmetry_impossible_GENERIC; machine-checked, sorry-free). This is a scope-boundary result about the legacy core's expressiveness - stronger than paper [A]'s own declared scope boundary. The corrected DeclaredMemory core removes the collapse premise and admits the non-vacuous numeric lookup witnesses (GB9). Related formal territory: Kemeny-Snell lumpability (1960; Buchholz 1994) and Chu-space morphisms (Barr 1979; Pratt 1999; Parente 2024), cited as analogy.

- **Grade:** theorem_audited_class — machine-checked in Lean (pinned toolchain, sorry-free, axioms audited in the fidelity table); a statement about the formal core, not about glass dynamics
- **Anchor note:** Filed in the fidelity table's scope_boundary_finding field with the five GENERIC theorem rows.
- **Artifacts:**
  - `lean/GlassWitness/ScopeBoundary.lean` `b29d612b26eddaa25183177e66a480e4b317ebd3e7794e16f1776a1e8ac08e11`
  - `artifacts/lean_fidelity_table.json` `712fa267299cef1fce505d5b88bb7689edac6f3cadbcdc932e371592a24ce78a`
- **Disclosed in:** `design/reference/A_holonomy_memory.md`
- **Nonclaims:**
  - Not a claim that Kovacs memory is unformalizable; only that the legacy core's coherence axioms foreclose non-vacuous witness instances.
  - Does not weaken the exact-rational computational witnesses.
- **F-II §16 items:** G1, G4
- **Paper section:** W-08

### FINDING.gt6_pressure_limits — Pressure on the GT6 shell: certified limit, zero conditional gap, finite contrast

For the tilted East transfer operator on the GT6 shell (N=8, epsilon=2/5, tilt 1/5), positive comparison vectors with exact exp/log interval arithmetic bound the limiting Fekete pressure in [1.039322, 1.039618]. Because some power of the tilted kernel is strictly positive, every nonzero initial law has this same limiting pressure, so conditioning only the initial law on energy fibers yields an exactly zero infinite-time weighted gap. With the original dynamics, the finite-time Jensen contrast is certified at least 1/1000 for every horizon n=1..8, but it is already present for the stationary comparison law and is not a glass-specific witness. Killing paths on energy-fiber exit gives a survival-pressure contrast certified above 1/2 (~0.6795); killing changes the dynamics and is not initial-law conditioning.

- **Grade:** theorem_audited_class — exact interval certificate on the declared operator; the zero-limit statement is a proof for primitive finite kernels
- **Artifacts:**
  - `math/gt6_pressure_certificate.json` `03ce6a60bbdd32dd6f1948f86e7085788ee1b86006370ffaf332f44d71ca3cf2`
  - `math/gt6_pressure_bridge.tex` `3f6cfbde5c1e2476f435545ca9198f35f039df9544a93803efa78e13a1ad309e`
  - `artifacts/gt6_bridge/pressure_closure.json` `65a549f6d4f7962610b02786aa0d29e2132017a4c41a3dd5e4988c73c723aa33`
- **Disclosed in:** `math/gt6_pressure_bridge.tex`
- **Nonclaims:**
  - No positive infinite-time gap is claimed for initial-law conditioning.
  - The finite Jensen contrast is not a glass-specific strictness witness or a KL closure deficit.
  - The killed survival contrast does not discharge a conditional-disintegration premise.
  - Finite-ladder endpoints in the pressure-closure table are float diagnostics, not limiting pressures.
- **F-II §16 items:** D3, G1, G2
- **Paper section:** W-06

## Honest negatives

### NEG.material_forcing_absent — Material P4<-P5 forcing is absent for the audited shell

H4_forcing.material_forcing_count = 0 for the audited shell: paper [C]'s thm:strict-extension (the fuller completion-dynamics route) is therefore NOT invoked anywhere; GT6's object-map strictness rests on F-III T12/T13 applied to the actual split pair. Filed as an honest negative sub-result, not as a satisfied hypothesis.

- **Grade:** certificate_shell_local — negative sub-result filed inside the GT6 shell-local certificate
- **Artifacts:**
  - `artifacts/gt6_bridge/strict_extension.json` `83603ae6bd44b85dcee00a82ab0583a20c6944efc065d0fe91d0df5b5ed3cfe5`
  - `artifacts/gt6_bridge/audit.json` `f90170ec0bd98b32a6c910a855ba92599bfd7ad8fa5fa930c08a04ddcb7ee82e`
- **Disclosed in:** `design/specs/08_gt6_extension.md`
- **Nonclaims:**
  - Absence of material forcing in this shell is not evidence about other shells or protocols.
- **F-II §16 items:** D3, G1, G2
- **Paper section:** W-06

### NEG.gt6_original_filing_failed — GT6 original strict-extension filing: verdict failed

The original GT6 promotion filing (bridge record, gate table, knockout panel) does not pass: its required stability gate G_stab asks for multiple fixed-point strata of the packaging map, but at epsilon=2/5 and tau=1 the packaging kernel is irreducible and preserves the Gibbs law, so it has exactly one stationary probability law (maximum prototype retention error 5/7). Saturation of reached support labels does not certify fixed points. The knockout panel does not certify full-loop lawfulness: P1-P3 are numeric ablations, P4-P6 are capability-loss rows, P5 uses an N=8 packaging diagnostic and P6 an auxiliary three-state system with a two-phase clock. Semantic AdmDomain exclusions remain pending. The filed object-map strictness (GT6) is unaffected; restoring the full filing would need a different completion or limit construction.

- **Grade:** certificate_shell_local — negative verdict filed inside the GT6 shell-local audit
- **Artifacts:**
  - `artifacts/gt6_bridge/audit.json` `f90170ec0bd98b32a6c910a855ba92599bfd7ad8fa5fa930c08a04ddcb7ee82e`
  - `artifacts/gt6_bridge/strict_extension.json` `83603ae6bd44b85dcee00a82ab0583a20c6944efc065d0fe91d0df5b5ed3cfe5`
  - `artifacts/gt6_bridge/knockouts.json` `209aac1e9f3fb88890b5b28771a711f7264735419f4e6883d465897a828ca20b`
- **Disclosed in:** `math/audit_repair_options.tex`, `design/specs/08_gt6_extension.md`
- **Nonclaims:**
  - Finite predictive persistence is not used to mark the fixed-point stability gate as passed.
  - No full-loop lawfulness or six-primitive causal activity is claimed.
- **F-II §16 items:** D3, G1, G2, H3
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
  - `artifacts/gt5_dimension/buyback_curve.json` `5a52aef79c46179740f51304a896ff2f2c5ff635930d00bc77fca3dfdf7c3a37`
- **Disclosed in:** `design/specs/00_architecture.md`, `design/specs/07_gt5_dimension.md`
- **Nonclaims:**
  - 'No admissible repair exists' is never asserted at any grade.
- **F-II §16 items:** C1, C2
- **Paper section:** W-10

### NEG.gt2_loop_certificate_not_built — GT2 loop certificate: not built

The planned GT2 loop certificate (route-loop asymmetry companion to the split-pair witness) is not filed. A tuned real East loop returns the current mean exactly, but the declared history carrier it generates does not close within six rounds (14 histories), so no quotient loop action is certified; a constant-temperature control loop scores zero on both quotients. The Kovacs witness stands alone as P4 staged-dependence.

- **Grade:** (none) — absent deliverable, disclosed as open
- **Artifacts:**
  - `artifacts/gt2_witnesses/kovacs_moment.json` `321f9bffdbf1368ec764a8fcde97d569dd9f4292ee5a98a0b6f30ac9483ce7bf`
- **Disclosed in:** `design/specs/00_architecture.md`, `design/specs/04_gt2_witnesses.md`, `tests/test_pipeline_kovacs_loop.py`
- **Nonclaims:**
  - No loop-asymmetry or P3 route-mismatch claim is made anywhere on GT2's behalf.
- **F-II §16 items:** B4
- **Paper section:** W-04

### NEG.gt1_b_parity_control_open — GT1 paper-[B] benchmark-parity control: open

The [B] example-chain benchmark-parity control for GT1 was not ported; the GT1 artifact files it as an explicitly skipped control with its reason. The GT1 certificate's declared scope does not depend on it; it remains an open control obligation.

- **Grade:** (none) — skipped control, filed inside the GT1 artifact
- **Artifacts:**
  - `artifacts/gt1_cd_tables/east_n8_l_energy.json` `287c64d67c666ebac399a10b237a8738183e25f41de1406d18153549dbbeadab`
- **Disclosed in:** `design/specs/03_gt1_nonclosure.md`
- **Nonclaims:**
  - No [B]-parity is claimed for GT1 until the control is actually run.
- **F-II §16 items:** A3
- **Paper section:** W-03

### NEG.lean_instance_structural — Lean checks witness tables, not East dynamics

The Lean witnesses are finite rational lookup tables exported from the exact Python computation: Lean checks the stated rational inequalities and their consequences in the corrected core, but does not compute the East kernel, the preparations, the randomized-stop tuning, the null-vector selector or the equality of the two current energy laws (verified in exact Python before export). The legacy glassInstance remains a typed, index-based structural mirror.

- **Grade:** recognition — scope disclosure inside the GB9 filing
- **Artifacts:**
  - `artifacts/lean_fidelity_table.json` `712fa267299cef1fce505d5b88bb7689edac6f3cadbcdc932e371592a24ce78a`
  - `lean/GlassWitness/Instance.lean` `8df214180a49c4bde6b73b456a2c34e7c32ddb4f33110f8e749a583144fa554b`
- **Disclosed in:** `design/reference/A_holonomy_memory.md`
- **Nonclaims:**
  - The Lean track certifies the abstract cores' theorems and the exported tables, not glass numerics end to end.
- **F-II §16 items:** G1, G4
- **Paper section:** W-08

## Totals

| kind | rows |
|---|---|
| gt_claim | 7 |
| gb_bridge | 4 |
| finding | 3 |
| honest_negative | 7 |
| **total** | **21** |
