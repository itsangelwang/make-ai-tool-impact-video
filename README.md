# Make AI Tool Impact Video

**给它一个 AI 工具的名字或链接，它帮你做出一条约 1 分钟、普通人能看懂的竖屏短视频。**

可在 Codex 和 Claude Code 中使用。**默认制作面向美国市场的英语视频**，也支持中文。

## 它做出来的视频长什么样

每条视频只讲**一个人、一件具体的事**，按这个顺序展开：

1. **痛点**：以前做这件事有多麻烦
2. **以前怎么做**：一步步展示手动操作
3. **现在怎么做**：AI 接手了哪一步，用同一个例子演示
4. **人还要做什么**：哪些结果必须自己检查、自己决定
5. **适合谁、怎么试**：现在能不能用，从哪里开始

视频里不会编造“节省 80% 时间”这类数据，每个说法都有来源记录。

**适合**：AI 办公、文档、研究、会议、简历、生活效率等工具。

## 快速开始

### 第 1 步：准备环境

电脑上需要装好这三样（不确定的话，可以直接让 AI 帮你检查和安装）：

| 软件 | 用途 |
|---|---|
| [Python 3](https://www.python.org/) | 运行检查脚本 |
| [Node.js](https://nodejs.org/) | 制作动画和导出视频 |
| [FFmpeg](https://ffmpeg.org/) | 检查成片质量 |

### 第 2 步：安装 Skill

**最简单的方法**：打开 Codex 或 Claude Code，直接说：

```text
帮我安装这个 Skill：https://github.com/itsangelwang/make-ai-tool-impact-video
```

**手动安装**：在终端运行下面的命令。两个工具会共用同一份文件，以后更新一次就行：

```bash
git clone https://github.com/itsangelwang/make-ai-tool-impact-video.git ~/skills/make-ai-tool-impact-video
mkdir -p ~/.codex/skills ~/.claude/skills
ln -s ~/skills/make-ai-tool-impact-video ~/.codex/skills/make-ai-tool-impact-video
ln -s ~/skills/make-ai-tool-impact-video ~/.claude/skills/make-ai-tool-impact-video
```

只用其中一个工具的话，跳过另一个工具对应的 `ln -s` 那一行即可。

### 第 3 步：开始制作

在 Codex 里输入 `$make-ai-tool-impact-video`，在 Claude Code 里输入 `/make-ai-tool-impact-video`，再接着描述需求。也可以直接用文字说明：

```text
使用 make-ai-tool-impact-video，为这个 AI 工具做一条一分钟竖屏视频：<产品名称或链接>
目标人群：刚入职的运营
具体任务：把一周的会议笔记整理成周报
先给我看脚本和画面，确认后再配音出片。
```

不写语言时默认做美式英语视频。要做中文视频，加一句“语言：中文，面向中国市场”；要做英国或澳大利亚市场，写明市场即可。

只提供工具名称也可以，人群和任务没写的话，AI 会先调研，再挑一个最容易讲清楚的例子。

## 制作过程中你需要做什么

整个流程中你只需要**确认一次**：

1. AI 调研产品，写脚本，设计画面
2. **你会收到一份审片包**：旁白、画面安排、封面、开头 3 秒预览、事实来源。不满意可以直接提修改意见
3. 你说“确认”之后，AI 才会配音、导出成片
4. 确认后如果再修改脚本或画面，需要重新确认一次

AI 不会自动把视频发布到任何平台。

**关于时长**：默认 55–65 秒。如果真实的操作演示需要更多时间，审片版最长可以到 75 秒，AI 会写明延长的原因，并记录在质检报告里。

## 品牌结尾

视频最后默认有 3–4 秒的 **ACEMODE** 品牌卡片（“10x Faster, Log Off Earlier.”），算在总时长里。品牌卡片默认只显示画面，不配音。

- **换成你自己的品牌**：提供品牌名、口号和 Logo，AI 会原样使用，不会改动拼写和大小写
- **不要品牌结尾**：直接说“不要品牌结尾”
- **需要念出品牌**：说“结尾把品牌念出来”

## 英语和中文视频

默认是英语（美国市场）。画面里的固定文字（例如“使用前 / 使用后”“今天可以这样试”）和字体，会根据视频语言自动切换。英语视频不会出现中文标签，也不会使用中文手写字体。

## 配音设置（可选）

不配音也能生成审片包。需要配音时，选一个服务，注册后拿到密钥（API Key）：

| 服务 | 适合 | 需要的密钥 |
|---|---|---|
| [Fish Audio](https://fish.audio/)（**推荐，默认**） | 英语和中文，声音自然、有情绪起伏 | `FISH_AUDIO_API_KEY` |
| [OpenRouter](https://openrouter.ai/) | 英语，有免费模型 | `OPENROUTER_API_KEY` |
| [Deepgram](https://deepgram.com/) | 英语 | `DEEPGRAM_API_KEY` |

**默认英语声音**：Fish Audio 官方的 “Sawyer”（美式男声），使用付费模型 `s2.1-pro`，语气会跟着故事起伏：讲痛点时有点烦，讲到 AI 帮忙时兴奋，提醒人工检查时冷静。想换声音时直接告诉 AI，它会先给你几段试听。

Fish Audio 的免费版一般只能个人使用。如果视频要商用，请在 Fish Audio 账户页面确认你的套餐包含商用权。

**密钥要保管好：**
- 放在 `~/.config/make-ai-tool-impact-video/.env`，格式参考 [`.env.example`](.env.example)
- 不要放进 Skill 文件夹，不要发到聊天里，也不要上传到 GitHub

## 你会得到什么

- 1080×1920、30fps 的 9:16 竖屏视频（MP4）
- 封面图
- 字幕文件
- 来源记录：每个画面素材和每个事实说法的出处
- 质检报告：分辨率、字幕位置、时长等是否达标

## 更新

让 AI 执行“更新 make-ai-tool-impact-video 这个 Skill”，或在 Skill 文件夹里运行 `git pull`。

## 参与维护

这个 Skill 同时用 Codex 和 Claude Code 打磨，两个工具共用 [AGENTS.md](AGENTS.md) 里的规则：

1. 开始前先 `git pull`，拿到最新版本
2. 同一时间只让一个工具修改
3. 每次修改开一个分支（`codex/...` 或 `claude/...`），测试通过后发 PR，确认后再合并
4. 让另一个工具审查这个 PR，互相查漏补缺

每个 PR 都会由 GitHub 自动运行测试，并检查视频模板能否正常渲染。PR 页面显示绿色对勾 ✅，说明没有改坏。

两个约定，避免两边越改越乱：

- **示范案例**：[examples/](examples/) 里有一套中文、一套英语的完整示范文件，AI 写新视频时照着这个格式来。
- **统一的数字**：时长、字数、字幕速度等规定只写在 `scripts/limits.json` 一个地方。如果文档里写的数字和它对不上，测试会报错。

完整的制作规范见 [SKILL.md](SKILL.md)。

## 来源与致谢

本项目参考并改编自 [Ah-ha07/AceMode-video-skill](https://github.com/Ah-ha07/AceMode-video-skill)，感谢原作者的探索与分享。

本仓库未添加开源许可证；上游代码、品牌和素材的使用权需另行确认。
