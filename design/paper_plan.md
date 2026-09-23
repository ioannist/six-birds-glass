# Phase 5 — Paper plan: "Glass Is an Unclosed Layer"

Status: PLAN ONLY — not yet executed. Authored 2026-07-06, after the external-review remediation
cycle closed (Eddy verdict SHIP; full suite 400/400; all gates clean).

Governing constraints (already binding on this phase, from the design pack and standing project
discipline):

- `design/specs/00_architecture.md` §Phase 5: structure mirrors proposal §3; every theorem cites its
  proposal-§4 anchor row; the nonclaims ledger and the Lean fidelity table are printed **in full**;
  the F-II §16 checklist (28 items, sections A–H in `design/reference/foundations_II.md`) is walked
  item-by-item as the final gate.
- Proposal §8 item 5: title "Glass Is an Unclosed Layer: Kovacs Memory as Predictive-Quotient
  Residue"; nonclaims ledger printed in full.
- Anti-reductionism spirit: the paper must never claim a green certificate suite proves emergence;
  foreclosure results are the gate working, not a reduction across the Q/M layer boundary.
- Operating model: Cody writes, Eddy reviews every certificate-producing/claim-carrying packet before
  the next builds on it, manager gates. Eddy review focus: scientific/arithmetic correctness and
  honesty-ledger compliance, not style.
- No git commits without explicit user instruction.

---

## Part 1 — Preparation (packets P5-01 … P5-08)

### P5-00 — User decisions needed before P5-01 (manager collects, no packet)

1. **Venue/format.** Recommendation: a long-form arXiv preprint (single-column article class,
   no journal page limit), cross-listed cond-mat.stat-mech + math-ph, with the Lean sources and the
   artifact tree as the ancillary/reproducibility package. Rationale: the paper's core value is the
   certificate discipline itself; a length-limited journal format would force cutting exactly the
   ledgers the design pack requires to be printed in full. A journal-targeted condensation can be a
   later derivative.
2. **Baseline commit.** The entire build to date is uncommitted; every artifact's `code_version` is
   stale at the pre-build commit. The paper must cite a frozen evidence base. Recommendation: one
   baseline commit before P5-01, then regenerate the (few) artifacts whose `code_version` field
   should reflect it — OR explicitly keep the established content-hash freeze discipline as the
   paper's citation mechanism and document that git history is not used (consistent with how GT7 was
   actually run). Either is honest; the second requires no regeneration churn. Manager recommends the
   second, with the commit still made for safety.
3. **Authorship / acknowledgments / license** for the preprint. Pure user decision.

### P5-01 — Evidence-base freeze + paper manifest

Build `paper/evidence_manifest.json`: every file under `artifacts/`, `registry/`, `bridges/`,
`lean/GlassWitness/`, plus the two checker scripts and the frozen scorer, with sha256 for each.
This is the single hash root the paper cites; nothing outside it may be cited as evidence.
Extend `tests/test_citation_consistency.py` to validate the manifest against current bytes.
Gate: manifest complete (compare against the 18 enveloped artifacts + registries + Lean fidelity
table); citation test green. Eddy review: completeness, no orphaned artifacts.

### P5-02 — Claims ledger (the paper's load-bearing skeleton)

Build `paper/claims_ledger.json` + human-readable `paper/claims_ledger.md`: one row per claim that
will appear in the paper — all GT1–GT7, the GB bridges actually built (GB1–GB3, GB6–GB10 as
applicable), the two independent findings (trap ε-invariance, Lean current/future collapse), and
every honest negative (material_forcing_count=0, GT7 8-pass/14-fail transfer outcome, GB5 not built,
GT2 loop certificate gap, [B] benchmark-parity control open). Each row: claim statement (exact,
final wording), claim grade (F-II vocabulary), quantifier domain, proposal-§4 anchor row, supporting
artifact paths + sha256 (from P5-01 manifest), nonclaims, and the F-II §16 items it must satisfy.
This ledger is what every results section is written FROM, and what the final checklist walk is
checked AGAINST.
Gate: every enveloped artifact is reachable from some row; every row's hashes resolve; wording for
each claim matches the corrected post-remediation scope (e.g. GT6 verdict basis = F-III T19/T20,
NOT paper [C]'s thm:strict-extension; GT5 saturation_budget=1 witness, not general single-scalar
insufficiency; GT1 scoped to East N=8 / L_energy).
Eddy review: MANDATORY and the most important review of Phase 5 — every subsequent packet copies
wording from this ledger.

### P5-03 — Gap triage: close vs. disclose

One packet deciding, per open item, "close before paper" vs "disclose as open" with a one-paragraph
justification each. Recommendation going in: **disclose everything, build no new science in Phase 5.**
The honest-negative filings are part of the contribution (the protocol produces falsifiable
outcomes), and the external review already accepted the disclosed-gap postures. Items: GB5 repair
sweep; GT2 loop certificate; [B] benchmark-parity control for GT1; GT7's 14 interval failures
(analysis of failure pattern belongs in the paper's discussion, not new runs); material forcing
absent for the shipped shell. Output: `paper/gap_register.md`.
Eddy review: is any "disclose" actually an item the paper's core claims silently depend on?

### P5-04 — Figures and tables plan + deterministic figure pipeline

Inventory every figure/table the paper needs, each sourced ONLY from manifest artifacts:
Kovacs hump traces (pipeline/kovacs_hump), GT1 CD/δ tables + ratios (1.639 vs margin 3/2; 289/121 vs
margin 2), GT2 witness table, GT3 foreclosure table, GT4 regime-triage table, GT5 buyback curve,
GT6 gate table + knockout panel + verdict_basis text, GT7 transfer scoreboard
(8 pass / 14 fail / 294 no-prediction / 22 unobserved) + east reference bands + deficit decay,
spectral gaps, Lean fidelity table (printed in full — 17 rows), nonclaims ledger (printed in full,
aggregated from all envelopes).
Build `paper/figures/build_figures.py`: deterministic (no timestamps/randomness — same discipline
that R-H enforced on GT1), reads only manifest-listed artifacts, writes PDF/PGF to
`paper/figures/out/`. New test: figure builder is byte-deterministic and touches only manifest paths.
Eddy review: numbers in figure sources vs artifact payloads.

### P5-05 — Bibliography

`paper/references.bib`, three strata:
1. SBT corpus (Primer, F-I…F-IV, [A], [B], [C], protocol-trap microarticle) with the citation keys
   the digests already use.
2. Literature already researched during the build: trap models (Bouchaud 1992; Monthus–Bouchaud
   1996; Diezemann–Heuer 2011; Bertin 2012), lumpability (Kemeny–Snell 1960; Buchholz 1994), Chu
   spaces (Barr 1979; Pratt 1999; Parente 2024).
3. Glass-physics canon the introduction needs: Kovacs 1963 (the original crossover experiment);
   Tool / Narayanaswamy / Moynihan fictive-temperature lineage; KCM reviews (Ritort–Sollich 2003;
   Garrahan–Sollich–Toninelli 2011); East model (Jäckle–Eisinger 1991); FA model (Fredrickson–
   Andersen 1984); aging/memory reviews (e.g. Berthier–Biroli 2011; Arceri et al. as appropriate);
   Kovacs-hump modern literature (e.g. Bertin–Bouchaud–Drouffe–Godrèche 2003).
   Every entry verified online (title/authors/year/identifier) before inclusion — no
   hallucinated references; anything unverifiable is dropped or replaced.
Eddy review: spot-check correctness of bibliographic data and that each in-text citation claim about
a reference is supported by that reference's actual content (using the digests + web checks).

### P5-06 — Narrative architecture memo

`paper/narrative.md`, ~2 pages, fixing before any prose is written:
- **Thesis sentence** (from proposal §0) and the four-part contribution list already agreed:
  (i) the certificate framework instantiated end-to-end on a real physics target with honest
  negative filings; (ii) the GT1–GT7 result complex with exact scopes; (iii) the freeze-and-transfer
  pre-registration protocol with its actual 8/14/294/22 outcome; (iv) the Lean-checked core with the
  scope-boundary/collapse finding.
- Section map mirroring proposal §3 (per the Phase 5 gate) with the writing order (Part 2 below).
- Where the two findings live: ε-invariance presented as a known-in-literature property (cited),
  used as a trap-model design caveat, NOT claimed as novel; the Lean collapse finding presented as a
  genuine formal result about RouteTransportCore's expressiveness boundary.
- Honesty-ledger placement: nonclaims as a dedicated section + per-result scope boxes.
- Tone rules: the banned-overclaim phrase list from the remediation ("full obligation stack
  satisfied", "provably insufficient", "git history is the proof", "controls at exact 0"
  unqualified) becomes a greppable denylist enforced by a test in P5-07.
Eddy review: does the narrative anywhere promise more than the claims ledger licenses?

### P5-07 — LaTeX infrastructure + paper gates

`paper/` build: `main.tex` skeleton (section stubs per narrative memo), `macros.tex` (one macro per
claim-citation: `\claimref{GT1.east.8.L_energy}{a0cea2…}` style so hashes are single-sourced from
the manifest), latexmk build, and **paper gates** wired into the test suite:
- `tests/test_paper_gates.py`: (a) every `\claimref` hash resolves against the manifest and current
  artifact bytes; (b) every claims-ledger row is cited at least once in the .tex; (c) denylist
  phrases absent; (d) the .tex compiles clean.
- The manager's per-packet full-suite gate now includes the paper gates.
Eddy review: are the gates real (not vacuous), same standard as the citation-consistency test.

### P5-08 — External-review-request template v3 (prepared, not sent)

Update `external_review/EXTERNAL_REVIEW_REQUEST` for a future full-paper review round (Phase 0
study-SBT-first structure retained; new Track C: does the paper's prose match the artifacts?).
Prepared now so the post-writing review round has no setup latency. Not sent until the user says so.

---

## Part 2 — Writing (packets W-01 … W-12 + gates)

Writing order is deliberately results-first, framing-last: results sections are transcription from
the claims ledger (low risk, high verifiability); the introduction is written only once the results
prose is frozen, so it cannot overpromise.

Each W-packet = one section drafted by Cody FROM the claims ledger + narrative memo, with these
uniform acceptance criteria: every quantitative statement carries a `\claimref`; scope/nonclaims box
present; no denylist phrases; paper gates + fast suite green. Each packet gets an Eddy review
(science + honesty, per standing focus) before the next section that depends on it starts;
stylistically independent sections may be drafted in parallel but are reviewed sequentially.

- **W-01 — Formal architecture + methods.** SBT background needed by a physics reader (compressed
  from the digests; cites the SBT corpus rather than re-deriving it), the certificate/envelope
  discipline, claim-grade vocabulary, the content-hash freeze mechanism as actually implemented.
- **W-02 — Models and pipeline.** East/FA/trap/unconstrained models, exact rational-arithmetic
  pipeline, benchmark parity with [A]/[B], the ε-invariance property of the declared trap weights
  (with literature citations) and its consequence for what the trap family can/can't probe.
- **W-03 — GT1** (non-closure; East N=8 L_energy certificate; the equilibrium≠zero-CD-for-
  constrained-models point as a stated lemma with the lumpable control; disclosed open: [B] parity
  control).
- **W-04 — GT2 + GT5** (Kovacs witness as P4 staged-dependence per F-II §16-B3; loop-certificate gap
  disclosed; MaxFiber ≥ 2 + buyback curve with saturation_budget=1 scope).
- **W-05 — GT3 + GT4** (foreclosure over the declared lens class — framed per the anti-reductionism
  rule: foreclosure is the gate working; regime-triage table with the five killed controls).
- **W-06 — GT6** (strict-extension certificate: gate table, knockout panel, verdict_basis verbatim —
  T19/T20 basis, material forcing checked-and-absent as an honest negative).
- **W-07 — GT7 + GB7** (freeze-and-transfer protocol F1–F5, the full scoreboard including the 14
  failures, failure-pattern discussion, run-only thesis as filed).
- **W-08 — GB9 / Lean** (what is formalized, fidelity table in full, the scope-boundary/collapse
  finding with the lumpability/Chu-space citations, what the formalization does NOT capture —
  the honest Instance.lean story: structural, not numeric).
- **W-09 — GB10 / empirical bridges + lab legs** (bridge records, what a lab replication would
  require).
- **W-10 — Discussion + nonclaims ledger in full** (what is established at which grade; what is
  open; explicit anti-reductionism paragraph; the gap register from P5-03).
- **W-11 — Introduction + abstract + conclusion** (written last, from frozen results prose; the
  "one-line essence" from proposal §8 as the closing frame).
- **W-12 — Consolidation pass** (one packet: terminology/notation consistency sweep across all
  sections, figure/table reference check, bibliography completeness, single voice).

### Final gates (in order; each blocks the next)

1. **G1 — F-II §16 checklist walk.** All 28 items (A1…H-final) walked item-by-item against the
   finished draft; filed as `paper/f2_s16_checklist.md` with per-item evidence (section + claimref).
   Any failure → fix packet, re-walk the affected section. This is the design pack's declared final
   gate and is executed by the manager, then independently re-walked by Eddy.
2. **G2 — Full verification run.** Full `pytest -q` (incl. paper gates), `lake build`, both checkers,
   figure-builder determinism, on a quiet tree.
3. **G3 — Eddy full-paper review.** Whole-draft review packet (science, arithmetic, honesty ledger,
   claim-vs-artifact fidelity). FIX-FIRST loop until SHIP.
4. **G4 — External review round 2.** Zip v3 + review request v3 (from P5-08) handed to the user to
   forward, per the established process. Remediate findings via the same R-series loop.
5. **G5 — User sign-off** on the final PDF; then (on explicit instruction only) baseline commit /
   arXiv packaging.

### Rough effort estimate

Preparation: 8 packets ≈ 8–10 Cody/Eddy cycles. Writing: 12 packets + 5 gates ≈ 15–18 cycles
(W-packets are prose-heavy but transcription-grade; the expensive reviews are P5-02, G1, G3).
No new simulations or proofs anywhere in Phase 5 unless gap triage (P5-03) overturns the
"disclose, don't build" recommendation.
