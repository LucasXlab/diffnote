import textwrap
from diffnote import analyze

SAMPLE = textwrap.dedent(
    """
    diff --git a/src/foo.py b/src/foo.py
    index 111..222 100644
    --- a/src/foo.py
    +++ b/src/foo.py
    @@ -1,3 +1,4 @@
     def f():
    -    return 1
    +    return 2
    +    # tweak
    diff --git a/migrations/0001.sql b/migrations/0001.sql
    new file mode 100644
    --- /dev/null
    +++ b/migrations/0001.sql
    @@ -0,0 +1,2 @@
    +CREATE TABLE users (id int);
    +ALTER TABLE users ADD COLUMN name text;
    diff --git a/tests/test_foo.py b/tests/test_foo.py
    index 333..444 100644
    --- a/tests/test_foo.py
    +++ b/tests/test_foo.py
    @@ -1 +1,2 @@
    +def test_foo(): pass
    diff --git a/old_name.py b/new_name.py
    similarity index 90%
    --- a/old_name.py
    +++ b/new_name.py
    @@ -1 +1 @@
    -x = 1
    +x = 2
    """
).strip()


def test_parse_diff_counts():
    files = analyze.parse_diff(SAMPLE)
    assert len(files) == 4
    by_path = {f["new"]: f for f in files}
    assert by_path["src/foo.py"]["added"] == 2
    assert by_path["src/foo.py"]["deleted"] == 1
    assert by_path["migrations/0001.sql"]["is_new"] is True
    assert by_path["new_name.py"]["renamed"] is True


def test_summary_groups_and_risks():
    files = analyze.parse_diff(SAMPLE)
    s = analyze.build_summary(files)
    assert s["total_files"] == 4
    assert "migration" in s["areas"] or "source" in s["areas"]
    labels = [r["label"] for r in s["risks"]]
    assert any("database migration" in l for l in labels)
    assert any("auth" in l or "security" in l for l in labels) is False


def test_suggest_title_from_conventional_commit():
    files = analyze.parse_diff(SAMPLE)
    s = analyze.build_summary(files, commit_messages=["feat: add user table"])
    assert s["title"] == "feat: add user table"
    assert s["section"] == "feat"


def test_suggest_title_derives_migration():
    files = analyze.parse_diff(SAMPLE)
    s = analyze.build_summary(files, commit_messages=[])
    assert "schema" in s["title"] or s["title"].startswith("feat")
