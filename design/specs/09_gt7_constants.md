# 09 — GT7: Run-Only Constants, GB7 No-Fit Harness, Leg-2 Sweeps

**Claim being produced (GT7).** Declared run readouts — Kovacs-hump peak-time/height scalings vs (ε_hi, ε_lo, ε_mid, t_w), memory-dimension profiles, deficit decay exponents — transfer out-of-sample across model families (East → FA → trap) under a frozen no-fitting protocol; and by GT3 they are non-definable from the current lens, which certifies their run-only status (Primer §5 doctrine: the non-existence of the shortcut *is* the genuineness — see `../reference/primer_and_protocol_trap.md`).

**Anchors:** Primer §§5, 8; F-IV F42 (Irreducibility), F26 (Moduli/Contingency), F44 (Critical locus); F-II `prop:probability-closure` (error bars are bridge/threshold annotations, not new roles). See `../reference/foundations_II.md` and `../reference/foundations_IV.md`.

---

## 1. The readouts (declare BEFORE any sweep)

All readouts are defined on the *output of a named protocol run* — never fitted to data. Definitions are exact and procedural:

| Readout id | Definition | Produced by |
|---|---|---|
| `t_K` | first step t on the ε_mid leg of `P_kovacs(t_w)` with (⟨E⟩(t) − E_eq(ε_mid)) changing sign | exact trace (N ≤ 10) or MC trace (N ≤ 16, frozen seeds) |
| `hump_height` | max_t≥t_K (⟨E⟩(t) − E_eq(ε_mid)); report as exact rational (certificate runs) or mean ± MC band (sweeps) | same |
| `t_peak` | argmax of the above | same |
| `hump_surface` | the map (ε_hi, ε_lo, ε_mid, t_w) ↦ (t_K, t_peak, hump_height) over the declared grid product | Leg-2 sweep |
| `memdim_profile` | MaxFiber and buyback-curve knots (see `07_gt5_dimension.md`) as functions of protocol-catalog index | pipeline |
| `deficit_decay` | the sequence CD_τ(Π_std) and δ_{τ,f} over the declared τ ladder during aging; the "exponent" is a declared secant slope between two frozen ladder points, NOT a fit | GT1 tables |

Rules:
- **No fitting anywhere.** No least squares, no curve families, no optimizer. Every "scaling" is a declared finite table of exact readouts plus declared secant slopes between named grid points. If a reviewer-facing plot draws a line, the line is decoration; the claim object is the table.
- Error bars (MC sweeps only): seed-resampling bands, filed as threshold annotations per F-II `prop:probability-closure` — they do not create new claim content.

## 2. GB7 freeze-and-transfer protocol (the core discipline)

The transfer claim is: functional relationships *read off* on East predict FA and trap families out-of-sample. "Functional relationship" means a **frozen comparison rule**, e.g. "t_peak is monotone decreasing in ε_mid at fixed (ε_hi, ε_lo, t_w)", "hump_height at grid point g is within declared factor ρ of the East-calibrated reference value after the declared timescale rescaling map R". All such rules are finite, declared, and machine-checkable.

Ordered freeze events (each is a git commit; hashes quoted in artifacts):

1. **F1 — Readout freeze.** Commit `registry/readouts.json`: the table of §1 definitions, the grid products, the τ ladders. Blocks: any later edit to readout definitions.
2. **F2 — East reference run.** Run the full East sweep; commit `artifacts/gt7_constants/east_reference.json`.
3. **F3 — Prediction commit.** From East results ONLY, author `registry/predictions_<hash>.json`: for each (target family, grid point, readout) either a numeric interval, an order/monotonicity statement, or an explicit "no prediction" cell. Every prediction names the rescaling map R (declared, e.g. spectral-gap-ratio time rescaling — computed from §01 gap tables, not fitted). Commit BEFORE any FA/trap run; the commit hash is the pre-registration proof.
4. **F4 — Target runs.** Run FA and trap sweeps with configs whose `freeze_refs` include the F3 hash.
5. **F5 — Scoring.** `experiments/score_transfer.py` mechanically compares F4 outputs to F3 predictions: each cell scored pass/fail/no-prediction. Output `artifacts/gt7_constants/gt7_transfer_scores.json` with per-cell verdicts and aggregate counts. **Failures are reported, not repaired.** A repaired prediction would be a new F3 with a new hash and its own fresh target runs on an extended grid — never a retro-edit.

The scoring script must be committed at F1 (before any data exists) so the success criterion itself is frozen.

## 3. Leg-2 sweep engine (Monte Carlo)

Certificates (Leg 1) are exact and small; the hump *surfaces* need larger N and many grid points → Monte Carlo:

- Continuous-time is unnecessary; use the same discrete-time kernels as §01 sampled by direct simulation (site pick + heat-bath resample), N ∈ {12, 16, 20 (East/FA)}, ensembles of trajectories per grid point (declared count, e.g. 10⁵), frozen seed lists in configs.
- ⟨E⟩(t) estimated by ensemble mean; bands by seed-block resampling (declared block structure).
- Cross-validation duty: at N = 10, the MC pipeline must reproduce the exact-rational traces within declared tolerance (e.g. 3 band-widths) — this is a control filed with every sweep artifact.
- Implementation is free to use numpy bit-tricks (uint arrays of configurations, vectorized site sampling); no exactness requirement here.

## 4. Non-definability tie-in (why "run-only" is a theorem, not a vibe)

The SBT certificate of run-only status = GT3's foreclosure artifact: the readouts of §1 are functions of the *run* (trajectory-ensemble under a named protocol) that are provably not factorizable through the declared current lens (no static formula in the declared vocabulary computes them). The GT7 artifact must cross-reference the GT3 sweep artifact hash for each readout it declares run-only. No new computation — just the explicit link, absence of which is a filing error the checker rejects.

## 5. Artifacts

- `artifacts/gt7_constants/east_reference.json`, `fa_target.json`, `trap_target.json` — envelope + payload: grid → readout table, seeds, bands.
- `registry/readouts.json`, `registry/predictions_<hash>.json` (schema: `../schemas/predictions_registry.schema.json`).
- `artifacts/gt7_constants/gt7_transfer_scores.json` — per-cell {predicted, observed, verdict}, aggregate {n_pass, n_fail, n_nopred}, failure narratives.
- Claim grade: `run_only_readout`; evidence: `monte_carlo_frozen_seeds` (+ `exact_rational` for the N=10 cross-checks).

## 6. Acceptance criteria (from proposal GB7 row)

1. Predictions file committed before target-family runs — verifiable from git history (commit timestamps + freeze_refs).
2. Scoring script frozen at F1 and untouched through F5 (same blob hash).
3. Failure-reporting path exercised: the artifact format and paper table must render fail cells; at least one synthetic fail is injected in tests to prove the path works.
4. MC/exact cross-validation control passes at N = 10.
5. Machine-readable claim ledger: every GT7 table row carries {readout id, quantifier_domain, freeze_refs, GT3 cross-ref}.
