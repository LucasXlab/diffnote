# Hacker News — Show HN

**Title:**
Show HN: diffnote – turn a git diff into a PR/changelog summary, fully offline

**URL:** https://github.com/LucasYanzy/diffnote

**Text (the submission comment):**
I got tired of staring at a diff and dreading the PR description, and I didn't
want yet another tool that ships my code to a cloud API for "AI summarization."
So I built diffnote: run it in any repo and it prints a review-ready summary —
suggested title, files grouped by area, and risk signals (DB migrations,
auth/security changes, dependency bumps, huge diffs).

Why it might be useful:
- Zero runtime dependencies (pure Python stdlib), `pip install diffnote`, done.
- No API key, no telemetry, your code never leaves the machine.
- It explains your *uncommitted working tree*, not just commits.
- Optional natural-language prose via a **local** Ollama model (`--llm`); if
  Ollama isn't running it silently falls back to the offline summary.

Outputs: terminal (default), `--markdown` (paste-ready PR body), `--json` (CI).
Comparison vs git-cliff / conventional-changelog / cloud PR bots is in the README.

It's small (~a few hundred lines) and MIT. Feedback and contributions welcome.

*(Note: keep the comment factual, no emoji, no hype. Reply to comments within the
first 2 hours; if asked "why not just use X", answer specifically and link the
comparison table.)*
