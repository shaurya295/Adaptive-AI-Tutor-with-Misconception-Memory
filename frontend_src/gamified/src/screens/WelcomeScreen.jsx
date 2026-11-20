import { DialogBox } from '../components/Dialog';
import { PixelButton } from '../components/PixelButton';
import { WizardSprite } from '../components/Sprites';
export const WelcomeScreen = ({
  next
}) => <div className="game-screen scanlines" style={{
  background: `linear-gradient(to bottom, #2a1050, #3d1f6e, #5b3a8e)`,
  display: `flex`,
  flexDirection: `column`,
  alignItems: `center`,
  paddingTop: 80,
  position: `relative`,
  overflow: `hidden`
}}><div className="relative mb-6" style={{
    animation: `float 3s ease-in-out infinite`
  }}><div style={{
      width: 96,
      height: 96,
      borderRadius: `50%`,
      background: `radial-gradient(circle, #ffe94a, #ff8c1a)`,
      boxShadow: `0 0 40px #ffe94a, 0 0 80px #ff8c1a44, 4px 4px 0 #000`,
      border: `4px solid #000`,
      display: `flex`,
      alignItems: `center`,
      justifyContent: `center`,
      fontSize: 48
    }}>☀️</div></div><svg className="absolute" style={{
    bottom: 112,
    left: 0,
    width: `100%`
  }} height="100" viewBox="0 0 800 100" preserveAspectRatio="none">{[0, 60, 130, 180, 240, 300, 360, 420, 500, 560, 620, 680, 740].map((e, t) => <rect x={e} y={100 - (40 + t % 3 * 30)} width={50} height={40 + t % 3 * 30} fill="#1a0a2e" opacity="0.8" key={e} />)}</svg><div className="absolute bottom-0 left-0 right-0 h-28 ground" /><h1 className="font-pixel text-center mb-6" style={{
    fontSize: `clamp(1.2rem,4vw,2rem)`,
    color: `#ffe94a`,
    textShadow: `3px 3px 0 #000`
  }}>✨ HELLO, HERO! ✨</h1><div className="flex items-end gap-6 relative z-10 max-w-xl w-full px-4"><div style={{
      animation: `walk 0.8s ease-out forwards`
    }}><WizardSprite mood="idle" size={1.3} /></div><div className="flex-1"><DialogBox speaker="PIXEL — AI TUTOR" text="Welcome, brave learner! I am Pixel, your magical AI tutor. Together we shall conquer every subject and level up your brain! Are you ready to begin your quest?" onNext={next} /></div></div><div className="relative z-10 mt-8"><PixelButton onClick={next} color="#ff00cc" size="lg">LET'S GO! ▶</PixelButton></div></div>;
