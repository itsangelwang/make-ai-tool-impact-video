# Pacing and review

## Narration capacity

Treat display completion and speakability as different constraints.

- Target roughly 150–190 Han characters for a 55–65 second video with readable transitions.
- Target 3–4 Han characters per second per spoken cue; flag any cue above 4.2.
- For English, target roughly 90–135 words: use 90–105 for an intentionally fast, energetic delivery with readable transition gaps, and 105–135 for a calmer delivery. Flag a cue above 2.7 words per spoken second.
- End a cue before a readable chapter transition begins.
- Preserve a short pause after the last spoken word and a stable hold after character animation completes.
- Cut narration that merely repeats an obvious action before extending duration.

For silent reviews, captions represent the intended narration and must still be speakable at natural speed.

Use this `timeline.json` shape with `scripts/audit_timeline.py`:

```json
{
  "duration_sec": 60,
  "captions": [
    {"start_sec": 0, "end_sec": 3.5, "text": "明天要开会，却要翻五份旧记录。"}
  ],
  "transitions": [
    {"start_sec": 7.5, "end_sec": 9, "label": "先看以前怎么做", "readable": true}
  ]
}
```

## Caption behavior

- Split by visual beat, not punctuation alone.
- Reveal Chinese characters or English words sequentially, then hold the completed phrase. Never animate English letter by letter.
- Adapt stagger to phrase length; long phrases may reveal faster but may not require faster speech.
- Highlight complete semantic terms, never random character intervals.
- Use the cool accent for the product and AI actions; use the warm accent for pain, unfinished work, risk, and human responsibility.
- Enlarge meaningful terms as a group: the tool name, task object, changed step, example value, and verification fields.
- Keep ordinary text neutral and captions inside the platform-safe lower region.

## Scene rhythm

Use rhythm in waves:

- Accelerate repetitive clicks, opening, importing, searching, and sorting.
- Slow down for the product promise, AI output, concrete example, decision, and responsibility boundary.
- Give every readable chapter transition a dedicated full-frame background for about 1.2–1.5 seconds.
- Do not stack two transitions with the same color, wording, and communication purpose. Replace the second with an object handoff or internal morph.
- A transition must finish before the incoming scene becomes visible.
- Build every consequential beat as enter → act → stable result. Do not cut immediately after the action.
- Reserve at least 1.2 seconds of stable result hold for a simple state and roughly 1.8–2.5 seconds for a product screen, generated output, evidence comparison, or responsibility boundary.
- If the viewer cannot inspect the state at normal playback speed, remove secondary text, split the beat, or extend the review. Do not solve overload by accelerating captions.
- Audit the second half independently; dense explainers often become faster after the product handoff even when the opening is readable.

## Token- and compute-efficient review

Use progressive review by default:

1. Render stills for composition, hierarchy, and safe-area checks.
2. Render 5–15 second clips for disputed motion, clicks, transitions, caption timing, and camera focus.
3. Render the full video only after the local clips establish the interaction and pacing direction, or when a global timeline change requires a continuity check.

Do not repeatedly render or re-analyze an unchanged full composition. Suppress verbose renderer progress when possible and report only failures, output paths, duration, and QA findings. Reuse representative frames for unchanged components. A local clip approval does not replace the final full-video audit before delivery.

## Review audit

Watch once without pausing and answer:

1. Can the first product screen be read before it changes?
2. Does every spoken cue describe the object currently visible?
3. Can each cue be spoken aloud before the next cue or transition?
4. Does every page answer one distinct question?
5. Does each upstream output visibly become the next page's input?
6. Are “draft,” “source,” “import,” “owner,” and “deadline” concrete on first use?
7. Is the AI/human division visible without reading the headline twice?
8. Are product UI, explanatory graphics, and generated illustration clearly distinguishable?
9. Are zooms attached to consequential details rather than decoration?
10. Can a viewer recount before, changed step, after, human check, and fit?

After any timing, script, voice, or visual-direction change, invalidate the previous review and inspect the full video again.

## Narration and regression checks

Reuse a previously accepted voice and documented auditions when the user has not changed the preference. Generate complete semantic sentences, not isolated caption fragments, and map the audio to the canonical timeline. Check each clip's natural duration before assembling; do not cut spoken words or stretch audio to conceal an overfull cue. Speech, action, and caption must describe the same state, including matching section names. User authorization to proceed after QA remains valid when that condition is satisfied.

Final QA must inspect the entire sequence as well as changed frames: empty deliverable → manual workload → substantial handoff → AI result → persistent same-document revision → human check → same exported file. Record what was actually verified; frame sampling or decoding is not equivalent to watching the full video or listening to the narration.

## Expressive audio and scoped revisions

For an energetic short-video voice, direct sentence-level emphasis, contrast and pitch variation, then audition one representative segment. Fast delivery alone is insufficient. Reuse accepted unchanged cues; regenerate only affected sentences. Preserve naturally spoken words and fit visual timing around measured audio.

Make typing sound like varied key presses, with brief pauses and a distinct return key, synchronized to human entry. AI generation should not sound like a person typing. Avoid piercing beeps. Keep music and operation sounds below speech; a gentle music dip and return can mark a chapter without an unrelated transition sweep. Use `scripts/generate_original_bgm.py` for an original configurable bed when appropriate; listen to the mix before approval.

If the requested workflow needs more than 75 seconds, first remove repetition, then explicitly record a justified duration exception in QA. Do not claim the default duration validator passed. A second model or tool should first improve one disputed 5–15 second segment from source and frames, preserving approved facts, voice and assets before expanding the scope.
