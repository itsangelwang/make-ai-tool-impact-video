# Make AI Tool Impact Video

**English** | [中文](README.zh-CN.md)

Give it the name or link of an AI tool, and it helps you make a one-minute vertical video that anyone can follow. Works in **Codex** and **Claude Code**.

## What the videos look like

Each video shows **one person using one AI tool to finish one real task**, in about a minute:

1. **The pain** — where this task used to get stuck
2. **Before** — the manual steps
3. **Now** — the same material handed to AI, and which step it takes over (for a new feature, what's new is called out right after the pain)
4. **What you still do** — the results a person must check and decide
5. **Try it** — whether it's available now, and a small first task

Principles:

- **True** — real product screenshots or recordings; every claim has a source and matches the official docs; no made-up "saves 80% of your time" numbers
- **Clear** — one point per screen, in the order *action → result → why*, with icons and motion instead of paragraphs
- **Easy to read** — few words per frame, something new every few seconds, a progress bar on top
- **Looks and sounds good** — big type for phones, a voice that follows the story, music and sound effects on the beat

## Install

You need [Python 3](https://www.python.org/), [Node.js](https://nodejs.org/) and [FFmpeg](https://ffmpeg.org/).

The easiest way: open Codex or Claude Code and say

```text
Install this skill: https://github.com/itsangelwang/make-ai-tool-impact-video
```

Or install by hand (both tools share one copy; skip the `ln -s` line for a tool you don't use):

```bash
git clone https://github.com/itsangelwang/make-ai-tool-impact-video.git ~/skills/make-ai-tool-impact-video
mkdir -p ~/.codex/skills ~/.claude/skills
ln -s ~/skills/make-ai-tool-impact-video ~/.codex/skills/make-ai-tool-impact-video
ln -s ~/skills/make-ai-tool-impact-video ~/.claude/skills/make-ai-tool-impact-video
```

To update later, run `git pull` in the skill folder.

## Use

Type `$make-ai-tool-impact-video` in Codex or `/make-ai-tool-impact-video` in Claude Code, then describe what you want:

```text
Make a one-minute vertical video for this AI tool: <product name or link>
The task: turn a week of meeting notes into a weekly update
```

No idea yet? Say "find me an AI feature worth covering this week". It scans official release notes since your last scan, scores what is new, recommends one, and suggests follow-on videos. It keeps a `topic-backlog.md` next to your project folders, so nothing repeats and re-tests come back when they are due.

Before starting, it checks whether the company or other creators have already covered the feature. If the same story is out there it looks for a new angle, and if there's nothing new to say it suggests a different topic.

You first get a review pack (script, frames, fact sources). **Nothing is voiced or rendered until you approve it**, and nothing is ever published automatically.

## Defaults

| Setting | Default | To change it |
|---|---|---|
| Language | US English | Say "Language: Chinese, for the China market" |
| Voice | Fish Audio "Sawyer" (Drama 3), each scene read in one take, 1.15× speed | Say "change the voice" — you'll get samples first |
| Music & sound | Real tracks and effects from royalty-free libraries (e.g. Pixabay), downloaded only after you pick them | Say "change the music" or "this sound effect doesn't work" |
| Brand ending | ACEMODE brand card, reading "10x Faster, Log Off Earlier." | Say "no brand ending", or give your own brand |
| Length | 55–65 seconds | Up to 75 seconds with a stated reason |

## Voice API key

Voiceover needs a [Fish Audio](https://fish.audio/) API key (OpenRouter and Deepgram also work). Put it in `~/.config/make-ai-tool-impact-video/.env`, following [`.env.example`](.env.example).

- Don't put it in the skill folder, paste it into a chat, or push it to GitHub
- Fish Audio's free tier is usually for personal use — check your plan before commercial use

## Output

A 1080×1920 vertical MP4, cover image, captions, source log, quality-check report, and 3 social-media titles each in English and Chinese (in `social-titles.md`).

## Credits

Adapted from [Ah-ha07/AceMode-video-skill](https://github.com/Ah-ha07/AceMode-video-skill) — thanks to the original author for exploring and sharing it. This repository has no open-source license yet; rights to the upstream code, brand and assets need to be confirmed separately.
