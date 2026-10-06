import HolonomyMemory.Loops

namespace HolonomyMemory

def CurrentLoopTrivial
    (T : RouteTransportCore) (i : T.Interface) (ℓ : Loop T i) : Prop :=
  ∀ q : CurrentQuotient T i, currentLoopAction T ℓ q = q

def PredictiveLoopNontrivial
    (T : RouteTransportCore) (i : T.Interface) (ℓ : Loop T i) : Prop :=
  ∃ q : PredictiveQuotient T i, predictiveLoopAction T ℓ q ≠ q

def LoopAsymmetry
    (T : RouteTransportCore) (i : T.Interface) (ℓ : Loop T i) : Prop :=
  CurrentLoopTrivial T i ℓ ∧ PredictiveLoopNontrivial T i ℓ

theorem predictiveToCurrent_eq_of_currentLoopTrivial
    (T : RouteTransportCore) {i : T.Interface}
    (ℓ : Loop T i)
    (hTriv : CurrentLoopTrivial T i ℓ)
    (q : PredictiveQuotient T i) :
    predictiveToCurrent T (predictiveLoopAction T ℓ q) =
      predictiveToCurrent T q := by
  calc
    predictiveToCurrent T (predictiveLoopAction T ℓ q) =
      currentLoopAction T ℓ (predictiveToCurrent T q) := by
        symm
        exact predictiveToCurrent_commutes_with_loopAction T ℓ q
    _ = predictiveToCurrent T q := by
      exact hTriv (predictiveToCurrent T q)

theorem loopAsymmetry_exhibits_movedPredictive_fixedCurrent
    (T : RouteTransportCore) {i : T.Interface}
    (ℓ : Loop T i)
    (hAsym : LoopAsymmetry T i ℓ) :
    ∃ q : PredictiveQuotient T i,
      predictiveLoopAction T ℓ q ≠ q ∧
      predictiveToCurrent T (predictiveLoopAction T ℓ q) =
        predictiveToCurrent T q := by
  rcases hAsym with ⟨hTriv, hNontriv⟩
  rcases hNontriv with ⟨q, hMoved⟩
  refine ⟨q, hMoved, ?_⟩
  exact predictiveToCurrent_eq_of_currentLoopTrivial T ℓ hTriv q

theorem loopAsymmetry_exhibits_movedPredictive_currentFixed
    (T : RouteTransportCore) {i : T.Interface}
    (ℓ : Loop T i)
    (hAsym : LoopAsymmetry T i ℓ) :
    ∃ q : PredictiveQuotient T i,
      predictiveLoopAction T ℓ q ≠ q ∧
      currentLoopAction T ℓ (predictiveToCurrent T q) =
        predictiveToCurrent T q := by
  rcases hAsym with ⟨hTriv, hNontriv⟩
  rcases hNontriv with ⟨q, hMoved⟩
  refine ⟨q, hMoved, ?_⟩
  exact hTriv (predictiveToCurrent T q)

end HolonomyMemory
