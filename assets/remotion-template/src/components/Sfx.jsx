import React, {createContext, useContext} from 'react';
import {Audio, Sequence, staticFile} from 'remotion';

/** Play public/<folder>/<name>.wav at frame `at` (local to the enclosing Sequence).
 * Pair every sound with a visible cause; keep it under the narration. */
/** Optional allowlist of sound kinds (story.sfx as an array); null plays every sound. */
export const SfxFilter = createContext(null);

export const Sfx = ({at, name, volume = 0.6, folder = 'audio/sfx', kind = name}) => {
  const allowed = useContext(SfxFilter);
  if (allowed && !allowed.includes(kind)) return null;
  return <Sequence from={Math.max(0, Math.round(at))} durationInFrames={30}>
    <Audio src={staticFile(`${folder}/${name}.wav`)} volume={volume} />
  </Sequence>;
};

/** Real keyboard typing for visible typing: one recorded clip trimmed to the typing span, faded out. */
export const Taps = ({from, count, every = 3, volume = 0.3, folder = 'audio/sfx'}) => {
  const allowed = useContext(SfxFilter);
  if (allowed && !allowed.includes('typing')) return null;
  const frames = Math.max(6, count * every);
  return <Sequence from={Math.max(0, Math.round(from))} durationInFrames={frames}>
    <Audio src={staticFile(`${folder}/typing.wav`)} volume={(f) => volume * Math.min(1, (frames - f) / 6)} />
  </Sequence>;
};
