import React, {createContext, useContext} from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {TimedCaptions} from './TimedCaptions';
import {ProgressBar} from './components/ProgressBar';
import {Icon, objectColor} from './components/Icon';
import {AccessChips, CheckCards, Correction, FeatureIntro, Flow, NewTag, ProductShot, RoleStrip, Scrub} from './components/Beats';

const FONTS = {
  zh: {body: 'PingFang SC, Noto Sans CJK SC, Arial, sans-serif', display: 'Hannotate SC, Kaiti SC, PingFang SC, sans-serif'},
  en: {body: 'Inter, Avenir Next, SF Pro Display, Arial, sans-serif', display: 'Inter, Avenir Next, SF Pro Display, Arial, sans-serif'},
};
const LABELS = {
  zh: {handoff: '交给 AI 处理这一步', humanCheck: '最后一步仍由人负责', nextAction: '今天可以这样试', before: '使用前', after: '使用后', you: '你'},
  en: {handoff: 'AI takes this step', humanCheck: 'You still own the final check', nextAction: 'Try this today', before: 'Before', after: 'After', you: 'YOU'},
};
const localeOf = (story) => (String(story.language || 'en-US').startsWith('en') ? 'en' : 'zh');
const FontContext = createContext(FONTS.zh.body);
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'};
const FPS = 30;
// Beat times in story.json are seconds from the scene start.
const at = (sec) => Math.round((Number(sec) || 0) * FPS);
const withFrames = (item) => (item ? {...item, at: at(item.at_sec)} : item);

const Card = ({children, index = 0, delay = null, accent = '#6857F5'}) => {
  const font = useContext(FontContext);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const start = delay === null ? index * 6 : delay;
  const p = frame < start ? 0 : spring({frame: frame - start, fps, config: {damping: 18, stiffness: 150}});
  return <div style={{padding: '26px 28px', marginBottom: 20, borderRadius: 28, background: '#fff', borderLeft: `10px solid ${accent}`, boxShadow: '0 16px 45px rgba(31,35,48,.10)', textWrap: 'balance', fontFamily: font, fontSize: 42, fontWeight: 600, color: '#161820', opacity: p, transform: `translateY(${(1-p)*55}px) scale(${.96 + p*.04})`}}>{children}</div>;
};

// Type levels: eyebrow (small, spaced caps) > headline (800, one accent word) > labels (600-700) > notes (500, muted).
const Badge = ({children, color}) => <div style={{display: 'inline-flex', alignItems: 'center', gap: 12, color, fontFamily: useContext(FontContext), fontSize: 26, fontWeight: 700, letterSpacing: 3, textTransform: 'uppercase'}}><span style={{width: 12, height: 12, borderRadius: '50%', background: color}} />{children}</div>;
// "*word*" in a headline is drawn in the scene's accent color.
const Headline = ({text, accent}) => String(text || '').split(/(\*[^*]+\*)/).map((part, i) => part.startsWith('*') && part.endsWith('*') ? <span key={i} style={{color: accent}}>{part.slice(1, -1)}</span> : part);

// Full-frame chapter card. Optional `from` / `to` icon lists turn it into an object handoff:
// the previous phase's objects slide in, converge, and become the next phase's objects.
// `kicker` is a short tag above the label (e.g. "NOW", "YOUR TURN").
const shade = (hex, amount) => {
  const n = parseInt(hex.slice(1), 16);
  const ch = (v) => Math.max(0, Math.min(255, Math.round(v * (1 - amount))));
  return `rgb(${ch(n >> 16)}, ${ch((n >> 8) & 255)}, ${ch(n & 255)})`;
};
export const FullFrameTransition = ({transition, displayFont, palette = {}, durationInFrames = 42}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const color = transition.color || '#6857F5';
  const enter = spring({frame, fps, config: {damping: 18, stiffness: 170}});
  const leave = interpolate(frame, [durationInFrames - 8, durationInFrames], [0, 1], clamp);
  const from = transition.from || [];
  const to = transition.to || [];
  const handoff = from.length && to.length;
  const merge = interpolate(frame, [8, 20], [0, 1], {...clamp, easing: (x) => x * x * (3 - 2 * x)});
  const words = String(transition.label || '').split(' ');
  const tile = (name, i, total, t, side) => {
    const spread = (i - (total - 1) / 2) * 150;
    const x = side === 'from' ? -230 + spread * (1 - merge) + merge * 140 : 230 + spread;
    const p = side === 'from' ? Math.min(1, enter * 1.4) * (1 - merge) : t;
    return <div key={`${side}-${name}-${i}`} style={{position: 'absolute', left: '50%', top: '50%', width: 130, height: 130, marginLeft: -65 + x, marginTop: -65, borderRadius: 32, background: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 18px 40px rgba(0,0,0,.22)', opacity: p, transform: `scale(${0.6 + 0.4 * p}) rotate(${(1 - p) * (side === 'from' ? -8 : 8)}deg)`}}><Icon name={name} size={78} color={objectColor(name, palette)} /></div>;
  };
  return <AbsoluteFill style={{clipPath: `circle(${(1 - leave) * 120}% at 50% 50%)`, background: `linear-gradient(160deg, ${color} 0%, ${shade(color, 0.32)} 100%)`, overflow: 'hidden'}}>
    <AbsoluteFill style={{backgroundImage: 'radial-gradient(rgba(255,255,255,.16) 2.5px, transparent 2.5px)', backgroundSize: '38px 38px', opacity: 0.8}} />
    <div style={{position: 'absolute', width: 820, height: 820, borderRadius: '50%', left: -260 + frame * 3, top: 180, background: 'rgba(255,255,255,.10)', filter: 'blur(30px)'}} />
    <div style={{position: 'absolute', width: 620, height: 620, borderRadius: '50%', right: -200 + frame * 2, bottom: 260, background: 'rgba(0,0,0,.12)', filter: 'blur(40px)'}} />
    <div style={{position: 'absolute', left: 0, right: 0, top: 620, height: 260}}>
      {handoff ? <>
        {from.map((name, i) => tile(name, i, from.length, 0, 'from'))}
        <div style={{position: 'absolute', left: '50%', top: '50%', marginLeft: -40, marginTop: -40, width: 80, height: 80, borderRadius: '50%', background: 'rgba(255,255,255,.22)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 48, fontWeight: 900, transform: `scale(${0.5 + merge})`}}>{transition.symbol || '→'}</div>
        {to.map((name, i) => tile(name, i, to.length, frame < 18 + i * 4 ? 0 : spring({frame: frame - 18 - i * 4, fps, config: {damping: 10, stiffness: 200}}), 'to'))}
      </> : <div style={{position: 'absolute', left: '50%', top: '50%', marginLeft: -75, marginTop: -75, width: 150, height: 150, borderRadius: 40, background: 'rgba(255,255,255,.22)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontSize: 84, fontWeight: 950, transform: `scale(${0.6 + enter * 0.4})`}}>{transition.symbol || '→'}</div>}
    </div>
    <div style={{position: 'absolute', left: 80, right: 80, top: 960, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 22, color: '#fff', textAlign: 'center'}}>
      {transition.kicker ? <div style={{padding: '10px 22px', borderRadius: 999, background: 'rgba(255,255,255,.2)', fontFamily: displayFont, fontSize: 28, fontWeight: 700, letterSpacing: 4, opacity: enter}}>{transition.kicker}</div> : null}
      <div style={{textWrap: 'balance', fontFamily: displayFont, fontSize: 66, fontWeight: 800, lineHeight: 1.1, letterSpacing: -1, maxWidth: 900}}>
        {words.map((word, i) => {
          const w = frame < 4 + i * 3 ? 0 : spring({frame: frame - 4 - i * 3, fps, config: {damping: 13, stiffness: 190}});
          return <span key={i} style={{display: 'inline-block', marginRight: '0.28em', opacity: w, transform: `translateY(${(1 - w) * 30}px)`}}>{word}</span>;
        })}
      </div>
    </div>
  </AbsoluteFill>;
};

export const BrandEnding = ({brand, palette, displayFont}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const glow = spring({frame, fps, config: {damping: 20, stiffness: 90}});
  const letters = brand.name.split('');
  const slogan = spring({frame: frame - letters.length * 2 - 6, fps, config: {damping: 16, stiffness: 140}});
  return <AbsoluteFill style={{background: palette.ink, display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden'}}>
    <div style={{position: 'absolute', width: 820, height: 820, borderRadius: '50%', background: `radial-gradient(circle, ${palette.cool}55 0%, ${palette.cool}00 70%)`, opacity: glow, transform: `scale(${.8 + glow * .25})`}} />
    <div style={{position: 'relative', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 34, color: '#fff', textAlign: 'center', padding: '0 72px'}}>
      <div style={{display: 'flex', fontFamily: 'Inter, Avenir Next, Arial, sans-serif', fontSize: 116, fontWeight: 950, letterSpacing: 4}}>
        {letters.map((letter, i) => {
          const p = spring({frame: frame - i * 2, fps, config: {damping: 9, stiffness: 180}});
          return <span key={i} style={{display: 'inline-block', whiteSpace: 'pre', opacity: p, transform: `translateY(${(1 - p) * 60}px) scale(${.7 + p * .3})`}}>{letter}</span>;
        })}
      </div>
      <div style={{fontFamily: 'Inter, Avenir Next, Arial, sans-serif', fontSize: 50, fontWeight: 800, opacity: slogan, transform: `translateY(${(1 - slogan) * 30}px)`}}>{brand.slogan}</div>
      {brand.line ? <div style={{fontFamily: displayFont, fontSize: 40, fontWeight: 700, opacity: slogan * .75}}>{brand.line}</div> : null}
    </div>
  </AbsoluteFill>;
};

const Scene = ({scene, palette, labels, sound}) => {
  const font = useContext(FontContext);
  const frame = useCurrentFrame();
  const local = frame;
  const pulse = interpolate(local, [0, 18, 45], [.96, 1.03, 1], clamp);
  const before = scene.before || [];
  const after = scene.after || [];
  const steps = scene.type === 'after-workflow' ? after : before;
  const beat = {palette, font, sound};
  const shot = scene.shot ? {shot: scene.shot, evidence: scene.shot.evidence, click: withFrames(scene.shot.click), reveal: withFrames(scene.shot.reveal), stamp: withFrames(scene.shot.stamp), callout: scene.shot.callout ? {...withFrames(scene.shot.callout), until: scene.shot.callout.until_sec === undefined ? undefined : at(scene.shot.callout.until_sec)} : undefined, focus: (scene.shot.focus || []).map(withFrames)} : null;
  const flow = scene.flow ? scene.flow.map(withFrames) : null;
  const stepAt = (i) => (scene.steps_at_sec ? at(scene.steps_at_sec[i]) : null);
  const showBox = Boolean(scene.visual);
  // An animated beat replaces the default text cards for this scene.
  const custom = Boolean(shot || flow || scene.scrub || scene.fix);
  const introAt = scene.new_feature ? at(scene.new_feature.at_sec) : null;
  const stackOpacity = introAt === null ? 1 : interpolate(local, [introAt - 6, introAt], [1, 0], clamp);
  return (
    <AbsoluteFill style={{padding: '112px 72px 360px', background: palette.paper, color: palette.ink, overflow: 'hidden'}}>
      <div style={{position: 'absolute', width: 650, height: 650, right: -350, top: -260, borderRadius: '50%', background: `${palette.cool}16`, transform: `scale(${pulse})`}} />
      <div style={{position: 'relative', zIndex: 2, height: '100%', display: 'flex', flexDirection: 'column'}}>
        <div><Badge color={scene.type === 'before-workflow' ? palette.warm : palette.cool}>{scene.label}</Badge></div>
        {scene.new_tag ? <div style={{marginTop: 22}}><NewTag at={0} {...beat}>{scene.new_tag}</NewTag></div> : null}
        <h1 style={{textWrap: 'balance', fontWeight: 800, fontFamily: font, fontSize: scene.type === 'pain-hook' ? 92 : 72, lineHeight: 1.08, margin: '38px 0 20px', letterSpacing: -2}}><Headline text={scene.headline} accent={['pain-hook', 'before-workflow', 'human-check'].includes(scene.type) ? palette.warm : palette.cool} /></h1>
        {/* The body sits centered between the headline and the caption zone. */}
        <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', position: 'relative', paddingBottom: 40}}>
        {shot ? <div style={{marginBottom: 38}}><ProductShot {...shot} {...beat} /></div> : null}
        {scene.asset ? <Img src={staticFile(scene.asset)} style={{width: '100%', height: 600, objectFit: 'cover', borderRadius: 34, boxShadow: '0 24px 70px rgba(31,35,48,.14)', marginBottom: 38}} /> : null}
        {scene.new_feature ? <div style={{position: 'absolute', left: 0, right: 0, top: '50%', transform: 'translateY(-55%)'}}><FeatureIntro at={introAt} feature={scene.new_feature} {...beat} /></div> : null}
        {scene.fix ? <div style={{marginTop: 10, marginBottom: 10}}><Correction fix={withFrames(scene.fix)} {...beat} /></div> : null}
        {flow ? <div style={{marginTop: 40, marginBottom: 30, opacity: scene.type === 'pain-hook' ? stackOpacity : 1}}><Flow items={flow} accent={['pain-hook', 'before-workflow'].includes(scene.type) ? palette.warm : palette.cool} {...beat} /></div> : null}
        {scene.type === 'pain-hook' && !custom ? <div style={{marginTop: 120, opacity: stackOpacity, transform: `rotate(${interpolate(local, [0, 45], [-3, 0], clamp)}deg)`}}>{before.map((step, i) => <div key={step} style={{padding: '28px 30px', marginBottom: 20, marginLeft: i * 34, borderRadius: 28, background: '#fff', borderLeft: `10px solid ${i === before.length - 1 ? palette.warm : palette.cool}`, boxShadow: '0 16px 45px rgba(31,35,48,.12)', fontFamily: font, fontSize: 44, fontWeight: 800}}>{step}</div>)}</div> : null}
        {['before-workflow', 'after-workflow'].includes(scene.type) && !custom ? steps.map((step, i) => <Card key={step} index={i} delay={stepAt(i)} accent={scene.type === 'after-workflow' ? palette.cool : palette.warm}>{step}</Card>) : null}
        {scene.type === 'ai-handoff' && !shot && showBox ? <div style={{marginTop: 120, textAlign: 'center', transform: `scale(${pulse})`}}><div style={{fontFamily: font, fontWeight: 900, fontSize: 56, padding: 42, background: palette.ink, color: '#fff', borderRadius: 36}}>{scene.visual}</div><div style={{height: 100, width: 10, background: palette.cool, margin: '0 auto'}} /><div style={{fontFamily: font, fontSize: 44, fontWeight: 850, color: palette.cool}}>{labels.handoff}</div></div> : null}
        {scene.type === 'before-after' && !custom ? <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24}}><div><Badge color={palette.warm}>{labels.before}</Badge>{before.map((x,i)=><Card key={x} index={i} accent={palette.warm}>{x}</Card>)}</div><div><Badge color={palette.cool}>{labels.after}</Badge>{after.map((x,i)=><Card key={x} index={i} accent={palette.cool}>{x}</Card>)}</div></div> : null}
        {scene.type === 'human-check' && showBox ? <div style={{padding: 46, border: `5px solid ${palette.warm}`, borderRadius: 36, background: '#fff'}}><div style={{fontFamily: font, fontSize: 34, fontWeight: 500, color: palette.muted}}>{labels.humanCheck}</div><div style={{textWrap: 'balance', fontFamily: font, fontSize: 56, lineHeight: 1.2, fontWeight: 700, marginTop: 18}}>{scene.visual}</div></div> : null}
        {scene.type === 'next-action' && showBox ? <div style={{padding: 48, background: palette.cool, color: '#fff', borderRadius: 40}}><div style={{fontFamily: font, fontSize: 30, fontWeight: 500, opacity: .85}}>{labels.nextAction}</div><div style={{textWrap: 'balance', fontFamily: font, fontSize: 58, lineHeight: 1.2, fontWeight: 700, marginTop: 18}}>{scene.visual}</div></div> : null}
        {scene.scrub ? <div style={{marginTop: 20}}><Scrub scrub={{...withFrames(scene.scrub), ask_at: scene.scrub.ask_at_sec === undefined ? undefined : at(scene.scrub.ask_at_sec)}} {...beat} /></div> : null}
        {scene.roles ? <div style={{marginTop: 30}}><RoleStrip at={at(scene.roles.at_sec)} you={scene.roles.you} ai={scene.roles.ai} youLabel={labels.you} {...beat} /></div> : null}
        {scene.checks ? <div style={{marginTop: 30}}><CheckCards at={at(scene.checks_at_sec)} checks={scene.checks} {...beat} /></div> : null}
        {scene.access ? <div style={{marginTop: 30}}><AccessChips at={at(scene.access.at_sec)} label={scene.access.label} plans={scene.access.plans} {...beat} /></div> : null}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// Every scene change gets a short nonverbal transition: the next scene enters over the
// previous one (which stays underneath for ENTER_FRAMES). Readable chapter transitions
// from story.transitions still play as full-frame cards on top.
const ENTER_FRAMES = 12;
const ENTER_CYCLE = ['slide', 'wipe', 'rise'];
const SceneEnter = ({type, children}) => {
  const frame = useCurrentFrame();
  const t = interpolate(frame, [0, ENTER_FRAMES], [0, 1], {...clamp, easing: (x) => 1 - (1 - x) ** 3});
  // isolation keeps each scene's layers together, so the next scene fully covers this one.
  const base = {isolation: 'isolate'};
  if (type === 'none' || t >= 1) return <AbsoluteFill style={base}>{children}</AbsoluteFill>;
  if (type === 'wipe') return <AbsoluteFill style={{...base, clipPath: `circle(${t * 120}% at 50% 60%)`}}>{children}</AbsoluteFill>;
  if (type === 'rise') return <AbsoluteFill style={{...base, transform: `translateY(${(1 - t) * 100}%)`, boxShadow: '0 -30px 60px rgba(23,25,35,.18)'}}>{children}</AbsoluteFill>;
  return <AbsoluteFill style={{...base, transform: `translateX(${(1 - t) * 100}%)`, boxShadow: '-30px 0 60px rgba(23,25,35,.18)'}}>{children}</AbsoluteFill>;
};

export const VerticalImpact = ({story}) => {
  const fps = 30;
  const locale = localeOf(story);
  const labels = {...LABELS[locale], ...(story.labels || {})};
  return (
    <FontContext.Provider value={FONTS[locale].body}>
    <AbsoluteFill style={{background: story.palette.paper}}>
      {story.scenes.map((scene, index) => {
        const start = Math.round(scene.start_sec * fps);
        const last = index === story.scenes.length - 1;
        // Stay on screen a little past the end so the next scene can enter over it.
        const duration = Math.round((scene.end_sec - scene.start_sec) * fps) + (last ? 0 : ENTER_FRAMES);
        const enter = index === 0 ? 'none' : scene.enter || ENTER_CYCLE[(index - 1) % ENTER_CYCLE.length];
        return <Sequence key={scene.id} from={start} durationInFrames={duration}><SceneEnter type={enter}><Scene scene={{...scene, before: story.before_steps, after: story.after_steps}} palette={story.palette} labels={labels} sound={Boolean(story.sfx)} /></SceneEnter></Sequence>;
      })}
      {story.progress !== false && story.scenes.length ? (() => {
        // Thin chapter bar at the top: one segment per scene, hidden on the brand card.
        const first = Math.round(story.scenes[0].start_sec * fps);
        const last = Math.round(story.scenes[story.scenes.length - 1].end_sec * fps);
        const durations = story.scenes.map((scene) => Math.max(1, Math.round((scene.end_sec - scene.start_sec) * fps)));
        return <Sequence from={first} durationInFrames={Math.max(1, last - first)}><ProgressBar durationsInFrames={durations} top={64} height={8} color={story.palette.cool} trackColor={`${story.palette.ink}22`} /></Sequence>;
      })() : null}
      {story.audio ? <Audio src={staticFile(story.audio)} /> : null}
      <TimedCaptions />
      {(story.transitions||[]).map((transition) => <Sequence key={`${transition.start_sec}-${transition.label}`} from={Math.round(transition.start_sec*fps)} durationInFrames={Math.round((transition.end_sec-transition.start_sec)*fps)}><FullFrameTransition transition={transition} palette={story.palette} displayFont={FONTS[locale].display} durationInFrames={Math.round((transition.end_sec-transition.start_sec)*fps)}/></Sequence>)}
      {story.brand ? <Sequence from={Math.round(story.brand.start_sec * fps)} durationInFrames={Math.round((story.brand.end_sec - story.brand.start_sec) * fps)}><BrandEnding brand={story.brand} palette={story.palette} displayFont={FONTS[locale].display} /></Sequence> : null}
    </AbsoluteFill>
    </FontContext.Provider>
  );
};
