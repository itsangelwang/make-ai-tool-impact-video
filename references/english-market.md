# English-market adaptation

Use this reference for English-speaking audiences. Default to US English unless the user names another market.

## Write natively

- Adapt the story; do not translate Chinese copy sentence by sentence.
- Open with a recognizable task and consequence: “Tomorrow's project meeting. Five old notes. What still needs a follow-up?”
- Use contractions, short clauses, and concrete workplace language. Prefer “prep brief,” “open action item,” “owner,” and “due Friday” over abstract productivity language.
- Keep one named example throughout. Use locally natural names, month-first dates for the US, and English product UI labels.
- Avoid announcer copy, startup hype, unexplained AI jargon, and unsupported time-saving claims.

## Pace and captions

- Target roughly 105–135 spoken English words for 55–65 seconds, including deliberate pauses.
- Keep the average near 2.0–2.5 words per spoken second and flag individual cues above 2.7 words per second.
- Reveal captions by word or short phrase, not letter by letter. Use 3–7 words per visual beat and no more than two mobile lines.
- Use sentence case. Reserve all caps for a one- or two-word label.
- Highlight complete meaning units only: the task, changed step, example value, owner, due date, and human check.

## Visual language

- Use native 9:16 full-frame composition without embedded black bars.
- Prefer Inter, Avenir Next, SF Pro, Arial, or another clean Latin typeface. Do not use Chinese handwriting fonts for English captions.
- Put less text on screen than in the Chinese version. Let product UI, icons, cursor actions, and object handoffs carry the explanation.
- Use push-ins or detail zooms only to point at consequential UI or evidence.
- Keep critical text and controls inside platform-safe regions; review the actual mobile crop.

## Voice

- Prefer a conversational American voice that sounds like a capable coworker, not an ad read or customer-service bot.
- For OpenRouter, audition `deepgram/flux-tts:free` first while its free alias is available. Use the dedicated speech endpoint, keep `OPENROUTER_API_KEY` out of files and logs, and generate only an 8–12 second passage until the user approves the voice. Shortlist `flux-hannah-en`, `flux-heather-en`, and `flux-wes-en`. Treat the generic free text router and Flux TTS as separate models; query the live catalog before every audition because free aliases can change.
- For Deepgram Flux TTS, shortlist `flux-hannah-en` (thoughtful storytelling), `flux-heather-en` (engaging), and `flux-wes-en` (warm). Audition the same 8–12 second passage for comparison.
- Start at speed `0.95` or `1.0` and expressivity `0` or `1`. Do not fix an overlong script by accelerating it.
- Flux TTS and `/v2/speak` are Early Access. If access or stability fails, use Aura-2 such as `aura-2-andromeda-en` or `aura-2-arcas-en`, disclose the fallback in the review, and require a fresh voice approval.
- Never commit or print `DEEPGRAM_API_KEY`. Keep generated voice files out of reusable templates unless redistribution rights are known.

## Review questions

Ask a native-English review pass:

1. Would a US office worker say this aloud?
2. Does the hook make sense without knowing the product?
3. Can each caption be read once at phone size?
4. Do the spoken words describe what is currently visible?
5. Does the example use consistent names, dates, owners, and artifacts?
6. Does the voice sound conversational at normal speed, without forced enthusiasm?
