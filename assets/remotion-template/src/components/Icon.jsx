import React from 'react';

const PATHS = {
  paste: <><rect x="16" y="10" width="32" height="44" rx="5" /><rect x="24" y="6" width="16" height="9" rx="3" /><path d="M24 28h16M24 37h16M24 46h10" /></>,
  table: <><rect x="8" y="12" width="48" height="40" rx="5" /><path d="M8 24h48M8 38h48M26 12v40M42 12v40" /></>,
  chart: <><path d="M10 54h44" /><rect x="14" y="30" width="9" height="24" rx="2" /><rect x="28" y="20" width="9" height="34" rx="2" /><rect x="42" y="36" width="9" height="18" rx="2" /></>,
  truck: <><rect x="6" y="20" width="32" height="22" rx="3" /><path d="M38 28h10l8 8v6H38z" /><circle cx="18" cy="46" r="5" /><circle cx="46" cy="46" r="5" /></>,
  percent: <><path d="M14 50L50 14" /><circle cx="18" cy="18" r="7" /><circle cx="46" cy="46" r="7" /></>,
  lock: <><rect x="12" y="28" width="40" height="28" rx="5" /><path d="M20 28v-8a12 12 0 0 1 24 0v8" /></>,
  doc: <><path d="M16 6h22l12 12v40H16z" /><path d="M38 6v12h12M22 30h22M22 39h22M22 48h14" /></>,
  sliders: <><path d="M10 18h44M10 32h44M10 46h44" /><circle cx="22" cy="18" r="6" fill="#fff" /><circle cx="42" cy="32" r="6" fill="#fff" /><circle cx="30" cy="46" r="6" fill="#fff" /></>,
  calendar: <><rect x="8" y="12" width="48" height="44" rx="5" /><path d="M8 26h48M20 6v12M44 6v12M18 36h8M30 36h8M18 46h8" /></>,
  search: <><circle cx="27" cy="27" r="16" /><path d="M39 39l15 15" /></>,
  user: <><circle cx="32" cy="22" r="11" /><path d="M12 56c2-12 10-18 20-18s18 6 20 18" /></>,
  slides: <><rect x="6" y="10" width="52" height="34" rx="4" /><path d="M32 44v10M22 56h20M16 22h20M16 31h14" /></>,
  mic: <><rect x="24" y="6" width="16" height="30" rx="8" /><path d="M14 30a18 18 0 0 0 36 0M32 48v8M24 56h16" /></>,
  play: <><circle cx="32" cy="32" r="24" /><path d="M27 22l14 10-14 10z" /></>,
  pause: <><circle cx="32" cy="32" r="24" /><path d="M27 22v20M37 22v20" /></>,
  keyboard: <><rect x="6" y="16" width="52" height="32" rx="5" /><path d="M14 26h4M24 26h4M34 26h4M44 26h6M14 35h4M24 35h4M34 35h4M44 35h6M20 42h24" /></>,
  mail: <><rect x="6" y="14" width="52" height="36" rx="5" /><path d="M8 18l24 18 24-18" /></>,
};

/** Line icons for task objects. name: one of ICON_NAMES; size in px; color: stroke. */
export const ICON_NAMES = Object.keys(PATHS);

// Each kind of object keeps one color for the whole video, so tiles in a row are easy to tell
// apart and the same object is recognizable when it reappears. Override per story with
// palette.objects ({icon: color}) or per item with `color`.
const OBJECT_HUES = {violet: '#6857F5', teal: '#0E9F8E', amber: '#D98A00', pink: '#D9467A', blue: '#2F7DE1', green: '#3D9A40'};
const OBJECT_COLORS = {
  table: 'violet', chart: 'violet', slides: 'violet',
  mic: 'teal', play: 'teal', pause: 'teal', keyboard: 'teal',
  mail: 'amber', paste: 'amber',
  calendar: 'pink', percent: 'pink',
  user: 'blue', search: 'blue',
  doc: 'green', truck: 'green', lock: 'green', sliders: 'green',
};
export const objectColor = (name, palette = {}, override) => override || palette.objects?.[name] || OBJECT_HUES[OBJECT_COLORS[name]] || palette.cool || OBJECT_HUES.violet;
export const Icon = ({name, size = 64, color = '#171923'}) => {
  if (!PATHS[name]) throw new Error(`Unknown icon: ${name}`);
  return <svg width={size} height={size} viewBox="0 0 64 64" fill="none" stroke={color} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">{PATHS[name]}</svg>;
};
