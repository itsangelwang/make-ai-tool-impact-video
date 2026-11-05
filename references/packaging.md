# Cover, titles and post copy

Read this when writing the cover, the titles and the post copy. They are one package: in a feed, a viewer sees only the cover and the title, and decides from them whether the video is worth a minute. The opening seconds then confirm the promise right away.

## One promise for title and cover

- Write the cover headline and the title together, from the same promise: the one concrete change this video shows (for example "five old notes become one brief"). Do not write the title first and decorate a cover for it afterwards.
- The cover makes the promise visible: a short headline plus one piece of real evidence (the product moment from the video). The title adds the situation or the why. Repeating a key word in both is fine; two different promises are not.
- **Cold read.** For each candidate, finish the sentence a stranger would think: "So this is just saying…". If the answer is an old idea ("AI saves time", "AI writes summaries"), change the angle. Find the detail in this video that the old idea does not cover (the exact handoff, the surprising output, what the person still checks). A louder word does not fix a flat promise.
- **Plain-version check.** Put the polished line next to a plain one the same facts support ("Paste three quotes, get a comparison table"). If the plain one makes the reason to watch clearer, use it and polish that instead. Curiosity should come from "I know what this is and want to see how", not from guessing what the words mean.
- The opening of the video must show the thing the cover promised within the first seconds; see "Open fast" in [visual-system.md](visual-system.md).
- Everything stays inside `claim-ledger.json`: no numbers, rankings or results the video does not show, and no illustrative on-screen value (a demo timer, a sample price) presented as a fact.

## The cover

The template renders a designed cover from `story.cover`, laid out separately for each ratio:

```json
"cover": {
  "kicker": "New in ChatGPT",
  "headline": "Five old notes, *one brief*",
  "frame_sec": 26,
  "crop": {"x": 40, "y": 260, "w": 1000, "h": 1100},
  "logo": "assets/chatgpt-icon.png"
}
```

- `headline`: the one promise, 2–3 short lines; `*word*` takes the accent color. Mark the word that carries the change.
- `kicker` (optional): a small chip, such as "New in ChatGPT" for a feature from the last 90 days. `logo` (optional) is the official icon already recorded in `source-ledger.json`.
- `frame_sec` and `crop`: the moment of the video and the part of the 1080×1920 frame shown below the headline as real evidence, usually the AI result. The inset never shows captions.
- `npm run cover` writes `qa/cover-9x16.png` (Shorts, TikTok, Reels) and `qa/cover-3x4.png` (Xiaohongshu). `check_story.py` checks the fields. Without `story.cover` the template falls back to a frame 2 seconds in; use that only for a quick draft, never for delivery.
- In 9:16, keep everything inside the centre 3:4 band (y 240–1680): TikTok and Instagram profile grids crop the cover to that. The template already does.
- The headline sizes in `Cover.jsx` are set so the smallest slot (a 3-column profile grid, about 130 pt wide) still shows the letters clearly bigger than the app's own 14 pt text. A headline that does not fit at that size has too many words; cut words instead of shrinking the type.

**Check at feed size, not at full size.** A cover that reads well at full size can be unreadable as a small card. Run:

```bash
python3 <skill-dir>/scripts/feed_preview.py \
  <project-dir>/video/qa/cover-9x16.png@155 <project-dir>/video/qa/cover-3x4.png@122 \
  --title "<the post title>" -o <project-dir>/video/qa/feed-preview.png
```

`@N` is the height in pixels of one headline line's letters in the 1080-wide cover (about 0.72 × the font size, the height of a capital; the template's cover gives about 155 and 122). The script places each cover in a YouTube Shorts shelf, the TikTok and Instagram profile grids and a Xiaohongshu card, draws the platform's title text beside it, and fails when the headline letters are not at least 1.3 × that text. Look at the sheet as well: you should see one focus, read the headline in a second, and recognise the product. Slot sizes in the script are estimates; re-measure them in the live apps when a layout changes.

Common failures: a frame grab with the caption bar and small UI text; a headline that only names the tool; two ideas on one cover; a generic illustration instead of the real result; a 3:4 cover made by cropping the 9:16 one.

## Titles and post copy

Write `<project-dir>/social-titles.md` from [assets/social-titles-template.md](../assets/social-titles-template.md). One file holds everything the person posting needs; each block can be copied as it is.

- **Header (not for posting):** which MP4 and which cover file the copy belongs to, and anything not yet verified (a link, plan access). Internal paths and notes stay here, never in a post block.
- **Title options:** three in English and three in Chinese. The video is English; the Chinese titles and posts are for putting the same video on Chinese platforms. Write each set natively for its audience, not translated, and tell Chinese viewers the video is in English when that matters (for example 「英文视频」 in the body). Short enough to read at a glance on a phone (about 60 characters in English, 25 in Chinese), conversational and punchy ("Stop replaying client calls."), naming the tool, no clickbait. Mark the pick and say in one line why it beats the others. When the feature is new (within 90 days, as the claim ledger records), lead with that fact ("New in ChatGPT:", "ChatGPT just added …", "ChatGPT 新功能") and note when that framing expires.
- **One block per platform**, ready to paste: YouTube Shorts (title and description), TikTok and Instagram Reels (one caption each) in English; Xiaohongshu (short title and body), Douyin / Channels (one block, say which) and Bilibili in Chinese. When the user names platforms, write only those.
- The first sentence of a caption goes straight into the situation or the change, not "In this video…". Keep the conditions that change the meaning next to the claim ("Plus plan, rolling out"). Skip empty praise ("game changer", "must-watch").
- Links: only the official page the viewer needs next, checked by opening it, with a few words on what it is. Instagram captions do not make links clickable; name the domain instead. Do not invent account handles; `#tag` and `@account` are different things.
- Hashtags: a few that match the tool, the task and the audience; no fixed count.
- **Platform settings (not for posting):** anything to set in the app, such as the cover upload or a linked video, marked checked or not checked.

Show the user the cover feed preview, the picked title and the platform blocks with the delivery. Do not post anything.

## Learning from feedback

When the user rejects a cover or title, or real numbers come back, add one line to the project's notes: what was tried → why it failed → what changed → what the user said or the numbers showed → when this applies. Separate the user's opinion, an editing guess and real audience data. Move only lessons that will hold for future videos into this file.
