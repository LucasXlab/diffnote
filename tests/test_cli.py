import json
import os
import subprocess
import tempfile

from diffnote import cli


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _make_dirty_repo():
    d = tempfile.mkdtemp()
    _git(d, "init", "-q")
    _git(d, "config", "user.email", "t@e.com")
    _git(d, "config", "user.name", "T")
    with open(os.path.join(d, "main.py"), "w") as fh:
        fh.write("print('hi')\n")
    _git(d, "add", "main.py")
    _git(d, "commit", "-q", "-m", "feat: bootstrap")
    with open(os.path.join(d, "main.py"), "w") as fh:
        fh.write("print('hello')\nprint('world')\n")
    with open(os.path.join(d, "README.md"), "w") as fh:
        fh.write("# hi\n")
    _git(d, "add", ".")
    return d


def test_terminal_output(capsys):
    import os
    d = _make_dirty_repo()
    old = os.getcwd()
    os.chdir(d)
    try:
        rc = cli.main(["--no-color"])
    finally:
        os.chdir(old)
    out = capsys.readouterr().out
    assert rc == 0
    assert "files changed" in out
    assert "Suggested title" in out


def test_json_output(capsys):
    import os
    d = _make_dirty_repo()
    old = os.getcwd()
    os.chdir(d)
    try:
        rc = cli.main(["--json", "--no-color"])
    finally:
        os.chdir(old)
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["total_files"] >= 1
    assert "title" in data


def test_markdown_output(capsys):
    import os
    d = _make_dirty_repo()
    old = os.getcwd()
    os.chdir(d)
    try:
        rc = cli.main(["--markdown"])
    finally:
        os.chdir(old)
    out = capsys.readouterr().out
    assert "## Summary" in out
    assert "## Changes" in out


def test_save_markdown_writes_file_without_stdout(capsys):
    d = _make_dirty_repo()
    output_path = os.path.join(d, "pr-body.md")
    old = os.getcwd()
    os.chdir(d)
    try:
        rc = cli.main(["--save", output_path, "--markdown"])
    finally:
        os.chdir(old)
    captured = capsys.readouterr()
    with open(output_path, encoding="utf-8") as output_file:
        saved = output_file.read()
    assert rc == 0
    assert captured.out == ""
    assert "## Summary" in saved
    assert "## Changes" in saved
    assert saved.endswith("\n")


def test_no_changes(capsys):
    import os
    d = tempfile.mkdtemp()
    _git(d, "init", "-q")
    _git(d, "config", "user.email", "t@e.com")
    _git(d, "config", "user.name", "T")
    old = os.getcwd()
    os.chdir(d)
    try:
        rc = cli.main(["--no-color"])
    finally:
        os.chdir(old)
    assert rc == 0
    assert "no changes" in capsys.readouterr().err.lower()


def _clean_repo():
    import os
    d = tempfile.mkdtemp()
    _git(d, "init", "-q")
    _git(d, "config", "user.email", "t@e.com")
    _git(d, "config", "user.name", "T")
    return d


def test_clean_tree_json_is_valid(capsys):
    import os
    d = _clean_repo()
    old = os.getcwd()
    os.chdir(d)
    try:
        rc = cli.main(["--json", "--no-color"])
    finally:
        os.chdir(old)
    assert rc == 0
    data = json.loads(capsys.readouterr().out)
    assert data["total_files"] == 0


def test_clean_tree_markdown_is_valid(capsys):
    import os
    d = _clean_repo()
    old = os.getcwd()
    os.chdir(d)
    try:
        rc = cli.main(["--markdown"])
    finally:
        os.chdir(old)
    assert rc == 0
    assert "## Summary" in capsys.readouterr().out
