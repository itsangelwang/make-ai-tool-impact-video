import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {Cursor, getClickState} from './components/Cursor';
import {TypingText} from './components/TypingText';
import {FocusZoom} from './components/FocusZoom';
import {ProgressBar} from './components/ProgressBar';

// Illustrative interface, not a reconstruction of a named product.
export const ComponentsDemo = () => {
  const frame = useCurrentFrame();
  const click = getClickState(frame, 60);
  const opening = interpolate(frame, [0, 18], [0.94, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const headerOpacity = interpolate(frame, [156, 180], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const result = interpolate(frame, [138, 150], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return <AbsoluteFill style={{background: '#f6f4ed', color: '#20252b', fontFamily: 'Arial, sans-serif'}}>
    <ProgressBar durationsInFrames={[40, 44, 66, 90]} />
    <FocusZoom startFrame={156} durationInFrames={36} scale={1.15} target={{x: 540, y: 1180}} destination={{x: 540, y: 980}}>
      <div style={{position: 'absolute', top: 220, left: 100, width: 880, transform: `scale(${opening})`, transformOrigin: 'center top'}}>
        <div style={{opacity: headerOpacity}}>
        <div style={{fontSize: 24, color: '#637078', marginBottom: 26}}>ILLUSTRATIVE WORKSPACE</div>
        <h1 style={{fontSize: 58, margin: '0 0 18px'}}>Prepare your brief</h1>
        <div style={{fontSize: 30, color: '#637078', marginBottom: 44}}>Bring your notes. Keep the decisions.</div>
        </div>
        <div style={{height: 910, background: '#fff', border: '2px solid #dcdedb', borderRadius: 28, padding: 40, position: 'relative'}}>
          <div style={{fontSize: 28, color: '#637078'}}>SOURCE DOCUMENT</div>
          <div style={{position: 'absolute', top: 110, left: 40, right: 40, height: 240}}>
            <div style={{opacity: click.oldOpacity}}>
              <div style={{fontSize: 38, marginBottom: 22}}>Add your meeting notes</div>
              <div style={{fontSize: 28, color: '#637078'}}>Choose a document to get started.</div>
            </div>
            <div style={{position: 'absolute', top: 0, opacity: click.newOpacity}}>
              <div style={{fontSize: 38, marginBottom: 22}}>✓ Meeting notes uploaded</div>
              <div style={{fontSize: 28, color: '#637078'}}>team-notes.txt · Ready to review</div>
            </div>
          </div>
          <div style={{position: 'absolute', left: 40, top: 285, width: 240, height: 76, borderRadius: 16, background: click.targetActive > 0 ? '#356a7c' : '#447d92', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 32, transform: `scale(${click.targetScale})`}}>Upload</div>
          <div style={{position: 'absolute', top: 415, left: 40, right: 40, opacity: click.newOpacity}}>
            <div style={{fontSize: 28, marginBottom: 16}}>Brief title</div>
            <div style={{height: 82, border: '2px solid #447d92', borderRadius: 12, padding: '22px 18px', boxSizing: 'border-box', fontSize: 30}}><TypingText text="Monday team brief" startFrame={90} charactersPerSecond={12} /></div>
          </div>
          <div style={{position: 'absolute', top: 625, left: 40, right: 40, opacity: result, transform: `translateY(${(1 - result) * 20}px)`, background: '#edf3ef', borderRadius: 18, padding: 28}}>
            <div style={{fontSize: 25, color: '#447d92', marginBottom: 18}}>READY FOR YOUR REVIEW</div>
            <div style={{fontSize: 38, marginBottom: 18}}>Monday team brief</div>
            <div style={{fontSize: 28, lineHeight: 1.5}}>Decision: launch the pilot.<br />Owner: Alex · Next step: check scope.</div>
          </div>
        </div>
      </div>
      <Cursor path={[{frame: 0, x: 790, y: 880}, {frame: 24, x: 790, y: 880}, {frame: 50, x: 280, y: 749}, {frame: 84, x: 280, y: 749}, {frame: 96, x: 680, y: 905}, {frame: 150, x: 680, y: 905}, {frame: 156, x: 840, y: 1240}]} clicks={[60]} />
    </FocusZoom>
  </AbsoluteFill>;
};
