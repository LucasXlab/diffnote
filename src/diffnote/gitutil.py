"""Bounded read-only Git access with validated revisions."""

import os
import re
import signal
import subprocess
import tempfile
import time

MAX_OUTPUT = 8 * 1024 * 1024
TIMEOUT = 15
OID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
CONFIG = [
    "--no-optional-locks",
    "-c",
    "core.fsmonitor=false",
    "-c",
    "core.hooksPath=/dev/null",
    "-c",
    "log.showSignature=false",
    "-c",
    "submodule.recurse=false",
    "-c",
    "core.quotePath=true",
    "-c",
    "color.ui=false",
    "-c",
    "core.attributesFile=/dev/null",
    "-c",
    "diff.suppressBlankEmpty=false",
]
DIFF = [
    "diff",
    "--no-ext-diff",
    "--no-textconv",
    "--no-color",
    "--no-relative",
    "--src-prefix=a/",
    "--dst-prefix=b/",
    "--ignore-submodules=none",
    "--submodule=short",
    "--find-renames",
    "--unified=3",
]


class GitError(RuntimeError):
    """An incomplete Git read, never an empty diff."""


def _environment():
    env = {
        k: os.environ[k]
        for k in ("PATH", "HOME", "TMPDIR", "LANG", "LC_ALL", "GIT_CEILING_DIRECTORIES")
        if k in os.environ
    }
    env.update(
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_CONFIG_NOSYSTEM="1",
        GIT_TERMINAL_PROMPT="0",
        GIT_NO_LAZY_FETCH="1",
        GIT_PAGER="cat",
        GIT_ATTR_NOSYSTEM="1",
        GIT_OPTIONAL_LOCKS="0",
    )
    return env


def _run(args, cwd=None, *, allow_failure=False):
    if os.name != "posix":
        raise GitError("bounded Git process handling supports macOS and Linux only")
    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
        try:
            proc = subprocess.Popen(
                ["git", *CONFIG, *args],
                cwd=cwd,
                env=_environment(),
                stdin=subprocess.DEVNULL,
                stdout=out,
                stderr=err,
                start_new_session=True,
            )
        except (OSError, ValueError) as exc:
            raise GitError("cannot start Git; check installation and repository access") from exc
        deadline = time.monotonic() + TIMEOUT
        failure = None
        while proc.poll() is None:
            if os.fstat(out.fileno()).st_size + os.fstat(err.fileno()).st_size > MAX_OUTPUT:
                failure = "Git output exceeds the 8 MiB analysis limit"
                break
            if time.monotonic() > deadline:
                failure = "Git read timed out"
                break
            time.sleep(0.01)
        if failure:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
            raise GitError(failure)
        if os.fstat(out.fileno()).st_size + os.fstat(err.fileno()).st_size > MAX_OUTPUT:
            raise GitError("Git output exceeds the 8 MiB analysis limit")
        out.seek(0)
        err.seek(0)
        result = subprocess.CompletedProcess(
            args,
            proc.returncode,
            out.read().decode("utf-8", "surrogateescape"),
            err.read().decode("utf-8", "replace"),
        )
    if result.returncode and not allow_failure:
        raise GitError(f"Git {args[0]} failed; check refs, available history, and repository state")
    return result


def repo_root(cwd=None):
    text = _run(["rev-parse", "--show-toplevel"], cwd).stdout.removesuffix("\n")
    if not text:
        raise GitError("not a working-tree repository")
    return text


def is_clean(cwd=None):
    _check_local(cwd)
    return not _run(["status", "--porcelain", "--ignore-submodules=all"], cwd).stdout.strip()


def resolve_ref(ref, cwd=None):
    if (
        not isinstance(ref, str)
        or not ref
        or ref.startswith("-")
        or len(ref) > 512
        or any(ord(c) < 32 or ord(c) == 127 for c in ref)
    ):
        raise GitError("invalid revision; option-like/control-character refs are not accepted")
    oid = _run(["rev-parse", "--verify", "--end-of-options", ref + "^{commit}"], cwd).stdout.strip()
    if not OID.fullmatch(oid):
        raise GitError("revision must identify exactly one commit")
    return oid


def _empty_tree(cwd):
    return _run(["hash-object", "-t", "tree", "--stdin"], cwd).stdout.strip()


def _head_or_empty(cwd):
    head = _run(
        ["rev-parse", "--verify", "--end-of-options", "HEAD^{commit}"], cwd, allow_failure=True
    )
    if head.returncode == 0:
        return head.stdout.strip()
    symbolic = _run(["symbolic-ref", "-q", "HEAD"], cwd, allow_failure=True)
    if not symbolic.returncode:
        exists = _run(
            ["show-ref", "--verify", "--quiet", symbolic.stdout.strip()], cwd, allow_failure=True
        )
        if exists.returncode == 1:
            return _empty_tree(cwd)
    raise GitError("HEAD cannot be read")


def _check_local(cwd):
    p = _run(
        ["config", "--get-regexp", r"^(extensions\.partialclone|remote\..*\.promisor)$"],
        cwd,
        allow_failure=True,
    )
    if p.returncode not in (0, 1) or p.stdout.strip():
        raise GitError("partial/promisor repositories are unsupported; no objects will be fetched")
    filters = _run(
        ["config", "--get-regexp", r"^filter\..*\.(clean|process)$"], cwd, allow_failure=True
    )
    if filters.returncode not in (0, 1) or filters.stdout.strip():
        raise GitError(
            "repositories with clean/process filters are unsupported; no filter programs will run"
        )
    index = _run(["ls-files", "--stage", "-z"], cwd).stdout
    if any(record.startswith("160000 ") for record in index.split("\0")):
        raise GitError(
            "repositories with submodule gitlinks are unsupported; no submodule programs will run"
        )


def _diff(revisions, cwd=None, staged=False, *, metadata=False):
    _check_local(cwd)
    args = [*DIFF]
    if staged:
        args.append("--cached")
    if metadata:
        args.remove("--unified=3")
        args += ["--numstat", "-z"]
    return _run([*args, *revisions, "--"], cwd).stdout


def get_diff_text(ref="HEAD", cwd=None, staged=False):
    oid = _head_or_empty(cwd) if ref == "HEAD" else resolve_ref(ref, cwd)
    return _diff([oid], cwd, staged)


def get_range_diff(base, head="HEAD", cwd=None, *, merge_base=False):
    left, right = resolve_ref(base, cwd), resolve_ref(head, cwd)
    if merge_base:
        left = _run(["merge-base", left, right], cwd).stdout.strip()
    return _diff([left, right], cwd)


def get_commit_messages(n=25, cwd=None, revision=None):
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 1000:
        raise GitError("commit count must be between 1 and 1000")
    revision = revision or resolve_ref("HEAD", cwd)
    p = _run(
        [
            "log",
            "--no-show-signature",
            "--no-color",
            "--no-decorate",
            f"--max-count={n}",
            "--format=%s",
            revision,
            "--",
        ],
        cwd,
    )
    return [x for x in p.stdout.splitlines() if x.strip()]


def guess_base(cwd=None):
    """Compatibility helper; only locally available refs are considered."""
    for ref in ("origin/main", "origin/master", "main", "master"):
        try:
            resolve_ref(ref, cwd)
            return ref
        except GitError:
            continue
    return None


def read_selection(*, cwd, base=None, range_spec=None, commits=None, staged=False):
    subjects = []
    if range_spec:
        m = re.fullmatch(r"(.+?)(\.\.\.?)(.+)", range_spec)
        if not m or ".." in m[1] or ".." in m[3]:
            raise GitError(
                "range must be A..B (endpoints) or A...B (merge base), with both endpoints"
            )
        left, right = resolve_ref(m[1], cwd), resolve_ref(m[3], cwd)
        if m[2] == "...":
            left = _run(["merge-base", left, right], cwd).stdout.strip()
        revisions = [left, right]
        subjects = get_commit_messages(cwd=cwd, revision=f"{left}..{right}")
        source = "committed range"
    elif commits is not None:
        if isinstance(commits, bool) or not 1 <= commits <= 1000:
            raise GitError("--commits must be between 1 and 1000")
        right = resolve_ref("HEAD", cwd)
        history = _run(
            ["rev-list", "--first-parent", f"--max-count={commits + 1}", right, "--"], cwd
        ).stdout.splitlines()
        if len(history) < commits:
            raise GitError("commit count exceeds available first-parent history")
        if len(history) == commits:
            if _run(["rev-parse", "--is-shallow-repository"], cwd).stdout.strip() == "true":
                raise GitError("requested commit range reaches a shallow boundary")
            left = _empty_tree(cwd)
            subjects = get_commit_messages(commits, cwd, right)
        else:
            left = history[commits]
            subjects = get_commit_messages(commits, cwd, f"{left}..{right}")
        revisions = [left, right]
        source = "first-parent commits"
    else:
        revisions = [resolve_ref(base, cwd) if base else _head_or_empty(cwd)]
        source = "staged changes" if staged else "tracked working tree"
    return (
        _diff(revisions, cwd, staged),
        _diff(revisions, cwd, staged, metadata=True),
        subjects,
        source,
    )


def verify_numstat(files, text):
    fields = text.split("\0")
    expected = []
    i = 0
    while i < len(fields) and fields[i]:
        parts = fields[i].split("\t", 2)
        i += 1
        if len(parts) != 3:
            raise GitError("unsupported numstat output")
        added, deleted, path = parts
        old = None
        if not path:
            if i + 1 >= len(fields):
                raise GitError("incomplete rename metadata")
            old, path = fields[i : i + 2]
            i += 2
        expected.append((path, old, added, deleted))
    actual = {f["new"]: f for f in files}
    if len(actual) != len(files) or len(expected) != len(files):
        raise GitError("patch and Git file metadata disagree; analysis incomplete")
    for path, old, added, deleted in expected:
        f = actual.get(path)
        if f is None or (old is not None and f["old"] != old):
            raise GitError("patch and Git paths disagree; analysis incomplete")
        if added == "-" and deleted == "-":
            if not f["binary"]:
                raise GitError("binary metadata missing from patch")
        elif (f["added"], f["deleted"]) != (int(added), int(deleted)):
            raise GitError("patch and Git line counts disagree; analysis incomplete")
