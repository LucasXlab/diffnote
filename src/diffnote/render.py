"""Context-safe renderers. JSON preserves paths; terminal controls are visible."""

import html
import json
import re
import unicodedata

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[36m"
DIM = "\033[2m"


def visible(text):
    return "".join(
        f"\\u{ord(c):04x}"
        if ord(c) < 32
        or 127 <= ord(c) < 160
        or 0xD800 <= ord(c) <= 0xDFFF
        or unicodedata.category(c) in {"Cf", "Zl", "Zp"}
        else c
        for c in str(text)
    )


def md(text):
    value = html.escape(visible(text), quote=False)
    return re.sub(r"([\\`*_{}\[\]()|#!])", r"\\\1", value)


def code(text):
    return "<code>" + html.escape(visible(text), quote=False).replace("|", "&#124;") + "</code>"


def _c(text, code_, color):
    return f"{code_}{text}{RESET}" if color else text


def render_terminal(summary, use_color=True):
    out = [
        _c("diffnote — reviewable PR draft", BOLD + CYAN, use_color),
        "─" * 52,
        f"  {summary['total_files']} files changed (+{summary['added']} / -{summary['deleted']} text lines)",
        "  Suggested title: " + visible(summary["title"]),
        "  Title source: " + visible(summary.get("title_source", "diff paths")),
        "  Change source: " + visible(summary.get("source", "provided diff")),
        "  Changelog section: " + visible(summary["section"]),
    ]
    if summary["risks"]:
        out += ["", "  Review signals (heuristics, not safety findings)"]
        for risk in summary["risks"]:
            out.append("   • " + visible(risk["label"]))
            for e in risk.get("evidence", []):
                out.append(
                    "       "
                    + visible(e["path"])
                    + " ["
                    + visible(e["rule"])
                    + "; "
                    + visible(e["source"])
                    + "]"
                )
    out += ["", "  Changes by area"]
    for area, count in sorted(summary["areas"].items(), key=lambda x: (-x[1], x[0])):
        out.append(f"   {area:<10} {count}")
    out += ["", "  Highlights"]
    for h in summary["highlights"]:
        mode = ""
        if h.get("old_mode") != h.get("new_mode"):
            mode = f" mode {h.get('old_mode') or '—'} → {h.get('new_mode') or '—'}"
        counts = (
            "binary; line counts unavailable"
            if h.get("binary")
            else f"+{h['added']} -{h['deleted']}"
        )
        old = (
            visible(h.get("old_path") or "") + " → " if h["status"] in ("renamed", "copied") else ""
        )
        out.append(f"   • {old}{visible(h['path'])} [{h['status']}] {counts}{mode}")
    if len(summary["highlights"]) < summary["total_files"]:
        out.append("   More files are available in JSON files[].")
    out += [
        "─" * 52,
        _c("  Offline heuristic draft. Tests were not run; review before sharing.", DIM, use_color),
    ]
    return "\n".join(out)


def render_markdown(summary):
    out = [
        "## Summary",
        "",
        f"- **{md(summary['title'])}**",
        "- Title source: " + md(summary.get("title_source", "diff paths")),
        "- Change source: " + md(summary.get("source", "provided diff")),
        f"- Changelog section: {code(summary['section'])}",
        f"- {summary['total_files']} files changed (+{summary['added']} / -{summary['deleted']} text lines)",
        "",
        "## Changes",
        "",
        "| File | Status | + | - | Area / metadata |",
        "|---|---|---:|---:|---|",
    ]
    for h in summary["highlights"]:
        path = code(h["path"])
        if h["status"] in ("renamed", "copied"):
            path = code(h.get("old_path") or "") + " → " + path
        meta = md(h["area"])
        if h.get("old_mode") != h.get("new_mode"):
            meta += f"; mode {h.get('old_mode') or '—'} → {h.get('new_mode') or '—'}"
        plus, minus = ("n/a", "n/a") if h.get("binary") else (h["added"], h["deleted"])
        if h.get("binary"):
            meta += "; binary"
        out.append(f"| {path} | {md(h['status'])} | {plus} | {minus} | {meta} |")
    if len(summary["highlights"]) < summary["total_files"]:
        out.append(
            f"| … {summary['total_files'] - len(summary['highlights'])} more in JSON files[] | | | | |"
        )
    if summary["risks"]:
        out += ["", "## Risk signals", ""]
        for risk in summary["risks"]:
            out.append("- " + md(risk["label"]))
            for e in risk.get("evidence", []):
                out.append(
                    "  - " + code(e["path"]) + " — " + md(e["rule"] + " (" + e["source"] + ")")
                )
    out += [
        "",
        "## Review checklist",
        "",
        "- [ ] Verify the title and intended behavior.",
        "- [ ] Run the relevant tests; diffnote did not run them.",
        "- [ ] Review omitted semantics, binary content, and possible sensitive paths.",
        "",
        "_Generated offline by diffnote. Heuristic draft; no safety or semantic correctness guarantee._",
    ]
    return "\n".join(out)


def render_json(summary):
    # ASCII escaping handles arbitrary Git filename bytes represented by surrogates.
    return json.dumps(summary, indent=2, ensure_ascii=True, allow_nan=False)
