# 发布行动清单（发布当天 + 之后一周）

> 渠道顺序依据调研结论：首发 GitHub + HN/Reddit/X，配套在线可玩 Demo/截图；
> 强演示（终端 GIF）是最大增长杠杆。时间以 UTC 为准，选开发者活跃的时段
> （约 14:00–17:00 UTC，避开周末）。

## 发布前 1 天
- [ ] 在 GitHub 创建仓库（org 名替换 `LucasYanzy`），推送 `main`。
- [ ] 确认 `pyproject.toml` 的 `Homepage/Repository` URL 正确。
- [ ] 录制一条 15–25 秒的终端演示 GIF（见下方命令），放进 README 顶部。
- [ ] 预填 5 个 good first issue（见 `GOOD_FIRST_ISSUES.md`）。
- [ ] 准备好 HN / Reddit / X / PH 文案（本目录）。

## 发布当天（D0）
- [ ] 09:00 UTC：在 GitHub 打 `v0.1.0` tag 并发布 Release（写一句亮点 + 链接 README）。
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

## 演示 GIF 录制（可选但强烈建议）
```bash
# 用 asciinema 录制，再转 gif（或 terminalizer）
pipx install asciinema
asciinema rec -d 2 demo.cast
# 找一个真实改动过的仓库，录制：diffnote / diffnote --markdown
# 转 gif：asciinema + asciinema-gif，或 https://svg-term.com
```
终端 GIF 是调研中 lazygit / open-interpreter 等爆款的核心传播素材，务必有。
