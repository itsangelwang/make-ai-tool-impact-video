import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame} from 'remotion';
import {Cursor, getClickState} from './components/Cursor';
import {TypingText} from './components/TypingText';
import {FocusZoom} from './components/FocusZoom';
import {ProgressBar} from './components/ProgressBar';

// Illustrative interface, not a reconstruction of a named product.
// All UI/pointer positions use the same 1080×1920 plane. Content ends at
// y=1500, above the 310px caption reserve. The 624px result becomes 936px
// wide at 1.5×, exactly inside the 72px horizontal safe margins.
export const ComponentsDemo = () => {
  const frame = useCurrentFrame();
  const click = getClickState(frame, 60);
  const inputClick = getClickState(frame, 94);
  const opening = interpolate(frame, [0, 18], [18, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const contextOpacity = interpolate(frame, [156, 180], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const result = interpolate(frame, [138, 150], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const surface = {background: '#fff', border: '2px solid #dcdedb', borderRadius: 28, boxSizing: 'border-box'};
  return <AbsoluteFill style={{background: '#f6f4ed', color: '#20252b', fontFamily: 'Arial, sans-serif'}}>
    <ProgressBar durationsInFrames={[40, 44, 66, 90]} />
    <FocusZoom startFrame={156} durationInFrames={36} scale={1.5} target={{x: 540, y: 1380}} destination={{x: 540, y: 1000}}>
      <div style={{opacity: contextOpacity}}>
        <div style={{position: 'absolute', top: 210 + opening, left: 72, width: 936}}>
          <div style={{fontSize: 28, lineHeight: '34px', color: '#637078', marginBottom: 20}}>ILLUSTRATIVE WORKSPACE</div>
          <h1 style={{fontSize: 72, lineHeight: '84px', margin: '0 0 18px'}}>Prepare your brief</h1>
          <div style={{fontSize: 36, lineHeight: '44px', color: '#637078'}}>Bring your notes. Keep the decisions.</div>
        </div>
        <div style={{...surface, position: 'absolute', top: 450, left: 72, width: 936, padding: 36}}>
          <div style={{fontSize: 28, lineHeight: '34px', color: '#637078', marginBottom: 24}}>SOURCE DOCUMENT</div>
          <div style={{display: 'grid', marginBottom: 28}}>
            <div style={{gridArea: '1 / 1', opacity: click.oldOpacity}}>
              <div style={{fontSize: 52, lineHeight: '64px', marginBottom: 16}}>Add your meeting notes</div>
              <div style={{fontSize: 36, lineHeight: '44px', color: '#637078'}}>Choose a document to get started.</div>
            </div>
            <div style={{gridArea: '1 / 1', opacity: click.newOpacity}}>
              <div style={{fontSize: 52, lineHeight: '64px', marginBottom: 16}}>✓ Meeting notes uploaded</div>
              <div style={{fontSize: 36, lineHeight: '44px', color: '#637078'}}>team-notes.txt · Ready to review</div>
            </div>
          </div>
          <div style={{width: 300, height: 100, borderRadius: 16, background: click.targetActive > 0 ? '#356a7c' : '#447d92', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 44, transform: `scale(${click.targetScale})`}}>Upload</div>
        </div>
        <div style={{position: 'absolute', top: 960, left: 72, width: 936}}>
          <div style={{fontSize: 36, lineHeight: '44px', marginBottom: 16}}>Brief title</div>
          <div style={{...surface, height: 100, borderColor: inputClick.targetActive > 0 ? '#447d92' : '#a9b3b6', background: inputClick.phase === 'press' ? '#edf3ef' : '#fff', padding: '22px 28px', fontSize: 44, lineHeight: '52px'}}>
            {frame < 102 && <span style={{color: '#637078'}}>Name your brief</span>}
            <TypingText text="Monday brief" startFrame={102} charactersPerSecond={18} showCaret={frame >= 94} />
          </div>
        </div>
      </div>
      <div style={{position: 'absolute', top: 1160, left: 228, width: 624, boxSizing: 'border-box', display: 'grid', background: '#edf3ef', borderRadius: 24, padding: 32}}>
        <div style={{gridArea: '1 / 1', opacity: 1 - result, color: '#637078'}}>
          <div style={{fontSize: 28, lineHeight: '34px', marginBottom: 20}}>BRIEF PREVIEW</div>
          <div style={{fontSize: 52, lineHeight: '64px', marginBottom: 24}}>Your meeting brief</div>
          <div style={{fontSize: 52, lineHeight: '63px', marginBottom: 8}}>Decision: pending</div>
          <div style={{fontSize: 52, lineHeight: '63px'}}>Owner: pending</div>
        </div>
        <div style={{gridArea: '1 / 1', opacity: result, transform: `translateY(${(1 - result) * 20}px)`}}>
        <div style={{fontSize: 28, lineHeight: '34px', color: '#447d92', marginBottom: 20}}>READY FOR YOUR REVIEW</div>
        <div style={{fontSize: 52, lineHeight: '64px', marginBottom: 24}}>Monday brief</div>
        <div style={{fontSize: 52, lineHeight: '63px', marginBottom: 8}}>Decision: launch pilot.</div>
        <div style={{fontSize: 52, lineHeight: '63px'}}>Owner: Alex</div>
        </div>
      </div>
      {/* Upload center: (260,748). Input center: (540,1070).
          Hold through both presses, then move clear of the result text. */}
      <Cursor path={[{frame: 0, x: 900, y: 900}, {frame: 24, x: 900, y: 900}, {frame: 50, x: 260, y: 748}, {frame: 80, x: 260, y: 748}, {frame: 84, x: 540, y: 1070}, {frame: 122, x: 540, y: 1070}, {frame: 150, x: 810, y: 1490}]} clicks={[60, 94]} />
    </FocusZoom>
  </AbsoluteFill>;
};
