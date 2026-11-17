import * as React from 'react';
import { PixelButton } from '../components/PixelButton';
import { COMPANIONS } from '../data/content';
export const AvatarSelectScreen = ({
  next,
  onSelect
}) => {
  let [n, r] = (0, React.useState)(null);
  return <div className="game-screen scanlines" style={{
    background: `linear-gradient(to bottom, #2a1050, #3d1f6e)`,
    display: `flex`,
    flexDirection: `column`,
    alignItems: `center`,
    paddingTop: 80,
    overflow: `hidden`
  }}><h1 className="font-pixel text-center mb-2" style={{
      fontSize: `clamp(0.9rem,3vw,1.4rem)`,
      color: `#ffe94a`,
      textShadow: `3px 3px 0 #000`
    }}>⚔ CHOOSE YOUR AVATAR ⚔</h1><p className="font-pixel text-xs mb-8 text-center" style={{
      color: `#00ffee`,
      textShadow: `1px 1px 0 #000`
    }}>SELECT YOUR STUDY COMPANION</p><div className="flex flex-wrap justify-center gap-4 max-w-2xl px-4 mb-8">{COMPANIONS.map(e => <button onClick={() => r(e.id)} className="pixel-btn flex flex-col items-center gap-2 p-4 border-4 border-black w-36" style={{
        background: n === e.id ? e.color : `#3d1f6e`,
        boxShadow: n === e.id ? `0 0 0 #000` : `5px 5px 0 #000`,
        transform: n === e.id ? `translate(5px,5px) scale(1.05)` : `translate(0,0)`
      }} key={e.id}><span className="text-5xl" style={{
          animation: `float 3s ease-in-out infinite`
        }}>{e.emoji}</span><span className="font-pixel text-xs text-white">{e.name}</span><span className="font-body text-xs text-white" style={{
          opacity: .8
        }}>{e.desc}</span>{n === e.id && <span className="font-pixel text-xs" style={{
          color: `#1a0a2e`,
          animation: `blink 1s step-end infinite`
        }}>✓ CHOSEN</span>}</button>)}</div><PixelButton onClick={() => {
      n && (onSelect(n), next());
    }} color={n ? `#4aff91` : `#555`} textColor="#000" size="lg">{n ? `▶ CONFIRM!` : `SELECT ONE...`}</PixelButton></div>;
};
