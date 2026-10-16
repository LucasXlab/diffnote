# Reddit posts

## r/python
**Title:** I built diffnote: a zero-dependency CLI that turns your git diff into a PR description (offline, no API key)

**Body:**
Hey all — like many of you I procrastinate on PR descriptions, and every
"solution" I found either needed an API key or sent my code to someone's server.
So I made a tiny pure-stdlib CLI.

What it does in one command:
```
$ diffnote
14 files changed  (+842 / -137)
Suggested title: feat: add offline diff summarizer
Risk signals
 • database migration / schema change (2)
 • auth / security related (1)
```
It groups files by area, flags risky changes (migrations, auth, deps, big diffs),
and can write a paste-ready GitHub PR body with `--markdown`. Add `--llm` and it
asks a *local* Ollama model for a prose blurb — no cloud, no key.

`pip install diffnote`, MIT, no deps. Code is ~a few hundred lines and easy to
read. Would love feedback, especially on the heuristics (what risk signals would
*you* want flagged?).

Repo: https://github.com/LucasYanzy/diffnote

## r/git
**Title:** A CLI that reads `git diff` and writes your PR description + risk signals (offline)

Same repo; shorter body focusing on the git integration (`--commits N`,
`--base main`, `--staged`). Mention it works on the working tree, not just
commits, which git-cliff etc. don't do.

## r/programming
**Title:** Offline-first tooling: a diff → PR summary CLI with zero dependencies

Angle: the "local-first / privacy" trend from the research — position diffnote as
part of the "your code stays on your machine" movement. Link repo + comparison
table.
