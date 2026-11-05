import React from 'react';
import {spring, useCurrentFrame, useVideoConfig} from 'remotion';
import captions from './captions.json';

const containsIndex = (text, index, terms = []) => terms.some((term) => {
  let start = text.indexOf(term);
  while (start !== -1) {
    if (index >= start && index < start + term.length) return true;
    start = text.indexOf(term, start + 1);
  }
  return false;
});

// A cue that will not fit on one line is split at the space nearest its middle, so the two
// lines have similar length and no line is left with one word.
const ONE_LINE_CHARS = 34;
export const balancedBreak = (units) => {
  const text = units.join('');
  if (text.length <= ONE_LINE_CHARS) return -1;
  let best = -1, bestDiff = Infinity, offset = 0;
  units.forEach((unit, index) => {
    offset += unit.length;
    const breakable = /^\s+$/.test(unit);
    const diff = Math.abs(text.length / 2 - offset);
    if (breakable && diff < bestDiff) { best = index; bestDiff = diff; }
  });
  return best;
};

// The caption bar ends at y 1450, above the account name and post text that YouTube Shorts,
// TikTok and Instagram Reels draw over the lower part of the video (about y 1460-1790).
export const CAPTION_BOTTOM = 470;

export const TimedCaptions = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const ms = frame * 1000 / fps;
  const cue = captions.find((item) => ms >= item.startMs && ms < item.endMs);
  if (!cue || cue.brand) return null;
  const units = cue.text.split(/(\s+)/).filter(Boolean);
  const localFrame = (ms - cue.startMs) * fps / 1000;
  const durationFrames = (cue.endMs - cue.startMs) * fps / 1000;
  const stagger = Math.min(3.2, Math.max(1.1, (durationFrames - 28) / Math.max(units.length, 1)));
  const lineBreak = balancedBreak(units);
  let characterOffset = 0;
  return (
    // The bar hugs its text (at most 820 wide, centred) so it stays clear of the button column on the right.
    <div style={{position:'absolute',left:0,right:0,bottom:CAPTION_BOTTOM,zIndex:100,display:'flex',justifyContent:'center'}}>
    <div style={{maxWidth:820,display:'flex',alignItems:'center',justifyContent:'center',flexWrap:'wrap',padding:'22px 27px',borderRadius:25,background:'rgba(23,25,35,.92)',boxShadow:'0 16px 42px rgba(0,0,0,.20)'}}>
      {units.map((char, index) => {
        const startIndex = characterOffset;
        characterOffset += char.length;
        const progress = spring({frame:localFrame-index*stagger,fps,config:{damping:12,stiffness:190}});
        const warm = containsIndex(cue.text,startIndex,cue.highlightWarm);
        const cool = !warm && containsIndex(cue.text,startIndex,cue.highlightCool);
        const emphasized = warm || cool;
        // The break falls on a space, which is replaced by the line break itself.
        if (index === lineBreak) return <div key={`br-${index}`} style={{flexBasis:'100%',height:0}} />;
        return <span key={`${char}-${index}`} style={{display:'inline-block',whiteSpace:/^\s+$/.test(char)?'pre':'normal',fontFamily:"system-ui, -apple-system, 'SF Pro Display', Inter, Arial, sans-serif",fontSize:emphasized?48:43,lineHeight:1.22,fontWeight:emphasized?900:650,color:warm?'#FF9B74':cool?'#B9AFFF':'#fff',opacity:progress,transform:`translateY(${(1-progress)*(emphasized?32:24)}px) scale(${.78+progress*.22})`}}>{char}</span>;
      })}
    </div>
    </div>
  );
};
