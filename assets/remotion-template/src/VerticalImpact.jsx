import React, {createContext, useContext} from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {TimedCaptions} from './TimedCaptions';
import {ProgressBar} from './components/ProgressBar';
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
  return <div style={{padding: '26px 28px', marginBottom: 20, borderRadius: 28, background: '#fff', borderLeft: `10px solid ${accent}`, boxShadow: '0 16px 45px rgba(31,35,48,.10)', textWrap: 'balance', fontFamily: font, fontSize: 42, fontWeight: 750, color: '#161820', opacity: p, transform: `translateY(${(1-p)*55}px) scale(${.96 + p*.04})`}}>{children}</div>;
};

const Badge = ({children, color}) => <div style={{display: 'inline-block', padding: '12px 20px', borderRadius: 999, color: '#fff', background: color, fontFamily: useContext(FontContext), fontSize: 28, fontWeight: 850, letterSpacing: 1}}>{children}</div>;

export const FullFrameTransition = ({transition, displayFont}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame,fps,config:{damping:18,stiffness:170}});
  return <AbsoluteFill style={{background:transition.color||'#6857F5',display:'flex',alignItems:'center',justifyContent:'center',overflow:'hidden'}}><div style={{position:'absolute',width:760,height:760,borderRadius:'50%',background:'rgba(255,255,255,.08)',transform:`scale(${.72+enter*.35})`}}/><div style={{position:'relative',display:'flex',flexDirection:'column',alignItems:'center',gap:30,color:'#fff',opacity:enter,transform:`translateY(${(1-enter)*55}px) scale(${.72+enter*.32})`}}><div style={{width:118,height:118,borderRadius:34,background:'rgba(255,255,255,.20)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:66,fontWeight:950}}>{transition.symbol||'→'}</div><div style={{textWrap:'balance',fontFamily:displayFont,fontSize:48,fontWeight:950,textAlign:'center',maxWidth:900}}>{transition.label}</div></div></AbsoluteFill>;
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
  const shot = scene.shot ? {shot: scene.shot, evidence: scene.shot.evidence, click: withFrames(scene.shot.click), reveal: withFrames(scene.shot.reveal), stamp: withFrames(scene.shot.stamp), callout: withFrames(scene.shot.callout), focus: (scene.shot.focus || []).map(withFrames)} : null;
  const flow = scene.flow ? scene.flow.map(withFrames) : null;
  const stepAt = (i) => (scene.steps_at_sec ? at(scene.steps_at_sec[i]) : null);
  const showBox = Boolean(scene.visual);
  const introAt = scene.new_feature ? at(scene.new_feature.at_sec) : null;
  const stackOpacity = introAt === null ? 1 : interpolate(local, [introAt - 6, introAt], [1, 0], clamp);
  return (
    <AbsoluteFill style={{padding: '112px 72px 360px', background: palette.paper, color: palette.ink, overflow: 'hidden'}}>
      <div style={{position: 'absolute', width: 650, height: 650, right: -350, top: -260, borderRadius: '50%', background: `${palette.cool}16`, transform: `scale(${pulse})`}} />
      <div style={{position: 'relative', zIndex: 2, height: '100%', display: 'flex', flexDirection: 'column'}}>
        <div><Badge color={scene.type === 'before-workflow' ? palette.warm : palette.cool}>{scene.label}</Badge></div>
        {scene.new_tag ? <div style={{marginTop: 22}}><NewTag at={0} {...beat}>{scene.new_tag}</NewTag></div> : null}
        <h1 style={{textWrap: 'balance', fontFamily: font, fontSize: scene.type === 'pain-hook' ? 92 : 72, lineHeight: 1.08, margin: '38px 0 20px', letterSpacing: -3}}>{scene.headline}</h1>
        {/* The body sits centered between the headline and the caption zone. */}
        <div style={{flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', position: 'relative', paddingBottom: 40}}>
        {shot ? <div style={{marginBottom: 38}}><ProductShot {...shot} {...beat} /></div> : null}
        {scene.asset ? <Img src={staticFile(scene.asset)} style={{width: '100%', height: 600, objectFit: 'cover', borderRadius: 34, boxShadow: '0 24px 70px rgba(31,35,48,.14)', marginBottom: 38}} /> : null}
        {scene.new_feature ? <div style={{position: 'absolute', left: 0, right: 0, top: '50%', transform: 'translateY(-55%)'}}><FeatureIntro at={introAt} feature={scene.new_feature} {...beat} /></div> : null}
        {flow ? <div style={{marginTop: 40, marginBottom: 30, opacity: scene.type === 'pain-hook' ? stackOpacity : 1}}><Flow items={flow} accent={['pain-hook', 'before-workflow'].includes(scene.type) ? palette.warm : palette.cool} {...beat} /></div> : null}
        {scene.type === 'pain-hook' && !flow ? <div style={{marginTop: 120, opacity: stackOpacity, transform: `rotate(${interpolate(local, [0, 45], [-3, 0], clamp)}deg)`}}>{before.map((step, i) => <div key={step} style={{padding: '28px 30px', marginBottom: 20, marginLeft: i * 34, borderRadius: 28, background: '#fff', borderLeft: `10px solid ${i === before.length - 1 ? palette.warm : palette.cool}`, boxShadow: '0 16px 45px rgba(31,35,48,.12)', fontFamily: font, fontSize: 44, fontWeight: 800}}>{step}</div>)}</div> : null}
        {['before-workflow', 'after-workflow'].includes(scene.type) && !shot && !flow ? steps.map((step, i) => <Card key={step} index={i} delay={stepAt(i)} accent={scene.type === 'after-workflow' ? palette.cool : palette.warm}>{step}</Card>) : null}
        {scene.type === 'ai-handoff' && !shot && showBox ? <div style={{marginTop: 120, textAlign: 'center', transform: `scale(${pulse})`}}><div style={{fontFamily: font, fontWeight: 900, fontSize: 56, padding: 42, background: palette.ink, color: '#fff', borderRadius: 36}}>{scene.visual}</div><div style={{height: 100, width: 10, background: palette.cool, margin: '0 auto'}} /><div style={{fontFamily: font, fontSize: 44, fontWeight: 850, color: palette.cool}}>{labels.handoff}</div></div> : null}
        {scene.type === 'before-after' && !flow ? <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24}}><div><Badge color={palette.warm}>{labels.before}</Badge>{before.map((x,i)=><Card key={x} index={i} accent={palette.warm}>{x}</Card>)}</div><div><Badge color={palette.cool}>{labels.after}</Badge>{after.map((x,i)=><Card key={x} index={i} accent={palette.cool}>{x}</Card>)}</div></div> : null}
        {scene.type === 'human-check' && showBox ? <div style={{padding: 46, border: `5px solid ${palette.warm}`, borderRadius: 36, background: '#fff'}}><div style={{fontFamily: font, fontSize: 40, color: palette.muted}}>{labels.humanCheck}</div><div style={{textWrap: 'balance', fontFamily: font, fontSize: 60, lineHeight: 1.2, fontWeight: 900, marginTop: 18}}>{scene.visual}</div></div> : null}
        {scene.type === 'next-action' && showBox ? <div style={{padding: 48, background: palette.cool, color: '#fff', borderRadius: 40}}><div style={{fontFamily: font, fontSize: 34, opacity: .8}}>{labels.nextAction}</div><div style={{textWrap: 'balance', fontFamily: font, fontSize: 62, lineHeight: 1.2, fontWeight: 900, marginTop: 18}}>{scene.visual}</div></div> : null}
        {scene.scrub ? <div style={{marginTop: 20}}><Scrub scrub={{...withFrames(scene.scrub), ask_at: scene.scrub.ask_at_sec === undefined ? undefined : at(scene.scrub.ask_at_sec)}} {...beat} /></div> : null}
        {scene.fix ? <div style={{marginTop: 30}}><Correction fix={withFrames(scene.fix)} {...beat} /></div> : null}
        {scene.roles ? <div style={{marginTop: 30}}><RoleStrip at={at(scene.roles.at_sec)} you={scene.roles.you} ai={scene.roles.ai} youLabel={labels.you} {...beat} /></div> : null}
        {scene.checks ? <div style={{marginTop: 30}}><CheckCards at={at(scene.checks_at_sec)} checks={scene.checks} {...beat} /></div> : null}
        {scene.access ? <div style={{marginTop: 30}}><AccessChips at={at(scene.access.at_sec)} label={scene.access.label} plans={scene.access.plans} {...beat} /></div> : null}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const VerticalImpact = ({story}) => {
  const fps = 30;
  const locale = localeOf(story);
  const labels = {...LABELS[locale], ...(story.labels || {})};
  return (
    <FontContext.Provider value={FONTS[locale].body}>
    <AbsoluteFill>
      {story.scenes.map((scene) => {
        const start = Math.round(scene.start_sec * fps);
        const duration = Math.round((scene.end_sec - scene.start_sec) * fps);
        return <Sequence key={scene.id} from={start} durationInFrames={duration}><Scene scene={{...scene, before: story.before_steps, after: story.after_steps}} palette={story.palette} labels={labels} sound={Boolean(story.sfx)} /></Sequence>;
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
      {(story.transitions||[]).map((transition) => <Sequence key={`${transition.start_sec}-${transition.label}`} from={Math.round(transition.start_sec*fps)} durationInFrames={Math.round((transition.end_sec-transition.start_sec)*fps)}><FullFrameTransition transition={transition} displayFont={FONTS[locale].display}/></Sequence>)}
      {story.brand ? <Sequence from={Math.round(story.brand.start_sec * fps)} durationInFrames={Math.round((story.brand.end_sec - story.brand.start_sec) * fps)}><BrandEnding brand={story.brand} palette={story.palette} displayFont={FONTS[locale].display} /></Sequence> : null}
    </AbsoluteFill>
    </FontContext.Provider>
  );
};
