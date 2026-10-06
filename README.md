# Glass Is an Unclosed Layer

Companion repository for the paper:

> **Glass Is an Unclosed Layer: Kovacs Memory as Predictive Quotient Residue**
> Ioannis Tsiokos. Preprint v2, 3 October 2026.
> DOI (v2): [10.5281/zenodo.23118261](https://doi.org/10.5281/zenodo.23118261);
> v1 (23 September 2026): [10.5281/zenodo.22911309](https://doi.org/10.5281/zenodo.22911309)

The repository contains the LaTeX manuscript and its compiled PDF, an exact-finite computational
laboratory with the certificates, witnesses, and tables the paper reports, and a Lean 4 core.

## Layout

```
paper/        LaTeX sources, compiled main.pdf, claims ledger, evidence manifest, figures,
              tables, and Zenodo submission records (released PDFs under submission/artifacts/)
src/          the sixbirds_glass Python package (models, pipeline, lenses, protocols, triage)
experiments/  builders and audits that produce the artifacts
artifacts/    generated certificates, witnesses, and tables
math/         mathematical audit records, certificates, and constructions
lean/         Lean 4 libraries: HolonomyMemory, DeclaredMemory, GlassWitness
bridges/      empirical bridge records
configs/      run configurations
registry/     predictions, readouts, and observations registries
design/schemas/  JSON schemas validated at runtime
tests/        pytest suite
```

## Build and test

Python 3.10 or later:

```bash
pip install -e ".[dev]"
pytest
```

Lean (toolchain pinned in `lean/lean-toolchain`):

```bash
cd lean && lake build
```

Paper (requires `latexmk` and a TeX distribution):

```bash
cd paper && latexmk -pdf main.tex
```

Build output is written under `paper/build/`, which is not tracked.

## Notes

Some tests and provenance strings refer to internal planning and design documents that are not
part of this repository.

The manuscript is distributed under CC-BY 4.0, as stated on its first page.
