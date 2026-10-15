# English-market adaptation

Use this reference for English-speaking audiences. Default to US English unless the user names another market.

## Write natively

- Adapt the story; do not translate Chinese copy sentence by sentence.
- Open with a recognizable task and consequence: “Tomorrow's project meeting. Five old notes. What still needs a follow-up?”
- Use contractions, short clauses, and concrete workplace language. Prefer “prep brief,” “open action item,” “owner,” and “due Friday” over abstract productivity language.
- Keep one named example throughout. Use locally natural names, month-first dates for the US, and English product UI labels.
- Avoid announcer copy, startup hype, unexplained AI jargon, and unsupported time-saving claims. For a new feature, say it is new right after the pain, not as the opener ("OpenAI just dropped…"); see "Introduce what is new" in [story-contract.md](story-contract.md).

## Pace and captions

- Target roughly 90–135 spoken English words for 55–65 seconds, including deliberate pauses; the 90–105 range suits the default energetic Fish Audio delivery with readable transitions.
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
- Default to Fish Audio with the approved preset: `scripts/fish_audio_tts.py --preset en-sawyer` (Fish Official "Sawyer", US male, model `drama-3`, temperature `0.85`, speed `1.08`). Skip auditions and reuse it unless the user asks for a different voice. To search for another voice, prefer Fish Official voices (author "Fish Official") and avoid community voices that imitate real people or characters.
- Use OpenRouter or Deepgram only when Fish Audio is unavailable, and require a fresh voice approval.

### Expressive delivery (Fish Audio S2 models)

The approved style follows the story's emotional arc instead of one flat or uniformly excited tone:

- Pain hook: `[frustrated]`. Question: `[curious]`. AI handoff and result: `[excited]`. Draft caveat and human check: `[calm]`. Next action: `[confident]`.
- Put one emotion tag at the start of the sentence it controls; at most one emotion change per cue. Put `[emphasis]` directly before the word to stress, at most once per cue.
- Write spoken English: short beats ("Now?"), contractions, and the occasional natural interjection ("And boom,"). Any word that is spoken must also appear in the caption.
- Put tags only in a cue's optional `voice` field in `timeline.json`; keep `text` clean for captions. `audit_timeline.py` fails if `voice`, minus its tags, does not match `text`. Synthesize each cue from `voice` when present, otherwise from `text`. See `examples/en-meeting-brief/timeline.json`.
- Tags use square brackets on S2 and `drama-3` models; parenthesis tags are for the retired S1 model. `drama-3` honors the same tags without reading them aloud.
- Synthesize one file per cue and measure each before final timing. `drama-3` is more theatrical than `s2.1-pro`: a long single take runs much slower, while per-cue takes stay close to the planned pace. Fit captions, scenes, and transitions to the measured audio rather than stretching speech.
- Fix pronunciation in `voice`, not in `text`: the audit compares them case-insensitively and ignores punctuation, so `AceMode` in `voice` reads as "Ace Mode" while the caption keeps `ACEMODE`.

### Other providers

- For OpenRouter, audition `deepgram/flux-tts:free` first while its free alias is available. Use the dedicated speech endpoint, keep `OPENROUTER_API_KEY` out of files and logs, and generate only an 8–12 second passage until the user approves the voice. Shortlist `flux-hannah-en`, `flux-heather-en`, and `flux-wes-en`. Treat the generic free text router and Flux TTS as separate models; query the live catalog before every audition because free aliases can change.
- For Deepgram Flux TTS, shortlist `flux-hannah-en` (thoughtful storytelling), `flux-heather-en` (engaging), and `flux-wes-en` (warm). Audition the same 8–12 second passage for comparison.
- For Deepgram or OpenRouter, start at speed `0.95` or `1.0` and expressivity `0` or `1`. With any provider, do not fix an overlong script by accelerating it beyond the approved preset speed.
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
7. For a new feature, does the viewer learn it is new within the first scene, and what exactly is new?
