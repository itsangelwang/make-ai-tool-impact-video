import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

/** Springs children into place at frame `at` (local to the Sequence); position with style. */
export const Pop = ({at, children, style = {}}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: frame - at, fps, config: {damping: 9, stiffness: 180}});
  return <div style={{position: 'absolute', opacity: Math.min(1, p * 2), transform: `scale(${p})`, ...style}}>{children}</div>;
};

/** One expanding ring centered at (x, y) from frame `at`; marks a creation moment. */
export const Burst = ({x, y, at, color = '#6857F5', size = 520, durationInFrames = 18}) => {
  const frame = useCurrentFrame();
  if (frame < at || frame > at + durationInFrames) return null;
  const t = interpolate(frame, [at, at + durationInFrames], [0, 1]);
  return <div style={{position: 'absolute', left: x - size / 2, top: y - size / 2, width: size, height: size, borderRadius: '50%', border: `8px solid ${color}`, opacity: 1 - t, transform: `scale(${0.3 + t * 0.9})`, pointerEvents: 'none'}} />;
};
