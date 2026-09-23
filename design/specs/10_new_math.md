# 10 — New Mathematics: GB1, GB2, GB4 (Problem Statements, Proof Plans, Demos)

**Audience:** implementer agent (math-capable). These are the genuinely new theorems. Each section: precise problem statement, proof plan with the known breakage points, the exact-finite demonstration that must accompany the theorem, and the fallback filing if the proof stalls (F-II conditional reporting — an honest open obligation, never a silent gap).

---

## GB1 — Temperature-Protocol Trap Theorem (most load-bearing)

**Context.** F-I `thm:protocol_trap` (T-AOT-02) bounds the apparent path-asymmetry a lawful *phase-indexed* protocol can produce without affinity, under hypothesis (ii): **all phase kernels reversible w.r.t. a common stationary π**. Kovacs kernels K_ε are reversible w.r.t. *different* Gibbs measures π_ε. Read first: `../reference/primer_and_protocol_trap.md` Part 2 (full published theorem, proof, 3-state example, and the GB1 breakage analysis) and `../reference/foundations_I.md` §protocol-trap.

**Problem statement.** Let Φ = {1,…,m} be a finite phase set with a **clock kernel S on Φ, reversible w.r.t. a clock measure s** (hypothesis (i) of the published theorem — retained; this is what makes the lifted support graph bidirected and Σ_T finite), and per-phase kernels K_φ on finite X, each satisfying detailed balance w.r.t. its own π_φ (Gibbs at the scheduled ε_φ) — hypothesis (ii′), replacing the published common-π hypothesis (ii). Consider the **random-scan lift** on X × Φ (with probability α advance the clock by S, else apply K_φ), as in the published theorem. Prove: the stationary path-reversal KL rate decomposes as

  Σ_T(μ*) ≤ T · [ α·EPR(S, s)  +  B ],

where α·EPR(S,s) is the **clock/drive term** (exactly the published driven-clock contribution — zero when S is reversible w.r.t. s, positive when the schedule itself is driven) and B is the new **temperature-boundary term** created by π_φ varying with φ. Conjectured form (from the digest's edge analysis): B ≤ α·Σ_φ s(φ)·Σ_{φ′} S(φ,φ′)·KL(π_φ ‖ π_{φ′}) + symmetrized variants; B = O(Δβ²) for small grid steps and B → 0 in the common-π limit (recovering T-AOT-02 exactly). Identify which cycle affinities of the lifted chain are nonzero: state-edge cycles cancel (each K_φ is DB w.r.t. its own π_φ); the genuine affinities live on **mixed state–phase square cycles** with A(γ) ~ ΔE·Δβ.

**Declared second variant (deterministic scan).** The Kovacs schedule as actually run is a deterministic successor s(φ) — that lift is NOT bidirected (φ→s(φ) has no reverse edge), stationary Σ_T is +∞, and per the digest it needs different techniques (transient/path-space treatment). File it as a separate declared variant: either (a) analyze finite-horizon path-space KL between the scheduled process and its declared reversal (no stationarity), or (b) treat the deterministic scan as the α→limit of lazy reversible clocks with a declared bound. Do not silently conflate the two variants.

**Deliverable form.** "Bound-and-attribute", not "EPR = 0": a lawful temperature loop without external drive carries exactly the clock budget plus the boundary budget B; measured asymmetry ≤ the budget is schedule-lawful; asymmetry above it certifies drive. This is the kill-test GT4(a) needs.

**Proof plan (routes 1–3 from the digest's strategy menu; 4–5 added by this spec):**
1. **Path-space chain rule** (digest-recommended for the Kovacs/transient case): expand the finite-horizon path KL between the lifted process and its reversal by the chain rule; per-step terms split into state-edge contributions (cancel by per-phase DB) and phase-edge contributions (the KL boundary form); sum.
2. Perturbative-at-μ*: direct decomposition of the stationary lifted log-ratio 1-form; main technical lemma: the lifted stationary measure is NOT product π_φ ⊗ s when π_φ varies — control the deviation by a perturbation bound in Δβ (finite-state, explicit constants).
3. Cycle-basis route: all affinity carried by the mixed square cycles; bound each by ΔE·Δβ; assemble.
4. *(added)* Two-scale/adiabatic comparison: compare against the quasi-static limit where the boundary term is exactly the KL sum; bound the finite-rate correction.
5. *(added)* If tight constants resist: prove the inequality version with explicit non-optimal constants — sufficient for GT4's kill-test as long as constants are computable on the declared class.

**Demonstration (acceptance criterion, protocol-trap microarticle style):** a 3-state example (mirror the published one, kernels as integer fractions) with a two-phase temperature schedule: compute exactly (Fractions) the lifted Σ_T, the per-edge affinity table, the B bound, and show (i) separation: schedule-induced asymmetry ≤ B while a genuinely driven variant exceeds B; (ii) common-π limit recovers the published theorem's zero. Artifact: `math/gb1_temperature_trap.md` (statement + proof) + `artifacts/gb1_demo.json`.

**Fallback:** GT4 ships with GT4(a) at conditional grade, the discipline cited as an open obligation, and the affinity audit reported raw (no lawfulness classification of the loop's asymmetry).

## GB2 — Protocol-Relative Closure Deficit

**Context.** [B]'s CD is stationary. Read `../reference/B_cast_a_stone.md` §§8–9: the eleven places stationarity enters, what survives (chain rule, KL form, Pinsker, inf-monotonicity are law-agnostic), the R1–R9 requirements, and the two candidate routes with sketches.

**Decision (per the digest's recommendation):** primary definition = **protocol-ensemble joint law**: fix the declared finite protocol catalog 𝒫 with declared rational weights λ(ρ), declared initial laws μ₀^(ρ), and declared evaluation times; CD^prot_τ := I(X_t; Y_{t+τ} | Y_t, [t, ρ visible or marginalized — declare BOTH variants: `windowed` (t, ρ) in the conditioning = per-cell tables; `ensemble` marginalized = the headline scalar]. Quasi-stationary-window slices are the reported GT1 table cells.

**Prove (the two propositions of the acceptance criterion):**
1. **Decomposition analogue (Prop 3.2′):** H(Y_{t+τ}|Y_t, C) = H(Y_{t+τ}|X_t, C) + CD^prot under the declared law with conditioning package C — chain-rule content, the work is showing each term is an explicit finite rational-weighted sum computable from the declared data, with the intrinsic-noise vs discarded-distinction reading intact.
2. **Lumpability equivalence (Prop 3.5′):** CD^prot = 0 iff the time-inhomogeneous lumpability condition holds along every positive-weight (ρ, t) cell: the fiber-conditioned one-step-τ macro law is independent of the micro state within each fiber, for the kernels active in that cell (Kemeny–Snell condition per cell, full-support caveat inherited — state it). Prove both directions finitely.

**Consistency theorem (the GT1 gate):** if every protocol in 𝒫 is the constant-ε protocol started from π_ε, CD^prot reduces exactly to [B]'s stationary CD.

**Demonstration:** exact computation on East N=6–8: equilibrium catalog (reduction check), lumpable control (exact zero via the factorization identity), aging catalog (CD^prot > 0). Artifact: `math/gb2_protocol_cd.md` + `artifacts/gb2_demo.json`.

## GB4 — Metastability Window Theorem

**Context.** F-I T-IC-02: δ_{τ,f} ≤ ε_{τ,f} (retention error), constant 1, proof via TV contraction + convexity (`../reference/foundations_I.md` §4 — the proof mechanism is quoted there because GB4 extends it).

**Problem statement.** For the East/FA models with lens `L_energy` and declared prototypes: prove a two-sided window bound — there exist explicit τ_β (fast/intra-block scale) and τ_α (slow/relaxation scale), computable from spectral data of the kernel(s), such that for τ_β ≪ τ ≪ τ_α: ε_{τ,f} ≤ C₁·g_fast(τ) + C₂·(τ/τ_α), with explicit constants on the audited class — formalizing "the glass layer exists at intermediate timescales." Route: spectral decomposition of K_ε restricted to lens blocks; τ_β from the within-block gap (fast equilibration onto block-quasi-stationary distributions), τ_α from the global gap; prototype choice `proto_gibbs` makes the block-quasi-stationary comparison natural. This is standard metastability technology (restricted spectral gaps / quasi-stationary distributions) applied to a declared finite chain — no asymptotics needed, all constants finite and computable.

**Demonstration:** numerically verified window edges — compute ε_{τ,f} exactly over the τ ladder at several ε; overlay the proved bounds; the window where δ stays small while CD > 0 persists is the GT1 "accessible τ-window" declaration. Artifact: `math/gb4_window.md` + window-edge table consumed by GT1/GT6 shell configs.

**Fallback:** GT1/GT6 declare the window empirically from `spectral_gaps.json` (a declared choice, not a theorem), with GB4 filed as open obligation.
