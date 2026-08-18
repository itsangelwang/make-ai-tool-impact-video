#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const out = process.argv[2];
if (!out) throw new Error('Usage: node generate_ui_sfx.mjs <output-dir>');
fs.mkdirSync(out, {recursive: true});
const sr = 48000;

const wav = (name, seconds, sample) => {
  const count = Math.ceil(seconds * sr);
  const pcm = Buffer.alloc(count * 2);
  for (let i = 0; i < count; i++) {
    const value = Math.max(-1, Math.min(1, sample(i / sr, i, count)));
    pcm.writeInt16LE(Math.round(value * 32767), i * 2);
  }
  const header = Buffer.alloc(44);
  header.write('RIFF', 0); header.writeUInt32LE(36 + pcm.length, 4);
  header.write('WAVEfmt ', 8); header.writeUInt32LE(16, 16);
  header.writeUInt16LE(1, 20); header.writeUInt16LE(1, 22);
  header.writeUInt32LE(sr, 24); header.writeUInt32LE(sr * 2, 28);
  header.writeUInt16LE(2, 32); header.writeUInt16LE(16, 34);
  header.write('data', 36); header.writeUInt32LE(pcm.length, 40);
  fs.writeFileSync(path.join(out, name), Buffer.concat([header, pcm]));
};

let seed = 9137;
const noise = () => { seed = (seed * 16807) % 2147483647; return seed / 1073741823.5 - 1; };
const fade = (t, duration, attack=.01, release=.05) => Math.min(1, t/attack, (duration-t)/release);

wav('ui-click.wav', .07, t => .16 * Math.sin(2*Math.PI*980*t) * fade(t,.07,.004,.055));
wav('key-tap.wav', .045, t => .07 * noise() * fade(t,.045,.002,.035));
wav('upload-rise.wav', .48, t => .065 * Math.sin(2*Math.PI*(420*t+1100*t*t)) * fade(t,.48,.04,.14));
wav('ui-success.wav', .38, t => (.08*Math.sin(2*Math.PI*880*t)*fade(t,.22,.01,.12)) + (t>.11?.075*Math.sin(2*Math.PI*1320*(t-.11))*fade(t-.11,.27,.01,.14):0));
wav('ui-whoosh.wav', .42, t => .045 * noise() * Math.sin(Math.PI*Math.min(1,t/.42)));

console.log(JSON.stringify({ok:true, output:path.resolve(out)}));
