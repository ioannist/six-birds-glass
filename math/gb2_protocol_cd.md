# GB2: Protocol-Relative Closure Deficit

## Setup

Let `X` be a finite microstate space and let `Pi: X -> Y` be a finite lens. A
declared protocol catalog is a finite set `P = {rho_1, ..., rho_m}` with
rational weights `lambda(rho) > 0` and `sum_rho lambda(rho) = 1`. Each protocol
rho provides a time-inhomogeneous kernel sequence
`P_1^(rho), P_2^(rho), ...` and a declared law at the evaluation time,
`mu_t^(rho) = mu_0^(rho) P_1^(rho) ... P_t^(rho)`.

For a fixed horizon `tau`, write
`P_{t+1:t+tau}^(rho)` for the declared continuation from time `t` to
`t+tau`. The protocol-ensemble joint law is

```text
Pr(R=rho, X_t=x, Y_{t+tau}=y)
  = lambda(rho) * mu_t^(rho)(x)
    * P_{t+1:t+tau}^(rho)(x, {x' : Pi(x') = y}).
```

Also write `Y_t = Pi(X_t)`. The windowed protocol-relative closure deficit is

```text
CD_tau^prot(Pi) := I(X_t ; Y_{t+tau} | Y_t, R).
```

The marginalized ensemble scalar `I(X_t ; Y_{t+tau} | Y_t)` is a separate
reported value. It can differ because the protocol label can itself carry
information about the future lens value.

## Proposition 3.2': Decomposition

For the ensemble law above,

```text
H(Y_{t+tau} | Y_t, R)
  = H(Y_{t+tau} | X_t, R) + CD_tau^prot(Pi).
```

### Proof

By the definition of conditional mutual information,

```text
I(X_t ; Y_{t+tau} | Y_t, R)
  = H(Y_{t+tau} | Y_t, R)
    - H(Y_{t+tau} | X_t, Y_t, R).
```

Since `Y_t = Pi(X_t)` is a deterministic function of `X_t`, adding `Y_t` to the
conditioning set after conditioning on `X_t` adds no information:

```text
H(Y_{t+tau} | X_t, Y_t, R)
  = H(Y_{t+tau} | X_t, R).
```

Substitution gives the stated identity. This proof uses only the chain rule and
the deterministic relation between `X_t` and `Y_t`; it is valid for any joint
law over `(R, X_t, Y_{t+tau})`. The GB2 content is that, for a declared finite
protocol catalog, every term is an explicit finite sum from rational weights,
finite kernels, and finite distributions.

## Proposition 3.5': Protocol-Cell Lumpability Equivalence

`CD_tau^prot(Pi) = 0` if and only if every positive-weight protocol/fiber cell
is tau-lumpable: for each protocol `rho`, each fiber `y` with
`lambda(rho) * mu_t^(rho)(Pi^{-1}(y)) > 0`, every realized pair
`x, x' in Pi^{-1}(y)`, and every target fiber `y'`,

```text
sum_{x'' in Pi^{-1}(y')} P_{t+1:t+tau}^(rho)(x, x'')
 =
sum_{x'' in Pi^{-1}(y')} P_{t+1:t+tau}^(rho)(x', x'').
```

### Proof

Use the standard expected-KL form of conditional mutual information under the
ensemble law:

```text
I(X_t ; Y_{t+tau} | Y_t, R)
 = E_{(y,rho)} [
     sum_x Pr(x | y, rho)
       KL(
         Pr(Y_{t+tau} | X_t=x, Y_t=y, R=rho)
         || Pr(Y_{t+tau} | Y_t=y, R=rho)
       )
   ].
```

Every KL term is nonnegative. The expectation is therefore zero exactly when
every term with positive weight is zero. A KL term is zero exactly when the two
conditional laws are equal. Here
`Pr(Y_{t+tau} | X_t=x, Y_t=y, R=rho)` is precisely the tau-step
fiber-pushforward from `x` through protocol `rho`'s declared kernel sequence,
and `Pr(Y_{t+tau} | Y_t=y, R=rho)` is the `mu_t^(rho)`-conditional average over
the same source fiber. Equality for every realized `x` in that fiber is exactly
the stated Kemeny-Snell fiber-transition identity, checked separately in each
positive-weight `(rho,t)` cell.

## Consistency With Stationary CD

If the catalog contains one constant-epsilon protocol, starts from the
stationary law `pi_epsilon`, and uses `K_epsilon` at every step, then
`CD_tau^prot(Pi)` reduces exactly to the stationary closure deficit `CD_tau(Pi)`.

With one protocol, conditioning on `R` is vacuous. Since
`mu_0 = pi_epsilon` and `pi_epsilon K_epsilon = pi_epsilon`, we have
`mu_t = pi_epsilon` for every evaluation time. Therefore the ensemble joint law
over `(X_t, Y_{t+tau})` is the same stationary joint law used in the original
definition of `[B]`'s `CD_tau(Pi)`.
