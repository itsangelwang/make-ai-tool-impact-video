import React from 'react';
import {Freeze, Img, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

/** Show one region of a real screenshot at a readable size.
 * src: file under public/ (e.g. 'assets/tool.png'); sourceWidth: the image's pixel width;
 * crop: {x, y, w, h} in source pixels; width: displayed width in frame pixels.
 * Map a source point (sx, sy) to the frame with left + (sx - crop.x) * width / crop.w.
 * Crop to the region being discussed so product text reaches ~40 px on mobile. */
/* A .mov/.mp4/.webm src plays as video from fromSec (seconds into the recording) at rate.
 * holdStartSec: show the first frame still until then, then play; freezeAtSec: stop on that moment.
 * alt: {at_sec, src, source_width, crop, from_sec, rate} fades to a second clip or image at at_sec
 * (e.g. the real result after a click); keep alt.crop the same aspect ratio as crop.
 * masks: [{x, y, w, h, from_sec, until_sec, style}] in source pixels and scene seconds, shown only
 * while on screen. style 'tile' is a solid card (fill, radius, optional label + font, e.g.
 * "Photo hidden"), 'bar' a grey text bar on bg (bar_w), anything else a blur. Use solid tiles for
 * people and a named business's identity, and check them frame by frame in the real render. */
export const Shot = ({src, sourceWidth, crop, width, style = {}, fromSec = 0, rate = 1, masks = [], freezeAtSec = null, holdStartSec = 0, alt = null}) => {
  if (!sourceWidth || !crop?.w || !crop?.h) throw new Error('Shot requires sourceWidth and a crop with positive w and h');
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const k = width / crop.w;
  const isVideo = /\.(mov|mp4|webm)$/i.test(src);
  const pos = {position: 'absolute', left: -crop.x * k, top: -crop.y * k, width: sourceWidth * k, maxWidth: 'none'};
  const t = frame / fps;
  return (
    <div style={{position: 'relative', width, height: crop.h * k, overflow: 'hidden', ...style}}>
      {isVideo ? (() => {
        const vid = <OffthreadVideo src={staticFile(src)} startFrom={Math.round(fromSec * fps)} playbackRate={rate} muted style={pos} />;
        if (t < holdStartSec) return <Freeze frame={0}>{vid}</Freeze>;
        if (freezeAtSec !== null && t >= freezeAtSec) return <Freeze frame={Math.round((freezeAtSec - holdStartSec) * fps)}>{vid}</Freeze>;
        return <Sequence from={Math.round(holdStartSec * fps)} layout="none">{vid}</Sequence>;
      })() : <Img src={staticFile(src)} style={pos} />}
      {alt && t >= alt.at_sec ? (() => {
        const ka = width / alt.crop.w;
        const apos = {position: 'absolute', left: -alt.crop.x * ka, top: -alt.crop.y * ka, width: alt.source_width * ka, maxWidth: 'none'};
        const op = Math.min(1, (t - alt.at_sec) / 0.25);
        return <div style={{position: 'absolute', inset: 0, opacity: op, background: '#fff', overflow: 'hidden'}}>{/\.(mov|mp4|webm)$/i.test(alt.src) ? <Sequence from={Math.round(alt.at_sec * fps)} layout="none"><OffthreadVideo src={staticFile(alt.src)} startFrom={Math.round((alt.from_sec || 0) * fps)} playbackRate={alt.rate || 1} muted style={apos} /></Sequence> : <Img src={staticFile(alt.src)} style={apos} />}</div>;
      })() : null}
      {masks.filter((m) => t >= (m.from_sec ?? 0) && t < (m.until_sec ?? 1e9)).map((m, i) => {
        const box = {position: 'absolute', left: (m.x - crop.x) * k, top: (m.y - crop.y) * k, width: m.w * k, height: m.h * k};
        if (m.style === 'tile') return <div key={i} style={{...box, background: m.fill || '#F3EFE8', borderRadius: m.radius ?? 12, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, color: '#8A7F70', fontFamily: 'Inter, -apple-system, sans-serif', fontWeight: 650, fontSize: m.font || 26}}>{m.label ? <><svg width={m.font ? m.font * 1.1 : 28} height={m.font ? m.font * 1.1 : 28} viewBox="0 0 64 64" fill="none" stroke="#8A7F70" strokeWidth="6"><rect x="12" y="28" width="40" height="28" rx="5" /><path d="M20 28v-8a12 12 0 0 1 24 0v8" /></svg>{m.label}</> : null}</div>;
        if (m.style === 'bar') return <div key={i} style={{...box, background: m.bg || '#fff'}}><div style={{position: 'absolute', left: 0, top: '28%', height: '44%', width: m.bar_w || '70%', borderRadius: 999, background: '#E7E8EC'}} /></div>;
        return <div key={i} style={{...box, backdropFilter: 'blur(14px)', WebkitBackdropFilter: 'blur(14px)', background: m.fill || 'rgba(240,241,245,.55)', borderRadius: 10}} />;
      })}
    </div>
  );
};
