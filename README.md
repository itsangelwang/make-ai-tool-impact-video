# Make AI Tool Impact Video

一个用于 Codex 的视频制作 Skill：把新出的 AI 工具讲成普通人能看懂的一分钟竖屏视频。现在同时支持中文市场和英语市场；英语模式会原生改写脚本、例子、视觉层级、字幕节奏和旁白，而不是逐句翻译中文版。

> English: Turn one AI tool into an evidence-based, one-minute vertical workflow story for Chinese or English-speaking audiences. The English mode localizes the hook, example, typography, captions, voice, and call to action instead of translating copy literally.

## 来源与致谢

本项目基于并参考 [Ah-ha07/AceMode-video-skill](https://github.com/Ah-ha07/AceMode-video-skill) 的视频制作工作流、事实核验思路和 Remotion 实现方向进行改编，感谢原作者的探索与分享。

在此基础上，本项目针对“指定一个 AI 工具，制作一分钟普通人能看懂的工作流影响视频”重新设计了内容结构、具体案例、上下游因果、真实产品素材规则、自然口播节奏、字幕语义高亮、全屏转场、AI 与人的职责分工、时间轴校验和 Acemode 品牌收尾。

截至本仓库更新时，原项目的 GitHub 元数据没有显示开源许可证。本处致谢与链接不代表原项目采用 MIT 或其他开源许可证。若需要复制、再分发或商业使用原项目中的代码、品牌或专属模板，请先向原作者确认授权。

本仓库不授予 AceMode 上游代码、品牌或专属模板的任何权利。在上游授权得到书面确认或相关实现完成独立重写之前，不应把本仓库改为 MIT 等开放许可证，也不应复制、再分发或商业使用可能源自上游的受保护内容。

它不只介绍产品功能，而是围绕同一个人物、同一个任务，说明：

- 使用前具体怎么做；
- AI 改变了工作流中的哪一步；
- 使用后具体怎么做；
- AI 生成的结果怎样用于下一步工作；
- 哪些判断和责任仍然属于人；
- 这个工具适合谁，以及怎样低风险尝试。

## 适用场景

你可以用它制作：

- AI 会议记录与会前准备视频；
- AI 简历修改工具视频；
- AI 旅行规划工具视频；
- AI 文档、研究、设计或办公工具视频；
- 新产品发布、功能更新或候补测试资格的通俗解释视频。

典型请求：

```text
使用 $make-ai-tool-impact-video，把这个 AI 工具制作成一分钟、9:16、普通人能看懂的竖屏视频：<产品链接>
```

还可以补充目标人物和任务：

```text
目标人物：经常阅读长资料的上班族
具体任务：把多份资料整理成一份会议准备摘要
先生成合并审片包，确认后再渲染完整视频
```

英语市场请求示例：

```text
Language: en-US
Market: US
Voice: Deepgram Flux TTS, conversational American English
Create the combined review package first. Wait for approval before the final voice and render.
```

## 它会做什么

Skill 包含一条完整制作流程：

1. 查阅官方资料并建立事实账本；
2. 选择一个具体人物、任务和贯穿案例；
3. 编写使用前、AI 介入点、使用后和人工检查的因果故事；
4. 优先使用真实产品界面和合法素材；
5. 用 Remotion 制作原生 1080×1920 动态视频；
6. 中文按语义逐字、英文按词或短语生成可读字幕；
7. 检查语速、转场重叠、素材来源和视频技术指标；
8. 先提交合并审片，获得确认后再完成配音和最终渲染。

## 这次实测沉淀的规则

- 同一个案例必须贯穿整支视频，不能每页换一个情境。
- 上一环节的输出必须成为下一环节的输入。
- “旧资料”“草稿”“原文”“负责人”等词第一次出现时，必须展示具体对象和具体值。
- 画面能说明的动作不重复口播。
- 55–65 秒视频通常控制在约 150–190 个中文字。
- 英语版通常控制在约 105–135 个英文单词，平均约 2.0–2.5 words/s。
- 单句建议保持约 3–4 个中文字/秒，超过 4.2 字/秒会被校验器拦截。
- 可读转场使用独立全屏画面，不能覆盖前后页面或字幕结尾。
- 字幕重点按语义高亮，不能随机给文字上色。
- AI 与人的职责使用不同视觉区域，并通过结果交接动画表现。
- 放大、缩小和转场必须帮助观众看清关键变化，而不是纯装饰。

## 目录结构

```text
make-ai-tool-impact-video/
├── SKILL.md
├── agents/openai.yaml
├── assets/remotion-template/
├── references/
│   ├── fact-rules.md
│   ├── story-contract.md
│   ├── visual-system.md
│   ├── pacing-and-review.md
│   ├── english-market.md
│   ├── brand-system.md
│   └── failure-modes.md
├── scripts/
│   ├── validate_package.py
│   ├── audit_timeline.py
│   ├── validate_sources.py
│   ├── project_state.py
│   ├── caption_pipeline.py
│   ├── deepgram_tts.py
│   ├── openrouter_tts.py
│   ├── generate_ui_sfx.mjs
│   ├── scaffold_project.py
│   └── verify_video.py
└── tests/test_skill.py
```

## 安装

克隆仓库：

```bash
git clone https://github.com/itsangelwang/make-ai-tool-impact-video.git
```

然后将整个 `make-ai-tool-impact-video` 文件夹放入 Codex 的 Skills 目录，或让 Codex 从这个 GitHub 仓库安装 Skill。

Remotion 模板依赖：

```bash
cd make-ai-tool-impact-video/assets/remotion-template
npm ci
```

## 校验与测试

运行 Skill 测试：

```bash
python3 -m unittest discover -s tests -v
```

## Deepgram Flux TTS

英文旁白默认支持 Deepgram Flux TTS 的批量 REST 接口。Flux TTS 目前属于 Early Access，因此 Skill 会把 Aura-2 作为回退方案。API key 只能通过环境变量读取：

```bash
export DEEPGRAM_API_KEY="your-key"
python3 scripts/deepgram_tts.py \
  --script script-package.json \
  --output video/public/audio/narration.mp3 \
  --model flux-hannah-en \
  --speed 0.95 \
  --expressivity 1
```

不要把 key 写进命令历史、JSON、`.env` 提交或 GitHub。仓库已忽略 `.env` 与 `.env.*`。建议先用同一段 8–12 秒英文试听 `flux-hannah-en`、`flux-heather-en` 和 `flux-wes-en`，确认后再生成整段旁白。

校验脚本与事实账本：

```bash
python3 scripts/validate_package.py script-package.json claim-ledger.json
```

校验字幕语速和转场：

```bash
python3 scripts/audit_timeline.py timeline.json
```

## 默认输出

- 约 55–65 秒的 9:16 视频；
- 1080×1920、30fps；
- 封面；
- 字幕文件；
- 来源清单；
- 事实边界；
- 基础 QA 报告；
- 可选 Acemode 品牌收尾。

## 边界

- 不自动发布到任何平台。
- 不把官方宣传改写成已经验证的效果。
- 不虚构节省时间或效率倍数。
- AI 生成插画不能冒充真实产品证据。
- 产品可用范围、价格、套餐和 beta 状态必须在制作时重新核验。
- 没有合法产品素材时，才退回清晰标注的抽象流程动画。

## 许可证

本仓库目前没有添加开源许可证。代码公开可见，但尚未主动授予复制、修改、再分发或商业使用的许可。后续可以根据发布目标再选择 MIT、GPL 或其他许可证。
