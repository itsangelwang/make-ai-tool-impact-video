import React from 'react';
import {Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';

/** Wrap content AND Cursor in this coordinate plane. target: {x,y} in unscaled
 * parent pixels; destination: its final screen position (default viewport center).
 * startFrame/durationInFrames schedule the push; scale is final magnification.
 * width/height default to composition dimensions; style customizes the outer viewport.
 * After the push the transform holds exactly, without spring drift. */
export const FocusZoom = ({children, target, destination, startFrame = 0, durationInFrames = 30, scale = 1.5, width, height, style = {}}) => {
  const frame = useCurrentFrame();
  const config = useVideoConfig();
  const w = width ?? config.width;
  const h = height ?? config.height;
  if (durationInFrames <= 0 || scale <= 0) throw new Error('FocusZoom duration and scale must be positive');
  const t = interpolate(frame, [startFrame, startFrame + durationInFrames], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});
  const s = 1 + (scale - 1) * t;
  const end = destination ?? {x: w / 2, y: h / 2};
  return <div style={{position: 'absolute', width: w, height: h, overflow: 'hidden', ...style}}><div style={{position: 'absolute', width: w, height: h, transformOrigin: '0 0', transform: `translate(${(end.x - target.x * scale) * t}px, ${(end.y - target.y * scale) * t}px) scale(${s})`}}>{children}</div></div>;
};
