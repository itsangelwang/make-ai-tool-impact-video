import React from 'react';
import {Img, staticFile} from 'remotion';

/** Show one region of a real screenshot at a readable size.
 * src: file under public/ (e.g. 'assets/tool.png'); sourceWidth: the image's pixel width;
 * crop: {x, y, w, h} in source pixels; width: displayed width in frame pixels.
 * Map a source point (sx, sy) to the frame with left + (sx - crop.x) * width / crop.w.
 * Crop to the region being discussed so product text reaches ~40 px on mobile. */
export const Shot = ({src, sourceWidth, crop, width, style = {}}) => {
  if (!sourceWidth || !crop?.w || !crop?.h) throw new Error('Shot requires sourceWidth and a crop with positive w and h');
  const k = width / crop.w;
  return (
    <div style={{position: 'relative', width, height: crop.h * k, overflow: 'hidden', ...style}}>
      <Img src={staticFile(src)} style={{position: 'absolute', left: -crop.x * k, top: -crop.y * k, width: sourceWidth * k, maxWidth: 'none'}} />
    </div>
  );
};
