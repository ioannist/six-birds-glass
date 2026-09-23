"""Build the Phase 5 paper evidence manifest."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from sixbirds_glass.io.config import canonical_json_bytes  # noqa: E402

OUTPUT_PATH = REPO_ROOT / "paper" / "evidence_manifest.json"
SCRIPT_PATHS = (
    Path("experiments/score_transfer.py"),
    Path("experiments/check_gt6_filing.py"),
    Path("experiments/check_bridges.py"),
)


def build_manifest() -> dict[str, Any]:
    """Return the deterministic Phase 5 evidence manifest."""

    paths_by_category = _scan_paths_by_category()
    entries = [_entry_for(path) for path in _all_paths(paths_by_category)]
    manifest: dict[str, Any] = {
        "manifest_kind": "paper_evidence_manifest",
        "purpose": ("Single hash root for every evidence file the Phase 5 paper may cite."),
        "freeze_note": (
            "The Phase 5 paper evidence base is frozen by sha256 content hashes rather "
            "than implementation git commits, matching the content-hash discipline used "
            "by the GT7 registries; content_hash is computed over canonical JSON with "
            "the content_hash field absent."
        ),
        "entries": entries,
        "counts": {
            "artifacts": len(paths_by_category["artifacts"]),
            "registry": len(paths_by_category["registry"]),
            "bridges": len(paths_by_category["bridges"]),
            "lean": len(paths_by_category["lean"]),
            "scripts": len(paths_by_category["scripts"]),
            "total": len(entries),
        },
    }
    manifest["content_hash"] = hashlib.sha256(canonical_json_bytes(manifest)).hexdigest()
    return manifest


def write_manifest(output_path: Path = OUTPUT_PATH) -> dict[str, Any]:
    """Write the manifest as sorted, newline-terminated JSON."""

    manifest = build_manifest()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return manifest


def main(output_path: Path = OUTPUT_PATH) -> None:
    manifest = write_manifest(output_path)
    print(f"wrote {output_path}")
    print(f"counts={json.dumps(manifest['counts'], sort_keys=True)}")
    print(f"content_hash={manifest['content_hash']}")


def _scan_paths_by_category() -> dict[str, list[Path]]:
    return {
        "artifacts": _glob("artifacts/**/*.json"),
        "registry": _glob("registry/*.json"),
        "bridges": _glob("bridges/*.json"),
        "lean": _lean_paths(),
        "scripts": [path for path in SCRIPT_PATHS if (REPO_ROOT / path).is_file()],
    }


def _glob(pattern: str) -> list[Path]:
    return sorted(path.relative_to(REPO_ROOT) for path in REPO_ROOT.glob(pattern) if path.is_file())


def _lean_paths() -> list[Path]:
    paths = [
        *_glob("lean/GlassWitness/*.lean"),
        *_glob("lean/HolonomyMemory/**/*.lean"),
        Path("lean/HolonomyMemory.lean"),
        Path("lean/lean-toolchain"),
        Path("lean/lakefile.toml"),
    ]
    return sorted(path for path in set(paths) if (REPO_ROOT / path).is_file())


def _all_paths(paths_by_category: dict[str, list[Path]]) -> list[Path]:
    paths = [path for paths in paths_by_category.values() for path in paths]
    return sorted(paths, key=lambda path: path.as_posix())


def _entry_for(relative_path: Path) -> dict[str, Any]:
    path = REPO_ROOT / relative_path
    data = path.read_bytes()
    return {
        "path": relative_path.as_posix(),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
    }


if __name__ == "__main__":
    main()
