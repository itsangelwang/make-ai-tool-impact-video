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
- Give every readable chapter transition a dedicated full-frame background for about 2.2 seconds (at least 2.0): the label must be fully on screen and still for over a second. Pause the narration while the card is up.
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

For an energetic short-video voice, direct contrast and emphasis through the words and a continuous scene take (see "Natural delivery" in `english-market.md`), then audition one representative segment. Fast delivery alone is insufficient. Reuse accepted unchanged cues; regenerate only affected scenes. Fit visual timing around measured audio: `fit_timeline_to_audio.py`, then `retime_story.py` to move every scene, transition and beat with its words.

Music: prefer a real royalty-free track over a synthesized bed; viewers found the synthesized score thin and sleepy. Find 2–3 candidates in different styles (for example on Pixabay Music), let the user preview them in the browser, and download only the one they pick, with their permission. Record title, author, page URL, license and the section used in `<project-dir>/music/SOURCE.md`. Use the track's structure: start it so its first full-energy section lands on the AI handoff, and splice its real ending under the brand card (`mix_story_audio.py --ending-jump`, a whole number of bars) instead of fading out mid-phrase. Never cut the music to silence at a transition; viewers hear that as a dropout. `scripts/generate_story_audio.py music` remains a fallback when no track can be used.

Sound effects: give each one a visible cause, and use recorded sounds the user has previewed (see `references/sound-library.md`); viewers found most synthesized effects odd, except the mouse clicks. When a sound is judged odd, replace it with a better recorded one rather than dropping it. Recorded typing should play only while text is visibly typed; AI generation should not sound like a person typing. Avoid piercing beeps. Limit which sounds play with `story.sfx` (a list of kinds; `true` plays all).

Mix with `scripts/mix_story_audio.py`: speech near -18 dBFS RMS, music about 21 dB under speech and up in gaps, short pauses kept ducked so the music does not pump. Final loudness: about -16 LUFS integrated with true peak at or below -1.5 dB. Remotion's bundled FFmpeg can measure this with `-af loudnorm=print_format=json` (read `input_i` and `input_tp`) and can apply a `volume` correction while copying the video stream; it lacks `ebur128`, `volumedetect`, `asplit`, `sidechaincompress` and `alimiter`.

If the requested workflow needs more than 75 seconds, first remove repetition, then explicitly record a justified duration exception in QA. Do not claim the default duration validator passed. A second model or tool should first improve one disputed 5–15 second segment from source and frames, preserving approved facts, voice and assets before expanding the scope.
