# Brand ending

Add a brand ending by default. Keep it separate from the fit/readiness conclusion so the editorial judgment does not look like a product advertisement.

Choose the brand in this order:

1. The user asks for no brand: omit the brand card.
2. The user supplies their own name, slogan, or logo: use exactly what they supplied; ask about anything missing instead of inventing it.
3. Otherwise: use the `ACEMODE` preset below.

Presets:

- `ACEMODE` (default)
  - Name: `ACEMODE`
  - Slogan: `10x Faster. Reclaim Your Time.`
  - No supporting line on the card.
  - Spoken by default: add a final narration cue with `text` `ACEMODE. 10x Faster. Reclaim Your Time.` and `voice` `[confident] AceMode. 10x faster. Reclaim your time.` so it is pronounced "Ace Mode".

Preserve the exact user-supplied spelling, capitalization, punctuation, logo, and slogan. Do not normalize them or add supporting lines unless requested. Keep the brand card to roughly 3–4 seconds. Use a distinct full-frame background, restrained brand glow, and character or word-level bounce. Do not place factual product claims on the brand card.

Configure the card with the `brand` object in `story.json` (`name`, `slogan`, optional `line`, `start_sec`, `end_sec`); the template renders it as a full-frame card. Place it after the `next-action` scene and include its 3–4 seconds in `duration_sec` and the total duration checks. Set `brand` to `null` to omit it. Do not hardcode a brand into the template components.

The ACEMODE ending is spoken by default; other brands are visual only unless the user asks for a spoken ending. For a spoken ending, include the brand and slogan as the last canonical narration cue and measure it. Start the voice about 0.1 seconds after the card appears and keep the card until the voice finishes, within the 4-second limit; do not clip the last word. Hide the caption bar while the brand card is on screen because the card already shows the same words; the cue still belongs in the caption file.
