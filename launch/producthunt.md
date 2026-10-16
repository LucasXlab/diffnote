# Product Hunt

**Tagline:**
Turn any git diff into a review-ready PR description — offline, no API key.

**Description (first comment / "what it does"):**
diffnote is a tiny CLI that reads your git changes and writes a clean PR /
changelog summary in seconds. It suggests a title and changelog section, groups
files by area (source / tests / docs / config / migration / ci), and raises risk
signals for database migrations, auth/security edits, dependency bumps, and
large diffs.

Why it's different:
- 🔌 Zero runtime dependencies — `pip install diffnote`, done.
- 🔒 Fully offline & private — your code never leaves your machine.
- 🧭 Explains your *uncommitted working tree*, not just commits.
- 🤖 Optional local-LLM prose via Ollama (`--llm`), graceful fallback.

Outputs: terminal, markdown (paste-ready PR body), and JSON for CI.

**Maker comment:**
Built it because I kept putting off PR descriptions and didn't want a cloud tool
touching my code. Open source (MIT), ~few hundred lines, easy to extend. Happy to
answer questions!

*(PH style: short sentences, benefit-led, one clear differentiator up top.)*
