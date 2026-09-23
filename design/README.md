# Glass Is an Unclosed Layer — Implementation Design Pack

This directory is the complete design package for executing the experiments of
[`../proposal_glass_unclosed_layer.md`](../proposal_glass_unclosed_layer.md). It is written so that the
implementer agent **never needs to read the SBT source papers or figure out SBT science**: the
`reference/` digests restate every needed definition/theorem with exact labels, and the `specs/` docs
turn the proposal's GT1–GT7 / GB1–GB10 items into concrete build instructions with acceptance criteria.

## How to use this pack (implementer runbook)

1. Read `specs/00_architecture.md` (what/where/order/honesty rules), then `specs/01_models.md` and
   `specs/02_pipeline.md` end-to-end. Skim every `reference/` digest's table of contents so you know
   where to look things up; read fully on demand.
2. Follow the phases of `00_architecture.md` §4. Do not start a phase before the previous gate is green.
3. Every universal/negative claim quantifies over a frozen finite class; every freeze is a git commit
   whose hash appears in dependent artifacts (`00_architecture.md` §7). When in doubt about claim
   wording, `reference/foundations_II.md` §16 is the binding checklist.
4. Borrow code per the borrow plans in `reference/code_route_transport.md` and
   `reference/code_randomness_cantor.md` (vendored copies with provenance headers, no cross-repo imports).
5. If a new-math item (GB1/GB2/GB4) stalls, use its spec's fallback filing — an explicit open
   obligation. Never silently downgrade a claim.

## Contents

### specs/ — build instructions (read in numeric order)

| Doc | Covers | Proposal items |
|---|---|---|
| `00_architecture.md` | repo layout, phases + gates, deliverable inventory, honesty ledger, freeze discipline | §5, §6, §8 |
| `01_models.md` | East/FA/trap/REM models, rational-grid discipline, kernels + detailed balance, protocols incl. Kovacs, lens catalog, controls, feasibility | §1, §2 substrate |
| `02_pipeline.md` | thermal port of [A]'s exact-finite package; exact witness constructions (reflection pairs, randomized-stop tuning, Kovacs loop); benchmark family; robustness | GB3, Leg 1 |
| `03_gt1_nonclosure.md` | CD_τ and δ_{τ,f} tables, prototype rules, controls at exact zero, GB2 gate | GT1 |
| `04_gt2_witnesses.md` | witness + loop certificates, P4 routing rule, Lean hooks | GT2 |
| `05_gt3_foreclosure.md` | constructive foreclosure sweep (2^|im f| predicates), M-canonicity exhibit, GB5 repair sweep | GT3, GB5 |
| `06_gt4_triage.md` | six-regime kill-test panel, 6×4 outcome matrix, affinity audit, CM2/CM5 imports, GB1 status | GT4 |
| `07_gt5_dimension.md` | MaxFiber/fiber profiles, buyback curves, F24 event filings | GT5 |
| `08_gt6_extension.md` | strict-extension stack: shell, knockouts-by-re-simulation, Fekete pressure (route (a) fixed), 5 hypotheses, disintegration gap, GB8 gate-table filing + checker | GT6, GB6, GB8 |
| `09_gt7_constants.md` | run-only readouts, GB7 freeze/pre-registration/scoring, Leg-2 MC sweeps | GT7, GB7, Leg 2 |
| `10_new_math.md` | GB1 temperature-trap theorem, GB2 protocol-relative CD, GB4 metastability window — statements, proof plans, demos, fallbacks | GB1, GB2, GB4 |
| `11_gb9_lean.md` | vendor [A] Lean, glass instance + export bridge, F-III name wrappers, fidelity table | GB9 |
| `12_gb10_bridges.md` | five-field bridge records for PVAc/spin-glass/colloid + checker | GB10, Leg 3 |

### reference/ — SBT science digests (self-contained, exact labels preserved)

| Doc | Source | Feeds |
|---|---|---|
| `foundations_I.md` | F-I Emergence Calculus | packaging endomap, defects, protocol trap, forcing, affinity audits |
| `foundations_II.md` | F-II Admissibility Meta-Theory | claim grades, six roles, bridges, fidelity legend, honesty checklist (§16) |
| `foundations_III.md` | F-III Interaction Calculus | T7/T8/T11–T14, promotion gates, AdmDomain, CM1–12, GT6 filing checklist (§15) |
| `foundations_IV.md` | F-IV Structural Laws | F2/F3/F8/F12/F20/F24/F46 etc. + glass instantiation notes |
| `A_holonomy_memory.md` | [A] Holonomy with Memory | the pipeline: quotients, witnesses, loops, diagnostics, benchmarks, Lean, porting checklist (§17) |
| `B_cast_a_stone.md` | [B] To Cast a Stone | closure deficit, buyback curves, benchmark discipline, GB2 requirements (§9) |
| `C_cantor_shell.md` | [C] Cantor Shell | strict-extension obligation stack, GT6/GB6 checklist (§9) |
| `primer_and_protocol_trap.md` | Primer + Protocol-Trap microarticle | validation doctrine, P1–P6, published trap theorem + GB1 analysis |
| `code_route_transport.md` | six-birds-route-transport repo | [A] pipeline borrow plan, artifact schemas, Lean layout |
| `code_randomness_cantor.md` | six-birds-randomness + six-birds-cantor repos | CD code, buyback code, [C] scripts, checker stack borrow plan |

### schemas/ — machine-readable contracts

`model_config`, `artifact_envelope` (common envelope: claim grade, quantifier domain, nonclaims,
controls), `continuation_catalog` (GB3; its hash scopes M), `witness_certificate` (GT2 payloads),
`predictions_registry` (GB7 pre-registration), `empirical_bridge` (GB10 five fields).

## Known open risks (tracked, not hidden)

1. **GB1** is the load-bearing new theorem; GT4(a) has a defined conditional-grade fallback.
2. **Exact witness constructions** rest on the declared-catalog moves of `02_pipeline.md` §4
   (reflection pairs, randomized-stop kernels); the disclosure discipline there is mandatory.
3. **Cost**: exact rational matrix powers cap certificate runs at N≈10 dense / N≈12 sparse-support;
   feasibility notes in `01_models.md` §9. Leg-2 float64 sweeps carry the larger N.
4. **Knockouts are by re-simulation** (parity with [C]'s pilot script, which also re-simulates —
   see the corrected note in `reference/code_randomness_cantor.md` §7); budget for six re-runs per
   frozen witness.
5. Digest provenance: each `reference/` doc distinguishes paper-verbatim content from digest
   reconstruction; where the proposal's gap-list numbering didn't match the papers, the digests say so
   explicitly (see `foundations_I.md`, `foundations_III.md`, `foundations_IV.md` notes).
