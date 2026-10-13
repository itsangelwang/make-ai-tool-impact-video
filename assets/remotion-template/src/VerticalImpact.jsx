import React, {createContext, useContext} from 'react';
import {AbsoluteFill, Audio, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {TimedCaptions} from './TimedCaptions';

const FONTS = {
  zh: {body: 'PingFang SC, Noto Sans CJK SC, Arial, sans-serif', display: 'Hannotate SC, Kaiti SC, PingFang SC, sans-serif'},
  en: {body: 'Inter, Avenir Next, SF Pro Display, Arial, sans-serif', display: 'Inter, Avenir Next, SF Pro Display, Arial, sans-serif'},
};
const LABELS = {
  zh: {handoff: '交给 AI 处理这一步', humanCheck: '最后一步仍由人负责', nextAction: '今天可以这样试', before: '使用前', after: '使用后'},
  en: {handoff: 'AI takes this step', humanCheck: 'You still own the final check', nextAction: 'Try this today', before: 'Before', after: 'After'},
};
const localeOf = (story) => (String(story.language || 'en-US').startsWith('en') ? 'en' : 'zh');
const FontContext = createContext(FONTS.zh.body);
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'};

const Card = ({children, index = 0, accent = '#6857F5'}) => {
  const font = useContext(FontContext);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const p = spring({frame: frame - index * 6, fps, config: {damping: 18, stiffness: 150}});
  return <div style={{padding: '26px 28px', marginBottom: 20, borderRadius: 28, background: '#fff', borderLeft: `10px solid ${accent}`, boxShadow: '0 16px 45px rgba(31,35,48,.10)', fontFamily: font, fontSize: 42, fontWeight: 750, color: '#161820', opacity: p, transform: `translateY(${(1-p)*55}px) scale(${.96 + p*.04})`}}>{children}</div>;
};

const Badge = ({children, color}) => <div style={{display: 'inline-block', padding: '12px 20px', borderRadius: 999, color: '#fff', background: color, fontFamily: useContext(FontContext), fontSize: 28, fontWeight: 850, letterSpacing: 1}}>{children}</div>;

const FullFrameTransition = ({transition, displayFont}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const enter = spring({frame,fps,config:{damping:18,stiffness:170}});
  return <AbsoluteFill style={{background:transition.color||'#6857F5',display:'flex',alignItems:'center',justifyContent:'center',overflow:'hidden'}}><div style={{position:'absolute',width:760,height:760,borderRadius:'50%',background:'rgba(255,255,255,.08)',transform:`scale(${.72+enter*.35})`}}/><div style={{position:'relative',display:'flex',flexDirection:'column',alignItems:'center',gap:30,color:'#fff',opacity:enter,transform:`translateY(${(1-enter)*55}px) scale(${.72+enter*.32})`}}><div style={{width:118,height:118,borderRadius:34,background:'rgba(255,255,255,.20)',display:'flex',alignItems:'center',justifyContent:'center',fontSize:66,fontWeight:950}}>{transition.symbol||'→'}</div><div style={{fontFamily:displayFont,fontSize:48,fontWeight:950,textAlign:'center',maxWidth:900}}>{transition.label}</div></div></AbsoluteFill>;
};

const BrandEnding = ({brand, palette, displayFont}) => {
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

const Scene = ({scene, palette, labels}) => {
  const font = useContext(FontContext);
  const frame = useCurrentFrame();
  const local = frame;
  const pulse = interpolate(local, [0, 18, 45], [.96, 1.03, 1], clamp);
  const before = scene.before || [];
  const after = scene.after || [];
  const steps = scene.type === 'after-workflow' ? after : before;
  return (
    <AbsoluteFill style={{padding: '112px 72px 360px', background: palette.paper, color: palette.ink, overflow: 'hidden'}}>
      <div style={{position: 'absolute', width: 650, height: 650, right: -350, top: -260, borderRadius: '50%', background: `${palette.cool}16`, transform: `scale(${pulse})`}} />
      <div style={{position: 'relative', zIndex: 2}}>
        <Badge color={scene.type === 'before-workflow' ? palette.warm : palette.cool}>{scene.label}</Badge>
        <h1 style={{fontFamily: font, fontSize: scene.type === 'pain-hook' ? 92 : 72, lineHeight: 1.08, margin: '38px 0 52px', letterSpacing: -3}}>{scene.headline}</h1>
        {scene.asset ? <Img src={staticFile(scene.asset)} style={{width: '100%', height: 600, objectFit: 'cover', borderRadius: 34, boxShadow: '0 24px 70px rgba(31,35,48,.14)', marginBottom: 38}} /> : null}
        {scene.type === 'pain-hook' ? <div style={{marginTop: 120, transform: `rotate(${interpolate(local, [0, 45], [-3, 0], clamp)}deg)`}}>{before.map((step, i) => <div key={step} style={{padding: '28px 30px', marginBottom: 20, marginLeft: i * 34, borderRadius: 28, background: '#fff', borderLeft: `10px solid ${i === before.length - 1 ? palette.warm : palette.cool}`, boxShadow: '0 16px 45px rgba(31,35,48,.12)', fontFamily: font, fontSize: 44, fontWeight: 800}}>{step}</div>)}</div> : null}
        {['before-workflow', 'after-workflow'].includes(scene.type) ? steps.map((step, i) => <Card key={step} index={i} accent={scene.type === 'after-workflow' ? palette.cool : palette.warm}>{step}</Card>) : null}
        {scene.type === 'ai-handoff' ? <div style={{marginTop: 120, textAlign: 'center', transform: `scale(${pulse})`}}><div style={{fontFamily: font, fontWeight: 900, fontSize: 56, padding: 42, background: palette.ink, color: '#fff', borderRadius: 36}}>{scene.visual}</div><div style={{height: 100, width: 10, background: palette.cool, margin: '0 auto'}} /><div style={{fontFamily: font, fontSize: 44, fontWeight: 850, color: palette.cool}}>{labels.handoff}</div></div> : null}
        {scene.type === 'before-after' ? <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24}}><div><Badge color={palette.warm}>{labels.before}</Badge>{before.map((x,i)=><Card key={x} index={i} accent={palette.warm}>{x}</Card>)}</div><div><Badge color={palette.cool}>{labels.after}</Badge>{after.map((x,i)=><Card key={x} index={i} accent={palette.cool}>{x}</Card>)}</div></div> : null}
        {scene.type === 'human-check' ? <div style={{padding: 46, border: `5px solid ${palette.warm}`, borderRadius: 36, background: '#fff'}}><div style={{fontFamily: font, fontSize: 40, color: palette.muted}}>{labels.humanCheck}</div><div style={{fontFamily: font, fontSize: 60, lineHeight: 1.2, fontWeight: 900, marginTop: 18}}>{scene.visual}</div></div> : null}
        {scene.type === 'next-action' ? <div style={{padding: 48, background: palette.cool, color: '#fff', borderRadius: 40}}><div style={{fontFamily: font, fontSize: 34, opacity: .8}}>{labels.nextAction}</div><div style={{fontFamily: font, fontSize: 62, lineHeight: 1.2, fontWeight: 900, marginTop: 18}}>{scene.visual}</div></div> : null}
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
        return <Sequence key={scene.id} from={start} durationInFrames={duration}><Scene scene={{...scene, before: story.before_steps, after: story.after_steps}} palette={story.palette} labels={labels} /></Sequence>;
      })}
      {story.audio ? <Audio src={staticFile(story.audio)} /> : null}
      <TimedCaptions />
      {(story.transitions||[]).map((transition) => <Sequence key={`${transition.start_sec}-${transition.label}`} from={Math.round(transition.start_sec*fps)} durationInFrames={Math.round((transition.end_sec-transition.start_sec)*fps)}><FullFrameTransition transition={transition} displayFont={FONTS[locale].display}/></Sequence>)}
      {story.brand ? <Sequence from={Math.round(story.brand.start_sec * fps)} durationInFrames={Math.round((story.brand.end_sec - story.brand.start_sec) * fps)}><BrandEnding brand={story.brand} palette={story.palette} displayFont={FONTS[locale].display} /></Sequence> : null}
    </AbsoluteFill>
    </FontContext.Provider>
  );
};
