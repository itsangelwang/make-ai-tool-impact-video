# Story package contract

Create JSON with `schema_version: 1` and these required fields:

- `language`: BCP-47-style output language: `en-US` (default), `en-GB` or `en-AU`. Videos are English-only.
- `market`: intended audience market such as `US`, `GB` or `AU`.
- `tool`: `name`, `url`, `one_line_capability`.
- `audience`: one concrete role or life situation.
- `task`: one observable task, unchanged before and after.
- `before_steps`: 2–3 short steps.
- `friction`: the bottleneck the viewer recognizes.
- `ai_change`: one step the tool changes; do not claim it replaces the whole job.
- `after_steps`: 2–4 steps showing person → AI → person responsibility.
- `human_check`: a concrete verification, judgment, privacy, or accountability duty.
- `readiness`: one of `use-now`, `try-now`, `watch`, `future`.
- `next_action`: a small, reversible experiment consistent with readiness that is safe to try at work: use non-sensitive or made-up material, stay within the employer's rules and approved apps, and let the AI produce a draft the person reviews rather than sending, posting, or changing records on its own. When access needs a paid plan or an admin to turn the feature on, say so.
- `narration`: natural speech with no stage directions; length as in "Narration capacity" in [pacing-and-review.md](pacing-and-review.md).
- `coverage`: the existing-coverage check from [topic-check.md](topic-check.md): `checked_at`, `existing` (each `by` = `official` or `creator`, `url`, `shows`), `our_angle`, and `decision` (`make` or `change-angle`; `skip` fails validation).
- `brand`: optional; `null` or `{name, slogan, start_sec, end_sec}` for the brand card that follows the last scene. See [brand-system.md](brand-system.md).
- `scenes`: 5–7 objects with `id`, `type`, `purpose`, `start_sec`, `end_sec`, `headline`, `visual`, and `claim_ids`.

Use scene types `pain-hook`, `before-workflow`, `ai-handoff`, `after-workflow`, `before-after`, `human-check`, and `next-action`. Include at least five distinct types. Start at 0 and keep scenes contiguous; the duration target, including any brand card, is in section 6 of `SKILL.md`. Give every scene an explicit communication purpose.

The first scene must show the audience/task pain. Mention the product only after relevance is clear. Keep headlines short enough for two mobile lines.

## Introduce what is new

Treat a tool or feature as new when its official announcement is within the last 90 days, or when the user asks to highlight it. Record the announcement date in the claim's `support`. Then make the newness visible at these points, and only these:

1. **Right after the pain (first scene, within about three seconds of the pain line):** one sentence that says it is new and what it changes for this task, such as "ChatGPT's new update turns this into one paste." Add a small on-screen label such as "NEW in <product>". Never open the video with the announcement itself.
2. **At the AI handoff result:** name the new capability by what the viewer now sees, not by its marketing name alone, such as "New in GPT-6: not just text. A table, and a chart." Mark the reveal with a short "NEW" stamp and sound.
3. **When a second new capability appears:** flag it once, such as "Here's the new trick: ask it to build a calculator."
4. **In the next action:** state current access from the official source with its boundary ("rolling out to all plans", "beta, US only").
5. **Cover and title:** written together as one promise that names the product or feature and one concrete change; see [packaging.md](packaging.md).

When the release upgrades something the product already did, say "upgraded" instead of "new" and make the delta itself the evidence: an old-vs-new value bar with its source, the real UI showing the new value (zoom on a label such as "720p · 0:15"), and, for a longer or faster output, a progress marker at the old limit that the result visibly passes (see "Lessons from the Google Vids video" in [visual-system.md](visual-system.md)).

Every "new" must be followed by what changed; never say "new" or "just launched" without it. Do not claim it is better than the previous version unless a source supports that comparison. When the feature is not new, skip this section rather than implying novelty. For a missed-it backup topic, say once near the start how long it has been available ("It's been in ChatGPT since March, and most people never found it").

Choose one concrete example thread before writing scenes. Reuse its task object, decision, unfinished item, owner, date, and source artifact wherever those concepts appear. The new workflow must show the exact handoff: direct workspace search, file import, upload, connection, prompt, or capture action supported by evidence.

Carry the same object literally: a prompt shown on screen must be the prompt of the clip that plays next, not one from another test.

The example is not an appendix. Introduce it in the old workflow, carry it through the AI output, turn it into a downstream action, and use the same item for human verification.

If the user removes the next-action scene, keep their decision: `validate_package.py` will report the missing `next-action` type, so record the user's choice in the review and QA notes and move the access facts (plan, quota, link) into the post copy rather than relabeling another scene to pass the check.
