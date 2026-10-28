"""Strict parser for ordinary Git unified patches (not mail or combined diffs)."""

import re

HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@(?:.*)$")


class ParseError(ValueError):
    """The input cannot support a complete summary."""


def decode_path(value):
    if not value.startswith('"'):
        return value
    if len(value) < 2 or not value.endswith('"'):
        raise ParseError("unterminated quoted Git path")
    data = bytearray()
    i = 1
    escapes = {"a": 7, "b": 8, "t": 9, "n": 10, "v": 11, "f": 12, "r": 13, '"': 34, "\\": 92}
    while i < len(value) - 1:
        char = value[i]
        i += 1
        if char != "\\":
            data.extend(char.encode("utf-8", "surrogateescape"))
            continue
        if i >= len(value) - 1:
            raise ParseError("invalid path escape")
        if value[i] in "01234567":
            m = re.match(r"[0-7]{1,3}", value[i:])
            number = int(m[0], 8)
            if number > 255:
                raise ParseError("invalid path byte")
            data.append(number)
            i += len(m[0])
        else:
            if value[i] not in escapes:
                raise ParseError("unsupported path escape")
            data.append(escapes[value[i]])
            i += 1
    return data.decode("utf-8", "surrogateescape")


def _header_pair(line):
    value = line[len("diff --git ") :]
    if value.startswith('"'):
        m = re.match(r'("(?:[^"\\]|\\.)*") (.*)$', value)
        if not m:
            raise ParseError("invalid file header")
        left, right = decode_path(m[1]), decode_path(m[2])
    else:
        candidates = []
        for m in re.finditer(r" b/", value):
            a, b = value[: m.start()], value[m.start() + 1 :]
            candidates.append((a, b))
        if not candidates:  # unquoted old path and quoted new path
            at = value.find(' "b/')
            if at < 0:
                raise ParseError("unsupported file header")
            left, right = value[:at], decode_path(value[at + 1 :])
        else:
            left, right = next(((a, b) for a, b in candidates if a[2:] == b[2:]), candidates[0])
    if not left.startswith("a/") or not right.startswith("b/"):
        raise ParseError("unsupported file prefix")
    return left[2:], right[2:]


def _file_path(value):
    # Git adds a tab delimiter to unquoted paths containing spaces. Literal tabs are quoted.
    if not value.startswith('"'):
        value = value.split("\t", 1)[0]
    value = decode_path(value)
    if value == "/dev/null":
        return None
    if not value.startswith(("a/", "b/")):
        raise ParseError("unsupported source path prefix")
    return value[2:]


def parse_diff(text):
    if len(text.encode("utf-8", "surrogateescape")) > 8 * 1024 * 1024:
        raise ParseError("patch exceeds the 8 MiB analysis limit")
    files = []
    cur = None
    old_left = new_left = 0
    saw_change = False

    def finish():
        if old_left or new_left:
            raise ParseError("truncated hunk")
        if cur is not None:
            if not saw_change:
                raise ParseError("file has no supported change metadata")
            new_path = cur["new"]
            cur["new_path"] = new_path
            cur["is_new"] = cur["old"] is None
            cur["is_deleted"] = new_path is None
            cur["renamed"] = (
                cur["old"] is not None
                and new_path is not None
                and cur["old"] != new_path
                and not cur["copied"]
            )
            cur["new"] = new_path if new_path is not None else cur["old"]
            if not cur["new"]:
                raise ParseError("empty file identity")
            files.append(cur)

    for line in text.split("\n"):
        if line.startswith("diff --git "):
            finish()
            old, new = _header_pair(line)
            cur = {
                "old": old,
                "new": new,
                "added": 0,
                "deleted": 0,
                "binary": False,
                "lines": [],
                "removed_lines": [],
                "old_mode": None,
                "new_mode": None,
                "copied": False,
            }
            saw_change = False
            continue
        if old_left or new_left:
            if line.startswith("\\ No newline at end of file"):
                continue
            if not line:
                raise ParseError("truncated or invalid hunk line")
            char, content = line[0], line[1:]
            if char == " ":
                old_left -= 1
                new_left -= 1
            elif char == "+":
                new_left -= 1
                cur["added"] += 1
                cur["lines"].append(content)
            elif char == "-":
                old_left -= 1
                cur["deleted"] += 1
                cur["removed_lines"].append(content)
            else:
                raise ParseError("unsupported hunk line")
            if old_left < 0 or new_left < 0:
                raise ParseError("hunk line count mismatch")
            continue
        if not line:
            continue
        if line.startswith("\\ No newline at end of file"):
            if cur is None:
                raise ParseError("newline marker without file metadata")
            continue
        if cur is None:
            raise ParseError("expected an ordinary Git unified diff")
        if line.startswith("@@"):
            m = HUNK.fullmatch(line)
            if not m:
                raise ParseError("unsupported hunk header")
            old_left = int(m[2]) if m[2] is not None else 1
            new_left = int(m[4]) if m[4] is not None else 1
            saw_change = True
            continue
        if line.startswith("--- "):
            cur["old"] = _file_path(line[4:])
            continue
        if line.startswith("+++ "):
            cur["new"] = _file_path(line[4:])
            continue
        if line.startswith("new file mode "):
            cur["old"] = None
            cur["new_mode"] = line[14:]
            saw_change = True
            continue
        if line.startswith("deleted file mode "):
            cur["new"] = None
            cur["old_mode"] = line[18:]
            saw_change = True
            continue
        if line.startswith("old mode "):
            cur["old_mode"] = line[9:]
            saw_change = True
            continue
        if line.startswith("new mode "):
            cur["new_mode"] = line[9:]
            saw_change = True
            continue
        if line.startswith(("rename from ", "copy from ")):
            cur["old"] = decode_path(line.split(" from ", 1)[1])
            cur["copied"] = line.startswith("copy")
            saw_change = True
            continue
        if line.startswith(("rename to ", "copy to ")):
            cur["new"] = decode_path(line.split(" to ", 1)[1])
            saw_change = True
            continue
        if line.startswith(("Binary files ", "GIT binary patch")):
            cur["binary"] = True
            saw_change = True
            continue
        if line.startswith("index "):
            mode = re.fullmatch(r"index [0-9a-f]+\.\.[0-9a-f]+ (\d{6})", line)
            if mode:
                if cur["old"] is not None and cur["old_mode"] is None:
                    cur["old_mode"] = mode[1]
                if cur["new"] is not None and cur["new_mode"] is None:
                    cur["new_mode"] = mode[1]
            continue
        if line.startswith(("similarity index ", "dissimilarity index ")):
            continue
        if cur["binary"]:
            continue  # opaque binary payload, never text line counts
        raise ParseError("unsupported patch metadata; analysis incomplete")
    finish()
    return files
