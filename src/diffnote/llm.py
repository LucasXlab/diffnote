"""Optional local-LLM prose via Ollama. Graceful no-op if unavailable."""

import json
import os
import urllib.request
import urllib.error


def _endpoint():
    return (os.environ.get("DIFFNOTE_OLLAMA") or "http://localhost:11434").rstrip("/")


def _model():
    return os.environ.get("DIFFNOTE_MODEL") or "llama3"


def summarize(diff_text, title, max_chars=6000):
    """Ask a local Ollama model for a one-paragraph PR summary.

    Returns a string, or None if the model is unreachable / disabled.
    """
    if not diff_text.strip():
        return None
    prompt = (
        "You are writing a pull-request description. Given this git diff, "
        "write ONE concise paragraph (max 3 sentences) describing what changed "
        "and why it matters. Be factual, no boilerplate.\n\n"
        f"Suggested title: {title}\n\nDIFF:\n{diff_text[:max_chars]}"
    )
    payload = {"model": _model(), "prompt": prompt, "stream": False}
    try:
        req = urllib.request.Request(
            _endpoint() + "/api/generate",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
        return (data.get("response") or "").strip() or None
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError, KeyError):
        return None
