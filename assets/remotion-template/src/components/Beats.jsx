import React from 'react';
import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';
import {Cursor, getClickState} from './Cursor';
import {Burst} from './Emphasis';
import {Icon} from './Icon';
import {Shot} from './Shot';
import {Sfx} from './Sfx';

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
        {feature.date ? <span style={{fontSize: 30, fontWeight: 800, color: palette.muted}}>{feature.date}</span> : null}
      </div>
      <div style={{fontSize: 80, fontWeight: 900, color: palette.ink, letterSpacing: -2, marginTop: 22, lineHeight: 1}}>{feature.name}{feature.accent ? <span style={{color: palette.cool}}> {feature.accent}</span> : null}</div>
      {feature.capability ? <div style={{fontSize: 40, fontWeight: 800, color: palette.muted, marginTop: 16}}>{feature.capability}</div> : null}
      {items.length ? <div style={{display: 'flex', gap: 22, marginTop: 32}}>{items.slice(0, 3).map((item, i) => {
        const t = frame < at + 12 + i * 6 ? 0 : spring({frame: frame - at - 12 - i * 6, fps, config: {damping: 9, stiffness: 200}});
        return <div key={item.label} style={{flex: 1, height: 170, borderRadius: 28, background: `${palette.cool}14`, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 10, transform: `scale(${t})`, opacity: Math.min(1, t * 2)}}>
          <Icon name={item.icon} size={76} color={palette.cool} /><span style={{fontSize: 34, fontWeight: 900, color: palette.ink}}>{item.label}</span>
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
      <div style={{fontSize: 28, fontWeight: 800, color: palette.muted}}>{youLabel}</div>
      <div style={{display: 'flex', alignItems: 'center', gap: 14, marginTop: 10}}><Icon name={you.icon} size={56} color={palette.ink} /><span style={{fontSize: 40, fontWeight: 900, color: palette.ink}}>{you.label}</span></div>
    </div>
    <div style={{display: 'flex', alignItems: 'center', fontSize: 50, color: palette.cool, fontWeight: 900}}>→</div>
    <div style={card({flex: 1, padding: '24px 28px', border: `4px solid ${palette.cool}`})}>
      <div style={{fontSize: 28, fontWeight: 800, color: palette.cool}}>{ai.name}</div>
      <div style={{display: 'flex', flexWrap: 'wrap', gap: 22, marginTop: 10}}>{(ai.outputs || []).map((out, i) => {
        const t = frame < tickAt(i) ? 0 : spring({frame: frame - tickAt(i), fps, config: {damping: 9, stiffness: 200}});
        return <div key={out.label} style={{display: 'flex', alignItems: 'center', gap: 10, opacity: 0.35 + 0.65 * Math.min(1, t)}}>
          <Icon name={out.icon} size={52} color={palette.cool} /><span style={{fontSize: 38, fontWeight: 900, color: palette.ink}}>{out.label}</span>
          <span style={{display: 'inline-flex', width: 40, height: 40, borderRadius: '50%', background: palette.cool, color: '#fff', fontSize: 26, alignItems: 'center', justifyContent: 'center', transform: `scale(${t})`}}>✓</span>
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
      <Icon name={check.icon} size={76} color={palette.warm} />
      <div style={{fontSize: 38, fontWeight: 900, color: palette.ink, marginTop: 14, lineHeight: 1.15}}>{check.label}</div>
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
    <div style={{fontSize: 28, fontWeight: 800, letterSpacing: 2, color: palette.muted, marginBottom: 14}}>{label}</div>
    <div style={{display: 'flex', gap: 12}}>{plans.map((plan, i) => {
      const start = at + 4 + i * 5;
      const t = plan.on && frame >= start ? spring({frame: frame - start, fps, config: {damping: 10, stiffness: 200}}) : 0;
      const lit = t > 0.5;
      return <div key={plan.name} style={{flex: 1, height: 84, borderRadius: 20, background: lit ? '#2E8B57' : '#fff', color: lit ? '#fff' : palette.muted, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 30, fontWeight: 900, textDecoration: plan.on ? 'none' : 'line-through', transform: `scale(${0.9 + Math.min(1, t) * 0.1})`, boxShadow: '0 8px 20px rgba(23,25,35,.08)'}}>
        {plan.name}{lit ? ' ✓' : ''}{sound && plan.on ? <Sfx at={start} name="pop" volume={0.35} /> : null}
      </div>;
    })}</div>
  </div>;
};

/** A real screenshot region with an optional cursor click, a top-down reveal of
 * the result, a NEW stamp, and a pointed callout. Coordinates are source pixels.
 * shot: {src, source_width, crop: {x, y, w, h}}; click: {at, x, y};
 * reveal: {at, frames}; stamp: {at, label}; callout: {at, x, y, title, note}. */
export const ProductShot = ({shot, width = 936, click, reveal, stamp, callout, evidence, palette, font, sound = false}) => {
  const frame = useCurrentFrame();
  const k = width / shot.crop.w;
  const toFrame = (x, y) => ({x: (x - shot.crop.x) * k, y: (y - shot.crop.y) * k});
  const shown = reveal ? interpolate(frame, [reveal.at, reveal.at + (reveal.frames || 30)], [0, 100], clamp) : 100;
  const press = click ? getClickState(frame, click.at) : null;
  const target = click ? toFrame(click.x, click.y) : null;
  const point = callout ? toFrame(callout.x, callout.y) : null;
  const calloutIn = useSpring(callout ? callout.at : 0, {damping: 9, stiffness: 180});
  return <div style={{position: 'relative', width}}>
    {evidence ? <div style={{fontFamily: font, fontSize: 28, fontWeight: 700, color: palette.muted, letterSpacing: 0.5, marginBottom: 14}}>{evidence}</div> : null}
    <div style={card({overflow: 'hidden', clipPath: `inset(0 0 ${100 - shown}% 0)`, transform: press ? `scale(${press.targetScale})` : undefined})}>
      <Shot src={shot.src} sourceWidth={shot.source_width} crop={shot.crop} width={width} />
    </div>
    {click ? <Cursor path={[{frame: Math.max(0, click.at - 30), x: target.x - 160, y: target.y + 260}, {frame: click.at - 4, x: target.x, y: target.y}, {frame: click.at + 10, x: target.x, y: target.y}, {frame: click.at + 34, x: target.x + 220, y: target.y + 520}]} clicks={[click.at]} rippleColor={palette.cool} /> : null}
    {stamp ? <NewStamp at={stamp.at} label={stamp.label} palette={palette} font={font} sound={sound} style={{right: -10, top: -40}} /> : null}
    {callout && calloutIn ? <div style={{position: 'absolute', left: point.x - 150, top: point.y - 130, width: 300, zIndex: 6, opacity: Math.min(1, calloutIn * 2), transform: `scale(${calloutIn})`, transformOrigin: '50% 100%'}}>
      <div style={{background: palette.warm, color: '#fff', borderRadius: 20, padding: '14px 18px', fontFamily: font, textAlign: 'center', boxShadow: '0 12px 30px rgba(240,100,73,.35)'}}>
        <div style={{fontSize: 34, fontWeight: 900}}>{callout.title}</div>{callout.note ? <div style={{fontSize: 26, fontWeight: 700}}>{callout.note}</div> : null}
      </div>
      <div style={{width: 0, height: 0, margin: '0 auto', borderLeft: '16px solid transparent', borderRight: '16px solid transparent', borderTop: `18px solid ${palette.warm}`}} />
    </div> : null}
    {sound && click ? <Sfx at={click.at} name="return" volume={0.6} /> : null}
    {sound && reveal ? <Sfx at={reveal.at} name="swish" volume={0.3} /> : null}
    {sound && callout ? <Sfx at={callout.at} name="pop" volume={0.5} /> : null}
  </div>;
};
