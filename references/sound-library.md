# Sound library

Recorded sound effects and music the user has previewed and approved. All are from Pixabay under the Pixabay Content License (free for commercial use, no attribution). Do not commit the audio files to this repository: the license does not allow redistributing them as standalone files. Download each one into the project (with the user's permission), record it in `<project-dir>/sfx-source/SOURCE.md`, and convert it with `scripts/prepare_sfx.py`.

| Template name | Used for | Sound (page) | Cut (s) |
|---|---|---|---|
| `return`, `key-2` | Every mouse click: send button, hang-up | Mouse click by MatthewVakaliuk73627 — https://pixabay.com/sound-effects/film-special-effects-mouse-click-290204/ | 0.03–0.20 (press and release) |
| `swish` | Scene and card transitions, push-ins, file drag | Thin Swoosh by Universfield — https://pixabay.com/sound-effects/film-special-effects-thin-swoosh-352756/ | 0.08–1.12 |
| `pop` | Icons, chips and cards appearing | UI Pop Sound — https://pixabay.com/sound-effects/film-special-effects-ui-pop-sound-316482/ | 0.03–0.45 |
| `typing` | Visible typing (plays only for the typing span) | Keyboard Typing Sound Effect — https://pixabay.com/sound-effects/film-special-effects-keyboard-typing-sound-effect-335503/ | 0.40–3.45 |
| `callend` | A call ending | End Call — https://pixabay.com/sound-effects/household-end-call-120633/ | whole clip |
| `coin`, `notify` | A result or message appearing | Soft Notification by Universfield — https://pixabay.com/sound-effects/film-special-effects-soft-notification-131438/ | 0.06–0.80 |
| `stamp` | A stamp landing | Stamp — https://pixabay.com/sound-effects/film-special-effects-stamp-81635/ | 0.05–0.28 (first hit) |
| `tick` | Row highlights, scrubbing | Soft UI Pop – light, minimal click by humordome — https://pixabay.com/sound-effects/technology-soft-ui-pop-light-minimal-click-451232/ | 0.00–0.28 (first click) |

The synthesized click is the fallback only; the user asked for a real recorded click. Rejected as odd-sounding: Positive Notification, Traditional Stamp, UI Checkbox Tick, and the synthesized swish, pop, coin, stamp, tick and uh-oh.

```bash
python3 <skill-dir>/scripts/prepare_sfx.py --out <project-dir>/video/public/audio/sfx \
  swish=<project-dir>/sfx-source/swoosh.mp3:0.08:1.12 pop=<project-dir>/sfx-source/pop.mp3:0.03:0.45
```

Music used so far: "Corporate Upbeat" by NastelBom (https://pixabay.com/music/upbeat-corporate-upbeat-323642/): light 16 s intro, full energy from 0:16, breakdown 1:04–1:20, ending at 1:52–1:54; 2 s bars. Starting it at 0:00 puts the full-energy entry on a handoff about 16 s in; `--ending-jump 60` lands its ending on a brand card near 50 s.
