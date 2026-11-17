import * as React from 'react';
import { PixelButton } from '../components/PixelButton';
export const SignInScreen = ({
  next,
  back,
  onSetName
}) => {
  let [r, i] = (0, React.useState)(``),
    a = () => {
      r.trim() && (onSetName(r.trim()), next());
    };
  return <div className="game-screen scanlines" style={{
    background: `linear-gradient(to bottom, #2a1050, #5b3a8e)`,
    display: `flex`,
    alignItems: `center`,
    justifyContent: `center`,
    position: `relative`
  }}><div className="relative z-10 flex flex-col items-center gap-6 w-full max-w-md px-4"><h1 className="font-pixel text-center" style={{
        fontSize: `clamp(0.9rem,3vw,1.4rem)`,
        color: `#ffe94a`,
        textShadow: `3px 3px 0 #000`,
        lineHeight: 1.8
      }}>ARE YOU<br />READY?</h1><div className="w-full bg-white border-4 border-black p-6" style={{
        boxShadow: `6px 6px 0 #000`
      }}><p className="font-pixel text-xs text-gray-800 mb-6" style={{
          lineHeight: 2
        }}>PLAYER 1 — ENTER YOUR NAME:</p><input className="w-full border-4 border-black bg-white text-gray-900 font-body px-3 py-2 mb-6 text-base outline-none" style={{
          borderColor: `#000`
        }} placeholder="HERO NAME..." maxLength={20} value={r} onChange={e => i(e.target.value)} onKeyDown={e => e.key === `Enter` && a()} onFocus={e => e.target.style.borderColor = `#ff00cc`} onBlur={e => e.target.style.borderColor = `#000`} /><div className="flex gap-4 justify-center"><PixelButton onClick={a} color="#4aff91" textColor="#000" size="md">✔ YES!</PixelButton><PixelButton onClick={back} color="#ff3355" size="md">✘ NO</PixelButton></div></div><div className="flex gap-2 items-center font-pixel text-xs" style={{
        color: `#ff3355`
      }}><span>LIVES:</span>{[`❤️`, `❤️`, `❤️`].map((e, t) => <span className="text-lg" key={t}>{e}</span>)}</div></div></div>;
};
