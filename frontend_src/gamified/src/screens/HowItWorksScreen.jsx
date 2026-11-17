import { PixelButton } from '../components/PixelButton';
import { HOW_IT_WORKS } from '../data/content';
export const HowItWorksScreen = ({
  next
}) => <div className="game-screen scanlines" style={{
  background: `#2a1050`,
  display: `flex`,
  flexDirection: `column`,
  alignItems: `center`,
  paddingTop: 80,
  paddingBottom: 96,
  overflowY: `auto`
}}><h1 className="font-pixel text-center mb-8" style={{
    fontSize: `clamp(1rem,3vw,1.5rem)`,
    color: `#ffe94a`,
    textShadow: `3px 3px 0 #000`
  }}>❓ HOW IT WORKS ❓</h1><div className="flex flex-col gap-4 max-w-lg w-full px-4">{HOW_IT_WORKS.map((e, t) => <div className="flex items-center gap-4 border-4 border-black p-4" style={{
      background: e.color + `22`,
      animation: `walk 0.8s ease-out forwards`,
      animationDelay: `${t * .1}s`
    }} key={t}><div className="w-16 h-16 flex items-center justify-center border-4 border-black text-4xl flex-shrink-0" style={{
        background: e.color,
        animation: `float 3s ease-in-out infinite`,
        animationDelay: `${t * .3}s`
      }}>{e.icon}</div><div><p className="font-pixel text-xs mb-1" style={{
          color: e.color,
          textShadow: `1px 1px 0 #000`
        }}>{e.title}</p><p className="font-body text-sm" style={{
          color: `#f0e8ff`
        }}>{e.text}</p></div></div>)}</div><div className="mt-8"><PixelButton onClick={next} color="#ff00cc" size="lg">GOT IT! ▶</PixelButton></div></div>;
