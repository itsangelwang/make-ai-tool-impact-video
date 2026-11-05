// Checks that every scene's body fits above the captions without shrinking too much.
// Usage: npm run layout -- [--min-fit 0.85]
// Renders the first frame of each scene and reads the scale the template applied
// (VerticalImpact logs it). Exits 1 when a scene is shrunk below --min-fit: trim or split it.
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';
import {readFileSync, mkdtempSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import path from 'node:path';

const arg = process.argv.indexOf('--min-fit');
const minFit = arg > -1 ? Number(process.argv[arg + 1]) : 0.85; // same as body_fit_min in the Skill's scripts/limits.json
const story = JSON.parse(readFileSync('src/story.json', 'utf8'));
const serveUrl = await bundle({entryPoint: path.resolve('src/index.jsx')});
const composition = await selectComposition({serveUrl, id: 'VerticalImpact'});
const out = mkdtempSync(path.join(tmpdir(), 'layout-'));
const results = {};
for (const scene of story.scenes) {
  const frame = Math.round(scene.start_sec * 30);
  await renderStill({
    serveUrl, composition, frame, output: path.join(out, `${scene.id}.png`),
    onBrowserLog: ({text}) => {
      const match = /^\[layout\] (.*)$/.exec(text);
      if (match) { const {scene: id, fit} = JSON.parse(match[1]); results[id] = fit; }
    },
  });
}
rmSync(out, {recursive: true, force: true});
let failed = false;
for (const scene of story.scenes) {
  const fit = results[scene.id];
  const bad = fit === undefined || fit < minFit;
  failed ||= bad;
  console.log(`${scene.id}: ${fit === undefined ? 'no layout report' : `body at ${Math.round(fit * 100)}%`}${bad ? ` — below ${Math.round(minFit * 100)}%: trim or split this scene` : ''}`);
}
process.exit(failed ? 1 : 0);
