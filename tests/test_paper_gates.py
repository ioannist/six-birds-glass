import hashlib
import json
import re
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = REPO_ROOT / "paper"

CLAIMREF_RE = re.compile(r"\\claimref\{([^}]*)\}\{([0-9a-f]{64})\}")
CLAIMREF_LOOSE_RE = re.compile(r"\\claimref\{([^}]*)\}\{([^}]*)\}")

DENYLIST_PHRASES = (
    "full obligation stack satisfied",
    "provably insufficient",
    "git history is the proof",
    # Exactness overclaims (Eddy full-draft review, finding 1): GT1's CD evidence is
    # float64_deterministic per its own artifact, so blanket exactness claims are false.
    "every certified quantity is a ratio of integers",
    "certificate quantity is a ratio of integers",
    "never the basis of a theorem-grade margin",
    # Knockout-panel conflation (finding 2): P4-P6 are capability-loss rows, no numeric threshold.
    "past its threshold in every row",
    # Gate-strength overclaim (finding 3): prose fidelity is human-audited, not machine-checked.
    "every sentence of this paper is a transcription",
    # 2026-09-22 Eddy FIX-FIRST (readability pass): GT3 overreach, blanket exactness, false
    # closure/idempotence equivalence, GT4 fixture mechanisms, T-AOT-02 as a memory theorem.
    "must carry declared memory",
    "no description by present observables",
    "every answer is an exact computation",
    "carry no numerical error",
    "would be idempotent",
    "persistent positivity is aging",
    "once the schedule is honestly written into the state",
    "theorem excluding this",
    # Round 2 (2026-09-22): residual equivalents of the round-1 overclaims.
    "computed without approximation",
    "grid temperature whose",
    "near the crossing the chain equals equilibrium",
)


def _tex_sources() -> list[Path]:
    return [*sorted((PAPER_DIR / "sections").glob("*.tex")), PAPER_DIR / "main.tex"]


def _tex_text() -> str:
    text = "\n".join(path.read_text(encoding="utf-8") for path in _tex_sources())
    # TeX line continuation: a % at end of line swallows the newline and leading whitespace
    # of the next line. Mirror that so multi-line \cite{...%\n...} argument lists parse.
    return re.sub(r"(?<!\\)%\n\s*", "", text)


def _ledger() -> dict:
    return json.loads((PAPER_DIR / "claims_ledger.json").read_text(encoding="utf-8"))


def _claimrefs() -> list[tuple[str, str]]:
    text = _tex_text()
    return [(row_id.replace(r"\_", "_"), sha) for row_id, sha in CLAIMREF_RE.findall(text)]


def test_every_claimref_hash_resolves_against_ledger_and_current_bytes() -> None:
    ledger_by_id = {row["row_id"]: row for row in _ledger()["rows"]}
    claimrefs = _claimrefs()
    assert claimrefs, "expected at least one \\claimref call in the paper sources"
    for row_id, sha in claimrefs:
        assert row_id in ledger_by_id, row_id
        cited_hashes = {citation["sha256"] for citation in ledger_by_id[row_id]["artifacts"]}
        assert sha in cited_hashes, (row_id, sha)
        matching = next(c for c in ledger_by_id[row_id]["artifacts"] if c["sha256"] == sha)
        actual = hashlib.sha256((REPO_ROOT / matching["path"]).read_bytes()).hexdigest()
        assert actual == sha, (row_id, matching["path"])


def test_every_claims_ledger_row_is_cited_at_least_once() -> None:
    cited_ids = {row_id for row_id, _sha in _claimrefs()}
    all_ids = {row["row_id"] for row in _ledger()["rows"]}
    missing = all_ids - cited_ids
    assert not missing, f"claims-ledger rows never cited in the paper sources: {sorted(missing)}"


def test_no_malformed_claimref_calls() -> None:
    text = _tex_text()
    loose_matches = CLAIMREF_LOOSE_RE.findall(text)
    strict_matches = CLAIMREF_RE.findall(text)
    assert len(loose_matches) == len(strict_matches), (
        "found \\claimref{...}{...} call(s) whose row_id or hash argument do not match the "
        "required ROW_ID + 64-hex-char sha256 shape"
    )
    for row_id, _sha in loose_matches:
        assert row_id.strip(), "claimref row_id must not be empty"


def test_denylist_phrases_absent_from_paper_sources() -> None:
    text = _tex_text().lower()
    for phrase in DENYLIST_PHRASES:
        assert phrase not in text, phrase


def test_gt6_knockout_prose_keeps_capability_loss_distinct() -> None:
    text = (PAPER_DIR / "sections" / "sec_07_gt6.tex").read_text(encoding="utf-8")
    if "P4" in text:
        assert "capability-loss" in text, (
            "GT6 prose discussing P4-P6 knockouts must use capability-loss language, "
            "not numeric-threshold language (P4-P6 rows have no numeric threshold)"
        )


def test_gt1_exactness_is_qualified_where_claimed() -> None:
    # GT1's CD artifacts self-declare float64_deterministic evidence; the methods section must
    # carry that qualification whenever it discusses the arithmetic discipline.
    artifact = json.loads(
        (REPO_ROOT / "artifacts" / "gt1_cd_tables" / "east_n8_l_energy.json").read_text()
    )
    assert artifact["evidence_type"] == "float64_deterministic"
    methods = (PAPER_DIR / "sections" / "sec_02_architecture_methods.tex").read_text(
        encoding="utf-8"
    )
    assert "float64\\_deterministic" in methods
    # The grade-definition gloss must also carry the qualification, so future edits cannot
    # reintroduce "theorem-grade = exact computation" (Eddy sign-off review, minor finding).
    assert "declared evidence type" in methods
    assert "exact computation quantified over a declared finite class" not in methods


def test_g3_recognition_open_ceiling_paragraph_present() -> None:
    # The F-II section-16 walk's one genuine gap (item G3) was fixed by declaring the
    # recognition-open ceiling in the discussion; it must stay declared.
    discussion = (PAPER_DIR / "sections" / "sec_11_discussion.tex").read_text(encoding="utf-8")
    assert "recognition-open" in discussion
    assert "recognition hypothesis" in discussion


def test_paper_compiles_clean() -> None:
    result = subprocess.run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "main.tex"],
        cwd=PAPER_DIR,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout[-4000:] + result.stderr[-4000:]
    # paper/latexmkrc sends all build output to paper/build/ (paper-template layout).
    log_text = (PAPER_DIR / "build" / "main.log").read_text(encoding="utf-8", errors="replace")
    assert "undefined" not in log_text.lower(), "undefined citation or reference in main.log"
    pdf_path = PAPER_DIR / "build" / "main.pdf"
    assert pdf_path.is_file()
    assert pdf_path.stat().st_size > 10_000
    subprocess.run(["latexmk", "-c"], cwd=PAPER_DIR, capture_output=True, text=True, timeout=60)


def test_references_bib_has_no_duplicate_keys() -> None:
    text = (PAPER_DIR / "references.bib").read_text(encoding="utf-8")
    keys = re.findall(r"@\w+\{([^,]+),", text)
    assert len(keys) == len(set(keys)), "duplicate bibtex keys in references.bib"
    assert len(keys) >= 25


def test_every_cite_key_used_in_paper_exists_in_bib() -> None:
    text = _tex_text()
    cite_calls = re.findall(r"\\(?:cite|sbtcite)\{([^}]*)\}", text)
    used_keys = {key.strip() for call in cite_calls for key in call.split(",")}
    bib_text = (PAPER_DIR / "references.bib").read_text(encoding="utf-8")
    bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib_text))
    missing = used_keys - bib_keys
    assert not missing, f"cited keys missing from references.bib: {sorted(missing)}"


def test_every_bib_key_is_cited_and_every_external_entry_has_identifier() -> None:
    # Citation pass 2026-09-22: no orphan bibliography entries, and every non-SBT entry carries a
    # DOI (or an ISBN for books) so the reference can be resolved mechanically.
    text = _tex_text()
    cite_calls = re.findall(r"\\(?:cite|sbtcite)\{([^}]*)\}", text)
    used_keys = {key.strip() for call in cite_calls for key in call.split(",")}
    bib_text = (PAPER_DIR / "references.bib").read_text(encoding="utf-8")
    entries = re.findall(r"@\w+\{([^,]+),(.*?)\n\}", bib_text, flags=re.S)
    orphans = {key for key, _ in entries} - used_keys
    assert not orphans, f"bibliography entries never cited: {sorted(orphans)}"
    without_identifier = [
        key
        for key, body in entries
        if not key.startswith("sbt-") and "doi" not in body.lower() and "isbn" not in body.lower()
    ]
    assert not without_identifier, without_identifier
    assert len(entries) >= 80
