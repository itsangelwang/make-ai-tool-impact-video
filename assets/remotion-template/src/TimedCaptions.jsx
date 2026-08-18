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

export const TimedCaptions = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const ms = frame * 1000 / fps;
  const cue = captions.find((item) => ms >= item.startMs && ms < item.endMs);
  if (!cue) return null;
  const english = (cue.language || 'zh-CN').startsWith('en');
  const units = english ? cue.text.split(/(\s+)/).filter(Boolean) : cue.text.split('');
  const localFrame = (ms - cue.startMs) * fps / 1000;
  const durationFrames = (cue.endMs - cue.startMs) * fps / 1000;
  const stagger = Math.min(english ? 3.2 : 1.35, Math.max(english ? 1.1 : .55, (durationFrames - 28) / Math.max(units.length, 1)));
  let characterOffset = 0;
  return (
    <div style={{position:'absolute',left:64,right:64,bottom:112,zIndex:100,display:'flex',alignItems:'center',justifyContent:'center',flexWrap:'wrap',padding:'22px 27px',borderRadius:25,background:'rgba(23,25,35,.92)',boxShadow:'0 16px 42px rgba(0,0,0,.20)'}}>
      {units.map((char, index) => {
        const startIndex = characterOffset;
        characterOffset += char.length;
        const progress = spring({frame:localFrame-index*stagger,fps,config:{damping:12,stiffness:190}});
        const warm = containsIndex(cue.text,startIndex,cue.highlightWarm);
        const cool = !warm && containsIndex(cue.text,startIndex,cue.highlightCool);
        const emphasized = warm || cool;
        return <span key={`${char}-${index}`} style={{display:'inline-block',whiteSpace:/^\s+$/.test(char)?'pre':'normal',fontFamily:english?'Inter, Avenir Next, Arial, sans-serif':'Hannotate SC, Kaiti SC, PingFang SC, sans-serif',fontSize:english?(emphasized?48:43):(emphasized?42:38),lineHeight:english?1.22:1.35,fontWeight:emphasized?900:800,color:warm?'#FF9B74':cool?'#B9AFFF':'#fff',opacity:progress,transform:`translateY(${(1-progress)*(emphasized?32:24)}px) rotate(${english?0:(1-progress)*(index%2?5:-4)}deg) scale(${(.78+progress*.22)*(emphasized?1.1:1)})`}}>{char}</span>;
      })}
    </div>
  );
};
