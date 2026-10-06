import Init.Data.Rat
import GlassWitness.Instance
import DeclaredMemory.Witnesses
import DeclaredMemory.Sufficiency

namespace GlassWitness.Numeric

/-- The current interface reads one declared mean; the probe reads its future value. -/
def observe (present : Rat) (future : Fin 2 → Rat) :
    {i : GlassInterface} → GlassHistory i → GlassEvent i → Rat
  | .mid, _, _ => present
  | .probe, h, _ => future h

/-- A finite lookup model using the corrected, explicitly declared event interface.
The exported tables certify the two-history signature statement. They do not
mechanize the full East transition kernel or assert closure for other futures. -/
def core (present : Rat) (future : Fin 2 → Rat) : DeclaredMemory.RouteTransportCore where
  Interface := GlassInterface
  History := GlassHistory
  Continuation := GlassContinuation
  Event := GlassEvent
  Observation := Rat
  idCont := GlassIdCont
  compose := GlassCompose
  push := GlassPush
  observe := observe present future
  push_id := by
    intro i h
    cases i <;> rfl
  push_compose := by
    intro i j k h γ δ
    cases i <;> cases j <;> cases k <;> cases γ <;> cases δ <;> rfl

def witness (present : Rat) (future : Fin 2 → Rat) (hNe : future 0 ≠ future 1) :
    DeclaredMemory.PredictiveWitness (core present future) GlassInterface.mid where
  h := (0 : Fin 2)
  h' := (1 : Fin 2)
  sameCurrent := by intro e; rfl
  notSameFuture := by
    intro hEq
    exact hNe (hEq (j := GlassInterface.probe) () ())

theorem strict_refinement
    (present : Rat) (future : Fin 2 → Rat) (hNe : future 0 ≠ future 1) :
    DeclaredMemory.StrictRefinement (core present future) GlassInterface.mid :=
  (witness present future hNe).induces_strictRefinement (core present future)

/-- F-III T12's witness-to-nonfactorization direction for the actual lookup maps. -/
theorem nonfactorization
    (present : Rat) (future : Fin 2 → Rat) (hNe : future 0 ≠ future 1) :
    ¬ ∃ f : Rat → Rat, ∀ h : Fin 2, f present = future h := by
  rintro ⟨f, hf⟩
  exact hNe ((hf 0).symm.trans (hf 1))

/-- This probe specifically fails current compatibility; no global collapse axiom is used. -/
theorem probe_not_currentCompatible
    (present : Rat) (future : Fin 2 → Rat) (hNe : future 0 ≠ future 1) :
    ¬ DeclaredMemory.CurrentCompatible (core present future)
      (i := GlassInterface.mid) (j := GlassInterface.probe) () := by
  intro hCompat
  exact hNe (hCompat (witness present future hNe).sameCurrent ())

theorem current_panel_not_futureSufficient
    (present : Rat) (future : Fin 2 → Rat) (hNe : future 0 ≠ future 1) :
    ¬ DeclaredMemory.FutureSufficient (core present future)
      (i := GlassInterface.mid)
      (fun _ : Fin 2 => present) := by
  intro hSuf
  exact (witness present future hNe).notSameFuture
    (DeclaredMemory.futureSufficient_stateEq_implies_futurePredictiveEquiv
      (core present future) (i := GlassInterface.mid) hSuf
      (h := (0 : Fin 2)) (h' := (1 : Fin 2)) rfl)

theorem index_state_futureSufficient
    (present : Rat) (future : Fin 2 → Rat) :
    DeclaredMemory.FutureSufficient (core present future)
      (fun h : (core present future).History GlassInterface.mid => h) := by
  intro obs
  exact ⟨fun h => DeclaredMemory.evalFutureObservable (core present future) obs h, fun _ => rfl⟩

theorem index_state_factors_onReachable
    (present : Rat) (future : Fin 2 → Rat) :
    ∃ f : DeclaredMemory.ReachableState (core present future)
        (fun h : (core present future).History GlassInterface.mid => h) →
        DeclaredMemory.PredictiveQuotient (core present future) GlassInterface.mid,
      ∀ h : (core present future).History GlassInterface.mid,
        f ⟨h, ⟨h, rfl⟩⟩ = Quotient.mk
          (DeclaredMemory.PredictiveSetoid (core present future) GlassInterface.mid) h := by
  exact DeclaredMemory.futureSufficient_factorsThroughPredictiveQuotient_onReachable
    (core present future) (index_state_futureSufficient present future)

/-- False-target control: the same constructor has no strictness when every
declared future value is constant. Strictness is supplied by the computed split. -/
theorem constant_future_not_strict (present futureValue : Rat) :
    ¬ DeclaredMemory.StrictRefinement (core present (fun _ => futureValue)) GlassInterface.mid := by
  intro hStrict
  rcases DeclaredMemory.strictRefinement_implies_predictiveWitness
      (core present (fun _ => futureValue)) hStrict with ⟨w⟩
  apply w.notSameFuture
  intro j γ e
  cases j <;> rfl

end GlassWitness.Numeric
