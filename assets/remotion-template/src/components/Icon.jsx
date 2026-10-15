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
  mail: <><rect x="6" y="14" width="52" height="36" rx="5" /><path d="M8 18l24 18 24-18" /></>,
};

/** Line icons for task objects. name: one of ICON_NAMES; size in px; color: stroke. */
export const ICON_NAMES = Object.keys(PATHS);
export const Icon = ({name, size = 64, color = '#171923'}) => {
  if (!PATHS[name]) throw new Error(`Unknown icon: ${name}`);
  return <svg width={size} height={size} viewBox="0 0 64 64" fill="none" stroke={color} strokeWidth="4" strokeLinecap="round" strokeLinejoin="round">{PATHS[name]}</svg>;
};
