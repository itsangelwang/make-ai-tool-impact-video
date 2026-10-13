# Brand ending

Add a brand ending by default. Keep it separate from the fit/readiness conclusion so the editorial judgment does not look like a product advertisement.

Choose the brand in this order:

1. The user asks for no brand: omit the brand card.
2. The user supplies their own name, slogan, or logo: use exactly what they supplied; ask about anything missing instead of inventing it.
3. Otherwise: use the `ACEMODE` preset below.

Presets:

- `ACEMODE` (default)
  - Name: `ACEMODE`
  - Slogan: `10x Faster, Log Off Earlier.`
  - Supporting Chinese line: `把时间留给更重要的事`
  - Supporting English line: `Make time for work that matters.`

Preserve the exact user-supplied spelling, capitalization, punctuation, logo, and slogan. Do not normalize them or add supporting lines unless requested. Keep the brand card to roughly 3–4 seconds. Use a distinct full-frame background, restrained brand glow, and character or word-level bounce. Do not place factual product claims on the brand card.

Configure the card with the `brand` object in `story.json` (`name`, `slogan`, optional `line`, `start_sec`, `end_sec`); the template renders it as a full-frame card. Place it after the `next-action` scene and include its 3–4 seconds in `duration_sec` and the total duration checks. Set `brand` to `null` to omit it. Do not hardcode a brand into the template components.

By default the card is visual only; add the brand and slogan to narration only when the user requests a spoken ending.

When the user requests a spoken brand ending, include the brand and slogan in the canonical narration and measure the complete spoken cue. Let the card last long enough for the voice to finish before fading; do not silently omit the ending or clip its last word.
