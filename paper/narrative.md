# Narrative memo (P5-06) — fixed before any prose is written

This memo pins the paper's thesis, contributions, tone, and placement decisions. Prose in
`paper/sections/` must not exceed what this memo licenses; the memo in turn must not exceed what
`paper/claims_ledger.json` licenses. Where this memo and the ledger disagree, the ledger wins.

## 1. Thesis, at post-build strength

The proposal's §0 thesis was written before the build. The paper's thesis is the same claim at the
strength actually achieved, which differs in four load-bearing places:

> **Glass, on the audited exact-finite class built here, is a layer that fails to close.** The
> declared thermodynamic lens has a positive closure deficit on the audited glassy scope, exceeding
> its own constrained-equilibrium baseline by a certified margin (GT1). The Kovacs effect supplies
> a certified predictive witness: an exact-rational split pair current-equal and future-different
> (GT2). On the declared finite lens class, no definable predicate separates what the witness
> separates — the order-parameter search is foreclosed *on that declared class* (GT3). The
> predictive-structure layer receives a shell-local strict-promotion certificate via
> non-factorization (GT6). The aging readouts are run-only: frozen before target runs and scored
> mechanically, with 8 of 22 scored predictions passing, 14 failing one-sidedly, and the trap
> family structurally out of the protocol's reach — the scoreboard, including its failures, is the
> deliverable (GT7).

Deltas from the proposal thesis, stated so no section drifts back to the stronger version:
1. "Validated out-of-sample under a no-fitting freeze" → "scored out-of-sample under a no-fitting
   freeze, with the honest scoreboard (8/14/294/22) as the result." The protocol worked; many
   predictions did not.
2. "Canonical by a universal-property theorem" (M as *the* state of glass) → the
   universal-property/uniqueness theorems are [A]-corpus results verified generically in Lean; what
   this build certifies on glass is the witness, the foreclosure over the declared class, and
   MaxFiber = 2 on the shipped pair. No new canonicity theorem is proved here.
3. "Machine-checked witness certificates" (GT2 grade target) → the witness is exact-rational
   *computational* evidence; the Lean scope-boundary finding (this paper's own result) proves
   non-vacuous witness instances are impossible in the vendored formal core, which is WHY the
   numeric witness is not Lean-checked. The loop-asymmetry certificate was not built.
4. GT6's verdict rests on F-III T19/T20 (non-factorization) with paper [C]'s fuller
   completion-dynamics theorem explicitly not invoked (material forcing checked and absent).

## 2. The four contributions (in order of what the paper is FOR)

C1. **An end-to-end instantiation of the SBT certificate discipline on a real physics target**,
    with machine-readable envelopes, declared finite quantifier domains, content-hash freezing,
    controls, and honest negatives filed as first-class results. The discipline itself — including
    where it forced claims to shrink — is the primary exhibit.
C2. **The GT1–GT7 result complex at exact scopes** (7 claims + 4 bridges + 6 honest negatives in
    the ledger), each with its proposal-§4 anchor row and hash-pinned artifacts.
C3. **The freeze-and-transfer protocol and its actual outcome**: pre-registered predictions,
    mechanical scoring, a one-sided failure pattern with a clean structural story (FA responds
    later/larger than East-anchored intervals at deep quench; trap is out of reach because its
    declared weight family is ε-invariant).
C4. **The Lean-checked core plus the scope-boundary collapse finding**: CurrentEventEquiv forces
    FuturePredictiveEquiv in RouteTransportCore — a machine-checked expressiveness boundary
    (stronger than [A]'s own declared one), explaining exactly which certificates can live in Lean
    and which must remain exact-rational computation.

## 3. Section map and writing order

Document order mirrors proposal §3 (per the Phase 5 gate); writing order is results-first:
W-01 methods → W-02 models → W-03 GT1 → W-04 GT2+GT5 → W-05 GT3+GT4 → W-06 GT6 → W-07 GT7 →
W-08 GB9/Lean → W-09 GB10 → W-10 discussion+nonclaims → W-11 intro/abstract/conclusion (last) →
W-12 consolidation. Ledger rows per section are pinned in each section file's header comment and
enforced by `tests/test_paper_gates.py`.

## 4. Findings placement

- **ε-invariance** (W-02): presented as a known-in-substance property with citations
  (Bouchaud 1992; Monthus–Bouchaud 1996; Diezemann–Heuer 2011; Bertin–Bouchaud–Drouffe–Godrèche
  2003), framed as a deliberate exact-rationality design choice with a proven consequence — and
  then CASHED IN at W-07, where it explains the 22 unobserved trap cells. Never framed as novel.
- **Lean collapse** (W-08, centerpiece): a genuine machine-checked result about the formal core,
  with the lumpability/Chu-space kinship cited; its consequence (structural-only instance) is
  presented as understanding, not as an apology.

## 5. Honesty-ledger placement

- Every GT/GB section carries a scope box (declared domain, verbatim from the envelope) and its
  nonclaims inline.
- W-10 prints the FULL nonclaims ledger (61 rows) and walks the gap register's seven items.
- The GT6 verdict_basis is quoted verbatim in W-06.
- The anti-reductionism paragraph in W-10 states plainly: a green certificate suite never proves
  emergence; GT3's foreclosure is the gate working, not a metaphysical discovery.

## 6. Tone rules

- No denylist phrases ("full obligation stack satisfied", "provably insufficient", "git history is
  the proof") — enforced by test.
- Failures are reported in the same typographical register as successes (no burying the 14).
- "Certified"/"theorem-grade" only where an artifact with that grade is cited in the same
  sentence or paragraph.
- Field-facing shadows ("no static order parameter") always carry their declared-class
  qualification in the same sentence.
- The paper never claims the ideal-glass transition exists or fails to exist, never makes
  continuum-limit claims, and never reads CD > 0 or witnesses as irreversibility (P6_drive was
  not audited).
