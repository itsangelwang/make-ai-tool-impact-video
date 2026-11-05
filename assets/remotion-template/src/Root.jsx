import React from 'react';
import {Composition} from 'remotion';
import {VerticalImpact} from './VerticalImpact';
import {ComponentsDemo} from './ComponentsDemo';
import {ToolkitPreview} from './ToolkitPreview';
import {Cover} from './Cover';
import story from './story.json';

export const Root = () => (
  <>
    <Composition
      id="VerticalImpact"
      component={VerticalImpact}
      width={1080}
      height={1920}
      fps={30}
      durationInFrames={Math.round((story.duration_sec || 60) * 30)}
      defaultProps={{story}}
    />
    {/* Covers: one layout per ratio. 9:16 for Shorts, TikTok and Reels; 3:4 for Xiaohongshu and profile grids.
        They last as long as the video so the frozen inset can show any moment (scenes past the
        composition's end would not render); `remotion still` takes frame 0. */}
    <Composition id="Cover" component={Cover} width={1080} height={1920} fps={30} durationInFrames={Math.round((story.duration_sec || 60) * 30)} defaultProps={{story, ratio: '9:16'}} />
    <Composition id="Cover34" component={Cover} width={1080} height={1440} fps={30} durationInFrames={Math.round((story.duration_sec || 60) * 30)} defaultProps={{story, ratio: '3:4'}} />
    <Composition id="ToolkitPreview" component={ToolkitPreview} width={1080} height={1920} fps={30} durationInFrames={60} />
    <Composition id="ComponentsDemo" component={ComponentsDemo} width={1080} height={1920} fps={30} durationInFrames={240} />
  </>
);
