#!/usr/bin/env python3
"""Install the built wheel into a fresh venv and run outside the source tree."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    wheels = list((ROOT / "dist").glob("diffnote-*.whl"))
    if len(wheels) != 1:
        raise RuntimeError("expected exactly one built wheel")
    with tempfile.TemporaryDirectory(prefix="diffnote-wheel-") as tmp:
        p = Path(tmp)
        home = p / "home"
        home.mkdir()
        repo = p / "repo"
        repo.mkdir()
        env = {
            k: os.environ[k] for k in ("PATH", "PIP_NO_INDEX", "PIP_FIND_LINKS") if k in os.environ
        }
        env.update(
            HOME=str(home),
            XDG_CONFIG_HOME=str(home / "config"),
            PYTHONNOUSERSITE="1",
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CEILING_DIRECTORIES=str(p),
            GIT_AUTHOR_NAME="Synthetic Contributor",
            GIT_COMMITTER_NAME="Synthetic Contributor",
            GIT_AUTHOR_EMAIL="fixture@example.invalid",
            GIT_COMMITTER_EMAIL="fixture@example.invalid",
        )

        def run(args, cwd=p):
            q = subprocess.run(
                [str(x) for x in args], cwd=cwd, env=env, text=True, capture_output=True, timeout=60
            )
            if q.returncode:
                raise RuntimeError(q.stderr or q.stdout)
            return q.stdout

        run([sys.executable, "-m", "venv", p / "venv"])
        py = p / "venv/bin/python"
        run([py, "-m", "pip", "install", "--no-index", "--no-deps", wheels[0]])
        imported = run([py, "-c", "import diffnote; print(diffnote.__file__)"]).strip()
        if str(p / "venv") not in imported:
            raise RuntimeError("wheel import escaped fresh venv")
        run(["git", "init", "-q", "-b", "main"], repo)
        (repo / "file.txt").write_text("old\n")
        run(["git", "add", "."], repo)
        run(["git", "-c", "commit.gpgsign=false", "commit", "-qm", "synthetic"], repo)
        (repo / "file.txt").write_text("new\n")
        result = json.loads(run([py, "-m", "diffnote", "--json"], repo))
        assert result["total_files"] == 1 and result["added"] == 1 and result["deleted"] == 1
        print("Fresh wheel import and real Git CLI smoke passed outside source checkout.")


if __name__ == "__main__":
    main()
