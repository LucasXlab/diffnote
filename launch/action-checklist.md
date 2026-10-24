> Historical launch planning. For the current verified source installation and status, use [README](../README.md).

# 发布行动清单（发布当天 + 之后一周）

> **状态更新（2026-10-16）**：仓库已建好并上线 — https://github.com/LucasXlab/diffnote
> ✅ 已完成：仓库创建（含 description + 9 topics）、main 首推、**v0.1.0 Release**、
> **CI 通过**（Python 3.8–3.12 矩阵）、**5 个 good first issue**（#1–#5）、
> **真实演示 GIF**（`demo.gif`，README 首屏）。
> ⏳ 仍需你本人：① PyPI 发布（见下"PyPI 发布"小节，无凭据我不能代做）；
> ② 按 D0 时间表把 `launch/` 里现成文案发到 HN/Reddit/X/PH。

## PyPI 发布（当前唯一硬性待办）
README 承诺 `pip install diffnote`，需先发布到 PyPI 才成立。已预置
`.github/workflows/publish.yml`（手动触发 + PyPI Trusted Publishing，无需 token）：
1. 在 https://pypi.org 注册/登录（首次发布需先做一次账号验证）。
2. 新建 pending 项目名 `diffnote`（若已被占用需换名并同步改 README/pyproject）。
3. PyPI 项目 → Settings → Publishing → Add GitHub publisher：
   owner `LucasXlab`，repo `diffnote`，workflow `publish.yml`，environment `pypi`。
4. GitHub 仓库 → Actions → "Publish to PyPI" → Run workflow。
5. 发布后验证：`pip install diffnote`（新 venv 中）→ `diffnote --version`。
   （PyPI 上手动发包会立即锁定该名字，建议尽快执行以防抢注。）

> 渠道顺序依据调研结论：首发 GitHub + HN/Reddit/X，配套在线可玩 Demo/截图；
> 强演示（终端 GIF）是最大增长杠杆。时间以 UTC 为准，选开发者活跃的时段
> （约 14:00–17:00 UTC，避开周末）。

## 发布前 1 天（✅ 全部完成 2026-10-16）
- [x] 在 GitHub 创建仓库（org 名替换 `LucasXlab`），推送 `main`。
- [x] 确认 `pyproject.toml` 的 `Homepage/Repository` URL 正确。
- [x] 终端演示 GIF 已生成（`demo.gif`，README 首屏；PIL + Menlo 渲染真实输出）。
- [x] 预填 5 个 good first issue（已发布为 issues #1–#5）。
- [x] 准备好 HN / Reddit / X / PH 文案（本目录）。

## 发布当天（D0）
- [x] ~~打 tag + Release~~：**v0.1.0 已发布**（含说明 + 链接 README）。
- [ ] 14:00 UTC：**Show HN** 首发（标题用 `launch/hacker-news.md`）。
- [ ] 14:30 UTC：Reddit r/python 发帖；15:00 r/git；15:30 r/programming。
- [ ] 16:00 UTC：X 线程（4 条，见 `x-twitter.md`）。
- [ ] 同日：Product Hunt 提交（选 America/New York 时区当天 12:01am 起算的"当日"）。
- [ ] 前 2 小时：盯 HN/Reddit 评论，逐条认真回复（技术质疑给具体答案 + 对比表链接）。
- [ ] 收集前 24h 的 issue/建议，当晚整理进 TODO。

## 之后一周（D1–D7）
- [ ] D1：把高频建议做成 1–2 个小改进并发布 patch，配更新说明（展示"听反馈"）。
- [ ] D2–D3：在相关中文社区（V2EX / 掘金 / 少数派）发一篇"为什么做 / 怎么用"短文。
- [ ] D3：回复所有 open issue，标记 good first issue 给新贡献者。
- [ ] D4：若 HN 沉了，换角度再发一次（如"我们如何用 0 依赖做 PR 摘要"）。
- [ ] D5：写一篇技术博客（架构 + 启发式思路），发到 dev.to / 个人博客。
- [ ] D6–D7：汇总 star 来源（哪个渠道带来最多），记一笔，用于下次迭代。
- [ ] 全程：**不刷 star、不买 star、不夸大功能**（已在约束中明确）。

## 演示 GIF（✅ 已完成，此节仅留作复现参考）
已用 PIL + Menlo 以真实 `diffnote` 输出渲染 `demo.gif`（35 帧，含 `pip install` → 出结果全过程）。
若以后想改用 asciinema 录制真实屏幕：
```bash
# 用 asciinema 录制，再转 gif（或 terminalizer）
pipx install asciinema
asciinema rec -d 2 demo.cast
# 找一个真实改动过的仓库，录制：diffnote / diffnote --markdown
# 转 gif：asciinema + asciinema-gif，或 https://svg-term.com
```
终端 GIF 是调研中 lazygit / open-interpreter 等爆款的核心传播素材，务必有。
