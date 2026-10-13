import React from 'react';
import {useCurrentFrame} from 'remotion';

/** durationsInFrames: positive chapter lengths in timeline order; startFrame:
 * chapter timeline origin. Each segment's flex width uses its actual duration.
 * height/top/inset/gap/color/trackColor customize the thin, unlabeled overlay.
 * style customizes the outer container; render outside FocusZoom. */
export const ProgressBar = ({durationsInFrames, startFrame = 0, height = 6, top = 120, inset = 72, gap = 8, color = '#447d92', trackColor = '#dcdedb', style = {}}) => {
  const frame = useCurrentFrame() - startFrame;
  if (!durationsInFrames?.length || durationsInFrames.some((duration) => !Number.isFinite(duration) || duration <= 0)) throw new Error('ProgressBar requires positive chapter durations');
  let offset = 0;
  return <div style={{position: 'absolute', top, left: inset, right: inset, height, display: 'flex', gap, zIndex: 50, ...style}}>{durationsInFrames.map((duration, i) => {
    const progress = Math.max(0, Math.min(1, (frame - offset) / duration));
    offset += duration;
    return <div key={i} style={{flex: duration, background: trackColor, overflow: 'hidden', borderRadius: height}}><div style={{height: '100%', width: `${progress * 100}%`, background: color}} /></div>;
  })}</div>;
};
