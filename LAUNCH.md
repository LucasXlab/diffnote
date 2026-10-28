# diffnote launch drafts

Local planning material, AI-assisted drafting and development. No post, submission, message, account operation, registry release or remote CI result is implied. Before using any permitted draft, verify the actual public source revision, attachments, install path and current platform rules. Never invent personal experience, users, stars, benchmarks or completed tests. Target repository metadata: [LucasXlab/diffnote](https://github.com/LucasXlab/diffnote); existence of a remote does not establish that this source revision is published.

Official HN, r/Python, r/SideProject and r/commandline pages were rechecked on 2026-10-27 for this local draft set. Platform rules and pinned threads can change; this check does not authorize a future submission.

## GitHub metadata

Description (under 350 characters):

> Turn local Git changes into reviewable PR drafts: file facts, line counts and traceable heuristic signals. Offline Python CLI with terminal, Markdown and JSON output. No model or API key required.

Exactly 10 topics:

`git` `git-diff` `pull-request` `changelog` `cli` `python` `developer-tools` `code-review` `offline` `markdown`

Social preview: [1280 × 640 PNG](assets/social-preview.png). Hero: [real synthetic CLI GIF](assets/demo.gif). [Provenance and reproduction](docs/showcase.md). Install from source using the three README commands; no PyPI or pipx release is claimed.

## Hacker News — internal examples only, do not submit

[HN guidelines](https://news.ycombinator.com/newsguidelines.html) prohibit generated submission text and generated or AI-edited comments. These AI-generated examples are only internal planning references and cannot be submitted or lightly edited into a supposedly human draft. A person who actually worked on the project must independently write any title and discussion from their own experience. [Show HN rules](https://news.ycombinator.com/showhn.html) also require a substantive, runnable work and personal participation. No submission is authorized here.

Internal title example: **Show HN: diffnote — local Git changes into reviewable PR drafts**

Internal first-comment example: diffnote is a small Python CLI that turns local tracked changes into a draft with file metadata, line counts and path/rule evidence. It has no model layer or runtime network request. The draft cannot know intent or run tests; the author must add both. Synthetic examples include binary files, empty files, rename/mode facts and a configured-filter refusal. An interesting design question is which observable facts belong in a PR draft without suggesting a semantic review has occurred.

## r/Python — monthly showcase comment draft

[Official rules](https://www.reddit.com/r/Python/about/rules.json) route showcases to the current monthly showcase or suitable daily thread, not a standalone showcase post. Find the current pinned thread before any use; this is an English comment draft with the requested sections, not moderator approval.

**What My Project Does**

diffnote is an offline Python 3.11+ CLI that reads local Git changes and produces a reviewable PR draft in terminal, Markdown or JSON form. It cross-checks paths and text counts against Git numstat and preserves empty/binary/rename/mode metadata. Signals cite finite rules and added/deleted/path evidence. Source: [LucasXlab/diffnote](https://github.com/LucasXlab/diffnote). [Synthetic demo](assets/demo.gif).

**Target Audience**

Developers assembling a factual first draft before explaining intent and actual validation. It does not execute tests, certify safety or infer correctness. Runtime needs Git and Python, no model or key. Development and this draft are AI-assisted; human review is required before sharing.

**Comparison**

`git diff` remains the patch reader and `git diff --stat` the compact size view. diffnote adds a structured draft and rule/path evidence beside those facts. No competitor quality or accuracy advantage has been measured. Feedback sought: which metadata should a draft preserve, and where does a signal imply too much?

## r/SideProject — technical feedback draft

[Official sidebar](https://old.reddit.com/r/SideProject/) requests `Project name - Short description` for link titles and welcomes constructive feedback. The 2026-10-27 check also found a pinned non-AI project thread; do not use that thread for this project. The [official rules endpoint](https://www.reddit.com/r/SideProject/about/rules.json) returned an empty community-rules list, which is not permission. Recheck sidebar, pinned threads and rules before use.

Title: **diffnote - Offline Git changes into reviewable PR drafts**

Body: diffnote reads tracked local or staged changes and builds terminal/Markdown/JSON drafts from file facts. Binary line counts stay unknown, renames keep their old path, and review signals identify rules and evidence. The goal is to reduce repetitive fact assembly; intent, tests and review decisions remain with the author. Source and a synthetic reproducible demo are linked in the repository. Code and this draft are AI-assisted. No usage, accuracy or growth results are claimed. Technical feedback sought: does the distinction between facts, signals and unverified intent remain clear, especially in JSON? Runtime is offline, while installation may download public build tools.

## r/commandline — excluded from this AI draft set

[Official rules](https://www.reddit.com/r/commandline/about/rules.json) prohibit AI-generated post text/titles and require AI-code disclosure; they also restrict very new or sparse-history projects and generative-AI-related software. Current diffnote has removed its model layer, but that does not make this generated text eligible. Do not submit these drafts there or conceal their origin. Fact brief only: Python/Git CLI; no GUI requirement; local file facts and heuristic evidence; source install; no accuracy benchmark. Any future human decision must independently establish all current eligibility conditions.

## X — five-post thread draft

1. diffnote turns local Git changes into a reviewable PR draft: file facts, line counts and rule/path evidence. Offline Python CLI, no model or API key. Source metadata targets LucasXlab/diffnote; check the published revision before trying it.
2. Start with the actual patch. Working-tree mode includes staged tracked edits; --staged reads only the index. Untracked files enter after staging. The draft helps assemble facts; you still explain why the change exists.
3. Empty files are changes too. Binary counts stay unavailable; rename and mode metadata stay visible. The bundled GIF comes from real installed CLI output on synthetic Git history, with reading holds explicitly added.
4. Review signals are finite heuristics, not a safety verdict. They cite a path, rule and added/deleted/path source. diffnote does not run tests; add the checks you actually performed and inspect the patch yourself.
5. Source install: use the README's venv, pip install ., and synthetic demo commands. Development and this draft are AI-assisted. Feedback sought on fact presentation and signal wording; no accuracy, user-count or star claim.

## 掘金草稿

标题：从 Git diff 到可修改的 PR 草稿：diffnote 的事实边界

PR 说明常要重复整理文件、增删行数和改动区域。diffnote 用本地 Python/Git 把这些可观察事实写成终端、Markdown 或 JSON 草稿，并为有限规则线索附上路径及新增/删除来源。空文件、二进制、重命名和权限变化保留各自含义。它不运行测试，也不能替作者理解意图；没有线索不表示安全。源码 README 提供三命令安装与合成演示，GIF 可追溯到完整本地录制。旧模型层已经移除，运行不需要模型或 key。开发和本文有 AI 辅助，发布前需人工核实。希望讨论：草稿中哪些信息真正帮助审阅，哪些措辞容易让人误以为已做语义审查？不声称准确率或真实用户成果。

## V2EX 草稿

标题：[分享创造] diffnote：离线整理 Git 变更，给 PR 说明一个事实起点

这是一个 Python/Git CLI，按工作树、暂存区或验证过的本地提交范围生成草稿。它保留文件状态和文本计数，规则提示附证据；二进制不会冒充 0 行文本。支持终端、Markdown、JSON，源码安装即可试合成例子，无模型服务。意图和真正跑过的检查仍由人补全。开发及这份草稿有 AI 辅助；没有用户量、准确率或收益数据。想收集事实展示和错误边界的技术反馈，请勿贴私人补丁或凭据。发帖前核对节点、现行推广规则与实际公开版本。

## 即刻草稿

把本地 Git 变更整理成 PR 草稿，需要先说清“看见了什么”。diffnote 保留文件、状态、行数及有来源的规则线索，不替你解释动机或声称测试已过。Python/Git、本地运行、无模型或 API key；有真实合成演示和完整来源。开发与这段文字有 AI 辅助。希望得到关于草稿可读性和提示措辞的反馈，不把小样本说成准确率。分享前先确认公开源码和社区规则。

## Product Hunt draft

Tagline: **Local Git changes into reviewable PR drafts**

Description: diffnote is an offline Python CLI for assembling a factual first draft of a pull request description. Choose tracked working-tree changes, the index or verified local revisions. Keep file states, text counts and traceable heuristic evidence in terminal, Markdown or JSON. No model or API key is required. It does not execute tests or establish semantic correctness. Install from source and try the bundled synthetic demo. Development and this draft are AI-assisted; no registry release, remote CI pass or user results are claimed.

## Pre-use checklist

Verify the final source revision and source installation; independently review media and every output for private data; replace relative attachment links with verified public asset links only after authorized publication; recheck current community rules; have an accountable human review eligible drafts. HN and r/commandline examples remain ineligible generated text. No sending or publishing action is included in this document.
