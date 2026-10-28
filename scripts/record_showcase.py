#!/usr/bin/env python3
"""Record locally to assets/recording/showcase.cast; never upload anything."""

import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    recorder = shutil.which("asciinema")
    if not recorder:
        raise SystemExit("Install asciinema==2.4.0 to record; no network access is performed here.")
    target = root / "assets/recording"
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="diffnote-recording-") as tmp:
        home = Path(tmp)
        env = {
            "PATH": os.defpath + os.pathsep + os.environ.get("PATH", ""),
            "HOME": str(home),
            "XDG_CONFIG_HOME": str(home / "config"),
            "ASCIINEMA_CONFIG_HOME": str(home / "asciinema"),
            "TMPDIR": tmp,
            "SHELL": "/bin/sh",
            "TERM": "xterm-256color",
            "NO_COLOR": "1",
            "PYTHONNOUSERSITE": "1",
            "LANG": "en_US.UTF-8",
            "LC_ALL": "en_US.UTF-8",
        }
        command = shlex.join(
            [sys.executable, "scripts/showcase.py", "--output", "assets/recording"]
        )
        subprocess.run(
            [
                recorder,
                "rec",
                "--overwrite",
                "--cols",
                "110",
                "--rows",
                "42",
                "-t",
                "diffnote / real CLI on synthetic Git history",
                "-c",
                command,
                "assets/recording/showcase.cast",
            ],
            cwd=root,
            env=env,
            check=True,
            timeout=120,
        )


if __name__ == "__main__":
    main()
