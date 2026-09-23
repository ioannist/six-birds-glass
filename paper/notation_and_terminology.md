# Notation and terminology — "Glass Is an Unclosed Layer"

This file fixes the notation and vocabulary used in `paper/sections/`. The operative rule for
this paper: **every framework term is introduced in ordinary probabilistic language first**
(`sections/sec_02_architecture_methods.tex` §2.1), and Six Birds Theory (SBT) labels appear only
as anchors or where a claim is filed in SBT vocabulary, always with a plain gloss. The intended
reader is a glass / statistical-physics reader with no SBT background.

## Models and parameters

| Symbol | Meaning | Notes |
|---|---|---|
| $N$ | number of spins (East, FA) | certificates at $N \le 10$ |
| $n_i \in \{0,1\}$ | spin at site $i$; up spin = mobile excitation | site 0 is a frozen up-spin wall (East) |
| $E(n) = \sum_i n_i$ | energy readout, the main lens $L_{\mathrm{energy}}$ | image size $N+1$ |
| $\epsilon$ | Boltzmann activation variable, role of $e^{-\beta}$ | declared rational grid $\{1/10,\dots,7/10\}$ |
| $c = \epsilon/(1+\epsilon)$ | up-spin equilibrium concentration | exactly rational |
| $T = -1/\ln\epsilon$ | nominal temperature | annotation only, never an input |
| $K_\epsilon$ | one-step random-scan heat-bath kernel at $\epsilon$ | reversible w.r.t. $\pi_\epsilon \propto \epsilon^{E}$ |
| $C_i(n)$ | kinetic constraint at site $i$ | East $n_{i-1}$; FA $\max(n_{i-1},n_{i+1})$; unconstrained $1$ |
| $w_k$ | trap escape weights (Bouchaud-type model) | $\pi_k \propto 1/w_k$ |
| $t_w$ | waiting (aging) time | |
| $\tau$ | prediction horizon (steps) | declared ladder $[1,2,4,8]$ |
| $t_K$, $t_{\mathrm{peak}}$ | Kovacs crossing time, hump peak time | run-only readouts |

## Closure objects

| Term | Symbol | Plain meaning |
|---|---|---|
| lens | $f$, $\Pi$ | the observable panel (map from microstate to readout) |
| closed / lumpable (at horizon $\tau$) | — | $\tau$-step readout transition probabilities agree across every positive-mass microstate with the same readout; equals lumpability of the (kernel, lens) pair only under full support; horizon-specific |
| closure deficit | $\mathrm{CD}_\tau(\Pi) = I(X_t; Y_{t+\tau} \mid Y_t)$ | nats (natural log) the readout must discard at horizon $\tau$; zero iff $\tau$-lumpable under the declared law and state distribution |
| packaging map | $E_{\tau,f}$ | evolve, push to lens, re-lift by declared prototypes |
| idempotence defect | $\delta_{\tau,f}$ | $\max_i \tfrac12\|(E^2-E)[i,\cdot]\|_1$: saturation diagnostic only; can be $>0$ for a lumpable lens (unconstrained $N{=}2$: $2/9$); reported as a ratio, never as a closure criterion |
| preparation history | $h$ | protocol word + resulting state distribution |
| current quotient | $Q$ | histories identified by equal present readout |
| predictive quotient | $M$ | histories identified by equal future statistics over the declared catalog |
| comparison map | $\pi: M \to Q$ | always exists; witnesses exist iff strictly refining |
| witness / split pair | $(h,h')$ | same now ($Q$-equal), different later ($M$-different); GT2 matches mean energy via a randomized stop with weight $\theta$ |
| MaxFiber | — | largest number of $M$-classes merged into one $Q$-class |
| buyback curve / lift | — | which added coordinates resolve the pair, per budget; loss = $(a-b)^2/2$ on the five-step future mean energies while unresolved, $0$ once separated |
| $T_f$, $D$, $n_1$ | — | GT5 coordinates: $T_f(\mu)=\mathbb{E}_\mu[i^*(E(n))]$ (grid index, not a temperature); expected up-up bond count; expected occupation of site 1 |
| shell | — | frozen eligibility conditions (model, $N$, $\epsilon$ grid, $\tau$ windows, non-equilibration, hump present) with an exit counter that must be $0$ |
| lens-definable predicate | $\mathrm{Def}(L)$ | yes/no function of the readout value; $2^{|\mathrm{im}\,f|}$ of them |
| strict extension / promotion | verdict `strict` | $M$ carries information $Q$ cannot; certified by gate table + knockouts |

## SBT filing vocabulary (used only with a gloss)

- **P1–P6**: the framework's six ways a description can fail to close. This paper files P4
  ("the future depends on more than the present readout", GT2) and P5 ("packaging the present
  readout is not a closed projection", GT1). P3 (route mismatch) and P6 (drive) are never claimed.
- **Grades**: theorem (audited class) · certificate (shell-local) · run-only readout ·
  recognition · control. Exactly one per claim.
- **Nonclaim**: an explicit statement of what a claim does not assert; printed in full in §11.
- **Anchors** (F-I, F-II, F-III, F-IV, [A], [B], [C]): SBT corpus references, listed per row in
  `paper/claims_ledger.json`.

## Wording rules

- "No static order parameter for glass" is used only as the declared-class shadow of GT3, with
  class, catalog, and suppressed content named in the same sentence. An order-parameter candidate
  is a readout-definable function that SEPARATES the exhibited pair; GT3 is never identified with
  "no closed coarsening of the energy exists" (a constant is trivially closed).
- Never describe the certificates as approximation-free or error-free as a blanket statement;
  GT1's CD grid is float64_deterministic and must be named as such wherever exactness is discussed.
- CD > 0 is never called novelty, irreversibility, or an arrow of time.
- GT3's separator ($n_1$ under the identity continuation) is a present structural coordinate, not
  temporal memory; do not write that a separating readout must carry memory. GT3 is never extended
  to the GT7 readouts.
- GT4 fixtures are schematic regime packages; do not describe them as implementing clock
  internalization or literal catalog completion.
- T-AOT-02 is an arrow-of-time (entropy-production) audit, not a memory or lumpability theorem.
- Every quantifier ranges over a declared finite class; no continuum or all-glasses statements.
- Each `\claimref{ROW}{sha256}` pins prose to a ledger row and artifact hash; never edit a hash by hand.
