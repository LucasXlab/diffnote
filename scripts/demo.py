#!/usr/bin/env python3
"""Run the installed CLI against temporary, explicitly synthetic Git data."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    with tempfile.TemporaryDirectory(prefix="diffnote-demo-") as tmp:
        work = Path(tmp)
        home = work / "home"
        home.mkdir()
        repo = work / "project"
        repo.mkdir()
        env = {
            "PATH": os.defpath + os.pathsep + os.environ.get("PATH", ""),
            "HOME": str(home),
            "XDG_CONFIG_HOME": str(home / "config"),
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Synthetic Contributor",
            "GIT_COMMITTER_NAME": "Synthetic Contributor",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
            "NO_COLOR": "1",
            "PYTHONNOUSERSITE": "1",
            "GIT_CEILING_DIRECTORIES": str(work),
        }

        def call(args):
            p = subprocess.run(args, cwd=repo, env=env, text=True, capture_output=True, timeout=20)
            if p.returncode:
                raise RuntimeError("synthetic demo command failed: " + p.stderr)
            return p.stdout

        def write(name, text):
            p = repo / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)

        call(["git", "init", "-q", "-b", "main"])
        write("src/total.py", "def total(items):\n    return sum(items)\n")
        write("tests/test_total.py", "def test_total():\n    assert 1 + 2 == 3\n")
        call(["git", "add", "."])
        call(
            ["git", "-c", "commit.gpgsign=false", "commit", "-qm", "feat: synthetic initial state"]
        )
        write("src/total.py", "def total(items):\n    return round(sum(items), 2)\n")
        write(
            "tests/test_total.py",
            "def test_total():\n    assert 1 + 2 == 3\n    assert round(1.234, 2) == 1.23\n",
        )
        print("Synthetic fixture; real installed diffnote output. No tests are executed.\n")
        print("$ diffnote --no-color\n")
        print(call([sys.executable, "-m", "diffnote", "--no-color"]))
        print("\n$ diffnote --markdown\n")
        print(call([sys.executable, "-m", "diffnote", "--markdown"]))


if __name__ == "__main__":
    main()
