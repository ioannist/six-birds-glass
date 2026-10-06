/- Adapted from six-birds-route-transport 864602a46bbbd8a2ee3c87b15476044216de6a72, lean/HolonomyMemory/Asymmetry.lean.
   Only module paths and namespace HolonomyMemory are renamed to DeclaredMemory.
   The legacy pullback-closed HolonomyMemory library remains separately available. -/
import DeclaredMemory.Loops

namespace DeclaredMemory

def CurrentLoopTrivial
    (T : RouteTransportCore) (i : T.Interface) (ℓ : Loop T i)
    (hCompat : CurrentCompatible T ℓ) : Prop :=
  ∀ q : CurrentQuotient T i, currentLoopAction T ℓ hCompat q = q

def PredictiveLoopNontrivial
    (T : RouteTransportCore) (i : T.Interface) (ℓ : Loop T i) : Prop :=
  ∃ q : PredictiveQuotient T i, predictiveLoopAction T ℓ q ≠ q

def LoopAsymmetry
    (T : RouteTransportCore) (i : T.Interface) (ℓ : Loop T i)
    (hCompat : CurrentCompatible T ℓ) : Prop :=
  CurrentLoopTrivial T i ℓ hCompat ∧ PredictiveLoopNontrivial T i ℓ

theorem predictiveToCurrent_eq_of_currentLoopTrivial
    (T : RouteTransportCore) {i : T.Interface}
    (ℓ : Loop T i)
    (hCompat : CurrentCompatible T ℓ)
    (hTriv : CurrentLoopTrivial T i ℓ hCompat)
    (q : PredictiveQuotient T i) :
    predictiveToCurrent T (predictiveLoopAction T ℓ q) =
      predictiveToCurrent T q := by
  calc
    predictiveToCurrent T (predictiveLoopAction T ℓ q) =
      currentLoopAction T ℓ hCompat (predictiveToCurrent T q) := by
        symm
        exact predictiveToCurrent_commutes_with_loopAction T ℓ hCompat q
    _ = predictiveToCurrent T q := by
      exact hTriv (predictiveToCurrent T q)

theorem loopAsymmetry_exhibits_movedPredictive_fixedCurrent
    (T : RouteTransportCore) {i : T.Interface}
    (ℓ : Loop T i)
    (hCompat : CurrentCompatible T ℓ)
    (hAsym : LoopAsymmetry T i ℓ hCompat) :
    ∃ q : PredictiveQuotient T i,
      predictiveLoopAction T ℓ q ≠ q ∧
      predictiveToCurrent T (predictiveLoopAction T ℓ q) =
        predictiveToCurrent T q := by
  rcases hAsym with ⟨hTriv, hNontriv⟩
  rcases hNontriv with ⟨q, hMoved⟩
  refine ⟨q, hMoved, ?_⟩
  exact predictiveToCurrent_eq_of_currentLoopTrivial T ℓ hCompat hTriv q

theorem loopAsymmetry_exhibits_movedPredictive_currentFixed
    (T : RouteTransportCore) {i : T.Interface}
    (ℓ : Loop T i)
    (hCompat : CurrentCompatible T ℓ)
    (hAsym : LoopAsymmetry T i ℓ hCompat) :
    ∃ q : PredictiveQuotient T i,
      predictiveLoopAction T ℓ q ≠ q ∧
      currentLoopAction T ℓ hCompat (predictiveToCurrent T q) =
        predictiveToCurrent T q := by
  rcases hAsym with ⟨hTriv, hNontriv⟩
  rcases hNontriv with ⟨q, hMoved⟩
  refine ⟨q, hMoved, ?_⟩
  exact hTriv (predictiveToCurrent T q)

end DeclaredMemory
