#!/usr/bin/env python3
"""Capture real installed CLI results from disposable, synthetic Git history.

The presentation selects exact stdout lines or labelled JSON fields. Complete
stdout/stderr, raw JSON, fixture inputs, Git facts and command results are saved.
No source fallback, model, network request, test execution or upload is used.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("assets/recording"))
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    commands, panels = [], []
    with tempfile.TemporaryDirectory(prefix="diffnote-showcase-") as tmp:
        work = Path(tmp)
        repo, home = work / "project", work / "home"
        repo.mkdir()
        home.mkdir()
        env = {
            "PATH": os.defpath + os.pathsep + os.environ.get("PATH", ""),
            "HOME": str(home),
            "XDG_CONFIG_HOME": str(home / "config"),
            "TMPDIR": str(work),
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_AUTHOR_NAME": "Synthetic Contributor",
            "GIT_COMMITTER_NAME": "Synthetic Contributor",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
            "GIT_AUTHOR_DATE": "2026-01-01T00:00:00Z",
            "GIT_COMMITTER_DATE": "2026-01-01T00:00:00Z",
            "GIT_CEILING_DIRECTORIES": str(work),
            "NO_COLOR": "1",
            "PYTHONNOUSERSITE": "1",
            "LANG": "en_US.UTF-8",
            "LC_ALL": "en_US.UTF-8",
        }

        def call(name, argv, expected=0):
            proc = subprocess.run(
                argv, cwd=repo, env=env, capture_output=True, timeout=20, check=False
            )
            safe_argv = ["python" if a == sys.executable else str(a) for a in argv]
            for stream, data in [("stdout", proc.stdout), ("stderr", proc.stderr)]:
                (output / f"{name}.{stream}.txt").write_bytes(data)
            commands.append(
                {
                    "name": name,
                    "cwd": "temporary synthetic project",
                    "argv": safe_argv,
                    "exit_code": proc.returncode,
                    "expected_exit_code": expected,
                    "stdout_sha256": sha(proc.stdout),
                    "stderr_sha256": sha(proc.stderr),
                }
            )
            if proc.returncode != expected:
                raise RuntimeError(f"{name}: expected exit {expected}, got {proc.returncode}")
            return proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8")

        def git(name, *argv):
            return call(name, ["git", *argv])[0]

        def write(path, content):
            target = repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content.encode() if isinstance(content, str) else content)

        def capture(name, flags=(), expected=0):
            stdout, stderr = call(name, [sys.executable, "-m", "diffnote", *flags], expected)
            if "--json" in flags and expected == 0:
                data = json.loads(stdout)
                (output / f"{name}.json").write_text(stdout)
                return data
            return stdout if expected == 0 else stderr

        def panel(name, title, command, text, source, selection):
            item = {
                "id": name,
                "title": title,
                "command": command,
                "source": source,
                "selection": selection,
                "text": text.rstrip(),
            }
            panels.append(item)
            print(f"\n=== {title} ===\n$ {command}\n{text.rstrip()}\n", flush=True)

        git("init", "init", "-q", "-b", "main")
        write("src/total.py", "def total(items):\n    return sum(items)\n")
        write("docs/guide.md", "# Synthetic guide\n")
        write("docs/legacy.md", "# Synthetic usage\nRead the patch before sharing a draft.\n")
        write("auth/session.py", "def display(value):\n    return sanitize(value)\n")
        write("data/icon.bin", b"\x00synthetic-image-v1\xff")
        git("initial-add", "add", ".")
        git("initial-commit", "-c", "commit.gpgsign=false", "commit", "-qm", "fixture: initial")
        write("docs/guide.md", "# Synthetic guide\nDocument the actual checks you run.\n")
        git("stage-docs", "add", "docs/guide.md")
        write("src/total.py", "def total(items):\n    return round(sum(items), 2)\n")
        working = capture("working", ["--no-color"])
        working_data = capture("working-json", ["--json"])
        staged = capture("staged", ["--staged", "--no-color"])
        staged_data = capture("staged-json", ["--staged", "--json"])
        assert working_data["total_files"] == 2 and staged_data["total_files"] == 1
        assert staged_data["files"][0]["path"] == "docs/guide.md"
        panel(
            "working",
            "Tracked working tree",
            "diffnote --no-color",
            working,
            "working.stdout.txt",
            "complete stdout",
        )
        panel(
            "staged",
            "Only the staged documentation",
            "diffnote --staged --no-color",
            staged,
            "staged.stdout.txt",
            "complete stdout",
        )

        git("reset-before-metadata", "reset", "--hard", "-q", "HEAD")
        git("rename", "mv", "docs/legacy.md", "docs/usage.md")
        write("data/empty.txt", b"")
        write("data/icon.bin", b"\x00synthetic-image-v2\xfe")
        (repo / "src/total.py").chmod(0o755)
        git("stage-metadata", "add", ".")
        metadata = capture("metadata", ["--staged", "--no-color"])
        facts = capture("metadata-json", ["--staged", "--json"])
        assert any(f["status"] == "renamed" for f in facts["files"])
        assert any(f["binary"] and f["added"] is None for f in facts["files"])
        assert any(f["path"] == "data/empty.txt" and f["added"] == 0 for f in facts["files"])
        git("metadata-numstat", "diff", "--cached", "--numstat", "-z", "-M")
        git("metadata-status", "diff", "--cached", "--name-status", "-z", "-M")
        panel(
            "metadata",
            "Empty, binary, rename and mode facts",
            "diffnote --staged --no-color",
            metadata,
            "metadata.stdout.txt",
            "complete stdout",
        )

        git("reset-before-signals", "reset", "--hard", "-q", "HEAD")
        write("auth/session.py", "def display(value):\n    return value\n")
        write("db/migrations/001_widgets.sql", "ALTER TABLE widgets ADD COLUMN note TEXT;\n")
        git("stage-signals", "add", ".")
        signals = capture("signals", ["--staged", "--no-color"])
        signal_data = capture("signals-json", ["--staged", "--json"])
        capture("signals-markdown", ["--staged", "--markdown"])
        assert any(e["source"] == "deleted" for r in signal_data["risks"] for e in r["evidence"])
        panel(
            "signals",
            "Signals have rule and path evidence",
            "diffnote --staged --no-color",
            signals,
            "signals.stdout.txt",
            "complete stdout",
        )

        # Explicit, labelled JSON field selection; full JSON is preserved unchanged.
        projection = {"source": facts["source"], "files": facts["files"], "limits": facts["limits"]}
        projected = json.dumps(projection, indent=2, ensure_ascii=True)
        (output / "metadata-projection.json").write_text(projected + "\n")
        panel(
            "json",
            "JSON facts for local tooling",
            "diffnote --staged --json  # metadata scenario",
            projected,
            "metadata-json.stdout.txt",
            "JSON projection: source, files, limits",
        )

        git("reset-before-refusal", "reset", "--hard", "-q", "HEAD")
        write("src/total.py", "def total(items):\n    return round(sum(items), 2)\n")
        # The deliberately configured helper would create a marker if ever executed.
        git("configure-filter", "config", "filter.synthetic.clean", "touch FILTER_EXECUTED")
        write(".gitattributes", "*.py filter=synthetic\n")
        refusal = capture("filter-refusal", ["--no-color"], expected=2)
        assert not (repo / "FILTER_EXECUTED").exists()
        (output / "filter-marker.json").write_text(json.dumps({"marker_exists": False}) + "\n")
        panel(
            "refusal",
            "Configured Git filters are rejected",
            "diffnote --no-color",
            refusal + "Expected exit: 2. Helper marker absent.\n",
            "filter-refusal.stderr.txt",
            "complete stderr plus labelled wrapper check",
        )

        (output / "commands.json").write_text(json.dumps(commands, indent=2) + "\n")
        (output / "panels.json").write_text(json.dumps(panels, indent=2, ensure_ascii=True) + "\n")
        sources = {
            "fixture": "Entirely synthetic Git history; no downloaded code or public PR patch.",
            "interpreter": f"Python {sys.version_info.major}.{sys.version_info.minor}",
            "path_normalization": "Only Python argv[0] is labelled python in commands.json; output is unchanged.",
            "core_sha256": {
                p.name: sha(p.read_bytes())
                for p in sorted(Path(__import__("diffnote").__file__).parent.glob("*.py"))
            },
            "tests": "No fixture code or tests are executed; assertions only check demo outcomes.",
            "recording": "Local asciinema capture; no upload. Media selects labelled panels with added reading pauses.",
        }
        (output / "provenance.json").write_text(json.dumps(sources, indent=2) + "\n")


if __name__ == "__main__":
    main()
