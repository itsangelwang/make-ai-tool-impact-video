import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Icon, ICON_NAMES} from './components/Icon';
import {Pop, Burst} from './components/Emphasis';

// Render check for the explainer toolkit: icons, a pop-in label, and a burst ring.
export const ToolkitPreview = () => (
  <AbsoluteFill style={{background: '#F7F4EE', padding: '200px 72px', fontFamily: 'Inter, Arial, sans-serif'}}>
    <div style={{display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 40}}>
      {ICON_NAMES.map((name) => (
        <div key={name} style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, fontSize: 32, color: '#5D6472'}}>
          <Icon name={name} size={120} color="#6857F5" />{name}
        </div>
      ))}
    </div>
    <Pop at={10} style={{left: 72, top: 1380}}>
      <div style={{background: '#F06449', color: '#fff', borderRadius: 20, padding: '16px 24px', fontSize: 40, fontWeight: 900}}>Cheapest?</div>
    </Pop>
    <Burst x={760} y={1420} at={6} />
  </AbsoluteFill>
);
