// The player's HUD (level, XP, coins, hearts, streak) shared by every screen.
// Real mode: filled from the server after sign-in and after every answer.
// Mock mode (?mock=1): the fixed values the UI reference shows.
import * as React from 'react';
import { isMock } from './mode';

const REFERENCE_HUD = { level: 3, xp: 270, xp_pct: 70, coins: 82, streak: 7, hearts: 3, max_hearts: 3, badges: [] };
let hud = isMock ? REFERENCE_HUD : { level: 1, xp: 0, xp_pct: 0, coins: 0, streak: 0, hearts: 3, max_hearts: 3, badges: [] };
const listeners = new Set();

export function setHud(next) {
  if (!next) return;
  hud = { ...hud, ...next };
  listeners.forEach((l) => l());
}

export function useHud() {
  return React.useSyncExternalStore((l) => (listeners.add(l), () => listeners.delete(l)), () => hud);
}
