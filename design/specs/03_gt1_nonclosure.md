# 03 — GT1: Non-Closure of the Thermodynamic Lens (CD and δ tables)

**Claim (GT1).** On the audited KCM class, in the glassy regime: CD_τ(Π_std) > 0 across the accessible τ-window, and δ_{τ,f} stays bounded away from 0 (packaging never reaches its fixed point); and the controls behave lawfully: CD vanishes exactly on structurally lumpable controls, while constrained equilibrium rows are filed as nonzero stationary baselines, and the packaging controls pass the fixed-point/macro-closure identities with δ at a small equilibrium baseline. (⚠️ The proposal's shorthand "both vanish on controls" is not literally achievable for δ — see §3.2; the paper must state the control claim in the corrected form.)

**Anchors.** F-III T8 (CD as attained KL minimum over admissible macro kernels — `../reference/foundations_III.md`); [B] Def 3.1 + Props 3.2/3.5 + `prop:rm-lower-bound` (`../reference/B_cast_a_stone.md`); F-I D-IC-01/D-IC-02/T-IC-02/T-CL-01 (`../reference/foundations_I.md` §§2–5); F-IV F20 conjunct 8 negated (`../reference/foundations_IV.md`). GB2 supplies the protocol-relative CD definition (spec `10_new_math.md` §GB2).

**Evidence grade.** Deterministic computational evidence (exact rational where feasible, float64 with residual columns elsewhere) — per F-I's disclosure, Markov results are *not* Lean theorems; label accordingly.

---

## 1. The two diagnostics

### 1.1 Closure deficit CD_τ(Π)

Stationary case ([B] Def 3.1): CD_τ(Π) = I(X_t; Y_{t+τ} | Y_t) under the stationary joint law of a chain P with lens Π; equals the attained KL minimum over admissible macro kernels; zero iff τ-lumpable ([B] `prop:cd-zero`).

Borrow: `six-birds-randomness/src/randomness_ledger/metrics.py::closure_deficit(P, pi_map, tau, pi_stationary=None)` — float64. Port note (from `../reference/code_randomness_cantor.md`): for certificate-grade **exact zeros on controls**, re-implement the same formula over Fractions (entropy terms can't be rational, so the exact-zero check is done on the *mutual-information numerator structure*: assert the conditional joint factorizes exactly — p(x_t, y_{t+τ} | y_t) = p(x_t|y_t)·p(y_{t+τ}|y_t) as Fraction identities — which is equivalent to CD = 0 without computing logs). Positive CD values are reported in float64 with a residual column, [B]-style.

Glass (nonequilibrium) case: use the **GB2 protocol-relative definition** (spec 10 §GB2; primary route = protocol-ensemble joint law, with quasi-stationary-window slices as reported tables, per [B] digest §9 recommendation). Until GB2's propositions are proved, tables carry the definition-choice flag and the equilibrium-limit consistency check (§4.3).

### 1.2 Idempotence defect δ_{τ,f}

F-I D-IC-01/02: E_{τ,f}(μ) = U_f(Q_f(μ P^τ)); δ_{τ,f} = ½·max_z row-ℓ1 of (E² − E) — **exactly computable** as a matrix computation over Fractions (E is a Z×Z rational kernel).

**Prototype declaration (mandatory modeling choice, F-I: "the glass instantiation must declare its prototype rule").** Declare TWO prototype rules and report both:
- `proto_gibbs(ε_ref)`: u_x = π_{ε_ref} conditioned on block B_x (Gibbs-within-fiber at a declared reference ε). Physically: "the lens value plus equilibrium assumption" — exactly the assumption TNM-style descriptions make.
- `proto_uniform`: u_x = uniform on B_x (maximum-entropy fiber fill).
Rationale to record: δ > 0 under `proto_gibbs` is the formal statement "re-instantiating the state from the current panel under the equilibrium assumption does not reproduce the aging dynamics" — the aging diagnostic of the proposal. Both rules give rational U_f.

For the **aging (time-inhomogeneous) reading**, evaluate the defect along the protocol: δ_{τ,f}(t) computed with P^τ replaced by the ordered product of the scheduled kernels over [t, t+τ] (the lifted-chain version is the autonomous equivalent; compute on the lifted chain to stay within F-I's autonomous setting, see `01_models.md` §7.2).

## 2. Experiment grid

For each model family (East primary; FA replication) and each N ∈ {6, 8, 10}:

| Axis | Values |
|---|---|
| lens | `L_energy` (primary), `L_panel` (secondary) |
| ε (equilibrium rows) | full declared grid |
| protocol (aging rows) | `P_quench` at declared (ε_hi → ε_lo) pairs, evaluated at declared ages t ∈ T_age ladder |
| τ | ladder {1, 2, 4, …, 2^k} up to past the measured relaxation time (from `spectral_gaps.json`) |
| prototype rule | both of §1.2 |

Outputs per cell: CD_τ (float64 + residual), δ_{τ,f} (exact rational, serialized "p/q"), ε_{τ,f} retention error (T-IC-02 bound column — report both δ and its bound to exhibit the bound's tightness for GB4).

## 3. Controls (every table ships with all four)

1. **Lumpable control** (`01_models.md` §8.1): unconstrained spins + `L_energy` → CD = 0 **exact** (factorization identity over Fractions), plus the exact macro-closure identity Q_f(μP^τ) = Q_f(μ)·K̂_τ (the induced macro kernel reproduces the pushed law for every declared μ — Fraction identity).
2. **Equilibrium consistency control**: for structurally lumpable models (the unconstrained control in item 1), any (ε, `P_eq`) row has CD = 0 exactly. For constrained East, equilibrium `P_eq` is not a zero-CD control: CD_τ(Π) = 0 iff the kernel is τ-lumpable with respect to Π, and East with `L_energy` is not lumpable because its kinetic constraints depend on site arrangement, not just total energy. East equilibrium rows therefore file a real nonzero stationary baseline and the GB2 consistency gate (protocol-relative CD equals stationary CD), plus the **fixed-point identity** E_{τ,f}(π_ε) = π_ε exact under `proto_gibbs(ε)`. ⚠️ Do NOT assert δ_{τ,f} = 0 here: δ is a sup over Diracs (initial-distribution-independent) and vanishes only when the prototype retention error does (T-IC-02); Gibbs-conditional prototypes leak mass across `L_energy` fibers in one step at any ε, so equilibrium-control δ is small-but-positive. The control claim is **contrast, not zero**: report the equilibrium-row δ as the baseline and require the aging-row δ to exceed it by the declared margin. (A provably-small-δ control is exactly GB4's metastable-block regime; cross-ref the window theorem.)
3. **Closure-discipline control** (F-I `cor:closure-saturates` context): T-CL-01 is an order-closure statement and E_{τ,f} is *not* a closure operator (F-I digest §5) — no E² = E assertion anywhere. The checkable discipline is item 2's fixed-point identity plus item 1's macro-closure identity.
4. **[B] benchmark parity**: run the ported CD code on [B]'s own published lumpable/non-lumpable example chains and reproduce its table values to float64 residual (~1e-15), per the replication discipline in `../reference/B_cast_a_stone.md` §6.

## 4. Claim assembly

### 4.1 "Bounded away from 0 over the accessible τ-window"
Formal content: min over the declared τ ladder (within the GB4 window τ_β ≪ τ ≪ τ_α) of the reported quantity, at each declared aging cell, exceeds the declared threshold (a rational, e.g. δ ≥ 1/100), while every control row is exactly 0. The threshold is declared **before** the run (freeze), the artifact reports the achieved min — F-II threshold-attachment discipline.

### 4.2 Interpretation guards (metadata assertions)
- CD > 0 filed as non-closure only; **never** novelty or irreversibility ([B] nonclaims, verbatim strings in `nonclaims`).
- δ > 0 is a saturation diagnostic; the D-IC-02 guardrail means any "multiple glass states" reading needs the separate nontriviality witness — supplied by GT5's MaxFiber artifact (cross-ref hash), not by δ itself.
- F-IV F20: file the aging law as the *negation of conjunct 8* with the F20 status vocabulary (see `../reference/foundations_IV.md` §F20).

### 4.3 GB2 consistency gate
The protocol-relative CD must reduce to [B]'s stationary CD in the equilibrium limit: run the GB2 definition on `P_eq(ε)` cells and assert agreement with the stationary computation to float64 residual (and exact-zero agreement on lumpable controls). This is GB2's acceptance criterion and blocks the GT1 aging tables from shipping without it.

## 5. Artifacts

`artifacts/gt1_cd_tables/<model>_<N>_<lens>.json`, `artifacts/gt1_delta_tables/…` — envelope + payload: grid → {cd, cd_residual, delta_pq, epsilon_retention_pq, window_flags}, controls block per §3, threshold declaration + achieved min. Claim id `GT1.<model>.<N>.<lens>`.

## 6. Acceptance criteria

1. All §3 controls pass (exact zeros where specified).
2. Glassy cells: achieved min ≥ declared threshold on the declared window for East N=8,10 under `L_energy`+`proto_gibbs`.
3. GB2 consistency gate (§4.3) passes.
4. Tables replicate under re-run byte-identically; [B] parity check green.
