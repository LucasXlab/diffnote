# Privacy

Default operation reads local Git data without network requests. `--llm` sends up to 6,000 diff characters and a suggested title to `DIFFNOTE_OLLAMA` (default `http://localhost:11434`). A remote setting sends that data off the machine. Reports can contain filenames and diff details.

## Demonstrations

Committed demos use synthetic inputs and fictional contributors. No personal repository, request history, cookie jar or agent home is used to generate them. Temporary absolute demo paths are normalized in exported output.

## Before sharing

Review reports, screenshots, request collections and logs for file paths, names, credentials and source content. Local processing does not make every output safe to publish. Submit minimal synthetic reproductions instead of real private data.

## Development and distribution

Dependency installation and hosted CI can contact package registries and GitHub. Publishing a repository or package is separate from running the tool locally. Do not include local reports, environment files, cookies or credentials in distributions.
