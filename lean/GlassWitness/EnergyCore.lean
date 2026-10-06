import Init.Data.Rat
import GlassWitness.Instance
import DeclaredMemory.Witnesses
import DeclaredMemory.Sufficiency

namespace GlassWitness.Energy

/-- Each declared continuation has its own horizon. Its image retains that
horizon, so a future event reads an actual single continuation, not a bundled
observable silently introduced at the current interface. -/
def History (T : Nat) : GlassInterface → Type
  | .mid => Fin 2
  | .probe => Fin 2 × Fin T

def Continuation (T : Nat) : GlassInterface → GlassInterface → Type
  | .mid, .mid => Unit
  | .mid, .probe => Fin T
  | .probe, .probe => Unit
  | .probe, .mid => Empty

def Event (E : Nat) : GlassInterface → Type
  | .mid => Fin E
  | .probe => Unit

def idCont {T : Nat} : {i : GlassInterface} → Continuation T i i
  | .mid => ()
  | .probe => ()

def compose {T : Nat} : {i j k : GlassInterface} →
    Continuation T i j → Continuation T j k → Continuation T i k
  | .mid, .mid, .mid, _, _ => ()
  | .mid, .mid, .probe, _, δ => δ
  | .mid, .probe, .mid, _, δ => Empty.elim δ
  | .mid, .probe, .probe, γ, _ => γ
  | .probe, .mid, .mid, γ, _ => Empty.elim γ
  | .probe, .mid, .probe, γ, _ => Empty.elim γ
  | .probe, .probe, .mid, _, δ => Empty.elim δ
  | .probe, .probe, .probe, _, _ => ()

def push {T : Nat} : {i j : GlassInterface} →
    History T i → Continuation T i j → History T j
  | .mid, .mid, h, _ => h
  | .mid, .probe, h, τ => (h, τ)
  | .probe, .mid, _, γ => Empty.elim γ
  | .probe, .probe, h, _ => h

def observe {E T : Nat} (current : Fin E → Rat) (future : Fin T → Fin 2 → Rat) :
    {i : GlassInterface} → History T i → Event E i → Rat
  | .mid, _, e => current e
  | .probe, h, _ => future h.2 h.1

/-- Exact exported finite observations. Kernel evolution remains a separately
replayed Python certificate; this core does not axiomatize its correctness. -/
def core {E T : Nat} (current : Fin E → Rat) (future : Fin T → Fin 2 → Rat) :
    DeclaredMemory.RouteTransportCore where
  Interface := GlassInterface
  History := History T
  Continuation := Continuation T
  Event := Event E
  Observation := Rat
  idCont := idCont
  compose := compose
  push := push
  observe := observe current future
  push_id := by
    intro i h
    cases i <;> rfl
  push_compose := by
    intro i j k h γ δ
    cases i <;> cases j <;> cases k <;> cases γ <;> cases δ <;> rfl

def witness {E T : Nat} (current : Fin E → Rat) (future : Fin T → Fin 2 → Rat)
    (τ : Fin T) (hNe : future τ 0 ≠ future τ 1) :
    DeclaredMemory.PredictiveWitness (core current future) GlassInterface.mid where
  h := (0 : Fin 2)
  h' := (1 : Fin 2)
  sameCurrent := by intro e; rfl
  notSameFuture := by
    intro hEq
    exact hNe (hEq (j := GlassInterface.probe) τ ())

theorem strict_refinement {E T : Nat}
    (current : Fin E → Rat) (future : Fin T → Fin 2 → Rat)
    (τ : Fin T) (hNe : future τ 0 ≠ future τ 1) :
    DeclaredMemory.StrictRefinement (core current future) GlassInterface.mid :=
  (witness current future τ hNe).induces_strictRefinement (core current future)

/-- Nonfactorization through the complete current vector, rather than its mean. -/
theorem nonfactorization {E T : Nat}
    (current : Fin E → Rat) (future : Fin T → Fin 2 → Rat)
    (τ : Fin T) (hNe : future τ 0 ≠ future τ 1) :
    ¬ ∃ f : (Fin E → Rat) → Rat, ∀ h : Fin 2, f current = future τ h := by
  rintro ⟨f, hf⟩
  exact hNe ((hf 0).symm.trans (hf 1))

theorem current_law_not_futureSufficient {E T : Nat}
    (current : Fin E → Rat) (future : Fin T → Fin 2 → Rat)
    (τ : Fin T) (hNe : future τ 0 ≠ future τ 1) :
    ¬ DeclaredMemory.FutureSufficient (core current future)
      (i := GlassInterface.mid) (fun _ : Fin 2 => current) := by
  intro hSuf
  exact (witness current future τ hNe).notSameFuture
    (DeclaredMemory.futureSufficient_stateEq_implies_futurePredictiveEquiv
      (core current future) (i := GlassInterface.mid) hSuf rfl)

/-- Every descriptor computed from the current energy law shares the split.
This includes nonlinear summaries and arbitrarily many energy-only scalars. -/
theorem energy_descriptor_not_futureSufficient {E T : Nat} {State : Type}
    (current : Fin E → Rat) (future : Fin T → Fin 2 → Rat)
    (τ : Fin T) (hNe : future τ 0 ≠ future τ 1)
    (descriptor : (Fin E → Rat) → State) :
    ¬ DeclaredMemory.FutureSufficient (core current future)
      (i := GlassInterface.mid) (fun _ : Fin 2 => descriptor current) := by
  intro hSuf
  exact (witness current future τ hNe).notSameFuture
    (DeclaredMemory.futureSufficient_stateEq_implies_futurePredictiveEquiv
      (core current future) (i := GlassInterface.mid) hSuf rfl)

/-- A constant future table cannot obtain strictness from this constructor. -/
theorem constant_future_not_strict {E T : Nat}
    (current : Fin E → Rat) (value : Fin T → Rat) :
    ¬ DeclaredMemory.StrictRefinement
      (core current (fun τ _ => value τ)) GlassInterface.mid := by
  intro hStrict
  rcases DeclaredMemory.strictRefinement_implies_predictiveWitness
      (core current (fun τ _ => value τ)) hStrict with ⟨w⟩
  apply w.notSameFuture
  intro j γ e
  cases j <;> rfl

end GlassWitness.Energy
