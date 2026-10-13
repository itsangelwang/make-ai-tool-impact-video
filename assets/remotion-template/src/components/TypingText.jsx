import React from 'react';
import {useCurrentFrame, useVideoConfig} from 'remotion';

/** UI entry, not captions. text: entered string; startFrame: first typing frame;
 * charactersPerSecond: entry speed; blinkFrames: full caret blink period;
 * caretColor/showCaret/style customize the inline editor content. */
export const TypingText = ({text, startFrame = 0, charactersPerSecond = 18, blinkFrames = 30, caretColor = 'currentColor', showCaret = true, style = {}}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  if (charactersPerSecond <= 0 || blinkFrames <= 0) throw new Error('TypingText speed and blink period must be positive');
  const characters = Array.from(text);
  const count = Math.max(0, Math.min(characters.length, Math.floor((frame - startFrame) * charactersPerSecond / fps)));
  const caretVisible = frame >= startFrame && (frame - startFrame) % blinkFrames < blinkFrames / 2;
  return <span style={{whiteSpace: 'pre-wrap', ...style}}>{characters.slice(0, count).join('')}{showCaret && <span style={{display: 'inline-block', width: 3, height: '1em', marginLeft: 3, background: caretColor, verticalAlign: '-0.12em', opacity: caretVisible ? 1 : 0}} />}</span>;
};
