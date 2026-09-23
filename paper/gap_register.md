# Gap register — Phase 5 close-vs-disclose triage

One entry per known open item. Decisions are made against the standing Phase 5 rule
(`design/paper_plan.md` §P5-03): disclose rather than build, unless a core paper claim would
silently depend on the gap. Every entry engages the strongest argument for the opposite decision.
Ledger row ids refer to `paper/claims_ledger.json`.

### GAP-1 — GB5 exhaustive repair-class sweep not built
- Status: OPEN — no frozen-repair-class witness ledger exists, so no repair-impossibility
  certificate of any grade.
- Decision: DISCLOSE
- Justification: The strongest argument for closing is that GB5 is the natural "converse" to GT5
  (buyback shows one added coordinate suffices for the shipped witness; GB5 would bound what NO
  admissible repair can do). But no shipped claim quantifies over a repair class: GT5's artifact
  carries the explicit nonclaim that buyback saturation is not a repair-impossibility certificate,
  and F-II item C2 licenses exactly this posture (strengthenings beyond the declared repair class
  are reported separately or not at all). Building GB5 would be new science — an exhaustive sweep
  over a class that has never been frozen — squarely outside Phase 5.
- Paper placement: W-10 discussion (open-obligations table); nonclaim restated in W-04 (GT5).
- What closing it would take: freeze a finite repair class (declared coordinate-addition schemas),
  enumerate it exhaustively, and file a per-member witness ledger — a full GT-scale packet.
- Ledger row: NEG.gb5_repair_sweep_not_built, GT5.

### GAP-2 — GT2 loop certificate not built
- Status: OPEN — the split-pair witness shipped; the planned route-loop companion certificate did
  not.
- Decision: DISCLOSE
- Justification: The strongest argument for closing is that the loop certificate was in the
  original GT2 spec, so its absence looks like an unfinished deliverable rather than a scope
  decision. But the GT2 claim as filed (and as worded in the ledger) is complete without it: P4
  staged-dependence needs exactly the split pair, and F-II item B3 explicitly forbids reading the
  witness as route/loop content anyway. The Lean track independently shows (FINDING.lean_collapse)
  that non-vacuous loop asymmetry is unwitnessable in the formal core, so a computational loop
  certificate would also need new formal footing — new science, not paper prep. The absence is
  already disclosed in the architecture and GT2 specs.
- Paper placement: W-04 (GT2 scope box); W-10 open-obligations table.
- What closing it would take: define the loop object over the declared continuation catalog,
  compute its exact-rational asymmetry, and file it as a certificate — plus resolve the formal
  question of what it would even assert given the Lean collapse result.
- Ledger row: NEG.gt2_loop_certificate_not_built, GT2.

### GAP-3 — GT1 paper-[B] benchmark-parity control open
- Status: OPEN — the [B] example-chain parity control is filed as `skipped` inside the GT1
  artifact, with its reason.
- Decision: DISCLOSE
- Justification: The strongest argument for closing is that this is the cheapest gap on the list
  (port a handful of known example chains, compare tables). But the GT1 certificate's margins are
  internal to its own declared scope — aging vs constrained-equilibrium baseline vs lumpable
  zero-control — and none of those comparisons route through [B]'s example chains; parity is a
  confidence control, not a hypothesis. The artifact already files the skip honestly with a
  machine-readable status, which is precisely the F-II conditional-reporting discipline. Closing
  it in Phase 5 would still be new computation on a frozen evidence base, forcing a manifest and
  ledger re-freeze for a control that changes no claim.
- Paper placement: W-03 (GT1 controls table row, marked skipped/open); W-10.
- What closing it would take: port the [B] example chains, run the parity comparison, regenerate
  the GT1 artifacts, and re-freeze manifest + ledger bindings.
- Ledger row: NEG.gt1_b_parity_control_open, GT1.

### GAP-4 — GT7: 14 interval failures + 22 unobserved cells
- Status: OPEN as an interpretive obligation (the scoreboard itself is complete and final).
- Decision: DISCLOSE — and the paper's discussion gets the following failure-pattern analysis,
  computed from the shipped artifacts only (`artifacts/gt7_constants/gt7_transfer_scores.json`,
  `artifacts/gt7_constants/trap_target.json`).
- Failure pattern (exact tallies from the artifact JSON):
  - Verdicts over all 338 cells: 8 pass, 14 fail, 294 no_prediction, 22 unobserved.
  - **All 14 failures are FA-family interval predictions** (5 t_K, 4 t_peak, 5 hump_height); no
    trap prediction was ever scored.
  - **All 14 failures are one-sided high**: the observed FA value exceeds the predicted upper
    bound in every failing cell. FA humps are systematically later (t_K, t_peak) and larger
    (hump_height) than the East-derived intervals allowed.
  - **Failures cluster at the deeper mid-quench**: 12 of 14 failing cells have epsilon_mid = 2/5,
    where every scored cell failed; at epsilon_mid = 1/2, 7 of 9 scored interval cells passed
    (plus the passing order-relation prediction), and the 2 misses there are borderline
    (hump_height 0.2033 vs bound 0.2008; t_K 5 vs [1,3]).
  - **All 22 unobserved cells are trap-family**: the trap target's exact hump search returned
    found=false in all 56 surface cells with the uniform miss reason "does not start below
    equilibrium". This is the dynamical corollary of FINDING.trap_epsilon_invariance: the declared
    trap family's stationary distribution is epsilon-invariant, so an epsilon-jump supplies no
    below-equilibrium starting condition and the Kovacs protocol cannot produce a hump there at
    all.
  - Honest interpretation options for the paper (to be presented as options, not adjudicated
    post hoc): (a) East-to-FA transfer of run-only constants degrades with quench depth, in the
    direction of FA responding slower and larger — the intervals were East-anchored and too tight;
    (b) the declared interval-scaling rule, not the readouts, is what failed; (c) the trap column
    is not a partial failure but a structural mismatch of the protocol to the declared trap
    family, predicted in hindsight by the epsilon-invariance lemma. All three are compatible with
    the run-only thesis; none may be promoted to a fitted scaling law.
- Justification: Nothing here is closable — the freeze-and-transfer protocol forbids re-running
  targets or widening intervals after the fact; the strongest "close" argument (run a second,
  better-calibrated prediction round) would be a NEW pre-registration cycle, which is legitimate
  future work but a new experiment, not remediation of this one.
- Paper placement: W-07 (scoreboard + pattern), W-10 (interpretation options).
- What closing it would take: a second pre-registered prediction round with re-derived intervals
  (new F3 freeze), and/or a trap-family redesign with non-multiplicative (Arrhenius-form) depth
  dependence so the Kovacs protocol is non-degenerate there.
- Ledger row: NEG.gt7_transfer_failures, GT7, FINDING.trap_epsilon_invariance.

### GAP-5 — Material P4<-P5 forcing absent (material_forcing_count = 0)
- Status: CLOSED AS NEGATIVE — not open work; listed here because the paper must frame it.
- Decision: DISCLOSE
- Justification: The strongest argument for "closing" (hunting for a shell where material forcing
  is nonzero) is that it would let the paper invoke paper [C]'s fuller thm:strict-extension. But
  the shipped verdict does not need it: F-III T19/T20 (non-factorization from the GT2/GT3
  witnesses) fully licenses `verdict: strict` for the audited shell, and the audit artifact's
  verdict_basis states the narrowed basis verbatim. Searching other shells for forcing would be
  new science with no bearing on the shipped shell's certificate.
- Paper placement: W-06 (verdict_basis quoted verbatim; honest-negative sub-result box).
- What closing it would take: a different audited shell (other N, other protocol windows) where
  the completion-dynamics route is exercised and material forcing is observed, then the full [C]
  obligation chain on that shell.
- Ledger row: NEG.material_forcing_absent, GT6.

### GAP-6 — Lean instance is structural, not numeric
- Status: OPEN in the weak sense that a numeric export does not exist; shown unbuildable honestly
  in this core.
- Decision: DISCLOSE
- Justification: The strongest argument for closing is that a numeric Kovacs witness in Lean was
  the original GB9 aspiration. But FINDING.lean_collapse is a machine-checked proof that
  non-vacuous PredictiveWitness/StrictRefinement/LoopAsymmetry instances cannot be built in
  RouteTransportCore at all — the gap is not unfinished work but a theorem about the core. The
  honest posture (typed structural mirror + fidelity table + the collapse finding as a result) is
  strictly more informative than a numeric encoding would have been. Re-architecting the core to
  admit numeric witnesses is future formal work.
- Paper placement: W-08 (the collapse finding IS the section's centerpiece; the structural-only
  instance is its consequence, filed with fidelity labels).
- What closing it would take: a revised formal core whose coherence axioms do not force the
  current/future collapse (e.g. weakening observe_push or the event quantification), then a real
  numeric export — genuinely new formalization work.
- Ledger row: NEG.lean_instance_structural, FINDING.lean_collapse, GB9.

### GAP-7 — GT1 certificate covers a single (model, N, lens) cell
- Status: OPEN as breadth, not as validity — East N=8, L_energy, tau ladder [1,2,4,8] only.
- Decision: DISCLOSE
- Justification: The strongest argument for closing (adding FA N=8, or East N=10, or L_panel)
  is rhetorical breadth: a one-cell theorem invites "is that all?" But the GT1 claim as worded in
  the ledger quantifies over exactly its declared scope, which is the F-II discipline working as
  designed (A2: declared finite class; no silent generalization). The margins inside that scope
  are not marginal (CD ratio 1.639 vs declared 3/2; delta 289/121 vs 2), the zero-control and
  nonzero-baseline structure is complete, and no other claim (including GT6's H5 citation)
  needs more breadth than the declared cell. Widening would re-open the frozen evidence base for
  a claim nobody overclaims.
- Paper placement: W-03 (scope box states the single cell plainly; out_of_scope list from the
  artifact reproduced verbatim); W-10 open-obligations table lists the FA/L_panel/N=10 extensions.
- What closing it would take: rerun the GT1 builder on the additional cells (mechanical but
  hours-scale), then re-freeze manifest + ledger.
- Ledger row: GT1, NEG.gt1_b_parity_control_open.

## Summary of decisions
All seven items: **DISCLOSE** (GAP-5 is disclosure-of-a-negative rather than an open item). No
ESCALATE items: no core paper claim silently depends on any gap — each gap is already carried as
an explicit nonclaim, skipped-control record, or honest-negative row in the claims ledger, and the
GT7 failure-pattern analysis above is derived entirely from shipped artifacts.
