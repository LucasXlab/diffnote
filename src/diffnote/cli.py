"""diffnote CLI entry point."""

import argparse
import sys

from . import __version__
from . import analyze
from . import gitutil
from . import llm
from . import render


def build_parser():
    p = argparse.ArgumentParser(
        prog="diffnote",
        description="Offline-first git diff → PR / changelog summary in one command.",
    )
    p.add_argument("--version", action="version", version=f"diffnote {__version__}")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--commits", type=int, metavar="N",
                     help="Summarize the last N commits (git diff HEAD~N HEAD).")
    src.add_argument("--base", metavar="REF",
                     help="Compare your work (incl. uncommitted changes) vs a base ref.")
    src.add_argument("--range", metavar="A..B",
                     help="Committed-only comparison, e.g. main..HEAD.")
    src.add_argument("--staged", action="store_true",
                     help="Summarize staged changes only.")
    fmt = p.add_argument_group("output")
    fmt.add_argument("--markdown", action="store_true",
                     help="Print a GitHub PR-body markdown.")
    fmt.add_argument("--save", metavar="PATH",
                     help="Write markdown output to PATH instead of stdout (requires --markdown).")
    fmt.add_argument("--json", action="store_true",
                     help="Print machine-readable JSON.")
    fmt.add_argument("--no-color", action="store_true",
                     help="Disable ANSI colors.")
    fmt.add_argument("--llm", action="store_true",
                     help="Enhance with a local Ollama model (needs Ollama running).")
    return p


def get_diff(args, cwd):
    if args.commits:
        return gitutil.get_range_diff(f"HEAD~{args.commits}", "HEAD", cwd=cwd)
    if args.range:
        a, _, b = args.range.partition("..")
        return gitutil.get_range_diff(a, b or "HEAD", cwd=cwd)
    if args.base:
        # Working tree (incl. uncommitted) vs base = everything a PR would contain.
        # Use --range for committed-only comparisons.
        return gitutil.get_diff_text(args.base, cwd=cwd)
    return gitutil.get_diff_text("HEAD", cwd=cwd, staged=args.staged)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.save and (not args.markdown or args.json):
        parser.error("--save requires --markdown and cannot be used with --json")
    try:
        cwd = gitutil.repo_root()
    except gitutil.GitError as exc:
        print(f"diffnote: {exc}", file=sys.stderr)
        return 1

    diff_text = get_diff(args, cwd)
    # Machine-readable modes always emit valid output so CI pipelines don't break
    # on a clean tree; only the human terminal mode short-circuits.
    machine = args.json or args.markdown
    if not diff_text.strip() and not machine:
        print("diffnote: no changes detected (working tree clean).", file=sys.stderr)
        return 0

    files = analyze.parse_diff(diff_text)
    if not files and not machine:
        print("diffnote: no file changes parsed.", file=sys.stderr)
        return 0

    commit_messages = gitutil.get_commit_messages(cwd=cwd)
    summary = analyze.build_summary(files, commit_messages)

    llm_prose = None
    if args.llm:
        llm_prose = llm.summarize(diff_text, summary["title"])
        if llm_prose is None:
            print("diffnote: local LLM unavailable (is Ollama running at "
                  f"{llm._endpoint()}?) — falling back to offline summary.",
                  file=sys.stderr)

    if args.json:
        print(render.render_json(summary, llm_prose))
    elif args.markdown:
        markdown = render.render_markdown(summary, llm_prose)
        if args.save:
            try:
                with open(args.save, "w", encoding="utf-8", newline="\n") as output_file:
                    output_file.write(markdown + "\n")
            except OSError as exc:
                print(f"diffnote: could not write {args.save}: {exc}", file=sys.stderr)
                return 1
        else:
            print(markdown)
    else:
        print(render.render_terminal(summary, use_color=not args.no_color, llm_prose=llm_prose))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
