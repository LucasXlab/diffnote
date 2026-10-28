# Privacy

Runtime analysis is entirely offline. The optional Ollama/LLM path has been removed; no model endpoints or API keys are read. Git override environment variables and global/system Git configuration are excluded. External diff, textconv, fsmonitor and signature display are disabled; configured clean/process filters and partial/promisor repositories and indexed submodules are rejected. This is defensive reading, not a sandbox for a compromised Git executable.

Outputs contain actual file paths, selected commit subjects and review signals. These can be private or identify people. No general anonymization is promised: review all reports, screenshots and package assets before sharing. Terminal/Markdown control characters are displayed visibly; JSON preserves filename identity. Do not upload real private diffs as examples.

The demo uses temporary synthetic files and fictional contributors, never personal repositories or homes. Developer dependencies and hosted CI can access package registries/GitHub. Publishing is a separate action. Keep local logs, private history, environment files and credentials out of distributions. Final publication requires independent review of source, packages, media and all proposed Git history.
