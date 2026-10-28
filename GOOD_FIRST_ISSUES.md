# Good first issues (prepared for launch)

These are ready to post as GitHub issues on day one. Each is scoped to be
approachable for a new contributor and touches one module.

---

### 1. Support more dependency manifest files
- **Area**: `analyze.py` (`DEP_FILES`)
- **Task**: Add common manifests we miss (e.g. `pdm.lock`, `poetry` groups,
  `npm-shrinkwrap.json`, `Cargo.lock` already covered). Add a unit test in
  `tests/test_analyze.py`.
- **Why**: dependency-change risk signal only fires for known files.

### 2. `--stats` flag: per-area added/deleted totals
- **Area**: `render.py` + `analyze.py`
- **Task**: Add a compact stats block (source +120/-30, tests +40/-0, …) to the
  terminal output behind `--stats`.
- **Why**: quick at-a-glance size of a change set.

### 3. Detect "breaking change" markers
- **Area**: `analyze.py`
- **Task**: If a commit message has `!:` (e.g. `feat!:`) or diff touches public
  API paths (`lib/`, `src/**/api`), add a "possible breaking change" risk.
- **Why**: reviewers care most about breaking changes.

### 4. Color-free fallback auto-detect
- **Area**: `render.py`
- **Task**: When output is not a TTY, default to `--no-color` automatically
  (respect an explicit override).
- **Why**: pasting colored output into files/CI looks noisy.

### 5. `--save <path>` to write markdown to a file
- **Area**: `cli.py`
- **Task**: Add `--save` that writes the `--markdown` output to a file instead of
  stdout, so it can be piped into a PR template.
- **Why**: smoother CI integration for auto-filling PR bodies.
