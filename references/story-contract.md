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
- `narration`: natural speech with no stage directions; normally 150–190 Han characters for `zh-CN` or 90–135 words for `en-US` when readable transitions are included. Use the low end only for a deliberately fast, energetic delivery.
- `brand`: optional; `null` or `{name, slogan, start_sec, end_sec}` for the brand card that follows the last scene. See [brand-system.md](brand-system.md).
- `scenes`: 5–7 objects with `id`, `type`, `purpose`, `start_sec`, `end_sec`, `headline`, `visual`, and `claim_ids`.

Use scene types `pain-hook`, `before-workflow`, `ai-handoff`, `after-workflow`, `before-after`, `human-check`, and `next-action`. Include at least five distinct types. Start at 0, target an ending (including any brand card) between 55 and 65 seconds, and allow review cuts up to 75 seconds when stable product interaction or evidence holds require it. Keep scenes contiguous and assign every scene an explicit communication purpose.

The first scene must show the audience/task pain. Mention the product only after relevance is clear. Keep headlines short enough for two mobile lines.

## Introduce what is new

Treat a tool or feature as new when its official announcement is within the last 90 days, or when the user asks to highlight it. Record the announcement date in the claim's `support`. Then make the newness visible at these points, and only these:

1. **Right after the pain (first scene, within about three seconds of the pain line):** one sentence that says it is new and what it changes for this task, such as "ChatGPT's new update turns this into one paste." / 「ChatGPT 刚更新的功能，把这件事变成粘贴一次。」 Add a small on-screen label such as "NEW in <product>". Never open the video with the announcement itself.
2. **At the AI handoff result:** name the new capability by what the viewer now sees, not by its marketing name alone, such as "New in GPT-6: not just text. A table, and a chart." Mark the reveal with a short "NEW" stamp and sound.
3. **When a second new capability appears:** flag it once, such as "Here's the new trick: ask it to build a calculator."
4. **In the next action:** state current access from the official source with its boundary ("rolling out to all plans", "beta, US only").
5. **Cover and title:** include the product or feature name and one concrete change.

Every "new" must be followed by what changed; never say "new" or "just launched" without it. Do not claim it is better than the previous version unless a source supports that comparison. When the feature is not new, skip this section rather than implying novelty.

Choose one concrete example thread before writing scenes. Reuse its task object, decision, unfinished item, owner, date, and source artifact wherever those concepts appear. The new workflow must show the exact handoff: direct workspace search, file import, upload, connection, prompt, or capture action supported by evidence.

The example is not an appendix. Introduce it in the old workflow, carry it through the AI output, turn it into a downstream action, and use the same item for human verification.
