# 11 — GB9: Lean Kernels (Vendor, Instantiate, Label)

**Scope (proposal GB9).** Instantiate [A]'s Lean modules on glass witnesses; wrap the F-III theorem names (T7/T12/T13/T14); label fidelities per F-II legend. New Lean only where cheap (witness checking); **no mechanization overclaim**. Acceptance: `lake build` green; fidelity table artifact.

**Read first:** `../reference/A_holonomy_memory.md` §7 (module layout, theorem names, declared scope boundary), `../reference/code_route_transport.md` §Lean (toolchain Lean 4.29.0, no mathlib, abstract `RouteTransportCore`; **no existing Python→Lean bridge — that is new work**), `../reference/foundations_II.md` §fidelity legend.

---

## 1. Vendor

Copy `six-birds-route-transport/lean/HolonomyMemory/` into `lean/HolonomyMemory/` unchanged (provenance header; keep toolchain pin). Verify `lake build` green before any additions.

## 2. Glass instantiation layer (`lean/GlassWitness/`)

New, deliberately small:

1. **Finite package instance.** A concrete instance of the abstract route-transport structure for a *specific exported witness*: finite types for the (tiny) declared history set, continuation index set, event index set; `obs` and `push` given by **rational lookup tables exported from Python** (the certificate data, not the 2^N kernels — instantiate at the quotient-relevant level: the declared histories and their signature tables, which is all the theorems quantify over).
2. **Export bridge (new work, keep minimal).** `experiments/export_lean_witness.py` writes a `.lean` file (or a `Decide`-friendly definition file) containing the lookup tables for: the witness pair's s⁰ equality entries, the separating (γ,e) entry values, and the loop's class action table. Generated code is checked in (regeneration must be byte-stable).
3. **Theorem applications** (the actual GB9 content):
   - `glass_witness_strict_refinement`: apply `strictRefinement_iff_nonempty_predictiveWitness` to the instance with the exported pair — conclusion: π strictly refining for the glass package.
   - `glass_loop_asymmetry`: apply `loopAsymmetry_exhibits_movedPredictive_fixedCurrent` with the exported hypotheses (L^Q trivial: finite `decide` over the exported class table; L^M nontrivial: the exported moved class).
   - `glass_M_canonicity`: apply `futureSufficient_factorsThroughPredictiveQuotient_onReachable` + `_unique_onReachable` to one exported sufficient abstraction.
   - Hypothesis discharge by `decide`/`native_decide` on the finite lookup tables where possible; if `native_decide` is needed, record it in the fidelity row (it weakens the trust story).
4. **F-III name wrappers**: thin Lean statements re-expressing the glass instances under the F-III names (δ₁^split nonempty; T12 `StrictExtensionNonfactorization` instance; T13 Δ_fact ≠ ∅; T14 as the 2^|im f| cardinality fact stated over `Fin k → Bool` (i.e. `Fintype.card (Fin k → Bool) = 2^k`, provable in core Lean — do NOT state it over `Set (Fin k)`, which needs Mathlib instances the vendored mathlib-free toolchain lacks) — wrappers over the same instance data, clearly marked as *name bridges*, not new mathematics.

## 3. What is NOT mechanized (state it, don't blur it)

Per [A]'s declared boundary + F-I's disclosure, the following stay **Python-only deterministic computational evidence**: loop *scores* (moved-class fractions), all CD/δ numerics, MaxFiber values as computed over full packages, benchmark tables, GB1/GB2/GB4 proofs (paper mathematics; Lean out of scope for v1). The fidelity table says so explicitly.

## 4. Fidelity table artifact

`artifacts/lean_fidelity_table.json`: one row per paper-claim ↔ Lean-artifact pair with the F-II legend grade (use the legend's five levels verbatim from `../reference/foundations_II.md`), the Lean name, file, whether `native_decide` was used, and for non-mechanized claims the explicit "computational evidence only" grade. The paper prints this table in full.

## 5. Acceptance criteria

1. `cd lean && lake build` green (CI target `make lean-build`).
2. The three glass theorem applications compile with the exported instance; regenerating exports is byte-stable.
3. Fidelity table complete: every GT-claim row present, graded at true fidelity, no row claiming more than its evidence.
4. No `sorry`, no axioms beyond the vendored baseline; `#print axioms` output recorded per theorem in the artifact.
