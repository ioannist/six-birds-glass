"""Build the current Lean libraries and query axioms for every local theorem."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LEAN_ROOT = REPO_ROOT / "lean"
OUTPUT_PATH = REPO_ROOT / "math" / "lean_axiom_audit.json"
ALLOWED_AXIOMS = {"propext", "Classical.choice", "Quot.sound"}


def build_audit() -> dict:
    build = subprocess.run(
        ["lake", "build"], cwd=LEAN_ROOT, capture_output=True, text=True, check=True
    )
    declarations = []
    sources = {}
    for path in sorted(LEAN_ROOT.rglob("*.lean")):
        if ".lake" in path.parts:
            continue
        source = path.read_text()
        sources[str(path.relative_to(REPO_ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        namespaces = re.findall(r"^namespace ([^\s]+)", source, re.M)
        if not namespaces:
            continue
        if len(namespaces) != 1:
            raise ValueError(f"audit requires an explicit namespace mapping for {path}")
        for name in re.findall(r"^(?:@\[[^\n]*\]\s*)?theorem\s+([^\s]+)", source, re.M):
            declarations.append(f"{namespaces[0]}.{name}")
    commands = (
        "import GlassWitness\nimport DeclaredMemory\n"
        + "\n".join(f"#print axioms {name}" for name in declarations)
        + "\n"
    )
    with tempfile.NamedTemporaryFile(mode="w", suffix=".lean", dir="/tmp") as handle:
        handle.write(commands)
        handle.flush()
        result = subprocess.run(
            ["lake", "env", "lean", handle.name],
            cwd=LEAN_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    rows = []
    for name in declarations:
        match = re.search(
            rf"'{re.escape(name)}' (does not depend on any axioms|depends on axioms: \[([^\]]*)\])",
            result.stdout,
        )
        if match is None:
            raise ValueError(f"missing live axiom report for {name}")
        axioms = [] if match.group(2) is None else [a.strip() for a in match.group(2).split(",")]
        if set(axioms) - ALLOWED_AXIOMS:
            raise ValueError(f"unapproved axiom dependencies for {name}: {axioms}")
        rows.append({"declaration": name, "axioms": axioms, "raw": match.group(0)})
    return {
        "toolchain": (LEAN_ROOT / "lean-toolchain").read_text().strip(),
        "build_stdout": build.stdout.strip(),
        "source_sha256": sources,
        "allowed_baseline_axioms": sorted(ALLOWED_AXIOMS),
        "theorem_count": len(rows),
        "theorems": rows,
        "scope": "current exported Lean declarations; numeric Python bridge audited separately",
    }


if __name__ == "__main__":
    audit = build_audit()
    OUTPUT_PATH.write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    print(f"live Lean axiom audit: {audit['theorem_count']} theorems")
