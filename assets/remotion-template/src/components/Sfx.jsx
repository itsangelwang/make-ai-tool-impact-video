import React from 'react';
import {Audio, Sequence, staticFile} from 'remotion';

/** Play public/<folder>/<name>.wav at frame `at` (local to the enclosing Sequence).
 * Pair every sound with a visible cause; keep it under the narration. */
export const Sfx = ({at, name, volume = 0.6, folder = 'audio/sfx'}) => (
  <Sequence from={Math.max(0, Math.round(at))} durationInFrames={30}>
    <Audio src={staticFile(`${folder}/${name}.wav`)} volume={volume} />
  </Sequence>
);

/** Key clicks for visible typing: `count` taps every `every` frames, cycling key variants. */
export const Taps = ({from, count, every = 3, volume = 0.3, folder = 'audio/sfx', names = ['key-1', 'key-2', 'key-3']}) => (
  <>{Array.from({length: count}, (_, i) => <Sfx key={i} at={from + i * every} name={names[(i * 7) % names.length]} volume={volume} folder={folder} />)}</>
);
