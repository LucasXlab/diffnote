"""Regression coverage for commit markers belonging to the selected diff."""

import json
import subprocess

import pytest

from diffnote import cli


def _git(repo, *args):
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def _init(repo):
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.name", "Scope Fixture")
    _git(repo, "config", "user.email", "fixture@example.invalid")


def _commit(repo, message, text):
    (repo / "README.md").write_text(text, encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "-c", "commit.gpgsign=false", "commit", "-qm", message)


def _summary(args, capsys):
    assert cli.main([*args, "--json"]) == 0
    return json.loads(capsys.readouterr().out)


def _is_breaking(summary):
    return any(risk["label"] == "possible breaking change"
               for risk in summary["risks"])


@pytest.mark.parametrize("args", [
    [],
    ["--staged"],
    ["--commits", "1"],
    ["--range", "old-marker..docs-end"],
    ["--base", "old-marker"],
])
def test_old_breaking_marker_does_not_contaminate_selected_docs(
    tmp_path, monkeypatch, capsys, args,
):
    _init(tmp_path)
    _commit(tmp_path, "feat!: retire an old API", "# Original\n")
    _git(tmp_path, "tag", "old-marker")
    _commit(tmp_path, "docs: clarify wording", "# Clarified\n")
    _git(tmp_path, "tag", "docs-end")
    (tmp_path / "README.md").write_text("# Current docs\n", encoding="utf-8")
    _git(tmp_path, "add", "README.md")
    monkeypatch.chdir(tmp_path)

    summary = _summary(args, capsys)

    assert summary["total_files"] == 1
    assert not _is_breaking(summary)
    assert summary["title"] != "feat!: retire an old API"


def test_range_reads_markers_from_selected_branch_instead_of_head(
    tmp_path, monkeypatch, capsys,
):
    _init(tmp_path)
    _commit(tmp_path, "docs: initial", "# Initial\n")
    _git(tmp_path, "tag", "start")
    _git(tmp_path, "checkout", "-qb", "feature")
    _commit(tmp_path, "feat!: remove legacy response", "# New response\n")
    _git(tmp_path, "tag", "feature-end")
    _git(tmp_path, "checkout", "-q", "main")
    _commit(tmp_path, "docs: sibling branch", "# Sibling\n")
    monkeypatch.chdir(tmp_path)

    summary = _summary(["--range", "start..feature-end"], capsys)

    assert _is_breaking(summary)
    assert summary["title"] == "feat!: remove legacy response"


def test_range_excludes_markers_committed_after_its_endpoint(
    tmp_path, monkeypatch, capsys,
):
    _init(tmp_path)
    _commit(tmp_path, "docs: initial", "# Initial\n")
    _git(tmp_path, "tag", "start")
    _commit(tmp_path, "docs: selected change", "# Selected\n")
    _git(tmp_path, "tag", "selected")
    _commit(tmp_path, "feat!: later change", "# Later\n")
    monkeypatch.chdir(tmp_path)

    summary = _summary(["--range", "start..selected"], capsys)

    assert not _is_breaking(summary)
    assert summary["title"] == "docs: selected change"


def test_commit_selection_is_not_silently_limited_to_25_messages(
    tmp_path, monkeypatch, capsys,
):
    _init(tmp_path)
    _commit(tmp_path, "docs: initial", "# Initial\n")
    _commit(tmp_path, "feat!: selected API change", "# API change\n")
    for i in range(26):
        _commit(tmp_path, "docs: update {}".format(i), "# Update {}\n".format(i))
    monkeypatch.chdir(tmp_path)

    summary = _summary(["--commits", "27"], capsys)

    assert _is_breaking(summary)
