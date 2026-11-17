# Pacing and review

## Narration capacity

Treat display completion and speakability as different constraints.

- Roughly 90–135 words fits 55–65 seconds. Treat the count as a warning, not a tone choice: set timing from the measured narration, then give each action, result hold, and pause the time it needs. Flag a cue above 4.5 words per spoken second (about 3 on average). Once a cue is fitted to its measured audio, its pause is the real one, so only the speed is checked.
- End a cue before a readable chapter transition begins.
- Preserve a short pause after the last spoken word and a stable hold after character animation completes.
- Cut narration that merely repeats an obvious action before extending duration.

For silent reviews, captions represent the intended narration and must still be speakable at natural speed.

Use this `timeline.json` shape with `scripts/audit_timeline.py`:

```json
{
  "duration_sec": 60,
  "captions": [
    {"start_sec": 0, "end_sec": 3.5, "text": "Thursday's meeting, and five old notes to dig through."}
  ],
  "transitions": [
    {"start_sec": 7.5, "end_sec": 9, "label": "The old way", "readable": true}
  ]
}
```

## Caption behavior

- Split by visual beat, not punctuation alone.
- Reveal words sequentially, then hold the completed phrase. Never animate letter by letter.
- Adapt stagger to phrase length; long phrases may reveal faster but may not require faster speech.
- Highlight complete semantic terms, never random letter intervals.
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

## Self-check before every review (required)

The user should not have to find problems one at a time. Before showing any review, key-frame sheet, or render, go through the video scene by scene as a viewer who has never used the tool, then watch it once without pausing. Answer every question, fix what you find, and write the answers with what you changed in the review's **Self-check** section. The list is a floor: also note anything else a newcomer could trip on, and if you found nothing, say what you checked.

**Story**

1. **Words match the screen.** Every spoken line and caption describes what is on screen at that moment: the same GIF version, the same screenshot, the same section names.
2. **One causal line.** Each scene answers one question and carries one causal line; cut detours, and give the human check more time. Each upstream output visibly becomes the next scene's input.
3. **Causes, not symptoms.** When something goes wrong, say the cause ("it starts on OPEN and flips late, then loops", not only "it shows OPEN"). State a fix as what worked in the test, not as the only rule.
4. **Nothing unexplained.** Every name, term or symbol (the example's name, an @mention, a button) is explained the first time it appears, and not shown before then. "Draft," "source," "import," "owner," and "deadline" show their concrete object on first use.
5. **A fast, clear opening.** The first seconds show the world of the example (a café needs a coffee cup), not only the object, and confirm what the cover promised. The hook makes sense without knowing the product; for a new feature, the viewer learns in the first scene what exactly is new.
6. **The before is real.** The "before" scene names the AI tools that already did this job, checked on their official pages, and says only the gap that remains.
7. **Tested where viewers will use it.** The claim was tested in the product surface viewers will use (for example the plain chat, not an agent mode) and checked on the downloaded result, not the in-app preview.
8. **Recountable.** A stranger can say what this is and why it matters to them, and can recount before, changed step, after, human check, and fit. The AI/human division is visible without reading the headline twice.

**Screen**

9. **Every element earns its place.** One focal point at a time; cut repeats (a big logo in the middle when the header already shows it).
10. **Made by a person, and finished.** Mature tone: no childish shapes, over-bouncy springs, emoji, or list-in-a-box layouts. No default fonts, flat fills, or frames that sit still; soft layered shadows instead of one heavy drop shadow. No AI tells (see "Look made by a person, not by AI" in `visual-system.md`).
11. **Physical sense; nothing covers anything.** Nothing floating, nothing hidden that should be seen. Marks never cross text, a corner card never covers a headline, and no source captions or transitions leak into crops.
12. **Clear meaning.** Each color carries one meaning and backgrounds never drift toward grey. Product UI, explanatory graphics, and generated illustration are clearly distinguishable. Zooms land on consequential details, not decoration.
13. **Readable at speed.** The first product screen can be read before it changes, each caption can be read once at phone size, and each cue can be spoken aloud before the next cue or transition.

**Sound and wording**

14. **Sounds like a person.** A US office worker would say these lines aloud; the voice is conversational at normal speed, without forced enthusiasm. No dead air; captions and voice in sync; audio balanced.
15. **Consistent and keepable.** The example keeps the same names, dates, owners, and artifacts. No dated labels or promises we cannot keep; licenses recorded; the ending call to action works.

For a big visual change, send the user a key-frame sheet (one or two stills per scene, quarter size) and get an OK before the full render. Render the full video once, then sample frames around every transition for problems that only show in motion. After any timing, script, voice, or visual-direction change, invalidate the previous review and inspect the full video again.

## Narration and regression checks

Reuse a previously accepted voice and documented auditions when the user has not changed the preference. Generate complete semantic sentences, not isolated caption fragments, and map the audio to the canonical timeline. Check each clip's natural duration before assembling; do not cut spoken words or stretch audio to conceal an overfull cue. User authorization to proceed after QA stays valid as long as speech, action, and caption still match (self-check 1).

Final QA must inspect the entire sequence as well as changed frames: empty deliverable → manual workload → substantial handoff → AI result → persistent same-document revision → human check → same exported file. Record what was actually verified; frame sampling or decoding is not equivalent to watching the full video or listening to the narration.

## Expressive audio and scoped revisions

For an energetic short-video voice, direct contrast and emphasis through the words and a continuous scene take (see "Natural delivery" in `english-market.md`), then audition one representative segment. Fast delivery alone is insufficient. Reuse accepted unchanged cues; regenerate only affected scenes. Fit visual timing around measured audio: `fit_timeline_to_audio.py`, then `retime_story.py` to move every scene, transition and beat with its words. Do not run them over a scene that plays a real clip with its own sound: packing the cues and rescaling the scene cuts the clip before its payoff. Place those cues by hand from the measured clip lengths and shift that scene as one block.

Music: prefer a real royalty-free track over a synthesized bed; viewers found the synthesized score thin and sleepy. Find 2–3 candidates in different styles (for example on Pixabay Music), let the user preview them in the browser, and download only the one they pick, with their permission. Record title, author, page URL, license and the section used in `<project-dir>/music/SOURCE.md`. Use the track's structure: start it so its first full-energy section lands on the AI handoff, and splice its real ending under the brand card (`mix_story_audio.py --ending-jump`, a whole number of bars) instead of fading out mid-phrase. Never cut the music to silence at a transition; viewers hear that as a dropout. Prefer Pixabay tracks whose page shows no Content ID notice, so uploads are not claimed. Match the cut to the music: measure the BPM, then move scene cuts, stage swaps, chapter cards and the brand card to the nearest beat (nudges of 0.3 s or less; narration stays put), and start the track so a downbeat lands on the main chapter card. Shape the music level to the story (quieter under the pain, a lift at the handoff, fullest under the result, a dip at the human check, a lift into the brand card), and duck it by about 10 dB under any dialogue inside a product clip, which `mix_story_audio.py` does not know about. When the user says the music does not fit, ask which kind: style, beat sync or energy arc. `scripts/generate_story_audio.py music` remains a fallback when no track can be used.

Sound effects: give each one a visible cause, keep it brief and below the narration, and place it on the exact frame of its action (a click on the button press, key taps only on visible typing, a soft tone on a completed state); a sound never justifies a faster cut. Use recorded sounds the user has previewed (see `references/sound-library.md`); viewers found most synthesized effects odd, except the mouse clicks. When a sound is judged odd, replace it with a better recorded one rather than dropping it. Recorded typing should play only while text is visibly typed; AI generation should not sound like a person typing. Avoid piercing beeps. Limit which sounds play with `story.sfx` (a list of kinds; `true` plays all). A whoosh on each beat-synced cut helps; use "Simple Whoosh" (see `sound-library.md`) and start it about 0.12 s early so its peak hits the cut. The longer Thin Swoosh, played alone and quiet on a cut, was heard as a dull "deng". When the user calls a sound odd, list each sound's times and what is on screen so they can point at it.

Mix with `scripts/mix_story_audio.py`: speech near -18 dBFS RMS, music about 21 dB under speech and up in gaps, short pauses kept ducked so the music does not pump. Final loudness: about -16 LUFS integrated with true peak at or below -1.5 dB. Remotion's bundled FFmpeg can measure this with `-af loudnorm=print_format=json` (read `input_i` and `input_tp`) and can apply a `volume` correction while copying the video stream; it lacks `ebur128`, `volumedetect`, `asplit`, `sidechaincompress` and `alimiter`. Renders often come out near -16 LUFS with a true peak around 0 dB; lower only the peaks with `scripts/limit_peaks.py` (a look-ahead limiter, default ceiling -2.3 dBFS) instead of turning the whole mix down.

A second model or tool should first improve one disputed 5–15 second segment from source and frames, preserving approved facts, voice and assets before expanding the scope.
