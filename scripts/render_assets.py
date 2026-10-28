#!/usr/bin/env python3
"""Render exact local CLI panels. No Git, network, recorder, or invented output."""

import hashlib
import html
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
RECORDING = ASSETS / "recording"
ACCENT, INK, MUTED = "#BAADFF", "#E9EDF5", "#97A8BF"
BACKGROUND, SURFACE, LINE = "#0B1019", "#131D2C", "#304056"
WIDTH, HEIGHT = 1440, 1080


def font(size, mono=False):
    choices = (
        ["/System/Library/Fonts/Menlo.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
        if mono
        else [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    )
    for path in choices:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    raise SystemExit("Install Menlo/Arial or DejaVu fonts before rendering.")


def terminal(panel, rows, page=1, pages=1):
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.text((52, 32), "diffnote", font=font(32), fill=INK)
    draw.text((52, 86), panel["title"], font=font(26), fill=ACCENT)
    draw.rounded_rectangle((32, 148, WIDTH - 32, HEIGHT - 104), 20, SURFACE, LINE, 2)
    for i, color in enumerate(["#F38581", "#EDC27A", "#7BC9A8"]):
        draw.ellipse((58 + i * 25, 173, 71 + i * 25, 186), fill=color)
    draw.text(
        (164, 168), "REAL INSTALLED CLI / SYNTHETIC GIT DATA", font=font(16, True), fill=MUTED
    )
    draw.text((58, 215), "$ " + panel["command"], font=font(22, True), fill="#8AD9B2")
    draw.line((58, 258, WIDTH - 58, 258), fill=LINE, width=1)
    y = 280
    for line in rows:
        color = ACCENT if any(x in line for x in ["Title source:", "Change source:"]) else INK
        if "heuristic" in line.lower() or "Tests were not run" in line:
            color = "#EDC27A"
        draw.text((58, y), line, font=font(22, True), fill=color)
        y += 25
    draw.text((52, HEIGHT - 78), panel["selection"], font=font(16), fill=MUTED)
    draw.text(
        (52, HEIGHT - 47),
        "Reading hold added. Full output and source commands in assets/recording/.",
        font=font(16),
        fill=MUTED,
    )
    draw.text((WIDTH - 132, HEIGHT - 62), f"{page:02}/{pages:02}", font=font(18, True), fill=ACCENT)
    return image


def badge(name, label, value, color):
    left, right = 10 + len(label) * 7, 10 + len(value) * 7
    width = left + right
    title = html.escape(label + ": " + value)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="24" role="img" aria-label="{title}"><title>{title}</title><rect width="{width}" height="24" rx="5" fill="#243247"/><path d="M{left} 0h{right - 5}q5 0 5 5v14q0 5-5 5h-{right - 5}z" fill="{color}"/><g fill="#F4F6FA" font-family="DejaVu Sans,Verdana,sans-serif" font-size="11" text-anchor="middle"><text x="{left / 2}" y="16">{html.escape(label)}</text><text x="{left + right / 2}" y="16">{html.escape(value)}</text></g></svg>\n'''
    (ASSETS / "badges" / f"{name}.svg").write_text(svg)


def main():
    panels = json.loads((RECORDING / "panels.json").read_text())
    cast_bytes = (RECORDING / "showcase.cast").read_bytes()
    cast = [json.loads(line) for line in cast_bytes.decode().splitlines()]
    transcript = "".join(event[2] for event in cast[1:] if event[1] == "o").replace("\r\n", "\n")
    (RECORDING / "showcase.txt").write_text(transcript.rstrip("\n") + "\n")
    for panel in panels:
        raw = (RECORDING / panel["source"]).read_text()
        if panel["id"] == "json":
            data = json.loads(raw)
            expected = json.dumps(
                {key: data[key] for key in ("source", "files", "limits")}, indent=2
            )
        elif panel["id"] == "refusal":
            assert not json.loads((RECORDING / "filter-marker.json").read_text())["marker_exists"]
            expected = raw + "Expected exit: 2. Helper marker absent.\n"
        else:
            expected = raw
        assert panel["text"] == expected.rstrip(), panel["id"]
        assert panel["text"] in transcript, panel["id"]
    media, frames, holds = [], [], []
    for panel in panels:
        rows = []
        for line in panel["text"].splitlines():
            rows.extend(
                textwrap.wrap(line, 94, replace_whitespace=False, drop_whitespace=False) or [""]
            )
        pages = [rows[i : i + 27] for i in range(0, len(rows), 27)]
        for number, page in enumerate(pages, 1):
            labelled = dict(panel)
            labelled["selection"] += f" / page {number} of {len(pages)}"
            frame = terminal(labelled, page, number, len(pages))
            frames.append(frame)
            holds.append(10000 if panel["id"] in {"signals", "json"} else 8000)
            if number == 1:
                filename = "demo.png" if panel["id"] == "working" else f"feature-{panel['id']}.png"
                frame.save(ASSETS / filename)
                media.append(
                    {
                        "path": "assets/" + filename,
                        "panel": panel["id"],
                        "page": 1,
                        "pages": len(pages),
                    }
                )
    frames[0].save(
        ASSETS / "demo.gif",
        save_all=True,
        append_images=frames[1:],
        duration=holds,
        loop=0,
        optimize=True,
    )
    (ASSETS / "logo.svg").write_text(
        """<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128" role="img" aria-label="diffnote: changes on a draft"><title>diffnote</title><rect width="128" height="128" rx="28" fill="#131D2C"/><path d="M43 22h35l19 19v65H43z" fill="#1D2B40" stroke="#BAADFF" stroke-width="4" stroke-linejoin="round"/><path d="M78 22v22h19M57 60h24M57 74h24M57 88h16" fill="none" stroke="#BAADFF" stroke-width="4" stroke-linecap="round"/><path d="M20 48h17M28.5 39.5v17" stroke="#8AD9B2" stroke-width="4" stroke-linecap="round"/><path d="M20 82h17" stroke="#F38581" stroke-width="4" stroke-linecap="round"/></svg>\n"""
    )
    (ASSETS / "badges").mkdir(exist_ok=True)
    for args in [
        ("source", "source", "0.1.0", "#65549C"),
        ("python", "Python", "3.11+", "#376486"),
        ("license", "license", "MIT", "#42695E"),
        ("ci", "CI", "prepared", "#685B3F"),
        ("stars", "Stars", "pending", "#535C70"),
    ]:
        badge(*args)
    image = Image.new("RGB", (1280, 640), BACKGROUND)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 10, 640), fill=ACCENT)
    draw.text((54, 52), "LOCAL GIT / REVIEWABLE DRAFTS", font=font(17, True), fill=ACCENT)
    draw.text((50, 130), "diffnote", font=font(76), fill=INK)
    draw.text((54, 244), "Start with the facts.", font=font(37), fill=INK)
    draw.text((54, 299), "Write the intent.", font=font(37), fill=ACCENT)
    draw.text((54, 419), "Paths. Counts. Evidence.", font=font(24), fill=MUTED)
    draw.text((54, 467), "Offline · No model or API key", font=font(21), fill=MUTED)
    draw.text((54, 561), "Source 0.1.0 / MIT", font=font(18, True), fill=MUTED)
    draw.rounded_rectangle((646, 54, 1230, 585), 22, SURFACE, LINE, 2)
    draw.text((673, 79), "ACTUAL CLI / SYNTHETIC INPUT", font=font(16, True), fill=ACCENT)
    rows = panels[0]["text"].splitlines()
    selection = rows[2:8] + [""] + rows[13:15] + [""] + rows[-1:]
    y = 135
    for line in selection:
        for part in textwrap.wrap(line, 43, replace_whitespace=False, drop_whitespace=False) or [
            ""
        ]:
            draw.text(
                (673, y),
                part,
                font=font(17, True),
                fill=INK if "Tests were not run" not in part else "#EDC27A",
            )
            y += 27
    draw.text((673, 548), "Excerpt; full output in recording/", font=font(15), fill=MUTED)
    image.save(ASSETS / "social-preview.png")
    manifest = {
        "cast_sha256": hashlib.sha256(cast_bytes).hexdigest(),
        "cast_duration_seconds": cast[-1][0],
        "cast_output_events": len(cast) - 1,
        "transcript_normalization": "CRLF to LF; final blank lines reduced to one final newline. Original cast unchanged.",
        "media": media,
        "gif_frames": len(frames),
        "gif_holds_ms": holds,
        "styling": "Native Pillow rendering; exact panels, wrapping, JSON pagination, static reading holds; no simulated typing or changed output.",
        "social_excerpt": "working.stdout.txt lines 3-8, 14-15, final disclaimer; wrapped without changing words",
    }
    (RECORDING / "render-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        "Rendered six real CLI PNGs, reading-hold GIF, native SVG logo, five badges and 1280x640 social card."
    )


if __name__ == "__main__":
    main()
