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

## Motion grammar

Give every transition a cause: stack, sort, compress, hand off, verify, or complete. Change hierarchy, scale, density, direction, or media every 2–4 seconds while preserving at least 1.2 seconds for important reading. Animate in the order task object → explanatory label → evidence → caption. Use one primary movement per beat.

Shape rhythm in waves rather than giving every scene the same pace. Accelerate repetitive operations such as opening, importing, searching, and sorting; slow down when showing the result, decision, evidence, or responsibility boundary. Carry a document, task, prompt, summary, or checkmark from one scene into the next so the downstream scene visibly receives the upstream output.

Use zoom only to direct attention to a consequential detail: the selected import file, the relevant product result, the unfinished task inside a summary, the source sentence used for verification, or the final output replacing a stack of inputs. Pair the zoom with a state change or highlighted evidence; avoid decorative push-ins that do not clarify the workflow.

When a chapter transition contains a readable label, give it a dedicated full-frame background for roughly 1.2–1.5 seconds. Do not layer a transition title over the outgoing or incoming scene. Hold the title stable long enough to read, then reveal the next scene; shorter overlays are reserved for nonverbal action handoffs.

End the outgoing caption before a readable transition begins. For character-by-character captions, adapt the stagger to phrase length and preserve a stable fully revealed hold; never let the transition cover the final words. Place a full-frame transition entirely before the next scene boundary so the incoming scene starts unobscured.

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

Prefer source-safe generated sounds or cleared product recordings. Use `scripts/generate_ui_sfx.mjs` to create a small reusable UI set when licensed recordings are unavailable. Align each sound to the exact action frame and leave the following visual result stable; sound does not justify a faster cut.

## Establish the task before the actions

Before showing a sequence of clicks, searches, or copy-and-paste actions, establish the concrete task those actions are meant to complete. Show the deadline or trigger, the desired deliverable, and two or three pieces of information the person needs. For example: tomorrow's meeting → one-page preparation summary → previous decisions, unfinished tasks, and owners.

The viewer should understand both “what is the person doing?” and “what are they trying to finish?” before the manual workflow accelerates. Keep the goal visible through a stable artifact, such as an empty summary page, checklist, calendar event, application form, itinerary, or draft. Let later actions visibly fill or complete that artifact.
