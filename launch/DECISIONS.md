> Historical launch planning. For the current verified source installation and status, use [README](../README.md).

# diffnote 轨道 · 决定与踩坑记录

> 工作区为多轨道并行环境，`research/假设.md`、`research/选题.md` 会被并行会话互相覆盖。
> 本文件是 diffnote 轨道的自包含决策记录（选题全文见 `research/选题_diffnote.md`）。

## 选题
- 从总报告机会清单提 10 个候选、四项打分，**diffnote 19 分居首**（痛点 5 / 演示 5 / 竞争 4 / 两周 5）选中。
- 与 git-cliff / conventional-changelog / 云端 AI PR 机器人的区分点：**未提交工作区 diff** +
  PR 正文 + 风险信号 + 离线优先 + 可选本地 Ollama，README 内有对比表。

## 实现
- 纯 Python 标准库、**零运行时依赖**（已实测：新 venv 装入 wheel 后 `pip list` 仅有 diffnote）。
- `--llm` 用 `urllib` 直连 localhost Ollama，无 Key、不外发、不可用时静默降级。
- **踩坑 1**：新增/删除文件不能靠 `diff --git a/… b/…` 行判断（新文件两处同名），必须解析
  `--- /dev/null`、`+++ /dev/null` 头部。已修 + 补测试。
- **踩坑 2**：`requirements.txt` 因 `.txt` 被同时计入 docs 与 config，改为 `path not in DEP_FILES` 排除。
- **修正 3（CI 破坏性）**：干净树时 `--json`/`--markdown` 不再早退，输出合法空摘要
  （`total_files: 0`）；仅终端模式友好提示退出 0。理由：`--json` 宣传用于 CI。
- **修正 4（语义）**：`--base REF` 从 `git diff BASE...HEAD` 改为 `git diff BASE`（含未提交），
  否则 staged 后开 PR 会得到"no changes detected"；`--range A..B` 保留纯提交比较。

## 验证
- 14 个 pytest 全绿；新 venv + wheel + 非 editable 安装，按 README 逐条跑通
  `diffnote / --staged / --commits N / --base / --range / --json / --markdown / --llm(降级)`。

## 发布（2026-10-16 已代为执行）
- `gh` 已认证（LucasYanzy）→ 建公共仓库 https://github.com/LucasXlab/diffnote、推 main、
  **v0.1.0 Release**、**issues #1–#5（good first issue）**、description + 9 topics；
  **CI 通过**（3.8–3.12 矩阵）。
- **演示 GIF 真实生成**：PIL + Menlo 渲染 35 帧（install → 出结果），内容为真实 `diffnote` 输出；
  README 文本演示同步替换为真实捕获数据（原示意数字 +842/-137 已改为真实 +12/-2，避免夸大）。
- **PyPI 未发布**（无凭据）：预置 `.github/workflows/publish.yml`（`workflow_dispatch` 手动触发 +
  PyPI Trusted Publishing，无需 token）；未挂 `release` 自动触发是为了用户配置 PyPI 前不出现红色
  失败运行。**这是 README `pip install diffnote` 承诺成立前的唯一硬性待办**，操作步骤见
  `launch/action-checklist.md`。
- HN / Reddit / X / PH 文案已就绪（本目录），真实发帖需用户账号，未代发。
