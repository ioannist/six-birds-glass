import GlassWitness.ScopeBoundary
import HolonomyMemory.Sufficiency

namespace GlassWitness

open HolonomyMemory

/--
Two-interface structural instance shaped like the Python Kovacs witness package:
`mid` has two declared histories (`0 = mu_K`, `1 = pi_eq`) and `probe` has the
corresponding index-preserving images under the one declared `probe_hold`
continuation. The observation function is deliberately structural: it returns
the history index, not the real rational energy/signature values from Python.
The scope-boundary theorem shows those real split-pair values cannot be encoded
coherently in `RouteTransportCore` with its global `pullEvent`/`observe_push`
axiom.
-/
inductive GlassInterface where
  | mid
  | probe
deriving DecidableEq

def GlassHistory : GlassInterface → Type
  | .mid => Fin 2
  | .probe => Fin 2

def GlassContinuation : GlassInterface → GlassInterface → Type
  | .mid, .mid => Unit
  | .mid, .probe => Unit
  | .probe, .probe => Unit
  | .probe, .mid => Empty

def GlassEvent : GlassInterface → Type := fun _ => Unit

def GlassObservation := Fin 2

def GlassIdCont : {i : GlassInterface} → GlassContinuation i i
  | .mid => ()
  | .probe => ()

def GlassCompose :
    {i j k : GlassInterface} →
      GlassContinuation i j →
      GlassContinuation j k →
      GlassContinuation i k
  | .mid, .mid, .mid, _, _ => ()
  | .mid, .mid, .probe, _, _ => ()
  | .mid, .probe, .mid, _, δ => Empty.elim δ
  | .mid, .probe, .probe, _, _ => ()
  | .probe, .mid, .mid, γ, _ => Empty.elim γ
  | .probe, .mid, .probe, γ, _ => Empty.elim γ
  | .probe, .probe, .mid, _, δ => Empty.elim δ
  | .probe, .probe, .probe, _, _ => ()

def GlassPush :
    {i j : GlassInterface} →
      GlassHistory i →
      GlassContinuation i j →
      GlassHistory j
  | .mid, .mid, h, _ => h
  | .mid, .probe, h, _ => h
  | .probe, .mid, _, γ => Empty.elim γ
  | .probe, .probe, h, _ => h

def GlassObserve : {i : GlassInterface} → GlassHistory i → GlassEvent i → GlassObservation
  | .mid, h, _ => h
  | .probe, h, _ => h

def GlassPullEvent :
    {i j : GlassInterface} →
      GlassContinuation i j →
      GlassEvent j →
      GlassEvent i :=
  fun _ _ => ()

def glassInstance : RouteTransportCore where
  Interface := GlassInterface
  History := GlassHistory
  Continuation := GlassContinuation
  Event := GlassEvent
  Observation := GlassObservation
  idCont := GlassIdCont
  compose := GlassCompose
  push := GlassPush
  observe := GlassObserve
  pullEvent := GlassPullEvent
  push_id := by
    intro i h
    cases i <;> rfl
  observe_push := by
    intro i j h γ e
    cases i <;> cases j <;> cases γ <;> rfl
  push_compose := by
    intro i j k h γ δ
    cases i <;> cases j <;> cases k <;> cases γ <;> cases δ <;> rfl

theorem glassPredictiveQuotient_futureSufficient :
    FutureSufficient glassInstance
      (fun h : glassInstance.History GlassInterface.mid =>
        (Quotient.mk (PredictiveSetoid glassInstance GlassInterface.mid) h :
          PredictiveQuotient glassInstance GlassInterface.mid)) := by
  exact predictiveQuotient_futureSufficient glassInstance GlassInterface.mid

end GlassWitness
