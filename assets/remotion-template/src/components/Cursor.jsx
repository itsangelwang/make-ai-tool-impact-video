import React from 'react';
import {Easing, interpolate, useCurrentFrame} from 'remotion';

const ramp = (frame, start, end) => interpolate(frame, [start, end], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.cubic)});

/** Shared click choreography. Frames are local to the enclosing Sequence.
 * clickFrame: press begins; approachFrames: target hover lead-in;
 * pressFrames: depression/ripple; exitFrames: old state fades; enterFrames: new state fades.
 * Use targetScale/targetActive on the target and oldOpacity/newOpacity on its states.
 */
export const getClickState = (frame, clickFrame, {approachFrames = 10, pressFrames = 6, exitFrames = 8, enterFrames = 12} = {}) => {
  const exitStart = clickFrame + pressFrames;
  const enterStart = exitStart + exitFrames;
  const hover = ramp(frame, clickFrame - approachFrames, clickFrame);
  const pressed = frame >= clickFrame && frame < exitStart;
  return {
    phase: frame < clickFrame - approachFrames ? 'approach' : frame < clickFrame ? 'target-reacts' : frame < exitStart ? 'press' : frame < enterStart ? 'old-exits' : 'new-enters',
    targetActive: hover,
    targetScale: pressed ? 0.96 : 1 + hover * 0.025,
    oldOpacity: 1 - ramp(frame, exitStart, enterStart),
    newOpacity: ramp(frame, enterStart, enterStart + enterFrames),
    rippleProgress: ramp(frame, clickFrame, enterStart),
    rippleVisible: frame >= clickFrame && frame < enterStart,
  };
};

/** path: ordered {frame, x, y} points in parent pixels (strictly increasing frames).
 * clicks: frame numbers at which the pointer presses; stop the path at the target
 * during its reaction/press. size/color/rippleColor customize the pointer.
 * Render target and state feedback using getClickState with the same click frame.
 */
/** hand: [[startFrame, endFrame], ...] ranges where the pointer is over a button and shows a
 * pointing hand, as a browser does; the fingertip stays on the same point as the arrow tip. */
export const Cursor = ({path, clicks = [], hand = [], size = 42, color = '#20252b', rippleColor = '#447d92', clickTiming = {}}) => {
  const frame = useCurrentFrame();
  if (!path?.length) return null;
  if (path.some((point, i) => !Number.isFinite(point.frame) || !Number.isFinite(point.x) || !Number.isFinite(point.y) || (i > 0 && point.frame <= path[i - 1].frame))) throw new Error('Cursor path requires finite coordinates and strictly increasing frames');
  const next = path.findIndex((point) => point.frame > frame);
  const from = next === 0 ? path[0] : next === -1 ? path[path.length - 1] : path[next - 1];
  const to = next <= 0 ? from : path[next];
  const t = from === to ? 0 : ramp(frame, from.frame, to.frame);
  const x = from.x + (to.x - from.x) * t;
  const y = from.y + (to.y - from.y) * t;
  const states = clicks.map((click) => getClickState(frame, click, clickTiming));
  const pressed = states.some((state) => state.phase === 'press');
  return <div style={{position: 'absolute', left: x, top: y, pointerEvents: 'none', zIndex: 20}}>
    {states.map((state, i) => state.rippleVisible && <div key={i} style={{position: 'absolute', width: 84, height: 84, left: -42, top: -42, border: `3px solid ${rippleColor}`, borderRadius: '50%', opacity: 1 - state.rippleProgress, transform: `scale(${0.25 + state.rippleProgress})`}} />)}
    {hand.some(([start, end]) => frame >= start && frame <= end)
      ? <svg width={size * 1.1} height={size * 1.35} viewBox="0 0 32 40" style={{position: 'absolute', left: -size * 0.45, top: -2, transformOrigin: '45% 0', transform: `scale(${pressed ? 0.88 : 1})`}}><path d="M12 4a3 3 0 0 1 6 0v11a3 3 0 0 1 6 1v1a3 3 0 0 1 5 2v8c0 6-4 11-10 11h-3c-4 0-7-2-9-6l-5-8a3 3 0 0 1 5-3l3 4V4z" fill="#fff" stroke={color} strokeWidth="2.2" strokeLinejoin="round" /><path d="M18 15v8M24 17v6" stroke={color} strokeWidth="1.8" strokeLinecap="round" /></svg>
      : <svg width={size} height={size * 1.3} viewBox="0 0 32 42" style={{transformOrigin: '0 0', transform: `scale(${pressed ? 0.86 : 1})`}}><path d="M2 2 L2 31 L10 24 L17 39 L23 36 L16 22 L28 22 Z" fill={color} stroke="white" strokeWidth="2" /></svg>}
  </div>;
};
