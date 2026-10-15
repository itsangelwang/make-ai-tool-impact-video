# Make AI Tool Impact Video

给它一个 AI 工具的名字或链接，它帮你做出一条约 1 分钟、普通人能看懂的竖屏短视频。可在 Codex 和 Claude Code 中使用。

## 安装

需要 [Python 3](https://www.python.org/)、[Node.js](https://nodejs.org/) 和 [FFmpeg](https://ffmpeg.org/)。

最简单的方法是打开 Codex 或 Claude Code，直接说：

```text
帮我安装这个 Skill：https://github.com/itsangelwang/make-ai-tool-impact-video
```

也可以手动安装（两个工具共用同一份文件；只用一个工具的话，跳过另一个的 `ln -s` 那行）：

```bash
git clone https://github.com/itsangelwang/make-ai-tool-impact-video.git ~/skills/make-ai-tool-impact-video
mkdir -p ~/.codex/skills ~/.claude/skills
ln -s ~/skills/make-ai-tool-impact-video ~/.codex/skills/make-ai-tool-impact-video
ln -s ~/skills/make-ai-tool-impact-video ~/.claude/skills/make-ai-tool-impact-video
```

以后更新：在 Skill 文件夹里运行 `git pull`。

## 使用

在 Codex 里输入 `$make-ai-tool-impact-video`，在 Claude Code 里输入 `/make-ai-tool-impact-video`，再描述需求：

```text
为这个 AI 工具做一条一分钟竖屏视频：<产品名称或链接>
具体任务：把一周的会议笔记整理成周报
```

AI 会先给你一份审片包（脚本、画面、事实来源），**你确认后才会配音出片**，不会自动发布。

## 默认设置

| 项目 | 默认 | 想改的话 |
|---|---|---|
| 语言 | 美式英语 | 说“语言：中文，面向中国市场” |
| 配音 | Fish Audio 官方声音 “Sawyer”（Drama 3 模型），语气随剧情起伏 | 说“换个声音”，AI 会先给你试听 |
| 品牌结尾 | ACEMODE 品牌卡，并念出 “10x Faster, Log Off Earlier.” | 说“不要品牌结尾”，或提供你自己的品牌 |
| 时长 | 55–65 秒 | 写明理由时最长 75 秒 |

## 配音密钥

配音需要 [Fish Audio](https://fish.audio/) 的 API Key（也支持 OpenRouter、Deepgram）。把密钥写进 `~/.config/make-ai-tool-impact-video/.env`，格式参考 [`.env.example`](.env.example)。

- 不要放进 Skill 文件夹，不要发到聊天里，也不要上传到 GitHub
- Fish Audio 免费版一般只能个人使用，商用前请确认你的套餐包含商用权

## 输出

1080×1920 竖屏 MP4、封面、字幕、来源记录和质检报告。

## 来源与致谢

本项目参考并改编自 [Ah-ha07/AceMode-video-skill](https://github.com/Ah-ha07/AceMode-video-skill)，感谢原作者的探索与分享。本仓库未添加开源许可证；上游代码、品牌和素材的使用权需另行确认。
