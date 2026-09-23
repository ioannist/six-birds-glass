# GB1: Temperature-Protocol Trap Boundary Term

## Setting

Let `X` be finite and let `Phi = {0, ..., m-1}` be a finite clock/phase set.
Phase `phi` carries a declared temperature `T_phi` and a phase-local Gibbs law

```text
pi_phi(x) = exp(-E(x) / T_phi) / Z_phi.
```

The random-scan lift on `Z = X x Phi` is

```text
P((x,phi),(x',phi'))
 = alpha * 1{x'=x} * S(phi,phi')
   + (1-alpha) * 1{phi'=phi} * K_phi(x,x').
```

The clock kernel `S` has stationary law `s`, and each `K_phi` is reversible
with respect to its own `pi_phi`. The phase Gibbs laws need not coincide.

## Where The Published Zero-EPR Argument Breaks

For the natural candidate measure

```text
hat_mu(x,phi) = pi_phi(x) * s(phi),
```

state edges at fixed `phi` cancel because `K_phi` is reversible with respect to
`pi_phi`. Phase edges at fixed `x` do not cancel unless all `pi_phi` agree. A
phase switch from `phi` to `phi'` contributes the defect
`log(pi_phi(x) / pi_phi'(x))`. Thus the published common-pi protocol-trap
theorem does not apply to temperature schedules with genuinely different Gibbs
laws.

The mixed-square affinity around the elementary cycle is

```text
(E(x') - E(x)) * (1/T_phi - 1/T_phi'),
```

which is nonzero in the non-null regime `Delta E * Delta beta != 0`.

## Proven Identity: Pseudo-EPR At The Candidate Measure

Let the directed edge-flux EPR functional be

```text
EPR(P,mu) = sum_{i,j} mu(i) P(i,j)
              log( mu(i) P(i,j) / (mu(j) P(j,i)) ).
```

Then

```text
EPR(P,hat_mu)
 = alpha * EPR(S,s)
   + alpha * sum_{phi != phi'} s(phi) S(phi,phi') KL(pi_phi || pi_phi').
```

### Proof

Split the directed edge sum into state-update edges and clock-update edges.

For a state edge at fixed phase `phi`,

```text
hat_mu(x,phi) (1-alpha) K_phi(x,x')
  = s(phi) pi_phi(x) (1-alpha) K_phi(x,x').
```

The reverse flux is

```text
s(phi) pi_phi(x') (1-alpha) K_phi(x',x).
```

These are equal by reversibility of `K_phi` with respect to `pi_phi`, so every
state-edge log ratio is zero.

For a clock edge at fixed state `x`,

```text
hat_mu(x,phi) alpha S(phi,phi')
  = alpha pi_phi(x) s(phi) S(phi,phi').
```

The reverse flux is

```text
alpha pi_phi'(x) s(phi') S(phi',phi).
```

The log ratio splits as

```text
log(s(phi)S(phi,phi') / (s(phi')S(phi',phi)))
  + log(pi_phi(x) / pi_phi'(x)).
```

Summing the first term over `x` gives the clock EPR contribution because
`sum_x pi_phi(x) = 1`. Summing the second term over `x` gives
`KL(pi_phi || pi_phi')`. Multiplying by the edge weight
`alpha s(phi)S(phi,phi')` and summing over directed phase edges proves the
identity.

If all `pi_phi` coincide, the KL boundary term is zero. If the clock is also
reversible, `EPR(S,s)=0`, recovering the published zero-EPR conclusion.

## Target Inequality And Path-Space Attempt

The desired theorem shape is

```text
Sigma_T(rho) <= T * [ alpha * EPR(S,s) + B ],
```

with

```text
B = alpha * sum_{phi != phi'} s(phi)S(phi,phi') KL(pi_phi || pi_phi').
```

The path-space strategy conditions on the realized clock trajectory
`phi_0, ..., phi_T`. Given that clock path, the state process is
time-inhomogeneous, but each update step is reversible with respect to the
step's phase-local Gibbs law. For one fixed clock path, the usual reversible
chain telescoping algebra becomes a telescoping sum with moving reference laws:
switches of the phase reference leave boundary increments of the form

```text
log(pi_{phi_t}(x_t) / pi_{phi_{t+1}}(x_t)).
```

This gives the correct local boundary term and explains why the pseudo-EPR
identity above is the right candidate bound.

## Open Obligation

I did not close the fully general inequality from this path-space decomposition.
The open step is converting the clock-path expectation of the moving-reference
telescoping boundary into the unconditional per-step KL envelope
`sum s(phi)S(phi,phi') KL(pi_phi || pi_phi')` for arbitrary evolving state laws,
without an additional domination or stationarity assumption. The pseudo-EPR
identity is complete and unconditional; the general transient inequality remains
an explicit open obligation.

## Three-State Demonstration

The implemented demonstration uses `X={0,1,2}`, energies `E=(0,1,2)`, two
temperatures, full heat-bath resampling kernels reversible to each phase Gibbs
law, a reversible two-state clock, and `alpha=1/3`.

In the common-temperature recovery case, all `pi_phi` coincide. The boundary
term is numerically zero and the true lifted-chain stationary EPR is zero to
machine precision.

In the hot/cold case, the true stationary law is computed by power iteration.
The finite path KL `Sigma_T(mu*)` is enumerated exactly over all lifted paths for
`T=1,2,3` and compared against `T` times the pseudo-EPR boundary. In this
declared three-state example the bound holds for all three horizons. The
mixed-square cycle affinity computed from energy matches the direct sum of
kernel log-ratios, confirming the `Delta E * Delta beta` diagnosis.
