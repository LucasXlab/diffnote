import json
import subprocess

import pytest

from diffnote import analyze, cli, gitutil, render
from diffnote.parser import ParseError, decode_path


def git(p, *args):
    return subprocess.check_output(["git", *args], cwd=p, text=True)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / "base.txt").write_text("one\ntwo\n")
    git(tmp_path, "add", ".")
    git(tmp_path, "commit", "-qm", "feat: unrelated previous subject")
    return tmp_path


def changes(repo):
    patch, stats, messages, source = gitutil.read_selection(cwd=repo)
    files = analyze.parse_diff(patch)
    gitutil.verify_numstat(files, stats)
    return files, analyze.build_summary(files, messages, source)


@pytest.mark.parametrize(
    "name",
    [
        "空格.py",
        "with space.py",
        "tab\tname",
        "line\nname",
        'double"quote',
        "back\\slash",
        "a b/c",
        "pipe|tick`name",
    ],
)
def test_real_git_paths_and_header_looking_hunks(repo, name):
    p = repo / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("-- old content\nkeep\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "synthetic file")
    p.write_text("++ new content\nkeep\n")
    files, summary = changes(repo)
    assert len(files) == 1 and files[0]["new"] == name
    assert (files[0]["added"], files[0]["deleted"]) == (1, 1)
    assert summary["title_source"] == "diff paths" and "unrelated" not in summary["title"]


def test_metadata_empty_binary_mode_rename_symlink(repo):
    (repo / "delete.bin").write_bytes(b"\0old")
    (repo / "mode.sh").write_text("hello\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "synthetic metadata base")
    (repo / "delete.bin").unlink()
    (repo / "new.bin").write_bytes(b"\0different\0")
    (repo / "empty").touch()
    (repo / "mode.sh").chmod(0o755)
    (repo / "link").symlink_to("base.txt")
    git(repo, "mv", "base.txt", "renamed.txt")
    git(repo, "add", ".")
    files, summary = changes(repo)
    by = {x["new"]: x for x in files}
    assert by["empty"]["is_new"] and by["new.bin"]["is_new"]
    assert by["delete.bin"]["is_deleted"] and by["delete.bin"]["binary"]
    assert by["renamed.txt"]["renamed"] and by["renamed.txt"]["old"] == "base.txt"
    assert by["mode.sh"]["new_mode"] == "100755"
    assert by["link"]["new_mode"] == "120000"
    binary = next(x for x in summary["files"] if x["path"] == "new.bin")
    assert binary["added"] is None and binary["deleted"] is None


def test_deleted_keywords_and_nested_dependency(repo):
    (repo / "logic.py").write_text("encrypt(value)\nDROP TABLE synthetic;\n")
    (repo / "pkg").mkdir()
    (repo / "pkg/package.json").write_text("{}\n")
    git(repo, "add", ".")
    git(repo, "commit", "-qm", "synthetic rules")
    (repo / "logic.py").write_text("pass\n")
    (repo / "pkg/package.json").write_text('{"private":true}\n')
    _, summary = changes(repo)
    evidence = [e for r in summary["risks"] for e in r["evidence"]]
    assert any(x["source"] == "deleted" and x["rule"] == "security-keyword" for x in evidence)
    assert any(x["rule"] == "dependency-basename" for x in evidence)
    assert any(x["source"] == "deleted" and x["rule"] == "schema-keyword" for x in evidence)


@pytest.mark.parametrize(
    "patch",
    [
        "random text",
        "diff --cc file\n",
        "diff --git a/x b/x\n--- a/x\n+++ b/x\n@@ -1,2 +1,2 @@\n-a\n+b\n",
        "diff --git a/x b/x\n--- a/x\n+++ b/x\n@@ broken\n",
        "diff --git a/x b/x\n",
        "diff --git a/x b/x\nnew file mode 100644\nunsupported metadata\n",
    ],
)
def test_incomplete_patch_rejected(patch):
    with pytest.raises(ParseError):
        analyze.parse_diff(patch)


@pytest.mark.parametrize("value", ['"bad\\q"', '"\\777"', '"unterminated'])
def test_bad_path_escape_rejected(value):
    with pytest.raises(ParseError):
        decode_path(value)


def test_controls_and_markdown_do_not_change_json_identity(repo):
    name = "pipe|tick`<tag>\x1b[31m\nname"
    f = {
        "old": name,
        "new": name,
        "new_path": name,
        "is_new": False,
        "is_deleted": False,
        "renamed": False,
        "added": 1,
        "deleted": 0,
        "binary": False,
        "lines": [],
    }
    s = analyze.build_summary([f], ["feat: <script>*unsafe*\x1b[31m"])
    js = json.loads(render.render_json(s))
    assert js["files"][0]["path"] == name
    terminal = render.render_terminal(s, use_color=False)
    assert "\x1b" not in terminal and "\\u001b" in terminal
    markdown = render.render_markdown(s)
    assert "<script>" not in markdown and "<tag>" not in markdown and "&#124;" in markdown
    assert "Tests were not run" in terminal


def test_cli_errors_and_unrelated_title(repo, monkeypatch, capsys):
    monkeypatch.chdir(repo)
    (repo / "README.md").write_text("docs\n")
    git(repo, "add", ".")
    assert cli.main(["--json"]) == 0
    s = json.loads(capsys.readouterr().out)
    assert s["title"] == "docs: update documentation" and s["title_source"] == "diff paths"
    assert cli.main(["--base=--output=marker"]) == 2
    assert not (repo / "marker").exists()
    assert capsys.readouterr().out == ""
    for args in [
        ["--commits", "0"],
        ["--commits", "-1"],
        ["--range", "main..."],
        ["--base", "missing"],
    ]:
        assert cli.main(args) == 2
        assert capsys.readouterr().out == ""
    with pytest.raises(SystemExit):
        cli.main(["--json", "--markdown"])
    with pytest.raises(SystemExit):
        cli.main(["--llm"])


@pytest.mark.parametrize("kind", ["clean", "process"])
def test_configured_clean_filter_is_not_executed(repo, kind):
    marker = repo / "marker"
    script = repo / "filter.sh"
    script.write_text(f'#!/bin/sh\ntouch "{marker}"\ncat\n')
    script.chmod(0o755)
    (repo / ".gitattributes").write_text("base.txt filter=fixture\n")
    git(repo, "config", f"filter.fixture.{kind}", str(script))
    with pytest.raises(gitutil.GitError, match="filters"):
        gitutil.get_diff_text(cwd=repo)
    with pytest.raises(gitutil.GitError, match="filters"):
        gitutil.is_clean(repo)
    assert not marker.exists()


def test_no_color_non_tty(repo, monkeypatch, capsys):
    monkeypatch.chdir(repo)
    (repo / "base.txt").write_text("three\n")
    monkeypatch.setenv("NO_COLOR", "1")
    assert cli.main([]) == 0
    assert "\x1b" not in capsys.readouterr().out


def test_configuration_title_does_not_claim_source_implementation():
    f = {
        "old": ".github/workflows/ci.yml",
        "new": ".github/workflows/ci.yml",
        "is_new": False,
        "is_deleted": False,
        "renamed": False,
        "added": 1,
        "deleted": 1,
        "binary": False,
        "lines": [],
        "removed_lines": [],
    }
    s = analyze.build_summary([f])
    assert s["title"] == "ci: review pipeline configuration"
    f["old"] = f["new"] = "config/settings.toml"
    assert analyze.build_summary([f])["title"] == "chore: review configuration changes"


def test_indexed_submodule_is_rejected_without_child_programs(repo):
    oid = git(repo, "rev-parse", "HEAD").strip()
    git(repo, "update-index", "--add", "--cacheinfo", "160000," + oid + ",child")
    with pytest.raises(gitutil.GitError, match="submodule"):
        gitutil.get_diff_text(cwd=repo)


def test_visible_unicode_bidi_and_orphan_marker():
    assert render.visible("name\u202eevil") == "name\\u202eevil"
    with pytest.raises(ParseError):
        analyze.parse_diff("\\ No newline at end of file\n")
