# X / Twitter thread

**Tweet 1 (hook):**
Every PR description tool wants your API key and ships your code to the cloud.
So I built one that runs fully offline. 🧵

`pip install diffnote` → point it at a repo → get a review-ready PR summary.
No deps. No key. No telemetry.

**Tweet 2 (demo):**
```
$ diffnote
14 files changed  (+842 / -137)
Suggested title: feat: add offline diff summarizer
Risk signals
 • database migration / schema change (2)
 • auth / security related (1)
```
It groups files by area and flags the changes reviewers actually worry about.

**Tweet 3 (the differentiator):**
Unlike git-cliff / conventional-changelog, diffnote explains your *uncommitted
working tree*. And `--llm` asks a **local** Ollama model for a prose summary —
if Ollama isn't running, it just falls back to the offline version.

**Tweet 4 (cta):**
Pure Python stdlib, MIT, ~few hundred lines. Stars / feedback welcome:
https://github.com/LucasYanzy/diffnote

*(Style notes from research: lead with the pain + the "offline/no key" wedge,
show a real terminal snippet, keep it under 280 chars each, no emoji spam.)*
