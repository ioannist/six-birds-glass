/- Adapted from six-birds-route-transport 864602a46bbbd8a2ee3c87b15476044216de6a72, lean/HolonomyMemory/Loops.lean.
   Only module paths and namespace HolonomyMemory are renamed to DeclaredMemory.
   The legacy pullback-closed HolonomyMemory library remains separately available. -/
import DeclaredMemory.Transport

namespace DeclaredMemory

abbrev Loop
    (T : RouteTransportCore) (i : T.Interface) :=
  T.Continuation i i

def predictiveLoopAction
    (T : RouteTransportCore) {i : T.Interface}
    (ℓ : Loop T i) :
    PredictiveQuotient T i → PredictiveQuotient T i :=
  predictiveTransport T ℓ

def currentLoopAction
    (T : RouteTransportCore) {i : T.Interface}
    (ℓ : Loop T i) :
    CurrentCompatible T ℓ →
    CurrentQuotient T i → CurrentQuotient T i :=
  currentTransport T ℓ

@[simp] theorem predictiveLoopAction_mk
    (T : RouteTransportCore) {i : T.Interface}
    (ℓ : Loop T i) (h : T.History i) :
    predictiveLoopAction T ℓ (Quotient.mk (PredictiveSetoid T i) h) =
      Quotient.mk (PredictiveSetoid T i) (T.push h ℓ) := by
  rfl

@[simp] theorem currentLoopAction_mk
    (T : RouteTransportCore) {i : T.Interface}
    (ℓ : Loop T i) (hCompat : CurrentCompatible T ℓ) (h : T.History i) :
    currentLoopAction T ℓ hCompat (Quotient.mk (CurrentSetoid T i) h) =
      Quotient.mk (CurrentSetoid T i) (T.push h ℓ) := by
  rfl

theorem predictiveToCurrent_commutes_with_loopAction
    (T : RouteTransportCore)
    {i : T.Interface}
    (ℓ : Loop T i)
    (hCompat : CurrentCompatible T ℓ)
    (q : PredictiveQuotient T i) :
    currentLoopAction T ℓ hCompat (predictiveToCurrent T q) =
      predictiveToCurrent T (predictiveLoopAction T ℓ q) := by
  exact predictiveToCurrent_commutes_with_transport T ℓ hCompat q

end DeclaredMemory
