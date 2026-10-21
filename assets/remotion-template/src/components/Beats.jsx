import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Cursor, getClickState} from './Cursor';
import {Burst} from './Emphasis';
import {Icon, objectColor} from './Icon';
import {Shot} from './Shot';
import {Sfx, Taps} from './Sfx';

// Story beats extracted from the first English video. Frames are local to the
// enclosing Sequence. Each takes `palette` and `font`; `sound` adds the matching
// effects from generate_story_audio.py sfx (leave false until those files exist).
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'};
const useSpring = (at, config = {damping: 14, stiffness: 160}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return frame < at ? 0 : spring({frame: frame - at, fps, config});
};
const card = (extra = {}) => ({background: '#fff', borderRadius: 28, boxShadow: '0 14px 34px rgba(23,25,35,.10)', ...extra});

/** Pill that says what is new, e.g. "NEW in ChatGPT". Position with style. */
export const NewTag = ({at, children, palette, font, style = {}}) => {
  const p = useSpring(at, {damping: 9, stiffness: 200});
  if (!p) return null;
  return <div style={{display: 'inline-flex', alignItems: 'center', gap: 12, padding: '12px 24px', borderRadius: 999, background: palette.cool, color: '#fff', fontFamily: font, fontSize: 32, fontWeight: 900, opacity: Math.min(1, p * 2), transform: `scale(${p})`, transformOrigin: '0 50%', ...style}}>
    <span style={{background: '#fff', color: palette.cool, borderRadius: 10, padding: '2px 10px', fontSize: 26, letterSpacing: 1}}>NEW</span>{children}
  </div>;
};

/** Rubber stamp for the moment a new capability's result appears. Position with style. */
export const NewStamp = ({at, label, palette, font, sound = false, style = {}}) => {
  const p = useSpring(at, {damping: 8, stiffness: 240});
  return <>
    {p ? <div style={{position: 'absolute', zIndex: 5, transform: `rotate(-10deg) scale(${2 - p})`, opacity: Math.min(1, p * 1.5), ...style}}>
      <div style={{border: `7px solid ${palette.cool}`, color: palette.cool, background: 'rgba(255,255,255,.94)', borderRadius: 18, padding: '10px 24px', fontFamily: font, fontSize: 44, fontWeight: 900}}>{label}</div>
    </div> : null}
    {sound ? <Sfx at={at} name="stamp" volume={0.7} /> : null}
  </>;
};

/** Names the new tool right after the pain: date, name, capability, and up to
 * three objects it produces. feature: {date, name, accent, capability, items: [{icon, label}]}. */
export const FeatureIntro = ({at, feature, palette, font, sound = false}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = useSpring(at, {damping: 15, stiffness: 150});
  if (!p) return null;
  const items = feature.items || [];
  return <div style={{position: 'relative', opacity: Math.min(1, p * 1.4), transform: `translateY(${(1 - p) * 200}px) scale(${0.9 + p * 0.1})`}}>
    <div style={card({border: `6px solid ${palette.cool}`, borderRadius: 40, padding: '38px 42px 42px', fontFamily: font, boxShadow: '0 30px 80px rgba(104,87,245,.25)'})}>
      <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
        <span style={{background: palette.cool, color: '#fff', borderRadius: 14, padding: '8px 18px', fontSize: 34, fontWeight: 900, letterSpacing: 2}}>NEW</span>
        {feature.date ? <span style={{fontSize: 30, fontWeight: 500, color: palette.muted}}>{feature.date}</span> : null}
      </div>
      <div style={{fontSize: 80, fontWeight: 800, color: palette.ink, letterSpacing: -2, marginTop: 22, lineHeight: 1, textWrap: 'balance'}}>{feature.name}{feature.accent ? <span style={{color: palette.cool}}> {feature.accent}</span> : null}</div>
      {feature.capability ? <div style={{fontSize: 38, fontWeight: 500, color: palette.muted, marginTop: 16, textWrap: 'balance'}}>{feature.capability}</div> : null}
      {items.length ? <div style={{display: 'flex', gap: 22, marginTop: 32}}>{items.slice(0, 3).map((item, i) => {
        const t = frame < at + 12 + i * 6 ? 0 : spring({frame: frame - at - 12 - i * 6, fps, config: {damping: 9, stiffness: 200}});
        const color = objectColor(item.icon, palette, item.color);
        return <div key={item.label} style={{flex: 1, height: 170, borderRadius: 28, background: `${color}1A`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10, transform: `scale(${t})`, opacity: Math.min(1, t * 2)}}>
          <Icon name={item.icon} size={76} color={color} /><span style={{fontSize: 32, fontWeight: 650, color: palette.ink}}>{item.label}</span>
        </div>;
      })}</div> : null}
    </div>
    <Burst x={468} y={300} at={at} size={760} color={palette.cool} />
    {sound ? <><Sfx at={at} name="swish" volume={0.45} /><Sfx at={at + 4} name="coin" volume={0.55} />{items.slice(0, 3).map((_, i) => <Sfx key={i} at={at + 12 + i * 6} name="pop" volume={0.4} />)}</> : null}
  </div>;
};

/** Who did what: the person's one action, then the AI's outputs ticking off.
 * you: {icon, label}; ai: {name, outputs: [{icon, label}]}. */
export const RoleStrip = ({at, you, ai, palette, font, sound = false, youLabel = 'YOU'}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = useSpring(at, {damping: 16, stiffness: 140});
  if (!p) return null;
  const tickAt = (i) => at + 18 + i * 18;
  return <div style={{display: 'flex', gap: 20, alignItems: 'stretch', fontFamily: font, opacity: p, transform: `translateY(${(1 - p) * 40}px)`}}>
    <div style={card({flex: '0 0 300px', padding: '24px 28px'})}>
      <div style={{fontSize: 24, fontWeight: 700, letterSpacing: 3, color: palette.muted}}>{youLabel}</div>
      <div style={{display: 'flex', alignItems: 'center', gap: 14, marginTop: 10}}><Icon name={you.icon} size={56} color={objectColor(you.icon, palette, you.color)} /><span style={{fontSize: 38, fontWeight: 700, color: palette.ink, whiteSpace: 'nowrap'}}>{you.label}</span></div>
    </div>
    <div style={{display: 'flex', alignItems: 'center', fontSize: 50, color: palette.cool, fontWeight: 900}}>→</div>
    <div style={card({flex: 1, padding: '24px 28px', border: `4px solid ${palette.cool}`})}>
      <div style={{fontSize: 24, fontWeight: 700, letterSpacing: 3, textTransform: 'uppercase', color: palette.cool}}>{ai.name}</div>
      <div style={{display: 'flex', flexWrap: 'wrap', gap: 22, marginTop: 10}}>{(ai.outputs || []).map((out, i) => {
        const t = frame < tickAt(i) ? 0 : spring({frame: frame - tickAt(i), fps, config: {damping: 9, stiffness: 200}});
        return <div key={out.label} style={{display: 'flex', alignItems: 'center', gap: 10, opacity: 0.35 + 0.65 * Math.min(1, t)}}>
          <Icon name={out.icon} size={52} color={objectColor(out.icon, palette, out.color)} /><span style={{fontSize: 36, fontWeight: 700, color: palette.ink}}>{out.label}</span>
          <span style={{display: 'inline-flex', width: 40, height: 40, borderRadius: '50%', background: objectColor(out.icon, palette, out.color), color: '#fff', fontSize: 26, alignItems: 'center', justifyContent: 'center', transform: `scale(${t})`}}>✓</span>
        </div>;
      })}</div>
    </div>
    {sound ? (ai.outputs || []).map((_, i) => <Sfx key={i} at={tickAt(i)} name="pop" volume={0.45} />) : null}
  </div>;
};

/** The concrete things the person still verifies, each checked in turn.
 * checks: [{icon, label}], up to three. */
export const CheckCards = ({at, checks, palette, font, sound = false}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return <div style={{display: 'flex', gap: 20}}>{checks.slice(0, 3).map((check, i) => {
    const start = at + i * 14;
    const t = frame < start ? 0 : spring({frame: frame - start, fps, config: {damping: 10, stiffness: 180}});
    return <div key={check.label} style={card({flex: 1, position: 'relative', padding: '30px 26px', fontFamily: font, opacity: Math.min(1, t * 1.5), transform: `translateY(${(1 - t) * 40}px)`})}>
      <Icon name={check.icon} size={76} color={objectColor(check.icon, palette, check.color)} />
      <div style={{fontSize: 36, fontWeight: 700, color: palette.ink, marginTop: 14, lineHeight: 1.15, textWrap: 'balance'}}>{check.label}</div>
      <div style={{position: 'absolute', right: 22, top: 22, width: 54, height: 54, borderRadius: '50%', background: palette.warm, color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 34, fontWeight: 900, transform: `scale(${t})`}}>✓</div>
      {sound ? <Sfx at={start + 6} name="pop" volume={0.5} /> : null}
    </div>;
  })}</div>;
};

/** Current access from the official source: plans light up one by one.
 * plans: [{name, on}]; label: e.g. "ROLLING OUT ON" or "BETA, US ONLY". */
export const AccessChips = ({at, label, plans, palette, font, sound = false}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = useSpring(at);
  return <div style={{fontFamily: font, opacity: p}}>
    <div style={{fontSize: 24, fontWeight: 700, letterSpacing: 3, color: palette.muted, marginBottom: 14}}>{label}</div>
    <div style={{display: 'flex', gap: 12}}>{plans.map((plan, i) => {
      const start = at + 4 + i * 5;
      const t = plan.on && frame >= start ? spring({frame: frame - start, fps, config: {damping: 10, stiffness: 200}}) : 0;
      const lit = t > 0.5;
      return <div key={plan.name} style={{flex: 1, height: 84, borderRadius: 20, background: lit ? '#2E8B57' : '#fff', color: lit ? '#fff' : palette.muted, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 30, fontWeight: plan.on ? 700 : 500, textDecoration: plan.on ? 'none' : 'line-through', transform: `scale(${0.9 + Math.min(1, t) * 0.1})`, boxShadow: '0 8px 20px rgba(23,25,35,.08)'}}>
        {plan.name}{lit ? ' ✓' : ''}{sound && plan.on ? <Sfx at={start} name="pop" volume={0.35} /> : null}
      </div>;
    })}</div>
  </div>;
};

/** A real screenshot region with an optional cursor click, a top-down reveal of
 * the result, a NEW stamp, and a pointed callout. Coordinates are source pixels.
 * shot: {src, source_width, crop: {x, y, w, h}}; click: {at, x, y};
 * reveal: {at, frames}; stamp: {at, label}; callout: {at, x, y, title, note}. */
const lerp = (a, b, t) => a + (b - a) * t;
const smooth = (x) => x * x * (3 - 2 * x);

/** Dims a shot except one horizontal band (source y, h), so the viewer reads one row at a time.
 * focus: [{at, y, h}] in order; each band holds until the next one starts. */
const FocusBands = ({focus, crop, k, palette}) => {
  const frame = useCurrentFrame();
  const active = [...focus].reverse().find((band) => frame >= band.at);
  if (!active) return null;
  const fade = interpolate(frame, [active.at, active.at + 8], [0, 1], clamp);
  const top = (active.y - crop.y) * k;
  const height = active.h * k;
  const shade = {position: 'absolute', left: 0, right: 0, background: palette.paper, opacity: 0.78 * fade, pointerEvents: 'none'};
  return <>
    <div style={{...shade, top: 0, height: Math.max(0, top)}} />
    <div style={{...shade, top: top + height, bottom: 0}} />
    <div style={{position: 'absolute', left: -6, right: -6, top: top - 4, height: height + 8, border: `5px solid ${palette.accent || palette.cool}`, borderRadius: 16, opacity: fade, pointerEvents: 'none'}} />
  </>;
};

/** A real screenshot region with real-feeling operation on top. Coordinates are source pixels.
 * shot: {src, source_width, crop}; zoom: {at, frames, from: crop} starts wide on the full result and
 * pushes in to `crop` (keep the same aspect ratio); drag: {at, frames, from: {x, y}, to: {x, y}, file,
 * region, mask} carries a file card in with the pointer and reveals `region` on drop; type: {at, frames,
 * region, lines, mask} reveals the real text left to right, line by line, with a caret; click: {at, x, y}
 * hovers (hand pointer, glow), presses, and ripples; wait: {at, frames} shows neutral progress dots;
 * reveal, stamp, focus, callout, and summary ({at, text, until}) as before. */
export const ProductShot = ({shot, width = 936, click, reveal, stamp, callout, focus, zoom, drag, type, wait, summary, evidence, palette, font, sound = false}) => {
  const frame = useCurrentFrame();
  const final = shot.crop;
  const zt = zoom ? smooth(interpolate(frame, [zoom.at, zoom.at + (zoom.frames || 24)], [0, 1], clamp)) : 1;
  const crop = zoom ? {x: lerp(zoom.from.x, final.x, zt), y: lerp(zoom.from.y, final.y, zt), w: lerp(zoom.from.w, final.w, zt), h: lerp(zoom.from.h, final.h, zt)} : final;
  const k = width / crop.w;
  const boxHeight = final.h * (width / final.w);
  const toFrame = (x, y) => ({x: (x - crop.x) * k, y: (y - crop.y) * k});
  const box = (r) => ({left: (r.x - crop.x) * k, top: (r.y - crop.y) * k, width: r.w * k, height: r.h * k});
  const shown = reveal ? interpolate(frame, [reveal.at, reveal.at + (reveal.frames || 30)], [0, 100], clamp) : 100;
  const press = click ? getClickState(frame, click.at) : null;
  const target = click ? toFrame(click.x, click.y) : null;
  const point = callout ? toFrame(callout.x, callout.y) : null;
  const calloutIn = useSpring(callout ? callout.at : 0, {damping: 9, stiffness: 180});
  const calloutGone = callout && Number.isFinite(callout.until) ? interpolate(frame, [callout.until, callout.until + 6], [1, 0], clamp) : 1;
  const summaryIn = useSpring(summary ? summary.at : 0, {damping: 12, stiffness: 180});
  const summaryGone = summary && Number.isFinite(summary.until) ? interpolate(frame, [summary.until, summary.until + 8], [1, 0], clamp) : 1;

  // One pointer path through the drag, then the click.
  const path = [];
  if (drag) {
    const a = toFrame(drag.from.x, drag.from.y), b = toFrame(drag.to.x, drag.to.y), f = drag.frames || 36;
    path.push({frame: drag.at, x: a.x, y: a.y}, {frame: drag.at + f * 0.55, x: lerp(a.x, b.x, 0.6), y: Math.min(a.y, b.y) - 70}, {frame: drag.at + f, x: b.x, y: b.y}, {frame: drag.at + f + 10, x: b.x + 30, y: b.y + 40});
  }
  if (click) {
    const last = path[path.length - 1];
    const startFrame = last ? Math.max(last.frame + 4, click.at - 34) : Math.max(0, click.at - 34);
    const from = last && last.frame < startFrame ? last : {x: target.x - 260, y: target.y + 240};
    if (!last || last.frame < startFrame) path.push({frame: startFrame, x: from.x, y: from.y});
    path.push({frame: lerp(startFrame, click.at - 6, 0.5), x: lerp(from.x, target.x, 0.55), y: Math.min(from.y, target.y) - 50}, {frame: click.at - 6, x: target.x, y: target.y}, {frame: click.at + 12, x: target.x, y: target.y}, {frame: click.at + 36, x: target.x + 120, y: target.y + 160});
  }
  const hover = click ? Math.min(1, Math.max(0, (frame - (click.at - 12)) / 6)) * (frame < click.at + 14 ? 1 : 0) : 0;

  // Drag: file card follows the pointer; the region stays hidden until the drop, then pops in.
  const dragEnd = drag ? drag.at + (drag.frames || 36) : 0;
  const pointerAt = (f) => {
    const next = path.findIndex((pt) => pt.frame > f);
    const p0 = next <= 0 ? path[Math.max(0, next === 0 ? 0 : path.length - 1)] : path[next - 1];
    const p1 = next <= 0 ? p0 : path[next];
    const t = p0 === p1 ? 0 : smooth(Math.min(1, (f - p0.frame) / (p1.frame - p0.frame)));
    return {x: lerp(p0.x, p1.x, t), y: lerp(p0.y, p1.y, t)};
  };
  const dropPop = drag ? interpolate(frame, [dragEnd, dragEnd + 8], [0, 1], clamp) : 1;
  // Typing: each line of the region is uncovered left to right in turn.
  const typeT = type ? interpolate(frame, [type.at, type.at + (type.frames || 45)], [0, 1], clamp) : 1;
  const lines = type ? type.lines || 1 : 1;

  return <div style={{position: 'relative', width}}>
    {evidence ? <div style={{fontFamily: font, fontSize: 24, fontWeight: 700, letterSpacing: 2, color: palette.muted, marginBottom: 14}}>{evidence}</div> : null}
    {/* Overlays share the screenshot's box so source coordinates line up exactly. */}
    <div style={{position: 'relative'}}>
    <div style={card({position: 'relative', height: boxHeight, overflow: 'hidden', clipPath: `inset(0 0 ${100 - shown}% 0)`})}>
      <Shot src={shot.src} sourceWidth={shot.source_width} crop={crop} width={width} />
      {drag && drag.region ? <div style={{position: 'absolute', ...box(drag.region), background: drag.mask || '#fff', opacity: 1 - dropPop}} /> : null}
      {type ? Array.from({length: lines}, (_, i) => {
        const r = type.region, lineH = r.h / lines;
        const t = Math.max(0, Math.min(1, typeT * lines - i));
        const b = box({x: r.x, y: r.y + i * lineH, w: r.w, h: lineH});
        return <div key={i} style={{position: 'absolute', left: b.left + b.width * t, top: b.top, width: b.width * (1 - t) + 4, height: b.height, background: type.mask || '#fff'}}>
          {t > 0 && t < 1 || (i === lines - 1 && typeT >= 1 && Math.floor(frame / 15) % 2 === 0 && frame < type.at + (type.frames || 45) + 20) ? <div style={{position: 'absolute', left: 0, top: b.height * 0.15, width: 3, height: b.height * 0.7, background: palette.ink}} /> : null}
        </div>;
      }) : null}
      {focus?.length ? <FocusBands focus={focus} crop={crop} k={k} palette={palette} /> : null}
      {click && hover > 0 ? <div style={{position: 'absolute', left: target.x - 46, top: target.y - 46, width: 92, height: 92, borderRadius: '50%', boxShadow: `0 0 0 ${6 * hover}px ${palette.cool}55`, background: press && press.phase === 'press' ? 'rgba(0,0,0,.18)' : 'transparent', transform: `scale(${press ? press.targetScale : 1})`}} /> : null}
      {wait && frame >= wait.at && frame < wait.at + (wait.frames || 30) ? <div style={{position: 'absolute', inset: 0, background: 'rgba(255,255,255,.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 16}}>
        {[0, 1, 2].map((i) => <div key={i} style={{width: 22, height: 22, borderRadius: '50%', background: palette.cool, transform: `translateY(${Math.sin((frame - wait.at) / 3 - i) * 10}px)`, opacity: 0.85}} />)}
      </div> : null}
    </div>
    {drag && frame >= drag.at && frame < dragEnd + 4 ? (() => {
      const pt = pointerAt(frame);
      const shrink = interpolate(frame, [dragEnd - 6, dragEnd + 4], [1, 0.4], clamp);
      return <div style={{position: 'absolute', left: pt.x + 18, top: pt.y + 18, zIndex: 19, transform: `scale(${shrink}) rotate(${-4 * shrink}deg)`, transformOrigin: '0 0', opacity: shrink, display: 'flex', alignItems: 'center', gap: 12, padding: '14px 20px', borderRadius: 18, background: '#fff', boxShadow: '0 18px 40px rgba(23,25,35,.25)', fontFamily: font, fontSize: 26, fontWeight: 600, color: palette.ink, whiteSpace: 'nowrap'}}>
        <Icon name="mic" size={40} color={objectColor('mic', palette)} />{drag.file}
      </div>;
    })() : null}
    {path.length ? <Cursor path={path} clicks={click ? [click.at] : []} hand={click ? [[click.at - 12, click.at + 14]] : []} rippleColor={palette.cool} /> : null}
    {summary && summaryIn && summaryGone > 0 ? <div style={{position: 'absolute', left: '50%', top: boxHeight + 26, transformOrigin: '50% 0', transform: `translateX(-50%) scale(${summaryIn})`, opacity: Math.min(1, summaryIn * 2) * summaryGone, zIndex: 7, padding: '20px 30px', borderRadius: 22, background: palette.ink, color: '#fff', fontFamily: font, fontSize: 38, fontWeight: 700, whiteSpace: 'nowrap', boxShadow: '0 20px 50px rgba(23,25,35,.35)'}}>{summary.text}</div> : null}
    {stamp ? <NewStamp at={stamp.at} label={stamp.label} palette={palette} font={font} sound={sound} style={{right: -10, top: -40}} /> : null}
    {callout && calloutIn && calloutGone > 0 ? <div style={{position: 'absolute', left: point.x - 150, top: point.y - 130, width: 300, zIndex: 6, opacity: Math.min(1, calloutIn * 2) * calloutGone, transform: `scale(${calloutIn})`, transformOrigin: '50% 100%'}}>
      <div style={{background: palette.warm, color: '#fff', borderRadius: 20, padding: '14px 18px', fontFamily: font, textAlign: 'center', boxShadow: '0 12px 30px rgba(240,100,73,.35)'}}>
        <div style={{fontSize: 34, fontWeight: 800, textWrap: 'balance'}}>{callout.title}</div>{callout.note ? <div style={{fontSize: 26, fontWeight: 500, opacity: 0.92}}>{callout.note}</div> : null}
      </div>
      <div style={{width: 0, height: 0, margin: '0 auto', borderLeft: '16px solid transparent', borderRight: '16px solid transparent', borderTop: `18px solid ${palette.warm}`}} />
    </div> : null}
    </div>
    {sound && drag ? <><Sfx at={drag.at} name="swish" volume={0.35} /><Sfx at={dragEnd} name="pop" volume={0.55} /></> : null}
    {sound && type ? <Taps from={type.at} count={Math.round((type.frames || 45) / 3)} every={3} volume={0.25} /> : null}
    {sound && focus ? focus.map((band) => <Sfx key={band.at} at={band.at} name="tick" volume={0.35} />) : null}
    {sound && click ? <Sfx at={click.at} name="return" kind="click" volume={0.6} /> : null}
    {sound && reveal ? <Sfx at={reveal.at} name="swish" volume={0.3} /> : null}
    {sound && zoom ? <Sfx at={zoom.at} name="swish" volume={0.25} /> : null}
    {sound && wait ? <Sfx at={wait.at + (wait.frames || 30)} name="coin" volume={0.45} /> : null}
    {sound && callout ? <Sfx at={callout.at} name="pop" volume={0.5} /> : null}
  </div>;
};

/** Icon tiles that appear one by one with arrows between them: the default way to show
 * steps or a handoff without text cards. items: [{icon, label, at}] (2-4); `label` is 1-2 words. */
export const Flow = ({items, palette, font, sound = false, accent}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const color = accent || palette.cool;
  const size = items.length > 3 ? 190 : 250;
  return <div style={{display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 14}}>
    {items.map((item, i) => {
      const t = frame < item.at ? 0 : spring({frame: frame - item.at, fps, config: {damping: 11, stiffness: 190}});
      const tint = objectColor(item.icon, palette, item.color);
      const grow = Math.min(1, t * 1.4); // a tile takes space as it appears, so the row stays centred
      return <React.Fragment key={`${item.label}-${i}`}>
        {i ? <div style={{width: 54 * grow, overflow: 'hidden', fontSize: 54, fontWeight: 900, color, opacity: Math.min(1, t * 2), textAlign: 'center'}}>→</div> : null}
        <div style={{width: size * grow, height: size, display: 'flex', justifyContent: 'center'}}><div style={card({width: size, height: size, flex: '0 0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 14, fontFamily: font, opacity: Math.min(1, t * 2), transform: `scale(${0.6 + t * 0.4})`, background: `linear-gradient(180deg, ${tint}1F, #fff 70%)`, border: `5px solid ${tint}`})}>
          <Icon name={item.icon} size={size * 0.42} color={tint} />
          <span style={{fontSize: 34, fontWeight: 700, color: palette.ink, textAlign: 'center', lineHeight: 1.1, textWrap: 'balance'}}>{item.label}</span>
        </div></div>
        {sound ? <Sfx at={item.at} name="pop" volume={0.4} /> : null}
      </React.Fragment>;
    })}
  </div>;
};

/** A wrong value gets struck through and the right one pops in: shows a correction without a paragraph.
 * fix: {at, label, wrong, right}; the strike starts 12 frames after `at`, the right value 10 later. */
export const Correction = ({fix, palette, font, sound = false}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = fix.at > frame ? 0 : spring({frame: frame - fix.at, fps, config: {damping: 14, stiffness: 160}});
  const strike = interpolate(frame, [fix.at + 12, fix.at + 22], [0, 1], clamp);
  const right = frame < fix.at + 24 ? 0 : spring({frame: frame - fix.at - 24, fps, config: {damping: 9, stiffness: 200}});
  return <div style={card({padding: '30px 36px', fontFamily: font, opacity: enter, transform: `translateY(${(1 - enter) * 40}px)`, boxShadow: '0 20px 50px rgba(23,25,35,.12)'})}>
    {fix.label ? <div style={{fontSize: 34, fontWeight: 500, color: palette.muted}}>{fix.label}</div> : null}
    <div style={{display: 'flex', alignItems: 'center', gap: 26, marginTop: 14, flexWrap: 'wrap'}}>
      <span style={{position: 'relative', fontSize: 54, fontWeight: 600, color: palette.muted}}>
        {fix.wrong}
        <span style={{position: 'absolute', left: -6, top: '52%', height: 8, width: `calc(${strike * 100}% + 12px)`, background: palette.warm, borderRadius: 4}} />
      </span>
      <span style={{fontSize: 54, fontWeight: 900, color: palette.warm, opacity: Math.min(1, right * 2)}}>→</span>
      <span style={{fontSize: 62, fontWeight: 800, color: '#2E8B57', transform: `scale(${right})`, display: 'inline-block'}}>{fix.right}</span>
    </div>
    {sound ? <><Sfx at={fix.at + 12} name="swish" volume={0.35} /><Sfx at={fix.at + 24} name="stamp" volume={0.6} /></> : null}
  </div>;
};

/** An audio player whose playhead jumps back and forth: shows "replay, pause, hunt" without text.
 * scrub: {at, length: "30:12", ask, ask_at}; `ask` pops above the bar at `ask_at` (e.g. "Who said Thursday?"). */
export const Scrub = ({scrub, palette, font, sound = false}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = frame < scrub.at ? 0 : spring({frame: frame - scrub.at, fps, config: {damping: 15, stiffness: 160}});
  const stops = [0.08, 0.62, 0.3, 0.74, 0.45, 0.55, 0.38];
  const t = Math.max(0, frame - scrub.at - 8) / 22;
  const i = Math.min(stops.length - 2, Math.floor(t));
  const local = Math.min(1, t - i);
  const eased = local < 0.5 ? 2 * local * local : 1 - (-2 * local + 2) ** 2 / 2;
  const head = stops[i] + (stops[i + 1] - stops[i]) * eased;
  const paused = Math.floor(t) % 2 === 1;
  const ask = scrub.ask_at === undefined || frame < scrub.ask_at ? 0 : spring({frame: frame - scrub.ask_at, fps, config: {damping: 9, stiffness: 190}});
  const total = scrub.length || '30:00';
  const [mm, ss] = total.split(':').map(Number);
  const secs = Math.round(head * (mm * 60 + ss));
  const stamp = `${Math.floor(secs / 60)}:${String(secs % 60).padStart(2, '0')}`;
  return <div style={{position: 'relative', paddingTop: 150, fontFamily: font, opacity: enter}}>
    {ask ? <div style={{position: 'absolute', top: 0, left: `${Math.min(70, head * 100)}%`, transform: `translateX(-40%) scale(${ask})`, transformOrigin: '30% 100%', background: palette.warm, color: '#fff', borderRadius: 22, padding: '16px 24px', fontSize: 38, fontWeight: 800, whiteSpace: 'nowrap', boxShadow: '0 12px 30px rgba(240,100,73,.35)'}}>{scrub.ask}</div> : null}
    <div style={card({padding: '30px 34px', display: 'flex', alignItems: 'center', gap: 26})}>
      <div style={{width: 92, height: 92, borderRadius: '50%', background: palette.ink, display: 'flex', alignItems: 'center', justifyContent: 'center', flex: '0 0 auto'}}>
        <Icon name={paused ? 'pause' : 'play'} size={70} color="#fff" />
      </div>
      <div style={{flex: 1}}>
        <div style={{position: 'relative', height: 16, borderRadius: 8, background: '#E4E6EB'}}>
          <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: `${head * 100}%`, borderRadius: 8, background: palette.warm}} />
          <div style={{position: 'absolute', left: `calc(${head * 100}% - 17px)`, top: -9, width: 34, height: 34, borderRadius: '50%', background: '#fff', border: `6px solid ${palette.warm}`}} />
        </div>
        <div style={{display: 'flex', justifyContent: 'space-between', marginTop: 16, fontSize: 30, fontWeight: 600, color: palette.muted, fontVariantNumeric: 'tabular-nums'}}><span>{stamp}</span><span>{total}</span></div>
      </div>
    </div>
    {sound ? [0, 1, 2, 3, 4, 5].map((n) => <Sfx key={n} at={scrub.at + 8 + n * 22} name="tick" volume={0.3} />) : null}
  </div>;
};

/** A system-style notification that slides down, e.g. "Call ended · Recording saved". Use it as an
 * opening hook so the first frame already shows the situation. toast: {at, icon, title, note, until}. */
export const Toast = ({toast, palette, font, sound = false}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = frame < toast.at ? 0 : spring({frame: frame - toast.at, fps, config: {damping: 14, stiffness: 170}});
  const leave = Number.isFinite(toast.until) ? interpolate(frame, [toast.until, toast.until + 8], [0, 1], clamp) : 0;
  const color = objectColor(toast.icon, palette, toast.color);
  return <div style={{opacity: enter * (1 - leave), transform: `translateY(${(1 - enter) * -60 - leave * 30}px)`}}>
    <div style={card({display: 'flex', alignItems: 'center', gap: 22, padding: '22px 26px', borderRadius: 30, fontFamily: font, boxShadow: '0 20px 50px rgba(23,25,35,.14)'})}>
      <div style={{width: 76, height: 76, borderRadius: 20, background: `${color}1F`, display: 'flex', alignItems: 'center', justifyContent: 'center', flex: '0 0 auto'}}><Icon name={toast.icon} size={48} color={color} /></div>
      <div style={{flex: 1}}>
        <div style={{fontSize: 34, fontWeight: 700, color: palette.ink}}>{toast.title}</div>
        {toast.note ? <div style={{fontSize: 28, fontWeight: 500, color: palette.muted, marginTop: 4}}>{toast.note}</div> : null}
      </div>
      <div style={{fontSize: 24, fontWeight: 500, color: palette.muted, alignSelf: 'flex-start'}}>now</div>
    </div>
    {sound ? <Sfx at={toast.at} name="notify" volume={0.55} /> : null}
  </div>;
};

/** A generic video call that ends: two participants, a running timer, a hang-up click, then the
 * saved recording slides out. Not any real product's UI. call: {at, people: [name, name],
 * timer: "30:12", end_at, file}; the hang-up click happens at end_at. */
export const CallEnd = ({call, palette, font, sound = false}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  // Already on screen at its first frame (it is often the cover), so the spring starts early.
  const enter = spring({frame: frame - call.at + 10, fps, config: {damping: 16, stiffness: 220}});
  const tilesOut = interpolate(frame, [call.end_at + 4, call.end_at + 10], [0, 1], clamp);
  const ended = interpolate(frame, [call.end_at + 10, call.end_at + 16], [0, 1], clamp);
  const fileIn = frame < call.end_at + 16 ? 0 : spring({frame: frame - call.end_at - 16, fps, config: {damping: 12, stiffness: 170}});
  const [mm, ss] = String(call.timer || '30:12').split(':').map(Number);
  const total = mm * 60 + ss;
  const elapsed = Math.min(total, total - 3 + Math.floor(Math.max(0, frame - call.at) / fps));
  const clock = `${Math.floor(elapsed / 60)}:${String(elapsed % 60).padStart(2, '0')}`;
  const tones = [palette.cool, '#0E9F8E'];
  const W = 936, H = 420;
  const hang = {x: W / 2 + 94, y: H - 62}; // centre of the red button, third in the control row
  const press = getClickState(frame, call.end_at);
  return <div style={{position: 'relative', opacity: enter, transform: `scale(${0.94 + 0.06 * enter})`}}>
    <div style={{position: 'relative', width: W, height: H, borderRadius: 36, background: '#1E2230', overflow: 'hidden', boxShadow: '0 30px 70px rgba(23,25,35,.28)', fontFamily: font}}>
      <div style={{position: 'absolute', left: 28, top: 22, display: 'flex', alignItems: 'center', gap: 12, color: '#fff', fontSize: 26, fontWeight: 600}}>
        <span style={{width: 14, height: 14, borderRadius: '50%', background: ended ? '#8A90A2' : '#FF4D4D', opacity: ended ? 1 : 0.6 + 0.4 * Math.abs(Math.sin(frame / 8))}} />
        <span style={{fontVariantNumeric: 'tabular-nums'}}>{ended > 0.5 ? clock : `REC  ${clock}`}</span>
      </div>
      <div style={{position: 'absolute', left: 28, right: 28, top: 70, height: 230, display: 'flex', gap: 20, opacity: 1 - tilesOut, transform: `scale(${1 - tilesOut * 0.06})`}}>
        {(call.people || ['A', 'B']).map((name, i) => {
          const talking = i === 1 && !ended;
          const ring = talking ? 6 + 5 * Math.abs(Math.sin(frame / 5)) : 0;
          return <div key={name} style={{flex: 1, borderRadius: 26, background: '#2B3042', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 14}}>
            <div style={{width: 112, height: 112, borderRadius: '50%', background: tones[i % 2], color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 52, fontWeight: 700, boxShadow: `0 0 0 ${ring}px ${tones[i % 2]}55`}}>{name[0]}</div>
            <div style={{color: '#C9CDDA', fontSize: 26, fontWeight: 500}}>{name}</div>
          </div>;
        })}
      </div>
      {ended > 0 ? <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: ended}}>
        <div style={{display: 'flex', alignItems: 'center', gap: 18, color: '#fff', fontSize: 44, fontWeight: 700}}><Icon name="phone" size={56} color="#FF5A5A" />Call ended</div>
      </div> : null}
      <div style={{position: 'absolute', left: 0, right: 0, bottom: 26, display: 'flex', justifyContent: 'center', gap: 22, opacity: 1 - ended * 0.6}}>
        {['mic', 'play'].map((name) => <div key={name} style={{width: 72, height: 72, borderRadius: '50%', background: '#3A4055', display: 'flex', alignItems: 'center', justifyContent: 'center'}}><Icon name={name} size={40} color="#C9CDDA" /></div>)}
        <div style={{width: 96, height: 72, borderRadius: 36, background: '#FF4D4D', display: 'flex', alignItems: 'center', justifyContent: 'center', transform: `scale(${press.targetScale})`, boxShadow: frame > call.end_at - 12 && frame < call.end_at + 10 ? '0 0 0 8px rgba(255,77,77,.35)' : 'none'}}><Icon name="phone" size={46} color="#fff" /></div>
      </div>
      <Cursor path={[{frame: Math.max(0, call.end_at - 30), x: W * 0.78, y: H * 0.55}, {frame: call.end_at - 6, x: hang.x + 6, y: hang.y}, {frame: call.end_at + 12, x: hang.x + 6, y: hang.y}, {frame: call.end_at + 34, x: W + 80, y: H + 60}]} clicks={[call.end_at]} hand={[[call.end_at - 12, call.end_at + 12]]} color="#ffffff" rippleColor="#FF8A8A" />
    </div>
    <div style={{display: 'flex', justifyContent: 'center', marginTop: -24, opacity: Math.min(1, fileIn * 2), transform: `translateY(${(1 - fileIn) * -40}px)`}}>
      <div style={card({display: 'flex', alignItems: 'center', gap: 16, padding: '18px 26px', borderRadius: 24, fontFamily: font, boxShadow: '0 20px 50px rgba(23,25,35,.18)'})}>
        <Icon name="mic" size={44} color={objectColor('mic', palette)} />
        <span style={{fontSize: 30, fontWeight: 700, color: palette.ink}}>{call.file}</span>
        <span style={{fontSize: 28, fontWeight: 500, color: palette.muted}}>{call.timer}</span>
      </div>
    </div>
    {sound ? <><Sfx at={call.end_at} name="key-2" kind="click" volume={0.5} /><Sfx at={call.end_at + 3} name="callend" volume={0.45} /><Sfx at={call.end_at + 16} name="pop" volume={0.5} /></> : null}
  </div>;
};
