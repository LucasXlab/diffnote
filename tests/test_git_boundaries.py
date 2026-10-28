import os
import subprocess

import pytest

from diffnote import gitutil as g


def git(p, *args):
    return subprocess.check_output(["git", *args], cwd=p, text=True)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / "file.txt").write_text("old\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "initial synthetic state")
    return tmp_path


@pytest.mark.parametrize(
    "ref",
    ["--output=must-not-exist", "--ext-diff", "-cfoo=bar", "", "HEAD\n--output=x", "missing-ref"],
)
def test_invalid_ref_fails_without_writes(repo, ref):
    before = sorted(str(p.relative_to(repo)) for p in repo.rglob("*"))
    with pytest.raises(g.GitError):
        g.get_diff_text(ref, repo)
    assert sorted(str(p.relative_to(repo)) for p in repo.rglob("*")) == before


def test_external_helpers_disabled(repo, tmp_path):
    marker = repo / "marker"
    script = repo / "helper.sh"
    script.write_text(f'#!/bin/sh\ntouch "{marker}"\necho changed\n')
    script.chmod(0o755)
    git(repo, "config", "diff.driver.textconv", str(script))
    git(repo, "config", "diff.external", str(script))
    (repo / ".gitattributes").write_text("file.txt diff=driver\n")
    (repo / "file.txt").write_text("new\n")
    os.environ["GIT_EXTERNAL_DIFF"] = str(script)
    assert "+new" in g.get_diff_text(cwd=repo)
    assert not marker.exists()


def test_diff_configuration_fixed(repo):
    (repo / "file.txt").write_text("new\n")
    git(repo, "config", "color.ui", "always")
    git(repo, "config", "diff.noprefix", "true")
    text = g.get_diff_text(cwd=repo)
    assert "\x1b" not in text and "--- a/file.txt" in text and "+++ b/file.txt" in text


def test_range_semantics(repo):
    git(repo, "checkout", "-qb", "feature")
    (repo / "feature").write_text("f\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "feature")
    git(repo, "checkout", "main")
    (repo / "main-only").write_text("m\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "main")
    two = g.read_selection(cwd=repo, range_spec="main..feature")[0]
    three = g.read_selection(cwd=repo, range_spec="main...feature")[0]
    assert "main-only" in two and "main-only" not in three and "feature" in three


@pytest.mark.parametrize("count", [0, -1, 1001, 10])
def test_invalid_commit_count(repo, count):
    with pytest.raises(g.GitError):
        g.read_selection(cwd=repo, commits=count)


def test_root_commit_and_empty_repo(repo, tmp_path):
    assert "file.txt" in g.read_selection(cwd=repo, commits=1)[0]
    p = tmp_path / "empty"
    p.mkdir()
    git(p, "init", "-q")
    assert g.get_diff_text(cwd=p) == ""
    (p / "new").write_text("new\n")
    git(p, "add", ".")
    assert "+new" in g.get_diff_text(cwd=p)


def test_partial_repo_rejected(repo):
    git(repo, "config", "remote.origin.promisor", "true")
    with pytest.raises(g.GitError, match="partial"):
        g.get_diff_text(cwd=repo)


def test_error_timeout_and_limit(repo, monkeypatch):
    with pytest.raises(g.GitError):
        g._run(["not-a-real-command"], repo)
    stub = repo / "fake-bin"
    stub.mkdir()
    executable = stub / "git"
    executable.write_text("#!/bin/sh\nsleep 2\n")
    executable.chmod(0o755)
    with monkeypatch.context() as scoped:
        scoped.setenv("PATH", str(stub) + os.pathsep + "/bin:/usr/bin")
        scoped.setattr(g, "TIMEOUT", 0.05)
        with pytest.raises(g.GitError, match="timed out"):
            g._run(["log"], repo)
    monkeypatch.setattr(g, "TIMEOUT", 15)
    monkeypatch.setattr(g, "MAX_OUTPUT", 1)
    with pytest.raises(g.GitError, match="limit"):
        g._run(["log"], repo)


def test_no_git_available(repo, monkeypatch):
    monkeypatch.setenv("PATH", "/nonexistent")
    with pytest.raises(g.GitError, match="cannot start"):
        g.repo_root(repo)
