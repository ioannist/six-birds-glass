# 01 — Model Specification: KCM Substrate, Protocols, Lenses

**Audience:** implementer agent. This document fully specifies the physical models, their exact-finite encodings, the temperature-protocol machinery, and the observable lenses. After reading this you should be able to build the model layer without consulting any physics literature.

**Cross-references:** SBT-side requirements are in `../reference/` (Foundations digests). The pipeline that consumes these models is specified in `02_pipeline.md`. Anchor names like F-I `def:D-IC-01` refer to the reference digests.

---

## 1. Design constraints (read first)

1. **Exact-finite discipline (F-I `def:tk-theory-package`, F-II `def:finite`).** Everything that enters a certificate must be computed in exact rational arithmetic (`fractions.Fraction` in Python, matching paper [A]'s exact-finite package spec). Floating point is allowed only in Leg 2 (Monte-Carlo sweeps) and in cross-check assertions.
2. **No unbookkept continua (F-II `def:finite`).** Temperature is NEVER a free real parameter. We declare a **finite rational grid in the Boltzmann activation variable**, not in T:
   - Declare ε ∈ ℚ ∩ (0,1) on a finite grid (e.g. ε ∈ {1/10, 1/5, 3/10, 2/5, 1/2, 3/5, 7/10}).
   - ε plays the role of e^(−β) = e^(−1/T). The "temperature" T = −1/ln(ε) is a **bridge annotation** (`Ann_Bridge`) attached for physics readability; it never enters computation.
   - The up-spin equilibrium concentration is then c = ε/(1+ε) ∈ ℚ exactly.
   - Every protocol schedule is a finite word over the declared ε-grid.
3. **Protocol register in the state (F-I autonomy axiom; `thm:protocol_trap` discipline).** The Markov chain must be autonomous. A temperature schedule makes the raw dynamics time-inhomogeneous; we restore autonomy by lifting the schedule phase into the state: Z = configurations × phase register. Never read anything off a stroboscopic fit of a non-autonomous chain (clock-audit rule).
4. **Size budget.** Exact rational evolution is feasible for N ≤ 12 (state space 2^12 = 4096; sparse kernel with ≤ N+1 nonzeros per row). N = 13–16 is feasible in float64 matrix form for verification sweeps; larger N (up to ~20, per `09_gt7_constants.md` §3) is feasible only via trajectory-sampling Monte Carlo, never matrix evolution. All *certificates* use N ≤ 12. All claims are indexed by the exact (N, boundary, grid) tuple — no thermodynamic-limit claims (standing nonclaim, proposal §6).

---

## 2. Model family 1: East model (primary substrate)

### 2.1 Configuration space

- N binary spins, configuration n = (n_1, …, n_N) ∈ {0,1}^N. n_i = 1 is an **excitation** (mobile/defect region); n_i = 0 is immobile.
- **Boundary condition:** a frozen virtual up-spin at site 0 (n_0 ≡ 1). This guarantees irreducibility of the constrained dynamics on all of {0,1}^N (every spin can eventually flip because facilitation propagates from the wall). Do NOT use periodic boundaries for certificates: with periodic boundaries the all-zero configuration is isolated (no spin has an up left-neighbor), which breaks irreducibility and poisons equilibrium controls.
- Energy (extensive): E(n) = Σ_{i=1}^N n_i. The declared one-time observable panel is built on this (§6).

### 2.2 Kinetic constraint

Spin i is **unconstrained** iff its left neighbor is up: C_i(n) = n_{i−1} (with n_0 ≡ 1). Only unconstrained spins may flip. The constraint does not depend on n_i itself — this is what makes detailed balance trivial (the constraint factor is symmetric under flipping spin i).

### 2.3 Discrete-time heat-bath kernel K_ε (the exact object)

We use a **random-scan discrete-time heat-bath chain** so all kernel entries are rational:

Given current configuration n, one step of K_ε:
1. Pick site i ∈ {1,…,N} uniformly (probability 1/N each).
2. If C_i(n) = 0: do nothing.
3. If C_i(n) = 1: resample n_i from the heat-bath marginal: set n_i = 1 with probability c = ε/(1+ε), n_i = 0 with probability 1−c = 1/(1+ε), independently of its current value.

Matrix entries (n ≠ n′ differing only at site i):
- K_ε(n, n^{i,1}) = (1/N) · C_i(n) · c   (flip up, if currently down)
- K_ε(n, n^{i,0}) = (1/N) · C_i(n) · (1−c)  (flip down, if currently up)
- K_ε(n, n) = 1 − Σ (off-diagonal row entries)  [includes both "site blocked" and "resample landed on the current value"]

All entries are in ℚ. Each row has at most N+1 nonzeros → store sparse (dict-of-dicts or CSR with Fraction data).

**Detailed balance.** K_ε is reversible w.r.t. the product Bernoulli measure π_ε(n) = c^{E(n)} (1−c)^{N−E(n)} = ε^{E(n)} / (1+ε)^N. Check: for a flip at unconstrained site i, π_ε(n) K_ε(n, n′)/[π_ε(n′) K_ε(n′, n)] = 1 because C_i(n) = C_i(n′) (constraint doesn't involve n_i). **Implementer must verify this identity programmatically for every ε on the grid — exact equality of Fractions — as a unit test.**

⚠️ Note for GB1: K_{ε} and K_{ε′} for ε ≠ ε′ are reversible w.r.t. **different** measures π_ε ≠ π_{ε′}. This is exactly the hypothesis failure of the published protocol-trap theorem that work item GB1 must repair. Keep the per-ε stationary measures exported as artifacts.

### 2.4 Relaxation timescales (for window selection, GB4)

The East model's relaxation time grows as an inverse power/quasi-exponential in ε (in physical terms: super-Arrhenius, τ_α ~ ε^{−log₂(1/c)}-ish scaling class). We do not rely on asymptotics: the implementer computes, for each ε on the grid, the exact spectral gap of K_ε (float64 eigensolve is fine here since gap values are diagnostics, not certificate content; for N ≤ 10 exact characteristic-polynomial checks are optional). Deliverable: a table `spectral_gaps.json` of (N, ε) → (gap, τ_rel = 1/gap, mixing-time bound). This table picks the τ-windows and the aging times t_w used in every experiment; the GB4 metastability-window theorem consumes it.

## 3. Model family 2: Fredrickson–Andersen (FA-1f)

Identical to §2 except the constraint: C_i(n) = 1 iff **at least one** neighbor is up: C_i(n) = max(n_{i−1}, n_{i+1}) with n_0 ≡ 1 (wall) and n_{N+1} ≡ 0. Same heat-bath kernel structure, same reversibility argument (constraint again independent of n_i), same rational grid. FA is the **transfer target** for GT7 (freeze functional forms on East, predict FA).

Irreducibility caveat: from the all-zero configuration, only site 1 (wall-facilitated) can flip — fine. Verify irreducibility programmatically for every (N, ε): the directed graph of nonzero off-diagonal kernel entries must be strongly connected. Ship this as a unit test for both models.

## 4. Model family 3: Bouchaud trap model (second transfer target)

- M traps (declare M on a finite grid, e.g. M ∈ {8, 16, 32}), trap k has a declared **rational escape weight** w_k ∈ ℚ ∩ (0,1] (the analogue of e^{−βE_k}; depths E_k are Ann_Bridge annotations, weights are the formal objects).
- Discrete-time kernel: from trap k, with probability w_k·ε_scale jump to a uniformly random trap (including possibly k), else stay. Temperature enters by scaling: at grid point ε, use per-trap escape probability p_k(ε) = w_k^{a(ε)} — but exponentiation breaks rationality for non-integer a. **Resolution:** declare the temperature action on traps as a finite family of declared rational weight vectors {w^{(ε)} ∈ ℚ^M : ε ∈ grid}, one per grid temperature, with the physical relation w^{(ε)}_k ≈ (w_k)^{β(ε)/β₀} recorded as an Ann_Bridge annotation (see Bouchaud 1992; Monthus & Bouchaud 1996 arXiv:cond-mat/9601012 for the standard Arrhenius form; Diezemann & Heuer 2011 arXiv:1102.0411 and Bertin, Bouchaud, Drouffe & Godreche 2003 arXiv:cond-mat/0306089 for trap-model Kovacs memory studies using it). This keeps the formal domain exactly finite and rational, per F-II `def:finite`.
- Stationary measure at ε: π^{(ε)}_k ∝ 1/w^{(ε)}_k (verify exactly).
- Lens for traps: a declared coarse partition of traps into "shallow/deep" bands (image size 2–4), mimicking a one-time observable.

## 5. Model family 4: p-spin / REM toy (optional third target)

A finite Random-Energy-Model chain: S = {1,…,2^K} states (K ≤ 8) with declared rational Boltzmann weights ρ^{(ε)}_s ∈ ℚ, single-spin-flip adjacency on {0,1}^K, Metropolis-style rational acceptance min(1, ρ_{s′}/ρ_s) — rational since ratios of rationals, and min is exact. Same declared-weight-vector-per-ε discipline as §4. This family is *optional*: include if time permits; GT7's minimum transfer set is East → FA + trap.

## 6. Lenses (the declared current-observable panels)

A lens is a map f: Z → O with finite image (F-I Def. 1 component f; the "thermodynamic lens" Π_std of the proposal). We declare a small catalog — the foreclosure theorem GT3 quantifies over definability from these, so their images must be exactly recorded.

| Lens id | Map | Image size (East/FA, N spins) | Role |
|---|---|---|---|
| `L_energy` | n ↦ E(n) = Σ n_i | N+1 | primary Π_std |
| `L_energy_phase` | (n, φ) ↦ (E(n), φ) | (N+1)·|Φ| | Π_std with protocol phase visible (honest-internalization variant, GT4(a)) |
| `L_panel` | n ↦ (E(n), n_1, D(n)) where D(n) = Σ_{i=1}^{N−1} n_i n_{i+1} (interior domain-adjacency count; wall bond n₀n₁ excluded so D is reflection-invariant) | ≤ (N+1)·2·N | "rich panel" — the strongest declared current lens; used for the two-glass matched-panel witnesses |
| `L_Tf` | n ↦ (E(n), T̂_f(n)) where T̂_f is the declared fictive-temperature readout: the grid ε′ whose equilibrium energy curve is closest to E(n) (ties broken low) | ≤ (N+1)·|grid| | TNM currentization attempt — the thing GT5 proves insufficient |
| `L_trap_band` | trap k ↦ band(k) | 2–4 | trap-model lens |

Rules:
- Every lens must be a *function of the current state only* (one-time observables). Two-time quantities are NEVER lens components — they are future-signature entries (see `02_pipeline.md` §continuations).
- The full declared lens class for GT3/GB5 is the finite set above plus its pointwise refinements up to a declared budget B (see `05_gt3_foreclosure.md` §3, the GB5 repair class). Freeze this catalog before any GT3 run; changing it post hoc voids the foreclosure claim.

## 7. Protocol machinery

### 7.1 Schedules

A **schedule** is a finite word σ = ((ε_1, τ_1), …, (ε_m, τ_m)): run τ_1 steps of K_{ε_1}, then τ_2 steps of K_{ε_2}, etc. All τ_j declared integers, all ε_j on the grid.

### 7.2 The lifted autonomous chain (mandatory form)

Given schedule σ with total length L = Σ τ_j, define phase set Φ = {0, 1, …, L} (or the economical version: {(j, r)} block-and-remainder pairs) and the lifted kernel on Z = {0,1}^N × Φ:

K_σ((n, t), (n′, t+1)) = K_{ε(t)}(n, n′),  where ε(t) is the grid letter active at step t; the terminal phase L is absorbing under K_{ε_m} (hold at final temperature) unless the schedule is declared cyclic, in which case phase L ≡ phase 0 and the lifted chain is a genuine autonomous loop.

This is the object all SBT diagnostics run on. The **Kovacs loop** ℓ is the cyclic declaration of the schedule in §7.3.

### 7.3 Named protocols (the experiment catalog; freeze before running)

All times below are per-(N, ε-grid) and chosen from the spectral-gap table of §2.4; concrete defaults given for N = 10, to be recomputed and frozen once §2.4 runs.

| Protocol id | Word | Purpose |
|---|---|---|
| `P_eq(ε)` | ((ε, τ_mix)) starting from π_ε | equilibrium control; CD and δ must be machine zero |
| `P_quench` | ((ε_hi, τ_mix), (ε_lo, t_w)) | aging: produces the nonequilibrium μ(t_w) family |
| `P_kovacs(t_w)` | ((ε_hi, τ_mix), (ε_lo, t_w), (ε_mid, τ_probe)) | the Kovacs protocol: equilibrate hot, age cold, up-jump to intermediate; the hump lives in the ε_mid leg |
| `P_kovacs_loop` | cyclic: (ε_mid holds equilibrium panel value) → quench → age → up-jump back to panel-matching moment | the thermal loop ℓ for GT2 loop-asymmetry: acts trivially on current quotient Q, non-trivially on predictive quotient M |
| `P_twoglass_A / P_twoglass_B` | two distinct words tuned (by exact search over declared (t_w, ε) pairs) so that the resulting states match the FULL `L_panel` value | matched-panel split pairs — the strongest witnesses |
| `P_probe_k` (k = 1…K) | short probe words appended after preparation: temperature steps, holds | the declared probe catalog defining future signatures (GB3) |

Default grid roles: ε_hi = largest grid value (hot), ε_lo = smallest (cold), ε_mid strictly between; the Kovacs condition is that at the up-jump moment the monitored E-expectation sits *below* its ε_mid equilibrium value so the approach crosses it (hump). The implementer verifies the crossing exists by exact computation of ⟨E⟩(t) along the ε_mid leg and records t_K (first crossing time) and the hump (max deviation after t_K) — these are the GT7 run-only readouts.

### 7.4 Kovacs-moment state pairs (the canonical witness input)

The certificate-grade split pair for GT2 is built from distributions, exactly:
- μ_K = state distribution at time t_K along `P_kovacs(t_w)` (energy expectation exactly equals ε_mid-equilibrium value — solve for the crossing between integer steps by declaring t_K as the first integer step where the sign flips, and record both flanking steps; no interpolation in certificates).
- μ_eq = π_{ε_mid}.
These two have (approximately at integer steps; exactly for the matched-panel pairs of `P_twoglass_*`) equal current signatures under the declared lens and provably different future signatures under the probe catalog. The pipeline doc specifies how these become formal witness certificates.

## 8. Controls (must-pass null instances)

Every diagnostic ships with controls that must hit exact zero / null status:

1. **Unconstrained (lumpable) control:** East/FA kernel with C_i ≡ 1 (constraint removed) = independent heat-bath spins. Under `L_energy` the induced count chain is exactly Markov (binomial birth–death) → lumpable → CD_τ = 0 **exactly** (Fraction equality, not epsilon). This is the primary machine-zero benchmark, replicating [B]'s discipline.
2. **Equilibrium control:** any model run under `P_eq(ε)`: E_{τ,f}(π_ε) = π_ε exactly under Gibbs prototypes (fixed-point identity, NOT δ = 0 — see `03_gt1_nonclosure.md` §3.2); witness count 0; loop scores 0.
3. **Constant-temperature loop control:** a "loop" that never changes ε: both loop-action scores must be 0.
4. The six [A]-benchmark regime controls rebuilt with thermal semantics — specified in `06_gt4_triage.md`.

## 9. Implementation notes

- Language: Python 3.11+, `fractions.Fraction` throughout the certificate path; `numpy` float64 only in Leg-2 sweeps and cross-checks. Borrow the kernel/distribution containers from `six-birds-route-transport` (see `../reference/code_route_transport.md` §port plan) rather than re-implementing.
- Sparse rational kernels: dict-of-dicts `{state_index: {state_index: Fraction}}`; states indexed by integer bitmask; phase-lifted states by (bitmask, phase) tuples interned to ints.
- Distribution evolution: μ ← μK is a sparse vector–matrix product over Fractions. Cost per step ~ nnz(K) ≈ 2^N·(N+1). For N = 12 and τ = 10⁴ steps this is ~5·10⁸ Fraction ops — too slow naïvely. Mitigations, in order of preference: (i) evolve only from the reachable support (support projection, per [A]'s package spec — after a quench from equilibrium the support is full, but matched-panel constructions often have small support); (ii) exponentiate by squaring for pure holds: precompute K^{2^k} sparse-but-densifying — at N ≤ 10 dense 1024×1024 Fraction matrices are fine, so certificates default to **N = 8–10 with dense rational matrix powers**, and N = 12 only where support stays small; (iii) keep N = 12–16 for the float64 Leg-2 sweeps. Record the choice per experiment in its config.
- Fraction blow-up: rational denominators grow along long evolutions. Monitor `max_denominator_bits` per step and record in run metadata; if it exceeds a declared cap (e.g. 4096 bits), the run config must shorten holds or coarsen the grid — never round.
- Every model + protocol + lens is constructed from a single JSON config (schema in `../schemas/model_config.schema.json`) so that runs are replayable and the GB7 freeze can hash configs.

## 10. Acceptance tests for this layer (write these first)

1. Detailed balance: for each model family and each grid ε, exact Fraction identity π_ε(n)K(n,n′) = π_ε(n′)K(n′,n) over all edges.
2. Irreducibility: strong connectivity of the kernel graph for all (N, ε) in the declared ranges.
3. Row sums exactly 1 (Fraction).
4. Unconstrained control: exact lumpability of the count chain (compare induced macro kernel rows across micro states in the same fiber — must be identical Fractions).
5. Kovacs hump existence: for the frozen default (N = 10, grid defaults), the exact ⟨E⟩(t) trace on the ε_mid leg crosses equilibrium and is non-monotone after crossing.
6. Reproducibility: rebuilding any object from its config JSON is bit-identical (serialize Fractions as "p/q" strings).
