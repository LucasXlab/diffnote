# Contributing to diffnote

Thanks for your interest! diffnote is intentionally small and dependency-free so
it stays easy to hack on.

## Dev setup (one command)
```bash
git clone https://github.com/LucasYanzy/diffnote
cd diffnote
pip install -e ".[test]"
```

## Running tests
```bash
pytest
```

## Project layout
- `src/diffnote/gitutil.py` — git subprocess wrappers
- `src/diffnote/analyze.py` — diff parsing + heuristics (grouping, risk, titles)
- `src/diffnote/llm.py` — optional Ollama integration (graceful no-op)
- `src/diffnote/render.py` — terminal / markdown / json output
- `src/diffnote/cli.py` — argparse entry point

## Guidelines
- Keep **zero runtime dependencies**. stdlib only. (Tests may use pytest.)
- New heuristics go in `analyze.py`; keep them offline and fast.
- Add/extend a unit test for any behavior change. See `tests/`.
- Run `pytest` before opening a PR.
- New contributors: look for issues labeled **good first issue**.

## Commit style
We read conventional-commit prefixes (`feat:`, `fix:`, `chore:`, …) — diffnote
actually uses them to suggest your PR title, so lead by example.
