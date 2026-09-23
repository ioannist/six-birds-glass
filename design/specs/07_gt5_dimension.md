# 07 — GT5: Effective Dimension (Fictive-Temperature Buyback, Quantified)

**Claim (GT5).** On the audited Kovacs witness package: MaxFiber := max_q #(π⁻¹(q)) ≥ 2 under the declared protocol catalog; the memory dimension (fiber structure of π: M→Q) is a measurable, protocol-indexed invariant; budgeted prediction exhibits the buyback curve. The shipped buyback curve for the minimal two-history pair saturates at B = 1 (any one declared scalar in {T_f, D, n_1} resolves the pair), so it demonstrates the buyback mechanism rather than proving general single-scalar insufficiency.

**Anchors.** [A] diagnostics `max_fiber_size` (eq `eq:max-fiber`), `exact_max_abs_future_gap` (`../reference/A_holonomy_memory.md` §10); [B] eq `eq:budgeted-rand` Rand_B monotone buyback + the order-0/1/2 saturation exhibit and its Appendix-A anti-monotonicity caution (`../reference/B_cast_a_stone.md` §5); F-IV F24 (RoleSplit ⟺ strict joint refinement; each new sufficient coordinate is a layer-multiplicity event with one of 8 typed resolutions — `../reference/foundations_IV.md`); F-II `prop:forgetting-lifts` (each lift = added data, recorded).

**Field translation (carried in the artifact):** TNM's single T_f is represented as one candidate coordinate in the declared buyback pool. The current shipped witness does not certify that one scalar is generally insufficient; that stronger statement requires GB5 or richer multi-instance evidence.

---

## 1. MaxFiber and the fiber profile

From the GT2 package: MaxFiber and, richer, the **fiber histogram** {q ↦ #(π⁻¹(q))} at each declared interface, per (model, N, lens, protocol catalog). MaxFiber ≥ 2 anywhere = one current class carrying ≥ 2 predictive classes, so the current lens is insufficient. It does not by itself show that every one-scalar refinement fails; that stronger statement belongs to the GB5 repair sweep or a richer multi-instance construction.

**Protocol-indexed invariant:** compute the fiber profile as a function of the catalog: for nested catalogs ℱ₁ ⊂ ℱ₂ ⊂ … (probe ladders of increasing depth/branching), report MaxFiber(ℱ_k). Expected monotone non-decreasing in k (more probes distinguish more); each strict increase is an F-IV F24 layer-multiplicity event — file its typed resolution (for glass: MemoryLayer) per the 8-case table. This ladder is the **memory-dimension profile** artifact and a GT7 transfer readout.

## 2. The buyback curve (budgeted prediction)

Port [B]'s Rand_B discipline to the glass setting (borrow `experiments/budget_curves/run_budget_curves.py` logic per `../reference/code_randomness_cantor.md`):

- **Budget B** = number of memory coordinates appended to the current lens. Coordinate pool: the frozen scalar catalog R_scalars of spec 05 §3.1 **plus** the exact predictive coordinates (indicator coordinates of M-classes) as the saturating tail.
- **Loss**: held-out prediction loss of the declared future-signature entries given the (lens ⊕ chosen coordinates) state — computed exactly on the declared history set: for budget B, the feasible class is all subsets of the pool of size ≤ B; per [B]'s rule, report the **feasible-class envelope** (min over subsets, cumulative-min across B — `np.minimum.accumulate` analogue) so the curve is monotone by construction, with the raw per-subset table preserved (Appendix-A anti-monotonicity caution: raw curves need not be monotone; only the envelope is).
- Loss functional: squared error over declared (γ,e) entries with declared rational weights (exact); report also the conditional-entropy version in float64 as a secondary column.
- **Saturation point**: smallest B where loss hits its M-resolved floor exactly; assert floor equals the loss of the full M-indicator state. The exhibit "strictly lowers held-out loss until M is resolved" = strict decrease of the envelope at each rung before saturation — this mirrors [B]'s order-0/1/2 pattern (1.09565 → 1.04394 → 1.03855 nats against theory 1.04953 in [B]'s exhibit; glass produces its own numbers).
- **Held-out discipline:** split the declared history set (or the declared protocol-cell grid) by a frozen deterministic rule (e.g. even/odd catalog index) — recorded in config; no tuning on the held-out half.

Each rung is filed as an F-II `prop:forgetting-lifts` record (added data, recorded) — the ladder of lifts IS the buyback curve in F-II vocabulary.

## 3. Controls

- Flat/equilibrium package: MaxFiber = 1, buyback curve flat at floor from B = 0.
- `latent_memory_base`: saturates exactly at B = 1 (one scalar suffices) — calibrates the machinery against a known one-rung case.
- Kovacs candidate: the shipped minimal two-history witness saturates at B = 1 because each declared scalar in {T_f, D, n_1} separates the pair. This calibrates the buyback mechanism; it is not a single-scalar-insufficiency certificate.

## 4. Artifacts and acceptance

- `artifacts/gt5_dimension/max_fiber.json` — fiber histograms + catalog-ladder profiles + F24 event filings.
- `artifacts/gt5_dimension/buyback_curve.json` — per-B envelope + raw subset table + saturation point + held-out split rule; controls block.
- Acceptance: (1) MaxFiber ≥ 2 for the Kovacs package; (2) buyback envelope computed honestly, with the shipped two-history candidate saturating at B = 1 if a declared scalar separates it, = 1 on `latent_memory_base`, = 0 on flat; (3) exactness: all certificate columns rational; (4) GB5 nonclaims present unless a future repair ledger exists; (5) catalog-ladder monotonicity holds or deviations are filed with F24 resolutions. No saturation B ≥ 2 claim is made unless a future richer construction supports it.
