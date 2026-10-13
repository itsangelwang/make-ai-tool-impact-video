# Make AI Tool Impact Video

一个可同时用于 Codex 和 Claude Code 的视频制作 Skill：把 AI 工具的功能，讲成普通人能看懂的竖屏短视频。支持中文和英语市场。

围绕一个具体任务，直观展示使用前怎么做、AI 改变了哪一步，以及使用后得到什么结果。

## 特点

- 用同一个案例贯穿输入、AI 处理、结果和后续使用。
- 用操作动画展示点击、打字、复制粘贴、修改和导出。
- 面向手机观看设计大字、字幕、转场和重点放大。
- 支持配音、操作音效和背景音乐。
- 先确认脚本和画面，再完成配音与成片。

适合制作 AI 办公、文档、研究、会议、简历和生活效率工具的视频。

## 安装

克隆一份到本地，再分别链接到 Codex 和 Claude Code 的 Skills 目录。两个工具共用同一份文件，不会出现两个版本：

```bash
git clone https://github.com/itsangelwang/make-ai-tool-impact-video.git ~/skills/make-ai-tool-impact-video
mkdir -p ~/.codex/skills ~/.claude/skills
ln -s ~/skills/make-ai-tool-impact-video ~/.codex/skills/make-ai-tool-impact-video
ln -s ~/skills/make-ai-tool-impact-video ~/.claude/skills/make-ai-tool-impact-video
```

配音密钥放在仓库外面，例如 `~/.config/make-ai-tool-impact-video/.env`（格式参考 `.env.example`）。

## 使用

在 Codex 里用 `$make-ai-tool-impact-video` 调用，在 Claude Code 里用 `/make-ai-tool-impact-video` 调用，或者直接描述需求：

```text
使用 make-ai-tool-impact-video，为这个 AI 工具制作一条约一分钟的竖屏视频：<产品名称或链接>
目标市场：美国
语言：英语
具体任务：把工作笔记整理成一份可继续修改的周报
先给我看脚本和画面，再完成视频。
```

可以补充目标人群、视频长度、配音风格和品牌结尾。

## 输出

默认制作 1080×1920、30fps 的 9:16 视频，并提供封面、字幕和来源说明。视频长度可按内容调整。

具体制作流程见 [SKILL.md](SKILL.md)。

## 用两个 AI 工具一起维护

规则写在 [AGENTS.md](AGENTS.md)，Codex 和 Claude Code 都会读取。简单来说：

1. 开始前先 `git pull`，拿到 GitHub 上的最新版本。
2. 同一时间只让一个工具修改。
3. 每次修改开一个分支（`codex/...` 或 `claude/...`），跑通测试后发 PR，确认后再合并。
4. 可以让另一个工具审查这个 PR，互相查漏补缺。

## 来源与致谢

本项目参考并改编自 [Ah-ha07/AceMode-video-skill](https://github.com/Ah-ha07/AceMode-video-skill)，感谢原作者的探索与分享。

本仓库未添加开源许可证；上游代码、品牌和素材的使用权需另行确认。
