# 00 — Architecture: Repo Layout, Execution Phases, Deliverable Inventory

**Audience:** implementer agent. This is the top-level map: what gets built, in what order, where it lives, and what "done" means for each piece. Detail lives in the numbered spec docs; SBT background lives in `../reference/`.

---

## 1. What is being built (one paragraph)

An exact-finite computational laboratory that instantiates the SBT emergence calculus on kinetically constrained glass models, producing machine-checkable certificates for seven glass theorems (GT1–GT7 of the proposal): the thermodynamic lens does not close (GT1); the Kovacs effect yields formal predictive witnesses while the loop certificate remains open (GT2); static order parameters are foreclosed and the predictive quotient M is the canonical state (GT3); glass memory survives the six-regime kill-test panel (GT4); MaxFiber ≥ 2 is certified with a buyback-curve mechanism, with `saturation_budget = 1` for the shipped witness (GT5); the structural-relaxation layer receives a shell-local strict-promotion certificate via F-III's generic non-factorization gate, while the fuller Cantor-shell material-forcing hypothesis was checked and found absent (GT6); Kovacs-hump constants are run-only, validated out-of-sample under a no-fitting content-hash freeze (GT7). Two genuinely new theorems (GB1 temperature-protocol trap, GB2 protocol-relative closure deficit) are proved alongside.

## 2. Target repo layout (build inside six-birds-glass)

```
six-birds-glass/
  design/                    # ← these docs (read-only for implementer)
  src/sixbirds_glass/
    models/                  # spec 01: east.py, fa.py, trap.py, rem.py, kernels.py, lift.py
    lenses/                  # spec 01 §6: lens catalog, definability enumeration
    protocols/               # spec 01 §7: schedule words, named protocol catalog, Kovacs search
    pipeline/                # spec 02: histories, continuations, quotients Q/M, π, witnesses,
                             #   loop actions, packaging endomap E_{τ,f}, deficits δ and CD
    triage/                  # spec 06: six-regime classifier + thermal benchmark family
    extension/               # spec 08: shell, Fekete functional, gate table, knockouts (GT6/GB6)
    constants/               # spec 09: hump readouts, buyback curves, transfer scoring (GT7/GB7)
    io/                      # config loading, Fraction serialization, artifact writers, hashing
  configs/                   # frozen JSON configs, one per experiment run
  experiments/               # runnable entry scripts, one per GT deliverable
  artifacts/                 # outputs: certificates, tables, audit records (git-tracked)
  registry/                  # GB7 freeze registry: hashes, pre-registered predictions
  lean/                      # GB9: vendored [A] modules + glass witness instances
  bridges/                   # GB10: empirical five-field bridge records (Kovacs/spin-glass/colloid)
  math/                      # GB1/GB2/GB4 theorem notes + proofs (LaTeX/markdown)
  tests/
```

Borrowing policy: copy modules from `../six-birds-route-transport` (pipeline core), `../six-birds-randomness` (CD computation), `../six-birds-cantor` (gate table/checker), `../six-birds-protocol-trap` (affinity audits) into `src/sixbirds_glass/` or `vendor/` with provenance headers, per the borrow plans in `../reference/code_*.md`. Do not import across repos at runtime; vendored copies keep the repo self-contained and hashable for the GB7 freeze.

## 3. Component dependency graph

```
models (01) ──► protocols (01 §7) ──► lifted autonomous chains
     │                                     │
     ▼                                     ▼
 lenses (01 §6) ─────────────► pipeline (02): histories/continuations (GB3)
                                   │
        ┌──────────────┬───────────┼──────────────┬───────────────┐
        ▼              ▼           ▼              ▼               ▼
   CD & δ tables   witnesses    foreclosure    MaxFiber       triage panel
   GT1 (03)        GT2 (04)     GT3 (05)       GT5 (07)       GT4 (06)
        │              │                                          │
        ▼              ▼                                          │
   GB2 math        Lean checks (GB9, spec 11)                 GB1 math (10)
        │              
        ▼              
   strict-extension stack GT6 (08: GB6 shell + gate table + GB8 filing)
        
   constants & transfer GT7 (09: GB7 harness, Leg-2 sweeps)   bridges (12: GB10)
```

Build order = phases below; the graph shows why: everything downstream consumes the pipeline layer, so GB3 (thermal continuation families) is the critical path.

## 4. Phases (with gate criteria)

**Phase 0 — Scaffold (spec 01 §10, 02 §setup).** Model layer + acceptance tests green. Gate: all six §10 tests pass for East and FA at N ∈ {6, 8, 10}; unconstrained-control lumpability exact.

**Phase 1 — Pipeline port (GB3 + GB8 skeleton).** Vendored [A] pipeline runs on the lifted East chain; the six [A] benchmarks re-instantiated with thermal semantics reproduce their published regime labels. Gate: benchmark-parity table — every thermal benchmark lands in the same regime class as its [A] original, artifact names preserved.

**Phase 2 — Core certificates (GT1, GT2, GT3, GT5; GB1, GB2 in parallel).** Gate: (i) GT1 tables with structurally lumpable CD controls at exact zero, constrained equilibrium rows filed as nonzero stationary baselines, and δ controls passing the fixed-point/macro-closure identities with aging rows exceeding the equilibrium baseline by the declared margin (see `03_gt1_nonclosure.md` §3 — δ has no exact-zero control); (ii) witness certificates non-empty at the Kovacs point and empty on controls, with the loop certificate explicitly filed open because declared-history closure does not stabilize; (iii) foreclosure check exhausts the declared lens class; (iv) MaxFiber ≥ 2 with a buyback curve mechanism, not a general single-scalar-insufficiency claim; (v) GB1/GB2 proofs drafted or their absence filed as explicit open obligations per F-II conditional reporting.

**Phase 3 — Strict-extension stack (GT6: GB6 shell → obligations in [C] order → gate table; GB5 repair sweep).** Gate: shell-local strict-promotion gate-table artifact passes the vendored checker; knockout panel complete; paper-[C] material forcing filed with its observed value; GB5 repair sweep remains a not-yet-built standalone obligation until an exhaustive frozen-class witness ledger exists.

**Phase 4 — Constants + bridges (GT7: GB7 freeze, Leg-2 sweeps; GB10 records; GB9 Lean build green).** Gate: `registry/readouts.json` and `registry/predictions_<hash>.json` are frozen by their own sha256 `content_hash` values (the registry `freeze_note` documents the content-hash substitution for unavailable implementation commits) BEFORE target-family runs; transfer scores + failure report; `lake build` green; bridge records pass the field checker.

**Phase 5 — Paper assembly (proposal §8 item 5).** Structure mirrors proposal §3; every theorem cites its §4 anchor row; the nonclaims ledger and the Lean fidelity table are printed in full; the F-II §16 checklist (see `../reference/foundations_II.md`) is walked item-by-item as the final gate. Out of scope for the experiment specs but tracked here so it has a home.

Phase ordering within 2–4 may interleave, but the GB7 freeze point is hard: no East-family functional form may be edited after the FA/trap prediction file is committed.

## 5. Deliverable inventory (claim → artifact → spec)

| Claim | Artifact(s) in `artifacts/` | Spec | Status vocabulary |
|---|---|---|---|
| GT1 | `gt1_cd_tables/…json`, `gt1_delta_tables/…json`, controls at exact 0 | 03 | theorem-grade (audited class); CD numerics = deterministic computational evidence, not Lean |
| GT2 | `gt2_witness_certificates/…json`; loop certificate open — declared-history closure under repeated real loop application does not stabilize (see `04_gt2_witnesses.md` §Open loop-certificate item); Lean check hashes | 04, 11 | witness theorem-grade; loop certificate open item |
| GT3 | `gt3_foreclosure/lens_class_sweep.json` (2^{im f} enumeration + constructive witness per lens) | 05 | theorem-grade |
| GT4 | `gt4_triage/regime_table.json` (candidate + 5 killed controls) | 06 | theorem-grade modulo GB1 (else conditional) |
| GT5 | `gt5_dimension/max_fiber.json`, `gt5_dimension/buyback_curve.json` | 07 | theorem-grade |
| GT6 | `gt6_bridge/gate_table.json`, `knockouts.json`, `pressure_closure.json`, `audit.json` | 08 | certificate-grade, shell-local |
| GT7 | `gt7_constants/…`, `registry/predictions_<hash>.json`, `gt7_transfer_scores.json` | 09 | run-only; bridge-annotated error bars |
| GB1/GB2/GB4 | `math/gb1_temperature_trap.md` (+ exact-finite demo artifact), `math/gb2_protocol_cd.md`, `math/gb4_window.md` | 10 | new theorems; if incomplete, filed open obligations |
| GB5 | `gt3_foreclosure/repair_sweep_ledger.json` — status: not yet built; requires the full declared repair-class sweep per `05_gt3_foreclosure.md` §3 | 05 §GB5 | open substantial standalone task |
| GB9 | `lean/` build + `artifacts/lean_fidelity_table.json` | 11 | fidelity-labelled per F-II legend |
| GB10 | `bridges/kovacs_pvac.json`, `bridges/spin_glass.json`, `bridges/colloid.json` | 12 | bridge claims only, never realization |

## 6. Honesty ledger (binding, from proposal §6)

The implementer must carry these as assertions in artifact metadata, not prose:
- CD > 0 claims never phrased as novelty or irreversibility; P6_drive audit required for any arrow language.
- P3/route data never used as directionality; Kovacs futures filed as P4 staged dependence.
- No continuum-limit or ideal-glass-transition claims; every result indexed by (model, N, grid, protocol catalog, lens catalog) — the frozen shell.
- Lean fidelity labels at true fidelity; Python-only evidence labelled as such.
- Empirical legs are five-field bridge records only.
- Every "no X exists" claim quantifies over a frozen declared finite class named in the artifact.
- **Recognition-hypothesis caveat (F-II `rem:recognition-open` item (a)):** the GB8 filing includes a residual check for a finite balance law irreducible to the six roles in the glass aging dynamics; if one is found, the no-seventh-role ceiling is hit and the affected claims are re-graded to recognition grade and reported separately (see `08_gt6_extension.md` §2.6).

## 7. Config and freeze discipline

- One JSON config per run; configs are content-hashed (sha256 of canonical JSON); artifacts embed their config hash.
- `registry/FREEZE.md` records the ordered freeze events; each is a git commit whose hash is quoted in dependent artifacts. Canonical order (specs must use these event names):
  1. **lens-catalog freeze** (before any GT3 run — `05` §1);
  2. **protocol/continuation-catalog freeze** (GB3; scopes M — `02` §5);
  3. **repair-class freeze** (GB5, before GT2 runs — `05` §3.1);
  4. **GT6 threshold freeze** (knockout degradation + Δ gap thresholds, after Phase-0 calibration, before witness runs — `08` §1.5);
  5. **readouts + scoring-script freeze** (GB7 F1 — `09` §2);
  6. **East reference run** (F2);
  7. **predictions commit** (F3 — this IS the East functional-form freeze; not a separate earlier event).
- Seeds: certificates are deterministic (no RNG). Leg-2 Monte Carlo uses fixed seed lists declared in configs.
