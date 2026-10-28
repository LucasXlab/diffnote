# Contributing

Use Python3.11+ and Git2.31+ on macOS/Linux. In a source checkout run `make dev`, then `make check` and `make demo`. The checks cover formatting, lint, tests with whole-package statement coverage, sdist/wheel builds and a fresh installed-wheel smoke outside the source tree. Use `make format` when editing.

Keep the finite heuristic limits explicit. A changed test file does not prove tests passed, and a review signal does not prove a vulnerability. Use real Git output or clearly valid unified patches for parser tests; reject unsupported/incomplete input rather than inventing facts. Preserve machine-readable path identity and test special filenames and metadata-only changes.

Use synthetic data and project-scoped contributor identities. Do not attach personal configuration, private source, credentials, source history or raw private reports to public issues. Keep runtime help, metadata and both README languages aligned. Regenerate the real installed-CLI transcript with `python scripts/demo.py` when output changes; final screenshot/GIF creation is a separate documented step.
