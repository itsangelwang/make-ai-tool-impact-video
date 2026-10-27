# Failure modes

- **Insufficient source material:** stop before scripting, list the unsupported claims, and request a better official link or product access.
- **Waitlist or demo only:** set readiness to `watch`; make a trend explainer rather than a how-to.
- **Vendor-only outcome claim:** attribute it and remove certainty, numbers, or before/after promises that lack comparison evidence.
- **No licensed product visuals:** use labeled code-native explanatory graphics; do not reconstruct an interface and present it as real.
- **No TTS timestamps:** measure final audio and distribute phrase cues, then visually inspect synchronization.
- **No system FFmpeg/FFprobe:** `verify_video.py` falls back to the copy bundled with Remotion in the project's `node_modules` and records `"tools": "remotion-bundled"` in the report. Measure loudness with its `loudnorm` filter as described in "Expressive audio and scoped revisions" in `pacing-and-review.md`. If neither is available, produce the review artifacts but do not describe the MP4 as QA-passed.
- **Bundled FFmpeg fails to start (`Library not loaded: libavdevice.dylib`):** run it with `DYLD_LIBRARY_PATH` (Linux: `LD_LIBRARY_PATH`) set to its own folder; the Skill's scripts do this. Its filter set is minimal: it decodes, trims (`-ss`/`-to`), resamples and runs `silencedetect`, `loudnorm` and `volume`, but cannot mix (`asplit`, `sidechaincompress`, `alimiter`, `afade` are missing). Mix in Python with `mix_story_audio.py`.
- **No Chromium/Remotion dependencies:** report the missing prerequisite; do not silently switch to a different visual system.
- **Duration outside 55–65 seconds:** first remove repetition. If verified interaction or stable evidence still needs more time, allow a review up to 75 seconds and disclose it; do not speed up or stretch narration.
- **Caption can display but cannot be spoken:** audit each cue by Han characters per second, cut redundant narration, and preserve pauses; do not treat character animation completion as speech timing.
- **Transition overlaps the next page:** use a dedicated full-frame transition ending at the next scene boundary; do not place a readable title over outgoing or incoming content.
- **Two transitions feel repetitive:** keep the chapter transition and replace the second with an object handoff, morph, zoom, or internal state change.
- **Abstract nouns confuse the viewer:** replace “draft,” “source,” “old material,” “owner,” or “deadline” with the named artifact and a concrete value on screen.
- **Changed approved input:** `project_state.py status` reports which input changed. If it changed meaning, voice, cover, or opening, rebuild and present the combined review; see the change levels in section 4 of `SKILL.md`.
