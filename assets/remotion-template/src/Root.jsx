import React from 'react';
import {Composition} from 'remotion';
import {VerticalImpact} from './VerticalImpact';
import story from './story.json';

export const Root = () => (
  <Composition
    id="VerticalImpact"
    component={VerticalImpact}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={Math.round((story.duration_sec || 60) * 30)}
    defaultProps={{story}}
  />
);
