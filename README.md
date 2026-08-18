# Make AI Tool Impact Video

一个用于 Codex 的视频制作 Skill：把新出的 AI 工具讲成普通人能看懂的一分钟竖屏视频。

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

## 它会做什么

Skill 包含一条完整制作流程：

1. 查阅官方资料并建立事实账本；
2. 选择一个具体人物、任务和贯穿案例；
3. 编写使用前、AI 介入点、使用后和人工检查的因果故事；
4. 优先使用真实产品界面和合法素材；
5. 用 Remotion 制作原生 1080×1920 动态视频；
6. 生成可读、可自然口播的逐字字幕；
7. 检查语速、转场重叠、素材来源和视频技术指标；
8. 先提交合并审片，获得确认后再完成配音和最终渲染。

## 这次实测沉淀的规则

- 同一个案例必须贯穿整支视频，不能每页换一个情境。
- 上一环节的输出必须成为下一环节的输入。
- “旧资料”“草稿”“原文”“负责人”等词第一次出现时，必须展示具体对象和具体值。
- 画面能说明的动作不重复口播。
- 55–65 秒视频通常控制在约 150–190 个中文字。
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
│   ├── brand-system.md
│   └── failure-modes.md
├── scripts/
│   ├── validate_package.py
│   ├── audit_timeline.py
│   ├── validate_sources.py
│   ├── project_state.py
│   ├── caption_pipeline.py
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
