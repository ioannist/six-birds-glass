"""Build the frozen GT7 readout registry."""

from __future__ import annotations

import hashlib
import json
from itertools import product
from pathlib import Path
from typing import Any

from sixbirds_glass.io.config import canonical_json_bytes
from sixbirds_glass.io.rational import rational_to_str
from sixbirds_glass.models.grid import DEFAULT_EPSILON_GRID

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "registry" / "readouts.json"
GT3_ARTIFACT_PATH = ROOT / "artifacts" / "gt3_foreclosure" / "lens_class_sweep.json"
GT3_ARTIFACT_RELATIVE = "artifacts/gt3_foreclosure/lens_class_sweep.json"


def build_registry() -> dict[str, Any]:
    gt3_hash = hashlib.sha256(GT3_ARTIFACT_PATH.read_bytes()).hexdigest()
    gt3_cross_ref = {
        "artifact_path": GT3_ARTIFACT_RELATIVE,
        "artifact_hash": gt3_hash,
    }
    registry: dict[str, Any] = {
        "registry_version": 1,
        "freeze_note": (
            "The design text describes F1 as a git commit, but this repository has only the "
            "manager-created design-pack commit and implementation commits are manager-gated. "
            "This registry is therefore frozen by its own canonical JSON content_hash, computed "
            "with the content_hash field removed."
        ),
        "readouts": [
            {
                "readout_id": "t_K",
                "definition": (
                    "first step t on the ε_mid leg of `P_kovacs(t_w)` with "
                    "(⟨E⟩(t) - E_eq(ε_mid)) changing sign"
                ),
                "produced_by": "exact trace (N ≤ 10) or MC trace (N ≤ 16, frozen seeds)",
                "run_only": True,
                "gt3_cross_ref": gt3_cross_ref,
            },
            {
                "readout_id": "hump_height",
                "definition": (
                    "max_t≥t_K (⟨E⟩(t) - E_eq(ε_mid)); report as exact rational "
                    "(certificate runs) or mean ± MC band (sweeps)"
                ),
                "produced_by": "same",
                "run_only": True,
                "gt3_cross_ref": gt3_cross_ref,
            },
            {
                "readout_id": "t_peak",
                "definition": "argmax of the above",
                "produced_by": "same",
                "run_only": True,
                "gt3_cross_ref": gt3_cross_ref,
            },
            {
                "readout_id": "hump_surface",
                "definition": (
                    "the map (ε_hi, ε_lo, ε_mid, t_w) ↦ "
                    "(t_K, t_peak, hump_height) over the declared grid product"
                ),
                "produced_by": "Leg-2 sweep",
                "run_only": True,
                "gt3_cross_ref": gt3_cross_ref,
            },
            {
                "readout_id": "memdim_profile",
                "definition": (
                    "MaxFiber and buyback-curve knots (see `07_gt5_dimension.md`) as "
                    "functions of protocol-catalog index"
                ),
                "produced_by": "pipeline",
                "run_only": True,
                "gt3_cross_ref": gt3_cross_ref,
            },
            {
                "readout_id": "deficit_decay",
                "definition": (
                    "the sequence CD_τ(Π_std) and δ_{τ,f} over the declared τ ladder "
                    'during aging; the "exponent" is a declared secant slope between '
                    "two frozen ladder points, NOT a fit"
                ),
                "produced_by": "GT1 tables",
                "run_only": True,
                "gt3_cross_ref": gt3_cross_ref,
            },
        ],
        "grid_products": _grid_products(),
    }
    registry["content_hash"] = hashlib.sha256(canonical_json_bytes(registry)).hexdigest()
    return registry


def write_registry(output_path: Path = REGISTRY_PATH) -> dict[str, Any]:
    registry = build_registry()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(registry, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return registry


def main(output_path: Path = REGISTRY_PATH) -> None:
    registry = write_registry(output_path)
    print(f"wrote {output_path}")
    print(f"gt3_hash={registry['readouts'][0]['gt3_cross_ref']['artifact_hash']}")
    print(f"content_hash={registry['content_hash']}")


def _grid_products() -> dict[str, Any]:
    epsilon_grid = [rational_to_str(epsilon) for epsilon in DEFAULT_EPSILON_GRID]
    epsilon_hi_values = [DEFAULT_EPSILON_GRID[-1], DEFAULT_EPSILON_GRID[-2]]
    epsilon_lo_values = [DEFAULT_EPSILON_GRID[0], DEFAULT_EPSILON_GRID[1]]
    hump_surface_cells = [
        {
            "epsilon_hi": rational_to_str(epsilon_hi),
            "epsilon_lo": rational_to_str(epsilon_lo),
            "epsilon_mid": rational_to_str(epsilon_mid),
            "t_w": t_w,
        }
        for epsilon_hi, epsilon_lo, epsilon_mid, t_w in product(
            epsilon_hi_values,
            epsilon_lo_values,
            DEFAULT_EPSILON_GRID,
            (20, 60),
        )
    ]
    return {
        "epsilon_grid": epsilon_grid,
        "hump_surface_cells": hump_surface_cells,
        "tau_ladder": [1, 2, 4, 8],
        "protocol_catalog_instances": [
            {
                "instance_id": "kovacs_default",
                "constructor": "p_kovacs",
                "params": {
                    "epsilon_hi": "7/10",
                    "tau_hot": 0,
                    "epsilon_lo": "1/10",
                    "t_w": 40,
                    "epsilon_mid": "2/5",
                    "tau_probe": 60,
                },
            },
            {
                "instance_id": "kovacs_short",
                "constructor": "p_kovacs",
                "params": {
                    "epsilon_hi": "7/10",
                    "tau_hot": 0,
                    "epsilon_lo": "1/10",
                    "t_w": 30,
                    "epsilon_mid": "2/5",
                    "tau_probe": 60,
                },
            },
            {
                "instance_id": "quench_only",
                "constructor": "p_quench",
                "params": {
                    "epsilon_hi": "7/10",
                    "tau_mix": 0,
                    "epsilon_lo": "1/10",
                    "t_w": 60,
                },
            },
        ],
    }


if __name__ == "__main__":
    main()
