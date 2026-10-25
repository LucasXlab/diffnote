"""Git helpers. Pure stdlib subprocess wrappers, no third-party deps."""

import subprocess


class GitError(RuntimeError):
    pass


def _run(args, cwd=None):
    try:
        proc = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as exc:
        raise GitError("git is not installed or not on PATH") from exc
    return proc


def repo_root(cwd=None):
    proc = _run(["rev-parse", "--show-toplevel"], cwd=cwd)
    if proc.returncode != 0 or not proc.stdout.strip():
        raise GitError("not a git repository (or no commits yet)")
    return proc.stdout.strip()


def is_clean(cwd=None):
    proc = _run(["status", "--porcelain"], cwd=cwd)
    return proc.stdout.strip() == ""


def get_diff_text(ref="HEAD", cwd=None, staged=False):
    """Return unified diff text (working tree or staged) against ref."""
    target = "--staged" if staged else ref
    proc = _run(["diff", "-M", target], cwd=cwd)
    return proc.stdout


def get_range_diff(base, head="HEAD", cwd=None):
    proc = _run(["diff", "-M", f"{base}...{head}"], cwd=cwd)
    return proc.stdout


def get_commit_messages(n=25, cwd=None, revision_range=None):
    """Read commit subjects, optionally restricted to an explicit comparison.

    Pass n=None to include every commit in a selected range.
    """
    args = ["log", "--no-merges", "--pretty=format:%s"]
    if n is not None:
        args.extend(["-n", str(n)])
    if revision_range is not None:
        args.append(revision_range)
    args.append("--")
    proc = _run(args, cwd=cwd)
    return [m for m in proc.stdout.splitlines() if m.strip()]


def guess_base(cwd=None):
    """Best-effort guess of the integration branch for PR summaries."""
    for ref in ("origin/main", "origin/master", "main", "master"):
        proc = _run(["rev-parse", "--verify", ref], cwd=cwd)
        if proc.returncode == 0 and proc.stdout.strip():
            return ref
    return None
