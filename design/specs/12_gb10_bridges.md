# 12 — GB10 / Leg 3: Empirical Bridge Records (Kovacs PVAc, Spin Glass, Colloid)

**Audience:** implementer agent. Leg 3 never runs new lab work and never claims the models "realize" the lab systems. It files **empirical-bridge records** per F-II `prop:empirical-bridge` — five typed fields per record, stored in `Audit(D)` — connecting the formal glass certificates to three published experimental literatures. See `../reference/foundations_II.md` §6 for the verbatim proposition.

**Target statement (proposal Leg 3):** *measured Kovacs signatures are lab-grade predictive witnesses; the measured insufficiency of single-T_f models is the lab shadow of MaxFiber ≥ 2.* Both clauses are bridge claims (grade `bridge_record`), reported per F-II `prop:visibility` as declared-class shadows.

---

## 1. The record format

Each bridge is one JSON file in `bridges/` validating against `../schemas/empirical_bridge.schema.json`, with the five mandatory fields (names fixed by F-II):

1. `substrate_observable` — the physical system and the measured one-time observable (e.g. PVAc specimen; specific volume v(t) at 1 atm).
2. `instrument` — measurement apparatus + resolution/visibility statement (what the instrument can and cannot see), filed as an `Ann_Vis`-style sub-record.
3. `level_map` — the explicit correspondence: which formal object each measured structure shadows. Always *formal → measured*, e.g. "model deficit CD_τ > 0 ↔ persistent aging drift of v(t) at fixed (T, P)"; "split-pair witness (μ_K, μ_eq) ↔ two specimens with equal v, different subsequent dv/dt".
4. `threshold_witness_relation` — the declared numeric criterion for when a measured signature *counts* as a witness shadow (e.g. "hump amplitude exceeding k× instrument noise band with sign reversal after crossing"), with thresholds declared before reanalysis.
5. `suppressed_structure_nonclaims` — what the bridge does NOT claim: no realization claim; no continuum-limit claim; the lab substrate's microscopic detail is suppressed structure; no claim that KCM kinetics are the lab kinetics.

Bridge records are **standalone top-level files** validating against `empirical_bridge.schema.json` (they do NOT nest inside the artifact envelope's `payload`); the envelope-equivalent metadata they need is already native to the schema (formal-artifact hashes in `level_map`, mandatory nonclaims, `status`).

## 2. The three bridges

### B1 — Kovacs 1963 PVAc volume recovery
- Substrate/observable: polyvinyl acetate, specific-volume departure δ(t) = (v − v_∞)/v_∞ after the T₀→T₁ (age t_w) →T₂ protocol; source: Kovacs 1963 (Fortschr. Hochpolym.-Forsch. 3, 394) + modern replications (e.g. Bertin et al. / McKenna-group data as available in the published figures — data extracted from figures must record the digitization method and resolution as part of `instrument`).
- Level map targets: t_K crossing ↔ formal t_K; hump non-monotonicity ↔ GT2 witness structure; hump-height dependence on t_w and ΔT ↔ GT7 `hump_surface` readouts (qualitative order relations only — the model is not the polymer).
- Threshold-witness relation: declared noise band from the source's stated precision (Kovacs reports ~10⁻⁴ resolution in δ); a measured pair (equal δ, different later δ-slope beyond band) = lab-grade split-pair shadow.

### B2 — Spin-glass memory/rejuvenation
- Substrate/observable: CuMn or CdCr₁.₇In₀.₃S₄-class spin glasses; ac susceptibility χ″(ω, T) under cooling-stop-reheat protocols (Jonason et al. 1998 PRL 81:3243 and successors).
- Level map: the memory dip reappearing on reheat ↔ loop acting trivially on current panel, non-trivially on predictive quotient (GT2 loop certificate shadow); rejuvenation ↔ route residue (F-IV F3 instantiation).
- Threshold: dip depth vs reference cooling curve exceeding declared multiple of quoted experimental scatter.

### B3 — Colloidal-glass aging
- Substrate/observable: PMMA or polystyrene colloidal suspensions near φ_g; intermediate scattering function f(q, t_w, t) two-time decay (Courtland & Weeks 2003-class DLS/confocal data).
- Level map: t_w-dependence of relaxation at fixed one-time structure (g(r) stationary while dynamics age) ↔ GT1 CD > 0 shadow (current panel stationary, future distribution t_w-dependent); this is the cleanest "equal current, different future" lab family.
- Threshold: declared band on f(q,t) separation at matched structural panels.

## 3. Workflow for the implementer

1. Write `../schemas/empirical_bridge.schema.json` mirroring §1 (five required fields + envelope).
2. Write `experiments/check_bridges.py`: validates schema, checks every `level_map` entry cross-references an existing formal artifact hash, checks every record has non-empty `suppressed_structure_nonclaims` containing the mandatory set, checks thresholds are declared numerals.
3. Fill B1–B3 from the published sources. Where exact numbers require figure digitization the record stores the digitized table inline with provenance (figure number, digitization tool, estimated error). If a source is inaccessible, file the record with `status: "pending_source"` and the citation — an honest gap, not a silent omission.
4. Acceptance (proposal GB10 row): each lab claim carries the complete five-field record; `check_bridges.py` passes on all three; no record makes a realization claim (checker greps a denylist: "realizes", "is the", "derived from first principles").

## 4. What Leg 3 must never do

- Fit model parameters to lab curves (that would be a realization move and would also violate GB7's no-fit freeze).
- Use lab data to *select* formal grid points post hoc.
- Present error bars as new formal content (F-II `prop:probability-closure`: they are threshold annotations).
