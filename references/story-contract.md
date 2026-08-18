# Story package contract

Create JSON with `schema_version: 1` and these required fields:

- `language`: BCP-47-style output language such as `zh-CN` or `en-US`.
- `market`: intended audience market such as `CN` or `US`.
- `tool`: `name`, `url`, `one_line_capability`.
- `audience`: one concrete role or life situation.
- `task`: one observable task, unchanged before and after.
- `before_steps`: 2–3 short steps.
- `friction`: the bottleneck the viewer recognizes.
- `ai_change`: one step the tool changes; do not claim it replaces the whole job.
- `after_steps`: 2–4 steps showing person → AI → person responsibility.
- `human_check`: a concrete verification, judgment, privacy, or accountability duty.
- `readiness`: one of `use-now`, `try-now`, `watch`, `future`.
- `next_action`: a small, reversible experiment consistent with readiness.
- `narration`: natural speech with no stage directions; normally 150–190 Han characters for `zh-CN` or 105–135 words for `en-US` when readable transitions are included.
- `scenes`: 5–7 objects with `id`, `type`, `purpose`, `start_sec`, `end_sec`, `headline`, `visual`, and `claim_ids`.

Use scene types `pain-hook`, `before-workflow`, `ai-handoff`, `after-workflow`, `before-after`, `human-check`, and `next-action`. Include at least five distinct types. Start at 0, target an ending between 55 and 65 seconds, and allow review cuts up to 75 seconds when stable product interaction or evidence holds require it. Keep scenes contiguous and assign every scene an explicit communication purpose.

The first scene must show the audience/task pain. Mention the product only after relevance is clear. Keep headlines short enough for two mobile lines.

Choose one concrete example thread before writing scenes. Reuse its task object, decision, unfinished item, owner, date, and source artifact wherever those concepts appear. The new workflow must show the exact handoff: direct workspace search, file import, upload, connection, prompt, or capture action supported by evidence.

The example is not an appendix. Introduce it in the old workflow, carry it through the AI output, turn it into a downstream action, and use the same item for human verification.
