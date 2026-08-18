# Pacing and review

## Narration capacity

Treat display completion and speakability as different constraints.

- Target roughly 150–190 Han characters for a 55–65 second video with readable transitions.
- Target 3–4 Han characters per second per spoken cue; flag any cue above 4.2.
- For English, target roughly 105–135 words and an average of 2.0–2.5 words per spoken second; flag a cue above 2.7 words per second.
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
