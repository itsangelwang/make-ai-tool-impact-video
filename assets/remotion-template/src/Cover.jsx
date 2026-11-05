import React from 'react';
import {AbsoluteFill, Freeze, Img, staticFile} from 'remotion';
import {FONTS, Headline, VerticalImpact, localeOf, phaseOf} from './VerticalImpact';

// A designed cover, laid out separately for each ratio (never a crop of the other one).
// story.cover = {
//   headline: "3 quotes, *one paste*",  // one promise; *word* takes the accent color
//   kicker: "New in ChatGPT",            // optional small chip above the headline
//   logo: "assets/chatgpt-icon.png",      // optional official icon, shown in the chip
//   frame_sec: 14.2,                       // the video moment shown as real evidence
//   crop: {x: 40, y: 320, w: 1000, h: 900} // the part of that 1080x1920 frame to show
// }
// Without story.cover it falls back to the old cover: the full frame 2 seconds in.
// In 9:16 everything sits inside the centre 3:4 band (y 240-1680), because TikTok and
// Instagram profile grids crop the cover to 3:4.
const DEFAULT_CROP = {x: 0, y: 300, w: 1080, h: 1100};

const Inset = ({story, cover}) => {
  const crop = {...DEFAULT_CROP, ...(cover.crop || {})};
  const width = 952;
  const scale = width / crop.w;
  return (
    <div style={{position: 'relative', flex: 1, minHeight: 0, width, borderRadius: 36, overflow: 'hidden', background: story.palette.paper, boxShadow: '0 24px 60px rgba(23,25,35,.22)', border: `4px solid ${story.palette.ink}14`}}>
      <div style={{position: 'absolute', width: 1080, height: 1920, left: -crop.x * scale, top: `calc(50% - ${(crop.y + crop.h / 2) * scale}px)`, transform: `scale(${scale})`, transformOrigin: 'top left'}}>
        <Freeze frame={Math.round((cover.frame_sec ?? 2) * 30)}>
          <VerticalImpact story={{...story, audio: null, sfx: false}} captions={false} />
        </Freeze>
      </div>
    </div>
  );
};

export const Cover = ({story, ratio = '9:16'}) => {
  const cover = story.cover;
  if (!cover) {
    return <Freeze frame={60}><VerticalImpact story={{...story, audio: null, sfx: false}} /></Freeze>;
  }
  const locale = localeOf(story);
  const accent = phaseOf('ai-handoff', story.palette).accent;
  const tall = ratio === '9:16';
  const font = FONTS[locale].body;
  // Sized for the smallest slot (a 3-column profile grid, about 130 pt wide): one line's letters
  // must come out clearly bigger than 14 pt UI text. That leaves room for about 2-3 words a line.
  const size = locale === 'en' ? (tall ? 215 : 170) : (tall ? 190 : 160);
  return (
    <AbsoluteFill style={{background: phaseOf('ai-handoff', story.palette).paper, fontFamily: font, color: story.palette.ink}}>
      <div style={{position: 'absolute', left: 64, right: 64, top: tall ? 270 : 64, bottom: tall ? 270 : 56, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: tall ? 44 : 34}}>
        <div style={{alignSelf: 'stretch'}}>
          {cover.kicker ? (
            <div style={{display: 'inline-flex', alignItems: 'center', gap: 16, padding: '12px 26px', borderRadius: 999, background: story.palette.ink, color: '#fff', fontSize: 46, fontWeight: 700, letterSpacing: 0.5}}>
              {cover.logo ? <Img src={staticFile(cover.logo)} style={{width: 52, height: 52, objectFit: 'contain'}} /> : null}
              {cover.kicker}
            </div>
          ) : null}
          <h1 style={{margin: cover.kicker ? '30px 0 0' : 0, fontSize: size, lineHeight: 1.02, fontWeight: 800, letterSpacing: locale === 'en' ? -4 : 0, textWrap: 'balance'}}>
            <Headline text={cover.headline} accent={accent} />
          </h1>
        </div>
        <Inset story={story} cover={cover} />
      </div>
    </AbsoluteFill>
  );
};
