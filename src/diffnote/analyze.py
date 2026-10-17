"""Heuristic analysis of a unified git diff: grouping, risk, titles."""

import re
from collections import Counter

FILE_RE = re.compile(r"^diff --git a/(.*?) b/(.*)$")
BINARY_RE = re.compile(r"^Binary files")

TEST_RE = re.compile(r"(^|/)(tests?|spec|__tests__|__mocks__)/|test_.*\.(py)|"
                     r"\.test\.(ts|tsx|js|jsx)|_test\.go|_spec\.rb|spec/(.*)\.rb", re.I)
DOC_RE = re.compile(r"\.(md|rst|txt|adoc|mdx)$|^(docs?|documentation)/|README|CHANGELOG|CONTRIBUTING", re.I)
CONFIG_RE = re.compile(r"\.(ya?ml|toml|json|ini|cfg|conf|env|example)$|"
                       r"^(config|configs|\.github)/|\.editorconfig|\.gitignore|\.dockerignore", re.I)
MIGRATION_RE = re.compile(r"(^|/)(migrations?|alembic|flyway|liquibase|db/migrate|supabase/migrations)/", re.I)
SQL_KW = re.compile(r"\b(CREATE TABLE|ALTER TABLE|DROP TABLE|ADD COLUMN|DROP COLUMN|"
                    r"CREATE INDEX|CREATE VIEW|FOREIGN KEY)\b", re.I)
AUTH_RE = re.compile(r"(^|/)(auth|oauth|login|logout|session|security|passport)/|"
                     r"(password|passwd|token|jwt|api[_-]?key|secret|credential|session)", re.I)
SECURITY_RE = re.compile(r"(vulnerab|injection|xss|csrf|cors|sanitiz|encrypt|decrypt|harden)", re.I)
CI_RE = re.compile(r"^((\.github|\.gitlab-ci\.yml|\.circleci|ci|workflows)/|\.travis\.yml)", re.I)
I18N_RE = re.compile(r"(^|/)(locale|locales|i18n|translations?|lang|messages)/|\.po$", re.I)
DEP_FILES = {
    "package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "requirements.txt", "pyproject.toml", "poetry.lock", "Pipfile", "Pipfile.lock",
    "uv.lock", "Cargo.toml", "Cargo.lock", "go.mod", "go.sum", "composer.json",
    "Gemfile", "Gemfile.lock", "pom.xml", "build.gradle", "build.gradle.kts",
    "bun.lockb", "flake.nix",
}

CONV_RE = re.compile(r"^(feat|fix|refactor|perf|chore|docs|test|style|build|ci)"
                     r"(\([^)]+\))?!?:", re.I)
BREAKING_COMMIT_RE = re.compile(r"^[a-z][a-z0-9-]*(?:\([^)]+\))?!:", re.I)
PUBLIC_API_RE = re.compile(r"^(?:lib/|src/(?:[^/]+/)*api(?:/|$))", re.I)


MINUS_RE = re.compile(r"^--- ")
PLUS_RE = re.compile(r"^\+\+\+ ")


def _path_from_header(line):
    p = line[4:].rstrip("\r")
    if p == "/dev/null":
        return None
    if p.startswith(("a/", "b/")):
        return p[2:]
    return p


def parse_diff(text):
    """Parse a unified diff into a list of file dicts.

    Each dict has: new(display path), is_new, is_deleted, renamed,
    added, deleted, binary, lines(list of added-line contents).
    New/deleted are detected from the `---`/`+++` headers (correct for
    new/deleted files, unlike the `diff --git` line).
    """
    files = []
    cur = None
    for line in text.splitlines():
        m = FILE_RE.match(line)
        if m:
            if cur:
                files.append(cur)
            cur = {
                "old": m.group(1), "new": m.group(2),
                "added": 0, "deleted": 0, "binary": False, "lines": [],
            }
            continue
        if cur is None:
            continue
        if MINUS_RE.match(line):
            cur["old"] = _path_from_header(line)
            continue
        if PLUS_RE.match(line):
            cur["new"] = _path_from_header(line)
            continue
        if BINARY_RE.match(line):
            cur["binary"] = True
            continue
        if line.startswith("@@"):
            continue
        if line.startswith("+") and not line.startswith("+++"):
            cur["added"] += 1
            cur["lines"].append(line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            cur["deleted"] += 1
    if cur:
        files.append(cur)

    for f in files:
        is_new = f["old"] is None
        is_deleted = f["new"] is None
        display = f["new"] if not is_deleted else f["old"]
        renamed = (not is_new and not is_deleted and f["old"] != f["new"])
        f["is_new"] = is_new
        f["is_deleted"] = is_deleted
        f["renamed"] = renamed
        f["new"] = display
    return files


def _categorize(path):
    tags = []
    if TEST_RE.search(path):
        tags.append("tests")
    if DOC_RE.search(path) and path not in DEP_FILES:
        tags.append("docs")
    if CONFIG_RE.search(path) or path in DEP_FILES:
        tags.append("config")
    if MIGRATION_RE.search(path):
        tags.append("migration")
    if CI_RE.search(path):
        tags.append("ci")
    if I18N_RE.search(path):
        tags.append("i18n")
    if not tags:
        tags.append("source")
    return tags


def _join_text(file):
    return "\n".join(file["lines"])


def assess_risks(files, commit_messages=None):
    """Return list of risk dicts: {label, files:[...]}."""
    risks = {}
    breaking_commit = any(BREAKING_COMMIT_RE.match(message) for message in (commit_messages or []))
    breaking_files = []
    for f in files:
        path = f["new"]
        content = _join_text(f)
        if MIGRATION_RE.search(path) or SQL_KW.search(content):
            risks.setdefault("database migration / schema change", []).append(path)
        if AUTH_RE.search(path) or SECURITY_RE.search(path) or SECURITY_RE.search(content):
            risks.setdefault("auth / security related", []).append(path)
        if path in DEP_FILES:
            risks.setdefault("dependency change", []).append(path)
        if f["added"] + f["deleted"] >= 500:
            risks.setdefault("large batch change (review carefully)", []).append(path)
        if breaking_commit or PUBLIC_API_RE.match(path):
            breaking_files.append(path)
    if breaking_files:
        risks["possible breaking change"] = breaking_files
    return [{"label": k, "files": v} for k, v in risks.items()]


def _status(file):
    if file["is_new"]:
        return "added"
    if file["is_deleted"]:
        return "deleted"
    if file["renamed"]:
        return "renamed"
    return "modified"


def _risk_labels_for(file, risks):
    path = file["new"]
    return [r["label"] for r in risks if path in r["files"]]


def build_summary(files, commit_messages=None):
    commit_messages = commit_messages or []
    if not files:
        return {
            "total_files": 0, "added": 0, "deleted": 0, "areas": {},
            "risks": [], "title": "(no changes detected)", "section": "none",
            "highlights": [],
        }
    total_added = sum(f["added"] for f in files)
    total_deleted = sum(f["deleted"] for f in files)
    areas = Counter()
    for f in files:
        for t in _categorize(f["new"]):
            areas[t] += 1

    risks = assess_risks(files, commit_messages)
    title = suggest_title(files, commit_messages)
    section = suggest_section(files, commit_messages)

    highlights = []
    for f in sorted(files, key=lambda x: x["added"] + x["deleted"], reverse=True)[:12]:
        highlights.append({
            "path": f["new"], "status": _status(f),
            "added": f["added"], "deleted": f["deleted"],
            "area": _categorize(f["new"])[0],
            "risks": _risk_labels_for(f, risks),
        })

    return {
        "total_files": len(files),
        "added": total_added,
        "deleted": total_deleted,
        "areas": dict(areas),
        "risks": risks,
        "title": title,
        "section": section,
        "highlights": highlights,
    }


def suggest_title(files, commit_messages):
    for msg in commit_messages:
        if CONV_RE.match(msg):
            return msg
    if any(f["new"] in DEP_FILES for f in files) and \
            all(_categorize(f["new"])[0] == "config" for f in files):
        return "chore(deps): bump dependencies"
    if any("database migration" in r["label"] for r in assess_risks(files)):
        return "feat: database schema migration"
    areas = Counter(_categorize(f["new"])[0] for f in files)
    top = areas.most_common(1)[0][0] if areas else "source"
    if top == "tests":
        return "test: add and update tests"
    if top == "docs":
        return "docs: update documentation"
    if top == "ci":
        return "ci: update pipeline"
    return "fix: update implementation"


def suggest_section(files, commit_messages):
    for msg in commit_messages:
        m = CONV_RE.match(msg)
        if m:
            return m.group(1).lower()
    areas = Counter(_categorize(f["new"])[0] for f in files)
    top = areas.most_common(1)[0][0] if areas else "fix"
    mapping = {
        "tests": "test", "docs": "docs", "config": "chore", "ci": "ci",
        "migration": "feat", "i18n": "feat", "source": "fix",
    }
    return mapping.get(top, "fix")
