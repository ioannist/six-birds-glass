"""Config-driven rebuild helpers."""

from __future__ import annotations

from typing import Any

from sixbirds_glass.io.config import validate_exact_equilibrium_preparation
from sixbirds_glass.io.rational import str_to_rational
from sixbirds_glass.pipeline.kovacs_hump import HumpResult, detect_kovacs_hump


def rebuild_hump_result_from_config(config: dict[str, Any]) -> HumpResult:
    """Recompute a Kovacs-hump result from a model_config-shaped dict."""

    model = config["model"]
    validate_exact_equilibrium_preparation(config)
    if model["family"] != "east":
        raise ValueError("only East Kovacs configs are supported")
    if model["boundary"] != "wall_up" or config["lens"]["id"] != "L_energy":
        raise ValueError("Kovacs rebuild requires wall-up East dynamics and the energy lens")
    N = int(model["N"])

    word = config["protocol"]["word"]
    if len(word) != 3 or word[0]["steps"] != 0:
        raise ValueError("Kovacs hump config must have a three-leg protocol word")

    epsilon_hi = str_to_rational(word[0]["epsilon"])
    epsilon_lo = str_to_rational(word[1]["epsilon"])
    epsilon_mid = str_to_rational(word[2]["epsilon"])
    t_w = int(word[1]["steps"])
    tau_probe = int(word[2]["steps"])

    return detect_kovacs_hump(
        N,
        epsilon_hi,
        epsilon_lo,
        epsilon_mid,
        t_w,
        tau_probe,
        denominator_bit_cap=int(config["arithmetic"].get("max_denominator_bits", 4096)),
    )
