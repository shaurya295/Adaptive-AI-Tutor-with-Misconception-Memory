import { delay } from '../api/mock';
import { PixelButton } from '../components/PixelButton';
import { PixelBuilding, PixelCloud } from '../components/Scenery';
import { WizardSprite } from '../components/Sprites';
export const LandingScreen = ({
  next
}) => <div className="game-screen scanlines" style={{
  background: `linear-gradient(to bottom, #2a1050, #3d1f6e, #5b3a8e)`,
  display: `flex`,
  flexDirection: `column`,
  alignItems: `center`,
  justifyContent: `center`,
  position: `relative`,
  overflow: `hidden`
}}>{Array.from({
    length: 30
  }).map((e, t) => <div className="absolute rounded-full" style={{
    width: t % 3 == 0 ? 4 : 2,
    height: t % 3 == 0 ? 4 : 2,
    background: t % 4 == 0 ? `#00ffee` : t % 4 == 1 ? `#ff4fa3` : `#fff`,
    top: `${t * 37 % 70}%`,
    left: `${t * 53 % 100}%`,
    animation: `startwink 1.5s ${t * .2 % 2}s ease-in-out infinite`
  }} key={t} />)}<svg className="absolute" style={{
    top: 32,
    left: 0,
    width: `100%`,
    overflow: `visible`
  }} height="80" viewBox="0 0 800 80"><g style={{
      animation: `cloudmove 22s linear infinite`
    }}><PixelCloud x={-80} y={5} scale={.6} color="#f0e8ff" delay="0s" /><PixelCloud x={200} y={15} scale={.5} color="#d0b8ff" delay="-6s" /><PixelCloud x={500} y={2} scale={.7} color="#f0e8ff" delay="-12s" /></g></svg><svg className="absolute" style={{
    bottom: 80,
    left: 0,
    width: `100%`
  }} height="200" viewBox="0 0 800 200" preserveAspectRatio="none"><PixelBuilding x={0} color="#5b3a8e" w={50} h={100} /><PixelBuilding x={60} color="#3d1f6e" w={40} h={140} /><PixelBuilding x={110} color="#6a2e9e" w={60} h={80} /><PixelBuilding x={180} color="#2a1050" w={35} h={160} /><PixelBuilding x={220} color="#5b3a8e" w={55} h={110} /><PixelBuilding x={285} color="#3d1f6e" w={45} h={90} /><PixelBuilding x={500} color="#5b3a8e" w={50} h={120} /><PixelBuilding x={560} color="#3d1f6e" w={60} h={150} /><PixelBuilding x={630} color="#6a2e9e" w={40} h={85} /><PixelBuilding x={680} color="#2a1050" w={55} h={130} /><PixelBuilding x={745} color="#5b3a8e" w={55} h={100} /></svg><div className="absolute bottom-0 left-0 right-0 h-20 ground" /><div className="absolute bottom-20 left-0" style={{
    animation: `busmove 10s linear infinite`
  }}><svg width="140" height="60" viewBox="0 0 140 60" style={{
      imageRendering: `pixelated`
    }}><rect x="0" y="10" width="120" height="40" fill="#ff8c1a" /><rect x="0" y="10" width="120" height="8" fill="#ff3355" /><rect x="120" y="18" width="20" height="32" fill="#ff8c1a" /><rect x="10" y="18" width="20" height="20" fill="#00ffee" opacity="0.8" /><rect x="40" y="18" width="20" height="20" fill="#00ffee" opacity="0.8" /><rect x="70" y="18" width="20" height="20" fill="#00ffee" opacity="0.8" /><circle cx="25" cy="52" r="8" fill="#1a0a2e" /><circle cx="95" cy="52" r="8" fill="#1a0a2e" /><circle cx="25" cy="52" r="4" fill="#666" /><circle cx="95" cy="52" r="4" fill="#666" /><rect x="128" y="25" width="10" height="6" fill="#ffe94a" /></svg></div><div className="relative z-10 text-center" style={{
    animation: `float 3s ease-in-out infinite`,
    marginBottom: 8
  }}><div className="font-pixel text-xs" style={{
      color: `#ffe94a`,
      letterSpacing: `0.15em`,
      marginBottom: 8
    }}>▶ PRESS START ◀</div><h1 className="font-pixel" style={{
      fontSize: `clamp(1.2rem,5vw,2.8rem)`,
      color: `#ffe94a`,
      textShadow: `4px 4px 0 #000, -1px -1px 0 #ff00cc, 1px 1px 0 #ff00cc`,
      letterSpacing: `0.05em`,
      lineHeight: 1.6
    }}>LET'S LEARN!</h1><p className="font-pixel text-xs mt-3" style={{
      color: `#00ffee`,
      textShadow: `2px 2px 0 #000`
    }}>— PIXEL TUTOR AI —</p></div><div className="relative z-10" style={{
    animation: `float 3s 0.5s ease-in-out infinite`
  }}><WizardSprite mood="idle" size={1.5} /></div><div className="relative z-10" style={{
    marginTop: 32
  }}><PixelButton onClick={next} color="#ff00cc" size="lg" glow={!0}>▶ START GAME</PixelButton></div><p className="relative z-10 font-pixel text-xs mt-4" style={{
    color: `#00ffee`,
    animation: `blink 1s step-end infinite`
  }}>© 2025 PIXEL TUTOR</p></div>;
