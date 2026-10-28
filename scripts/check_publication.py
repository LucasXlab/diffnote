#!/usr/bin/env python3
"""Dependency-free checks for the committed repository presentation.

This catches common publication mistakes, not every possible private datum.
History identities and package archives are audited separately before release.
"""

import re
import struct
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDES = {
    "README.md": "docs/guide.md",
    "README.zh-CN.md": "docs/guide.zh-CN.md",
}
REQUIRED = [
    "README.md",
    "README.zh-CN.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "PRIVACY.md",
    "SECURITY.md",
    "assets/logo.svg",
    "assets/demo.png",
    "assets/demo.gif",
    "assets/social-preview.png",
    "assets/feature-staged.png",
    "assets/feature-metadata.png",
    "assets/feature-signals.png",
    "assets/feature-json.png",
    "assets/feature-refusal.png",
    "assets/recording/showcase.cast",
    "assets/recording/showcase.txt",
    "assets/recording/commands.json",
    "assets/recording/panels.json",
    "assets/recording/render-manifest.json",
    "docs/showcase.md",
    "LAUNCH.md",
    "demo/terminal.txt",
    "scripts/demo.py",
    "scripts/showcase.py",
    "scripts/record_showcase.py",
    "scripts/render_assets.py",
    ".github/workflows/ci.yml",
    *GUIDES.values(),
]
errors = []
if (ROOT / "launch").exists() or (ROOT / "demo.gif").exists():
    errors.append("obsolete launch directory or duplicate root GIF remains")
badges = sorted((ROOT / "assets/badges").glob("*.svg"))
if len(badges) != 5:
    errors.append("exactly five local metadata/configuration badges required")
for name in REQUIRED:
    if not (ROOT / name).is_file() or (ROOT / name).stat().st_size == 0:
        errors.append(name + ": required file missing or empty")
for name, guide_name in GUIDES.items():
    if not (ROOT / name).exists():
        continue
    text = (ROOT / name).read_text()
    local_links = []
    for target in re.findall(r'\]\(([^)]+)\)|(?:src|href)="([^"]+)"', text):
        link = next((v for v in target if v), "").split("#", 1)[0].split("?", 1)[0]
        if not link or re.match(r"[a-z]+://|mailto:", link):
            continue
        local_links.append(link)
        if not (ROOT / link).exists():
            errors.append(name + ": broken local link " + link)
    if guide_name not in local_links:
        errors.append(name + ": missing link to " + guide_name)
    guide = ROOT / guide_name
    if guide.is_file():
        diagrams = re.findall(r"^```mermaid\s*\n([\s\S]*?)^```\s*$", guide.read_text(), re.M)
        if not any(
            re.match(r"\s*(?:flowchart|graph)\s+(?:TD|TB|LR|RL|BT)\b", diagram) and "-->" in diagram
            for diagram in diagrams
        ):
            errors.append(guide_name + ": missing Mermaid architecture flowchart")
paths = (
    subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "-co", "--exclude-standard", "-z"])
    .decode()
    .split("\0")
)
for rel in set(paths):
    f = ROOT / rel
    if not rel or not f.is_file():
        continue
    try:
        text = f.read_text()
    except (UnicodeError, OSError):
        continue
    # Match complete home directories, not generic /path/to/project examples.
    for label, pattern in [
        ("personal absolute path", r"/" + r'Users/[^/\s"\x27]+|[A-Za-z]:\\Users\\[^\\\s]+'),
        ("personal email", r"[\w.+-]+@(?:outlook|gmail|hotmail|yahoo|qq|163)\.[A-Za-z]+"),
        (
            "placeholder repository",
            r'github\.com/(?:your[-_]?(?:org|user|name)|diffblast/diffblast|httpeek/httpeek)(?:[/\s"\x27]|$)',
        ),
    ]:
        for i, line in enumerate(text.splitlines(), 1):
            if re.search(pattern, line):
                errors.append(rel + ":" + str(i) + ": " + label)
    if f.name in {".env", ".env.local", "cookies.json", "history.jsonl"}:
        # Deliberately synthetic scanner fixtures are kept out of distributed packages.
        if not rel.startswith(("test/fixtures/", "demo/fixtures/")):
            errors.append(rel + ": local state must not be published")
card = ROOT / "assets/social-preview.png"
if card.exists():
    data = card.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or struct.unpack(">II", data[16:24]) != (1280, 640):
        errors.append("social preview must be 1280x640 PNG")
if errors:
    print("\n".join(errors))
    sys.exit(1)
print(
    "Publication checks passed: required files, README links, preview size and common personal-data patterns."
)
