---
name: make-ai-tool-impact-video
description: Research a named AI tool and create a roughly one-minute, 9:16 Chinese workflow explainer for ordinary people, with one concrete before/after case, verified claims, real product evidence, Remotion motion design, readable paced captions, combined review, and delivery QA. Use when turning an AI product name, launch page, demo, or capability into an accessible vertical video that explains what changes, what the person still owns, who it suits, and how to try it safely.
---

# Make AI Tool Impact Video

Explain one workflow change for one person doing one task. Treat the tool as the intervention, not the protagonist.

## Inputs

Require a tool name or URL. Accept audience, task, platform, voice, palette, and end-brand preferences. When audience or task is absent, research first and choose the clearest supported ordinary-person case.

Use `<skill-dir>` as this Skill directory and replace placeholders with absolute paths.

## 1. Research and bound the claim

Read [references/fact-rules.md](references/fact-rules.md).

- Browse current official documentation for capability, access, plan, beta, platform, privacy, and consent claims.
- Prefer real product UI, official screenshots/video, or user-provided assets. Record every asset in `source-ledger.json`.
- Write every narrated factual claim to `claim-ledger.json`; separate observation, vendor claim, inference, and hypothesis.
- Never convert vendor outcomes into measured results. Never invent time saved or efficiency multipliers.

Choose exactly one audience, task, and example thread. Define `before_steps`, `ai_change`, `after_steps`, `human_check`, `readiness`, and `next_action`.

## 2. Build one causal story

Read [references/story-contract.md](references/story-contract.md) and [references/visual-system.md](references/visual-system.md). When the project uses silent or animated captions, also read [references/pacing-and-review.md](references/pacing-and-review.md). Read [references/brand-system.md](references/brand-system.md) only when an end brand is requested.

Use this order:

1. Background and concrete pain.
2. One-sentence product promise after relevance is clear.
3. The previous workflow, shown as actions.
4. The new workflow, including the exact handoff or import step.
5. One concrete example carried through input, AI output, downstream use, and verification.
6. What AI changed and what the person still owns.
7. Fit, readiness boundary, reversible next action, and optional brand ending.

Carry the same task object through the story. An item found in the old record must become the AI input, appear in the summary, become the next action or question, and remain the item the person verifies. Do not introduce “draft,” “source,” “old material,” “owner,” or “deadline” without showing the concrete artifact or value.

Create `script-package.json` and `claim-ledger.json`, then validate:

```bash
python3 <skill-dir>/scripts/validate_package.py \
  <project-dir>/script-package.json \
  <project-dir>/claim-ledger.json
```

## 3. Create the combined review

Scaffold the vertical project:

```bash
python3 <skill-dir>/scripts/scaffold_project.py <project-dir>/video
```

Populate `video/src/story.json`, add cleared assets under `video/public/assets/`, and validate sources:

```bash
python3 <skill-dir>/scripts/validate_sources.py \
  <project-dir>/video/source-ledger.json
```

Produce one review containing the narration, factual boundaries, scene plan, cover, first-three-second preview, target voice/palette, and blockers. For silent review captions, create `timeline.json` and run:

```bash
python3 <skill-dir>/scripts/audit_timeline.py \
  <project-dir>/video/src/timeline.json
```

Register the review bundle with `project_state.py review`. Wait for explicit approval before final TTS or delivery render. Any registered script, claim, story, source, cover, voice, or opening change invalidates approval.

## 4. Iterate by communication purpose

When feedback reveals confusion, repair the causal chain rather than polishing the isolated page.

- If a term is unclear, show its concrete object and example value.
- If two pages feel repetitive, assign each a different question or merge them.
- If a page feels dense, reveal one information layer at a time.
- If a transition is unreadable, give it a dedicated full-frame hold and end the outgoing caption first.
- If captions cannot be spoken naturally, cut repeated narration before extending the video.
- If AI and human roles blur, use separate regions and animate the artifact handoff.

Render local review segments for disputed beats; render the full review after the causal chain or timing changes.

## 5. Finish and verify

Generate final TTS only after approval. Never use a voice the user has rejected. Prefer a neural provider with timestamps; otherwise measure audio and generate phrase timing with `caption_pipeline.py`.

Target 55–65 seconds. Do not time-stretch speech. Render `VerticalImpact`, then run:

```bash
python3 <skill-dir>/scripts/verify_video.py \
  <project-dir>/video/renders/final.mp4 \
  --captions <project-dir>/video/src/captions.json \
  --report <project-dir>/video/qa/final-qa.json
```

Visually inspect the full video and representative frames. Confirm native 1080×1920, complete decoding, safe captions, natural speech pace, semantic highlighting, readable transitions, real product evidence, and a viewer-recountable before → change → after → human responsibility chain.

## 6. Deliver

Deliver the MP4, cover, captions, source ledger, claim ledger, and QA report. State actual duration and publication blockers. Do not publish automatically.

Use [references/failure-modes.md](references/failure-modes.md) when evidence, access, rights, TTS, browser, FFmpeg, or rendering is unavailable.
