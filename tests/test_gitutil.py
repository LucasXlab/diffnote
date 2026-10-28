import os
import subprocess
import tempfile

from diffnote import gitutil


def _git(cwd, *args):
    subprocess.run(
        ["git", *args], cwd=cwd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )


def _make_repo():
    d = tempfile.mkdtemp()
    _git(d, "init", "-q")
    _git(d, "config", "user.email", "fixture@example.invalid")
    _git(d, "config", "user.name", "Test")
    with open(os.path.join(d, "a.txt"), "w") as fh:
        fh.write("hello\n")
    _git(d, "add", "a.txt")
    _git(d, "commit", "-q", "-m", "feat: initial")
    with open(os.path.join(d, "a.txt"), "w") as fh:
        fh.write("hello world\n")
    return d


def test_repo_root_and_diff():
    import os

    d = _make_repo()
    assert os.path.realpath(gitutil.repo_root(d)) == os.path.realpath(d)
    diff = gitutil.get_diff_text("HEAD", cwd=d)
    assert "a.txt" in diff
    assert "+hello world" in diff


def test_clean_repo():
    d = tempfile.mkdtemp()
    _git(d, "init", "-q")
    _git(d, "config", "user.email", "fixture@example.invalid")
    _git(d, "config", "user.name", "T")
    assert gitutil.is_clean(d) is True


def test_guess_base_absent():
    d = _make_repo()
    # fresh repo with only local commits has no origin/main
    assert gitutil.guess_base(cwd=d) in (None, "main", "master")


def test_not_a_repo():
    d = tempfile.mkdtemp()
    try:
        gitutil.repo_root(d)
        assert False, "expected GitError"
    except gitutil.GitError:
        pass
