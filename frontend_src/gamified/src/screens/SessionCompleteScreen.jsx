import { PixelButton } from '../components/PixelButton';
import { WizardSprite } from '../components/Sprites';
import { getLastSummary, isMock } from '../api/client';

const REFERENCE_ROWS = [[`QUESTIONS`, `10 / 10`], [`CORRECT`, `8`], [`XP EARNED`, `+340`], [`COINS`, `+25 🪙`], [`TIME`, `14:32`]];
function summaryRows() {
  if (isMock) return REFERENCE_ROWS;
  const s = getLastSummary();
  if (!s) return [[`QUESTIONS`, `0`], [`CORRECT`, `0`], [`XP EARNED`, `+0`], [`COINS`, `+0 🪙`], [`TIME`, `0:00`]];
  const mins = Math.floor(s.duration_s / 60), secs = String(s.duration_s % 60).padStart(2, `0`);
  return [[`QUESTIONS`, `${s.questions} / ${s.questions}`], [`CORRECT`, `${s.correct}`], [`XP EARNED`, `+${s.xp_earned}`], [`COINS`, `+${s.coins_earned} 🪙`], [`TIME`, `${mins}:${secs}`]];
}

export const SessionCompleteScreen = ({
  next
}) => <div className="game-screen scanlines starfield" style={{
  background: `#1a0a2e`,
  display: `flex`,
  flexDirection: `column`,
  alignItems: `center`,
  justifyContent: `center`,
  position: `relative`,
  overflow: `hidden`
}}>{Array.from({
    length: 50
  }).map((e, t) => <div className="absolute rounded-full" style={{
    width: 2,
    height: 2,
    background: t % 3 == 0 ? `#00ffee` : `#fff`,
    top: `${t * 41 % 100}%`,
    left: `${t * 67 % 100}%`,
    animation: `startwink 1.5s ${t * .1 % 3}s ease-in-out infinite`
  }} key={t} />)}<div className="relative z-10 text-center flex flex-col items-center gap-6"><p className="font-pixel text-xs" style={{
      color: `#00ffee`,
      animation: `blink 1s step-end infinite`,
      textShadow: `2px 2px 0 #000`
    }}>*** GAME SAVED ***</p><h1 className="font-pixel" style={{
      fontSize: `clamp(1rem,4vw,2rem)`,
      color: `#ffe94a`,
      textShadow: `4px 4px 0 #000`,
      animation: `glitch 0.3s ease-in-out infinite`,
      lineHeight: 1.6
    }}>SESSION<br />COMPLETE!</h1><div className="border-4 border-black p-6 flex flex-col gap-3 w-72" style={{
      background: `#3d1f6e`,
      boxShadow: `6px 6px 0 #000`,
      borderColor: `#ffe94a`
    }}>{summaryRows().map(([e, t]) => <div className="flex justify-between font-pixel text-xs" key={e}><span style={{
          color: `#00ffee`
        }}>{e}</span><span style={{
          color: `#ffe94a`
        }}>{t}</span></div>)}</div><WizardSprite mood="celebrate" size={1.4} className="animate-float" /><PixelButton onClick={next} color="#ffe94a" textColor="#000" size="lg" glow={!0}>▶ CLAIM REWARD</PixelButton></div></div>;
