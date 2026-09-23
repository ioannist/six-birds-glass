import HolonomyMemory.Witnesses

namespace HolonomyMemory

/--
The `RouteTransportCore` axioms make current equivalence imply future-predictive
equivalence for every instance: every future event can be pulled back to a
current event. Consequently `PredictiveWitness`, `StrictRefinement`, and the
loop-asymmetry shape are outside this core's honest scope for the glass Python
certificates, which use a finite declared future catalog instead of `pullEvent`.

This is structurally an instance of a known pattern rather than an isolated
fact: it has the same proof shape as Markov chain strong lumpability (Kemeny &
Snell 1960, *Finite Markov Chains*; Buchholz 1994, *J. Appl. Probab.* 31(1)
59-75) -- a local, one-step coherence condition forcing local equivalence to
hold at every future time -- and `CurrentEventEquiv`'s collapse is exactly
"biextensional collapse" in the Chu-space sense (Barr 1979, *-Autonomous
Categories, LNM 752; Pratt 1999, Annals of Pure and Applied Logic 96(1-3)
319-333), where `pullEvent` plays the role of a Chu transform's defining
naturality condition. Contrast computational mechanics' causal-state /
prescient-statistic framework (Shalizi & Crutchfield 2001, J. Stat. Phys. 104
817-879, arXiv:cond-mat/9907176), where current agreement generally does NOT
imply full future agreement except in special cases -- underscoring that the
collapse here is forced specifically by this core's naturality axiom, not a
generic feature of prediction.
-/
theorem current_implies_future_GENERIC
    (T : RouteTransportCore) {i : T.Interface}
    (h h' : T.History i)
    (hCur : CurrentEventEquiv T h h') :
    FuturePredictiveEquiv T h h' := by
  intro j γ e
  have step1 : T.observe (T.push h γ) e = T.observe h (T.pullEvent γ e) := T.observe_push h γ e
  have step2 : T.observe (T.push h' γ) e = T.observe h' (T.pullEvent γ e) := T.observe_push h' γ e
  have step3 : T.observe h (T.pullEvent γ e) = T.observe h' (T.pullEvent γ e) := hCur (T.pullEvent γ e)
  rw [step1, step2, step3]

theorem predictiveWitness_impossible_GENERIC
    (T : RouteTransportCore) (i : T.Interface) :
    ¬ Nonempty (PredictiveWitness T i) := by
  intro hWitness
  rcases hWitness with ⟨w⟩
  exact w.notSameFuture (current_implies_future_GENERIC T w.h w.h' w.sameCurrent)

theorem strictRefinement_impossible_GENERIC
    (T : RouteTransportCore) (i : T.Interface) :
    ¬ StrictRefinement T i := by
  intro hStrict
  exact predictiveWitness_impossible_GENERIC T i
    ((strictRefinement_iff_nonempty_predictiveWitness T i).mp hStrict)

end HolonomyMemory
