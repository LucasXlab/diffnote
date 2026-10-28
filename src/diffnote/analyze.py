"""Heuristic analysis of a unified git diff: grouping, risk, titles."""

import re
from collections import Counter
from pathlib import PurePosixPath

from .parser import ParseError as ParseError
from .parser import parse_diff as parse_diff

TEST_RE = re.compile(
    r"(^|/)(tests?|spec|__tests__|__mocks__)/|test_.*\.(py)|"
    r"\.test\.(ts|tsx|js|jsx)|_test\.go|_spec\.rb|spec/(.*)\.rb",
    re.I,
)
DOC_RE = re.compile(
    r"\.(md|rst|txt|adoc|mdx)$|^(docs?|documentation)/|README|CHANGELOG|CONTRIBUTING", re.I
)
CONFIG_RE = re.compile(
    r"\.(ya?ml|toml|json|ini|cfg|conf|env|example)$|"
    r"^(config|configs|\.github)/|\.editorconfig|\.gitignore|\.dockerignore",
    re.I,
)
MIGRATION_RE = re.compile(
    r"(^|/)(migrations?|alembic|flyway|liquibase|db/migrate|supabase/migrations)/", re.I
)
SQL_KW = re.compile(
    r"\b(CREATE TABLE|ALTER TABLE|DROP TABLE|ADD COLUMN|DROP COLUMN|"
    r"CREATE INDEX|CREATE VIEW|FOREIGN KEY)\b",
    re.I,
)
AUTH_RE = re.compile(
    r"(^|/)(auth|oauth|login|logout|session|security|passport)/|"
    r"(password|passwd|token|jwt|api[_-]?key|secret|credential|session)",
    re.I,
)
SECURITY_RE = re.compile(r"(vulnerab|injection|xss|csrf|cors|sanitiz|encrypt|decrypt|harden)", re.I)
CI_RE = re.compile(r"^((\.github|\.gitlab-ci\.yml|\.circleci|ci|workflows)/|\.travis\.yml)", re.I)
I18N_RE = re.compile(r"(^|/)(locale|locales|i18n|translations?|lang|messages)/|\.po$", re.I)
DEP_FILES = {
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "requirements.txt",
    "pyproject.toml",
    "poetry.lock",
    "Pipfile",
    "Pipfile.lock",
    "uv.lock",
    "Cargo.toml",
    "Cargo.lock",
    "go.mod",
    "go.sum",
    "composer.json",
    "Gemfile",
    "Gemfile.lock",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "bun.lockb",
    "flake.nix",
}

CONV_RE = re.compile(
    r"^(feat|fix|refactor|perf|chore|docs|test|style|build|ci)"
    r"(\([^)]+\))?!?:",
    re.I,
)


def _categorize(path):
    tags = []
    if TEST_RE.search(path):
        tags.append("tests")
    if DOC_RE.search(path) and PurePosixPath(path).name not in DEP_FILES:
        tags.append("docs")
    if CONFIG_RE.search(path) or PurePosixPath(path).name in DEP_FILES:
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
    return "\n".join(file["lines"] + file.get("removed_lines", []))


def assess_risks(files):
    """Finite review signals with rule/path provenance, not a safety verdict."""
    signals = {}

    def record(label, path, rule, direction):
        item = signals.setdefault(label, {"label": label, "files": [], "evidence": []})
        if path not in item["files"]:
            item["files"].append(path)
        item["evidence"].append({"path": path, "rule": rule, "source": direction})

    for f in files:
        path = f["new"]
        paths = [p for p in (f.get("old"), path) if p]
        if any(MIGRATION_RE.search(p) for p in paths):
            record("database migration / schema change", path, "migration-path", "path")
        if any(AUTH_RE.search(p) or SECURITY_RE.search(p) for p in paths):
            record("auth / security related", path, "auth-path", "path")
        for field, direction in [("lines", "added"), ("removed_lines", "deleted")]:
            content = "\n".join(f.get(field, []))
            if SQL_KW.search(content):
                record("database migration / schema change", path, "schema-keyword", direction)
            if SECURITY_RE.search(content):
                record("auth / security related", path, "security-keyword", direction)
        if any(PurePosixPath(p).name in DEP_FILES for p in paths):
            record("dependency change", path, "dependency-basename", "path")
        if f["added"] + f["deleted"] >= 500:
            record("large batch change (review carefully)", path, "line-count", "metadata")
    return list(signals.values())


def _status(file):
    if file.get("copied"):
        return "copied"
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


def build_summary(files, commit_messages=None, source="provided diff"):
    commit_messages = commit_messages or []
    if not files:
        return {
            "total_files": 0,
            "added": 0,
            "deleted": 0,
            "areas": {},
            "risks": [],
            "title": "(no changes detected)",
            "section": "none",
            "highlights": [],
            "files": [],
            "source": source,
            "title_source": "diff paths",
            "limits": ["No semantic verification; tests were not run."],
        }
    total_added = sum(f["added"] for f in files)
    total_deleted = sum(f["deleted"] for f in files)
    areas = Counter()
    for f in files:
        for t in _categorize(f["new"]):
            areas[t] += 1

    risks = assess_risks(files)
    title = suggest_title(files, commit_messages)
    section = suggest_section(files, commit_messages)

    highlights = []
    for f in sorted(files, key=lambda x: x["added"] + x["deleted"], reverse=True)[:12]:
        highlights.append(
            {
                "path": f["new"],
                "old_path": f.get("old"),
                "new_path": f.get("new_path", f["new"]),
                "status": _status(f),
                "binary": f.get("binary", False),
                "old_mode": f.get("old_mode"),
                "new_mode": f.get("new_mode"),
                "added": f["added"],
                "deleted": f["deleted"],
                "area": _categorize(f["new"])[0],
                "risks": _risk_labels_for(f, risks),
            }
        )

    return {
        "total_files": len(files),
        "added": total_added,
        "deleted": total_deleted,
        "areas": dict(areas),
        "risks": risks,
        "title": title,
        "section": section,
        "highlights": highlights,
        "files": [
            {
                "path": f["new"],
                "old_path": f.get("old"),
                "new_path": f.get("new_path", f["new"]),
                "status": _status(f),
                "added": None if f["binary"] else f["added"],
                "deleted": None if f["binary"] else f["deleted"],
                "binary": f["binary"],
                "old_mode": f.get("old_mode"),
                "new_mode": f.get("new_mode"),
            }
            for f in files
        ],
        "source": source,
        "title_source": "related commit subject"
        if any(CONV_RE.match(m) for m in commit_messages)
        else "diff paths",
        "limits": [
            "Heuristic draft; semantic correctness is unverified.",
            "Tests were not run. Absence of signals is not evidence of safety.",
        ],
    }


def suggest_title(files, commit_messages):
    for msg in commit_messages:
        if CONV_RE.match(msg):
            return msg
    if any(PurePosixPath(f["new"]).name in DEP_FILES for f in files) and all(
        _categorize(f["new"])[0] == "config" for f in files
    ):
        return "chore(deps): review dependency-file changes"
    if any("database migration" in r["label"] for r in assess_risks(files)):
        return "chore: review database schema changes"
    areas = Counter(_categorize(f["new"])[0] for f in files)
    top = areas.most_common(1)[0][0] if areas else "source"
    if top == "tests":
        return "test: review test-file changes"
    if top == "docs":
        return "docs: update documentation"
    if top == "ci" or (top == "config" and any(CI_RE.search(f["new"]) for f in files)):
        return "ci: review pipeline configuration"
    if top == "config":
        return "chore: review configuration changes"
    return "chore: review source changes"


def suggest_section(files, commit_messages):
    for msg in commit_messages:
        m = CONV_RE.match(msg)
        if m:
            return m.group(1).lower()
    areas = Counter(_categorize(f["new"])[0] for f in files)
    top = areas.most_common(1)[0][0] if areas else "fix"
    mapping = {
        "tests": "test",
        "docs": "docs",
        "config": "chore",
        "ci": "ci",
        "migration": "chore",
        "i18n": "chore",
        "source": "chore",
    }
    return mapping.get(top, "chore")
