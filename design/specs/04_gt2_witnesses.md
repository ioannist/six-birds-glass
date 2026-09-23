# 04 — GT2: Kovacs Witness and Loop-Asymmetry Certificates

**Claim (GT2).** The Kovacs protocol generates predictive witnesses (h ≡⁰ h′, ¬(h ≡⁺ h′)); and the thermal loop ℓ acts trivially on the current quotient Q and nontrivially on the predictive quotient M.

**Anchors.** [A] Defs 2.2–2.4, Thms 3.5–3.6 + Lean names (`../reference/A_holonomy_memory.md` §§3–6, 7); F-IV F2 (split-pair engine), F3 (route residue forces memory — note F3's own instantiation list includes Preisach/return-point memory), F7, F13a; F-III T7, T12, T13 (`../reference/foundations_III.md`).

**Routing rule (binding, F-II `prop:causality-closure` + `rem:p6-drive`):** the "different future" is filed as a **P4 staged-dependence** projection. It is NOT P3 route mismatch and NOT a directionality claim. No arrow language anywhere in GT2 artifacts; any irreversibility statement would need a separate P6_drive audit which GT2 does not perform. The checker greps GT2 artifacts for a denylist ("irreversib", "arrow", "entropy production") outside the nonclaims block.

**Grade.** Machine-checked witness certificates: exact rational computation + Lean anchoring via [A]'s modules (see `11_gb9_lean.md`). Loop *scores* are computational evidence only ([A]'s declared Lean scope boundary).

---

## 1. Inputs (all built in spec 02)

- The glass route-transport package with the Kovacs constructions: reflection pairs (02 §4.1), tuned Kovacs-moment pair (μ_K, π_{ε_mid}) (02 §4.2), the loop ℓ_Kovacs with pre-declared loop images (02 §4.3), matched-panel two-glass pairs from exact search (`P_twoglass_*`, 01 §7.3).
- Frozen continuation catalog ℱ (02 §5) — M is protocol-catalog-relative by construction; the artifact must name the catalog hash.

## 2. Witness certificate content (`witness_certificate` artifact)

For each declared witness family, the payload:
1. The pair (h, h′) — full rational distributions (or references into the package file).
2. `s0_equal_entries` — the shared current signature, one (event_id, value) row per declared event; the generator computes both histories' observations and writes the row only after asserting exact Fraction equality (equality is checked at generation, so a single shared value per event is stored).
3. The separating entry: index (γ, e) ∈ ℱ with `obs(push_γ h, e) ≠ obs(push_γ h′, e)`, both values as exact rationals, difference = contribution to `exact_max_abs_future_gap`.
4. Quotient summary: `current_quotient_size`, `predictive_quotient_size`, `max_fiber_size`, witness count over the declared history set.
5. Theorem hook: statement instance "witnesses nonempty ⟹ π strictly refining" with the Lean name `strictRefinement_iff_nonempty_predictiveWitness` and the fidelity label from GB9.

## 3. Loop certificate content (`loop_certificate` artifact)

1. The declared loop ℓ (schedule word + tuning parameters θ*, all rational).
2. Current side: for every class c of Q, L^Q(c) = c — verified by exact signature equality of pushed representatives; `loop_action_score_current_quotient` = 0.
3. Predictive side: the moved class(es): m with L^M(m) ≠ m, exhibited by the differing future-signature entry; `loop_action_score_predictive_quotient` > 0 (exact fraction).
4. The intertwining instance: π(L^M(m)) = π(m) — the moved-predictive/fixed-current exhibit; Lean name `loopAsymmetry_exhibits_movedPredictive_fixedCurrent`.
5. Control loops: constant-temperature loop and equilibrium loop, both scoring (0, 0) — filed in the `controls` envelope block.

### Open loop-certificate item

The real East loop-certificate artifact is not filed. The honest obstruction found during the GT2 loop work is that closing the declared `mid` history set under repeated application of the real loop kernel does not stabilize: each closure round produces new exact distributions that would need to be pre-declared before `loop_action_score` can be computed. Filing a truncated declaration would violate the finite-declaration discipline, so GT2 currently ships the Kovacs-moment witness certificate only; the loop certificate remains an open item.

## 4. Witness families to certify (minimum set)

| Family | Panel | Model/N | Why included |
|---|---|---|---|
| `W_reflection` | (E, D) reflection-invariant panel | East N=8,10 | exact, structural, rich panel |
| `W_kovacs_moment` | {w_E} | East N=8,10 | the literal Kovacs-at-t_K pair |
| `W_twoglass` | full `L_panel` | East N=8 | matched-full-panel pair (exact search; if search finds none, file the negative result honestly and rely on the other two — the claim needs *a* witness family, not all three) |
| `W_fa` | (E) | FA N=8 | cross-family replication |

Each family also runs on its **null control**: the same construction at equilibrium (both members drawn from π_ε) must give zero witnesses.

## 5. Loop certificates (minimum set)

`L_kovacs` (East N=8, per 02 §4.3); `L_kovacs_fa` (FA N=8); controls: `L_const_temp`, `L_eq_cycle` (a hot–cold–hot cycle applied to an equilibrium-prepared history set at ε_mid — note: this generically moves predictive classes too unless the histories are loop-invariant; construct it on ℋ = {π_{ε_mid}} alone where push_ℓ π_{ε_mid} has exactly-restored panel by tuning, and predictive entries are checked — if they differ, that is itself informative and the control becomes "loop on equilibrium singleton": score defined on the singleton quotient; document the outcome either way).

## 6. Acceptance criteria

1. ≥ 2 witness families certify with exact s⁰ equality and named separating entries; null controls at zero.
2. `L_kovacs` certifies (0, >0) with pre-declared loop images; control loops at (0, 0) or documented per §5.
3. Lean instances build (GB9): the glass package instantiates [A]'s abstract structures and the two theorem applications type-check; fidelity table row emitted.
4. Artifacts validate against `../schemas/witness_certificate.schema.json`; P4-routing denylist check passes.
