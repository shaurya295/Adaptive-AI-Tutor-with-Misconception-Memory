import { PixelButton } from '../components/PixelButton';
export const MainMenuScreen = ({
  goTo
}) => <div className="game-screen scanlines" style={{
  background: `linear-gradient(to bottom, #2a1050, #5b3a8e)`,
  display: `flex`,
  flexDirection: `column`,
  alignItems: `center`,
  justifyContent: `center`,
  position: `relative`
}}><svg className="absolute bottom-16 left-1/2" style={{
    transform: `translateX(-50%)`
  }} width="200" height="160" viewBox="0 0 200 160" preserveAspectRatio="xMidYMax meet"><rect x="40" y="60" width="120" height="100" fill="#3d1f6e" /><rect x="10" y="40" width="50" height="120" fill="#2a1050" /><rect x="140" y="40" width="50" height="120" fill="#2a1050" />{[0, 1, 2].map(e => <rect x={10 + e * 16} y={30} width="10" height="14" fill="#2a1050" key={e} />)}{[0, 1, 2].map(e => <rect x={140 + e * 16} y={30} width="10" height="14" fill="#2a1050" key={e} />)}<rect x="24" y="60" width="18" height="18" fill="#ffe94a" /><rect x="158" y="60" width="18" height="18" fill="#ffe94a" /><rect x="88" y="80" width="24" height="30" fill="#ffe94a" /><rect x="80" y="120" width="40" height="40" fill="#1a0a2e" /><rect x="85" y="115" width="30" height="8" fill="#000" /><rect x="97" y="10" width="4" height="50" fill="#c8a050" /><rect x="101" y="12" width="24" height="16" fill="#ff00cc" /></svg><div className="absolute bottom-0 left-0 right-0 h-16 ground" /><div className="relative z-10 flex flex-col items-center gap-3 mb-8"><h1 className="font-pixel text-center mb-4" style={{
      fontSize: `clamp(1rem,3.5vw,1.6rem)`,
      color: `#ffe94a`,
      textShadow: `4px 4px 0 #000`
    }}>⚔ MAIN MENU ⚔</h1><PixelButton onClick={() => goTo(`signin`)} color="#ff00cc" size="lg" className="w-64">👤 SIGN IN</PixelButton><PixelButton onClick={() => goTo(`pretest`)} color="#00ffee" textColor="#000" size="lg" className="w-64">📚 START LESSON</PixelButton><PixelButton onClick={() => goTo(`freequest`)} color="#ffe94a" textColor="#000" size="lg" className="w-64" glow={!0}>✨ FREE QUEST</PixelButton><PixelButton onClick={() => goTo(`leaderboard`)} color="#ff4fa3" size="lg" className="w-64">🏆 LEADERBOARD</PixelButton><PixelButton onClick={() => goTo(`progress`)} color="#4aff91" textColor="#000" size="lg" className="w-64">📊 PROGRESS</PixelButton><PixelButton onClick={() => goTo(`howitworks`)} color="#5b3a8e" size="lg" className="w-64">❓ HOW IT WORKS</PixelButton><PixelButton onClick={() => goTo(`evalmetrics`)} color="#ff8c1a" textColor="#000" size="lg" className="w-64">📈 EVAL METRICS</PixelButton><PixelButton onClick={() => goTo(`misconceptions`)} color="#ff3355" size="lg" className="w-64">🧠 MISCONCEPTIONS</PixelButton><PixelButton onClick={() => goTo(`spacedrepeat`)} color="#00ffee" textColor="#000" size="lg" className="w-64">📅 SPACED REVIEW</PixelButton><PixelButton onClick={() => goTo(`switchstudent`)} color="#ff4fa3" size="lg" className="w-64">👥 SWITCH STUDENT</PixelButton></div></div>;
