# Vertical motion system

Build natively at 1080×1920 and 30 fps. Use a warm near-white background, near-black text, one cool accent, and one warm accent. Avoid branded imitation, glassmorphism, neon HUDs, generic particles, and decorative camera motion.

## Reusable scenes

- `pain-hook`: tangible backlog, repetitive clicks, or scattered inputs; reveal the payoff within three seconds.
- `before-workflow`: stack 2–3 manual steps and make the bottleneck visible.
- `ai-handoff`: compress or route the stack into the tool; distinguish real UI from explanatory graphics.
- `after-workflow`: show the changed order and fewer handoffs, without unsupported clocks or multipliers.
- `before-after`: compare the same task and person, not unrelated stock imagery.
- `human-check`: pause motion and foreground the approval, correction, privacy, or judgment step.
- `next-action`: resolve into one reversible experiment and readiness label.

## Every screen: reading load, pacing, and variety

Check every scene, not only the whole video. Render a still at each scene's busiest moment and read it at phone size.

- **One idea per screen.** Keep authored on-screen text (label, headline, card and beat labels; captions and real UI excluded) at or under 18 words per scene. If a screen needs more, split it into beats that appear one at a time, in sync with the words that name them.
- **Animate instead of writing.** Turn a list into a `flow` of icons, a changed value into a `fix` (strike and replace), a long screenshot into `focus` bands that light one row at a time, a "find it in the recording" step into a `scrub`. Hide the human-check and next-action text boxes by leaving `visual` empty when beats already carry the point.
- **Show the real thing, not a word for it.** When a screen can show what the thing actually looks like, simulate it instead of writing its name in a box: a phone lock screen filling with notifications for "too much news", a channel card with real thumbnails and a pointer clicking Follow for "follow us", the real product UI for a feature. Use text only for what a picture cannot carry.
- **No cheap icons in place of words.** Do not swap text for emoji, clip-art, or a row of generic icons in boxes; they look cheap and still need reading. Icons are fine when they are simple line drawings with one stroke width and the video's colors, and better when they move (a stopwatch hand that turns, a check that draws itself). If no good picture exists, leave the point to the narration.
- **Composition reads top to bottom.** Each screen reads in one order: what this screen is about (eyebrow or headline) at the top, the one thing to look at in the middle, the caption at the bottom. Give the screen one visual focus and no competing headings: when reusing footage from another video, crop out its own headline, labels and captions so only this screen's set remains, and zoom so the action fills the frame instead of floating in empty space.
- **Open fast.** The first frame must already show the situation, and something new should appear within the first second; take the cover once the opening hook is complete (the template's `npm run cover` uses frame 60, about 2 seconds in), never from an empty frame.
- **Keep the screen moving, but readable.** Something visible should change at least every 4 seconds; a scene that sits still longer loses the viewer. Keep each new state up for at least 1.2 seconds so it can be read.
- **Vary the form.** Mix real UI, icon flows, audio scrubbing, corrections, role strips, focus bands, stamps, and chips. Do not use the same form in two neighboring scenes.
- **One color per object.** Icons in the same row must not share a color. The template gives each kind of object a fixed color for the whole video (recording teal, table violet, email amber, date pink, person blue, document green); keep it when the object reappears so the viewer can follow it. Override with `palette.objects` or an item's `color`.
- **Calm, harmonious color.** Light tinted backgrounds, white cards, one phase accent per screen, and object colors only on icons. Avoid muddy browns and olive, neon on neon, red text on a coral background, and more than three saturated colors on one screen.
- **Layered type, not all bold.** Use four levels: an eyebrow (small spaced capitals with a colored dot), one headline (semibold, about 700, with one key word in the accent color via `*word*`), labels (medium, 500–600), and notes (regular, 400–450, muted). Only one element per screen gets the heaviest weight (800+), usually a single display word; captions stay at 600 with only emphasized words heavier. Check that the font really has these weights on the rendering machine: when the named font is missing, the browser falls back to another one and every weight can look the same heavy black. The template puts the system font (SF Pro on a Mac) first for English for this reason. Look at a still and ask whether you can tell headline, label and note apart at a glance; if not, step the weights down.
- **No lonely words.** Never leave one word alone on a line in a headline, card, or caption. The template balances headline and caption lines automatically; rewrite a headline if it still breaks badly.
- **Nothing covers anything.** No element may hide another element's text or the detail it points at. Put callouts beside or above their target without covering it or a column header, put stamps in empty corners, keep content above the caption zone, and make sure the incoming scene fully covers the outgoing one during a transition. Check stills in the middle of every transition as well as in the middle of every scene.
- **Each phase looks different.** The template themes scenes by phase: the problem (pain, before) on coral with a red-orange accent, what AI changes (handoff, after) on lavender with violet, the person's job (human check) on light blue with blue (the person color), and the try-it on mint with green. Chapter-card gradients run from a light tint to a deep, saturated tone of the same color; never darken a warm color toward brown. The eyebrow, headline accent, a large faint phase word in the background, and the progress-bar segment all take the phase color. Match each chapter card's `color` to the phase it opens. Override with `palette.phases`.
- **Transitions between phases.** Every scene change gets a short entrance (about 0.4 s) that cycles slide, circle wipe, and rise; set a scene's `enter` (`slide`, `wipe`, `rise`, `none`) to choose one. A phase change (before → AI handoff or after, after → human check) gets a readable full-frame chapter card from `story.transitions` (about 2.2 s, at least 2.0; ends at the next scene's start; no narration over it). Give each card `kicker` (a 1–2 word tag such as "NOW" or "YOUR TURN") and, whenever the phase change has a cause, `from` and `to` icon lists so the card shows the handoff (three notes become one table; a table becomes a date and a person to check) over a gradient background. Use at most two or three chapter cards, each with its own color and symbol; `check_story.py` requires one between before and after.
- **Progress bar.** The template draws a thin chapter progress bar at the top (one segment per scene, hidden on the brand card). Set `"progress": false` in story.json only when the platform already shows one.

`scripts/check_story.py` enforces the word limit and the 4-second rule (both in `scripts/limits.json`) and lists neighboring scenes that share a form.

## Story beats in story.json

The template turns these optional scene fields into the beats proven in the first English video. Times (`at_sec`) are seconds from the scene start; place them on the matching narration words after fitting the timeline to the audio. Run `scripts/check_story.py <project-dir>/video/src/story.json` before rendering.

- `new_feature` (pain hook): `{at_sec, date, name, accent, capability, items: [{icon, label}]}`. The pain stack yields to a card naming what is new, its official date, and up to three objects it produces.
- `new_tag`: short text such as `"New in ChatGPT"` shown as a NEW pill under the scene label.
- `shot`: a real screenshot region, `{src, source_width, crop: {x, y, w, h}, evidence, click, reveal, stamp, callout}`. Coordinates are source pixels. `click: {at_sec, x, y}` moves the cursor to the control and presses it; `reveal: {at_sec, frames}` wipes the result in; `stamp: {at_sec, label}` marks the new capability; `callout: {at_sec, x, y, title, note, until_sec}` points at the detail to check, with (x, y) just above it; set `until_sec` so it leaves when the focus moves on. Crop so product text reaches about 40 px. `evidence` labels the source, e.g. "REAL CHATGPT TEST".
- `roles`: `{at_sec, you: {icon, label}, ai: {name, outputs: [{icon, label}]}}`. One action from the person, outputs ticking off for the AI.
- `checks` with `checks_at_sec`: up to three `{icon, label}` items the person verifies.
- `plans`: `{at_sec, title, feature, icon, plans: [{name, on}]}` from the official source. Reads like a pricing table: `title` says whose plans ("ChatGPT plans"), `feature` heads the ✓/✕ column ("Audio uploads"), and included rows tick in turn. Prefer it to `access`, whose colored chips did not say what was included where.
- `access`: `{at_sec, label, plans: [{name, on}]}`, the older chip row; unavailable plans are struck through.
- `flow`: 2–4 `{icon, label, at_sec}` tiles with arrows, each appearing at its own time; labels are 1–2 words. Replaces text cards in any scene.
- `call_end`: `{at_sec, people: [name, name], timer, end_at_sec, file}` a generic video call (not any real product): two people, a running timer, a hang-up click at `end_at_sec`, then the saved recording slides out. Opens a story that starts from a meeting.
- `toast`: `{at_sec, icon, title, note, until_sec}` a system-style notification that slides down. Open with one so the first frame already shows the situation ("Call ended · Recording saved") and the first seconds move fast.
- `fix`: `{at_sec, label, wrong, right}`. The wrong value is struck through and the right one pops in.
- `scrub`: `{at_sec, length, file, ask, ask_at_sec}`. The recording's waveform player whose playhead jumps back and forth; `ask` pops above it (e.g. "Who said Thursday?"); `file` hangs the recording chip under it.
- `replay` and `send` (human check against the source): `replay: {at_sec, jump_sec, replay_sec, file, length, who, quote, marker}` shows the same recording player; at `jump_sec` the playhead jumps to the moment `who` said `quote`, and at `replay_sec` it rewinds there again. `send: {at_sec, label}` is a button the cursor clicks once the check is done. Put `jump_sec` on the narration that names the quote, and `send.at_sec` on "send". Use them instead of "Replay → Send" icon tiles.
- `tryit` (next action): `{consent: {at_sec, people: [a, b], ask, yes}, old: {at_sec, file, length}}`. The opening's call window returns small: one person asks (`"OK to record?"`), the other agrees (`"Sure!"`), and the recording dot starts; then the window slides away and the cursor drags an earlier recording into a ChatGPT-style box. `old.file` is a placeholder (`old-call-xxx.mp3`, length `xx:xx`), never a realistic name. Start `old` at least 1 s after `consent`.
- `shot.zoom`: `{at_sec, frames, from}` starts on a wide crop of the whole result (same aspect ratio as `crop`) and pushes in, so viewers see everything the tool produced before the detail. Pair it with `shot.summary`: `{at_sec, text, until_sec}`, one short line such as "5 action items · owners · dates", shown just below the screenshot so it never covers it.
- `shot.drag`: `{at_sec, frames, from, to, file, region, mask}` carries a file card in with the pointer and reveals the real attachment (`region`) on drop.
- `shot.type`: `{at_sec, frames, region, lines, mask}` uncovers the real typed text left to right, line by line, with a caret and key sounds.
- `shot.click` now hovers first (hand pointer and a glow), presses, and ripples; `shot.wait`: `{at_sec, frames}` shows neutral progress dots (never an imitation of the product's own loading screen).
- Build a product interaction as one flow, the way a person works: open → drag the file in → type the request → hover and click → wait → result in full → push in to the detail.
- `shot.focus`: `[{at_sec, y, h}]` source-pixel bands; everything else in the screenshot dims so one row is read at a time.
- `steps_at_sec`: times at which before/after step cards appear, instead of all at once.

Set `"sfx": true` in story.json after generating `public/audio/sfx` with `generate_story_audio.py sfx`; each beat then plays its matching swish, pop, stamp, or return. Icons come from `components/Icon.jsx`; add a new icon there rather than inlining SVG in a scene.

Write a custom scene component only for a beat these fields cannot express, such as a bespoke object handoff, and reuse the components in `components/Beats.jsx` inside it. `public/assets/example-ui.svg` is placeholder UI for the template; never ship it in a video.

## Lessons from the ChatGPT audio-upload video

The user asked for each of these; build them in from the start.

- **One object, one look.** Whatever the story follows (a recording, a file, a document) looks the same every time it appears: the same chip, icon, color, name and length, and the same waveform for audio. `RecordingChip` and the shared waveform do this for recordings in `call_end`, `scrub`, `shot.drag` (set `drag.length`), `replay` and `tryit`. Viewers should be able to tell it is one recording from the opening to the end.
- **Highlights stay whole.** A focus frame keeps all four sides visible, including on a screenshot's first or last row; the template keeps it inside the card. Crop so the last highlighted row ends inside the crop with a little margin.
- **Show the check, not its name.** For "verify before you act", animate the act (jump to the moment in the source, show what was said, correct the value, then click the action) rather than tiles labeled "Replay" and "Send".
- **Say whose plans.** A plan table names the product's plans and the feature, e.g. "ChatGPT plans" with an "Audio uploads" column.
- **No boxed text-and-icon cards for next steps.** The user rejected cards holding an icon, a number and a label, and cards with mini illustrations, as ugly and confusing. Animate a concrete moment with objects the viewer has already seen (`tryit`), or leave the step to the narration.
- **Placeholders for illustrative things.** A file, name or number that only illustrates (not evidence) uses an obvious placeholder such as `xxx`, so it cannot be mistaken for a real one. Keep fictional company names generic; check that they do not match a well-known brand.
- **Nothing jumps.** An element that appears later keeps its space from the start, so the rest of the layout does not shift when it arrives.

## Motion grammar

Give every transition a cause: stack, sort, compress, hand off, verify, or complete. Change hierarchy, scale, density, direction, or media every 2–4 seconds while preserving at least 1.2 seconds for important reading. Animate in the order task object → explanatory label → evidence → caption. Use one primary movement per beat.

Shape rhythm in waves rather than giving every scene the same pace. Accelerate repetitive operations such as opening, importing, searching, and sorting; slow down when showing the result, decision, evidence, or responsibility boundary. Carry a document, task, prompt, summary, or checkmark from one scene into the next so the downstream scene visibly receives the upstream output.

Use zoom only to direct attention to a consequential detail: the selected import file, the relevant product result, the unfinished task inside a summary, the source sentence used for verification, or the final output replacing a stack of inputs. Pair the zoom with a state change or highlighted evidence; avoid decorative push-ins that do not clarify the workflow.

When a chapter transition contains a readable label, give it a dedicated full-frame background for about 2.2 seconds. Do not layer a transition title over the outgoing or incoming scene. Hold the title stable long enough to read, then reveal the next scene; shorter overlays are reserved for nonverbal action handoffs.

End the outgoing caption before a readable transition begins. For captions revealed by semantic word groups, adapt the stagger to phrase length and preserve a stable fully revealed hold; never let the transition cover the final words. Place a full-frame transition entirely before the next scene boundary so the incoming scene starts unobscured.

Render captions once at composition root. Keep critical content inside 72 px horizontal and 120 px vertical safe margins. Reserve the lower 310 px for captions and platform controls.

## Show the work, not only the labels

When a workflow step describes a visible human action, prefer an embodied demonstration over a list of text cards. Keep the same person, task object, and workspace continuous while showing the action itself: opening files, moving the cursor, searching, highlighting, copying, dragging, checking, or approving.

For a three-step manual workflow, default to three consecutive beats in one stable scene:

1. Show the person performing the first action on the task object.
2. Move or zoom to the exact information being found or changed.
3. Show the result being transferred into the next artifact.

Use short on-screen labels to clarify the action, but do not make labels the primary evidence that the action occurred. Animate the causal objects: documents open, highlights appear, selected content moves, and the summary fills. Preserve enough screen time to understand each action before advancing.

Use an abstract workflow only when a literal action cannot be shown clearly, would falsely imply access to a real product, or lacks legally usable visual evidence. An abstract workflow must still be immediately understandable without relying on its labels:

- Give every step a recognizable icon or miniature task object, such as a document, folder, search lens, highlight marker, clipboard, calendar, person, check mark, warning, or approval button.
- Animate the actual verb: a file opens, a lens scans, a marker highlights, selected text moves, cards merge, a person checks, or a status changes.
- Preserve the task object across steps so the viewer can follow what changed. Do not replace the object with unrelated icons at every stage.
- Use direction, spacing, scale, and color to distinguish input, processing, output, and human responsibility.
- Keep labels short and secondary. If the diagram only makes sense after reading all the text, redesign it.
- Avoid static checklists, generic boxes connected by arrows, decorative particles, or icons that do not participate in the action.

Prefer one clear action per beat. For a three-step abstract workflow, show three short animated beats rather than placing all steps on screen at once.

## Reconstruct real interaction when evidence permits

Use this evidence ladder for any visible product operation:

1. Cleared real screen recording or official product demo.
2. Cleared real screenshot animated with truthful cursor, crop, zoom, and state changes.
3. A clearly labeled, faithful reconstruction of the real interaction environment based on verified UI behavior.
4. An abstract workflow only when the first three options are unavailable or would imply unsupported access.

For a reconstructed interaction, preserve the product's recognizable information architecture without copying protected brand assets beyond cleared evidence. Show the surrounding workspace, the control being clicked, the resulting menu or modal, and the next state. Do not replace `Settings → Import → Choose files` with three static cards. Animate the cursor clicking Settings, reveal Import inside the settings surface, open a file picker, select concrete files, confirm the action, and show the imported result.

Treat a click as a causal event with five visible phases: cursor approaches, target reacts, click feedback appears, the old state yields, and the new state enters. Hold the new state long enough to understand the relationship. For prompts, show typing, a clearly visible Send click, immediate button feedback, a short processing state, and the resulting view entering slowly enough to connect cause and effect.

Use camera-scale motion as attention guidance. Push in toward the clicked control, selected file, generated result, unfinished item, or verification sentence; then settle gently to a stable scale. Avoid constant zooming. Every push-in must answer “what should the viewer inspect now?”

## UI sound as causal feedback

Use restrained interface sound when it makes an on-screen action easier to understand. Synchronize a light click with button depression, subtle key taps with visible typing, a short rising cue with upload or processing, and a quiet confirmation tone with a completed state. Keep sounds dry, brief, and lower than narration. Do not add decorative beeps to static text or play a sound without a visible cause.

Prefer recorded, licensed sounds the user has previewed (`references/sound-library.md`); fall back to `scripts/generate_story_audio.py sfx` only when none can be used. Align each sound to the exact action frame and leave the following visual result stable; sound does not justify a faster cut.

## Establish the task before the actions

Before showing a sequence of clicks, searches, or copy-and-paste actions, establish the concrete task those actions are meant to complete. Show the deadline or trigger, the desired deliverable, and two or three pieces of information the person needs. For example: tomorrow's meeting → one-page preparation summary → previous decisions, unfinished tasks, and owners.

The viewer should understand both “what is the person doing?” and “what are they trying to finish?” before the manual workflow accelerates. Keep the goal visible through a stable artifact, such as an empty summary page, checklist, calendar event, application form, itinerary, or draft. Let later actions visibly fill or complete that artifact.

## Product identity and workflow continuity

Use official original logo and wordmark assets with their native proportions and colors. Do not substitute an asterisk, emoji, generic typeface, or the video accent color for a product identity. Record the source and rights status separately from factual UI evidence. Narrative mentions can use the video font; branded headers, avatars, and identity labels use the real mark. Preserve user-supplied brand spelling and tagline exactly.

Build input, output, human edits, verification, and export from one shared example data model. Show enough substantive input to justify the output; use honest scrolling and page counts rather than padding with repeated text. Keep draft/completed, sent/approved, and scheduled/performed distinct throughout.

Before and after must show who performs the work: manually read, decide, and type versus AI drafting and organizing, followed by human review. Prove each important feature through a visible action: reopen a saved artifact, ask for a change on the same document, type a direct edit, show saving, and carry that edit into the export. Do not rely on a badge or headline as feature evidence.

UI typing uses character entry and a caret. Captions reveal short semantic word groups with a stable final hold; they are not an editor typing simulation. Copy/paste must show selection, contextual menu or shortcut, and the full transferred payload; rewriting must show actual new typing. Anchor zoom to the pointer or target in the same coordinate system. Stop camera motion while people read the result.

For mobile, show one question per page and distinguish section headings through hierarchy, spacing, icons, and background blocks. Never draw outlines over the text. Use a separate transition before explaining a product distinction. Prefer an animated same-document interaction over a dense competitor table. Verify competitor AI features before claiming a difference.

## Introduce the tool or new feature

Give the product promise its own visual beat; a small badge is not enough. When the narration first names the tool or new feature (see "Introduce what is new" in [story-contract.md](story-contract.md)):

- Dim and soften the pain scene (about 15–20% opacity with a light blur) so the task stays visible behind the introduction.
- Raise one feature card in the cool accent with a short spring and a single ring burst, synced to the product name. Contents, revealed top to bottom: a "NEW" label and the official announcement date (only when new), the product or feature name as the largest text, one plain-language capability line, two to four capability objects as icon tiles that pop in one by one, and one line connecting it to this task's object ("3 quotes → 1 paste").
- Lead the card with the tool's real logo or app icon. During research, look for it in the official brand, press-kit, or media page, and record its source and usage terms in `source-ledger.json`. Use the same mark everywhere the product identity appears (feature card, AI reply avatar, chat header, cover), at native proportions and colors, and follow the vendor's brand rules (clear space, no recoloring, no implied endorsement). Fall back to the name set in the video font only when no official asset exists or its terms do not permit this use, and say so in the review. Keep the card inside the caption-safe area and hold it until the scene ends.
- Sound: one swish on entry, one chime on the name, a soft pop per tile.

Then echo the newness at most twice more, each tied to visible product evidence: a short rotated "NEW in <product>" stamp on the first real AI result, and a small "NEW" tag where a second new capability is requested. The rollout or access status appears as concrete chips (plans, regions, platforms) in the next-action scene. Never put a "NEW" mark on illustration-only UI.

## Collaboration, persistence, and navigation

For collaborative AI documents, demonstrate access and causality: share the document, choose verified editing permissions, show the invited person entering, send a human request, then show the AI revision on that same document. Do not imply automatic team access or unsolicited continuous AI edits. Verify the actual product interaction before reconstructing it.

Show the selected input as one example, not a mandatory route. When supported, briefly show alternatives such as existing conversation or a file with large recognizable objects. Avoid a small-print disclaimer.

Use a thin, unlabeled segmented progress bar when chapter titles already exist. Align segment lengths to real chapter durations; avoid duplicate headings. Keep official wordmarks and product descriptors on one line with preserved proportions, and do not describe a custom descriptor as an official logo.

Explain an important boundary through a readable action and result, not tiny footnotes. If the same-document workspace is the distinction, show saving, reopening, a requested revision and a direct human edit rather than claiming that competing editors lack AI.

## Make each screen easy to follow

Learned from review of the first English video; apply to every scene.

- One focal point at a time. If a viewer could ask "where do I look?", remove or defer an element. Do not show a real screenshot, a summary card, and an explainer graphic that say the same thing at once.
- Stack a consequential change as one column, top to bottom: cause (what the person typed or clicked) → effect (what the product showed, as a tight crop of the real UI) → why (one explainer, such as a break-even bar). Reveal each block when the narration reaches it.
- Prefer one visual explainer over arithmetic. A labeled threshold ("C is cheaper below $1,030") with a marker for the typed value explains a flip better than equations.
- Fill empty space with explanation, not decoration: a "who did what" strip (You: 1 paste → AI: table ✓ chart ✓), a callout on the exact detail, or the next object in the story.
- Never repeat the caption as on-screen text. Late scenes (human check, next action) should use icons and small actions — an envelope sent and a stamped reply, checkmark tiles, keycaps, plan chips — rather than sentences.
- Show differences as aligned rows. Compare options in a grid with one row per rule (price, shipping, discount) so the differences line up.
- Replace generic transition cards with an object handoff that performs the step (quotes flying into the chat box; a field typing the number that decides).
- Label any graphic you draw on or near real product UI as "Illustration" (loading states, emails, stamps) so it is never mistaken for a screenshot. Typed-value animations must reveal the exact values in the screenshot.
- Crop screenshots to the region being discussed and scale them to mobile-readable text (about 40 px or larger) instead of shrinking a whole window.

## Reusable Remotion motion components

Use the prop-driven building blocks in `<skill-dir>/assets/remotion-template/src/components/`; `ComponentsDemo` shows an eight-second English example at 1080×1920, 30 fps. They use only React and Remotion and derive all motion from frame numbers. Frames are local to the enclosing Sequence; coordinates are unscaled parent pixels.

- **Cursor**: use for a visible click or navigation. Pass `path={[{frame: 0, x: 700, y: 900}, {frame: 50, x: 280, y: 750}, {frame: 84, x: 280, y: 750}]}` and `clicks={[60]}`. Points must have strictly increasing frames; movement eases between points and holds at the endpoints. Hold the pointer on the target during the click. Customize `size`, `color`, `rippleColor`, and `clickTiming` as needed. Call `getClickState(frame, 60, clickTiming)` for the target and its old/new content: bind `targetActive` to hover styling, `targetScale` to button depression, and `oldOpacity` / `newOpacity` to the outgoing/incoming views. The cursor renders press feedback and the ripple. Default timing is approach → target reaction (10 frames before press) → press/ripple (6 frames) → old exit (8 frames) → new entry (12 frames); hold the new state for reading. Pass identical timing to the helper and cursor. The caller supplies the truthful UI states rather than the pointer inventing them.
- **TypingText**: use inside an editor or input, never as narration captions. Pass `text`, `startFrame`, and `charactersPerSecond`; customize `blinkFrames` (full blink period), `caretColor`, `showCaret`, and `style`. Text enters by Unicode code point; the caret remains frame-synchronized after typing finishes. Size the input to fit the completed text.
- **FocusZoom**: use to inspect a consequential result. Wrap both the interface and Cursor in it, pass `target={{x: 540, y: 1120}}`, `startFrame`, `durationInFrames`, and final `scale`. `destination` defaults to viewport center; `width` / `height` default to composition dimensions. The transform eases to the final position and then holds exactly. Coordinates must belong to this same wrapper, including any interface offsets. Keep result text readable and within safe margins after zooming.
- **ProgressBar**: use outside FocusZoom at composition root. Pass `durationsInFrames` in chapter order, using actual chapter durations, and optional `startFrame`. Segment widths are proportional to duration, and each fills during its own chapter. Customize `height`, `top`, `inset`, `gap`, `color`, `trackColor`, or `style`; keep it thin and unlabeled. Defaults respect the 72 px horizontal / 120 px vertical safe margins.

- **Shot**: show a tight crop of a real screenshot. Pass `src` (under `public/`), `sourceWidth`, `crop={{x, y, w, h}}` in source pixels, and display `width`; map a source point to the frame with `left + (sx - crop.x) * width / crop.w`.
- **Pop** / **Burst** (`Emphasis.jsx`): spring a callout, sticker, or chip into place at a frame; draw one expanding ring when a tool or result appears. Use them on consequential details only.
- **Icon**: line icons for task objects (`paste`, `table`, `chart`, `truck`, `percent`, `lock`, `doc`, `sliders`, `mail`). Prefer icon tiles over sentences in late scenes.
- **Sfx** / **Taps**: play a sound from `public/audio/sfx` at a frame, or varied key clicks for visible typing. Generate the default set with `scripts/generate_story_audio.py sfx`.
- `FullFrameTransition` and `BrandEnding` are exported from `VerticalImpact.jsx` for custom compositions. `ToolkitPreview` renders the icons and emphasis components for layout checks.

Render `ComponentsDemo` at frames 0 (opening), 62 (press/ripple), and 210 (settled result) for layout checks. Also inspect the intermediate states when changing timing; stills alone cannot establish motion quality. Use the components for verified product evidence or clearly identified illustrative UI, not as proof of unsupported product behavior.
