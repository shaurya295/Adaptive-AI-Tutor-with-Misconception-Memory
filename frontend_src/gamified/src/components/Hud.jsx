export const Hud = ({
  coins = 0,
  level = 1,
  xp = 60,
  goTo,
  playerName = ``
}) => <div className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-4 py-2 bg-px-dark border-b-4 border-black font-pixel" style={{
  background: `#1a0a2e`,
  borderBottom: `4px solid #000`
}}><div className="flex items-center gap-3"><span className="font-pixel text-xs" style={{
      color: `#ffe94a`
    }}>{"⭐ LVL "}{level}</span><div className="hp-bar-track" style={{
      width: 128,
      height: 16
    }}><div className="hp-bar-fill" style={{
        "--fill": `${xp}%`
      }} /></div><span className="font-pixel text-xs" style={{
      color: `#4aff91`
    }}>{"XP "}{xp}%</span></div><div className="flex items-center gap-3">{playerName && <span className="font-pixel text-xs" style={{
      color: `#ff4fa3`
    }}>{"👤 "}{playerName.slice(0, 8)}</span>}<button onClick={() => goTo(`leaderboard`)} className="font-pixel text-xs" style={{
      color: `#ff4fa3`,
      background: `none`,
      border: `none`,
      cursor: `pointer`
    }}>🏆</button><button onClick={() => goTo(`freequest`)} className="font-pixel text-xs" style={{
      color: `#00ffee`,
      background: `none`,
      border: `none`,
      cursor: `pointer`
    }}>❓</button><div className="flex items-center gap-1" style={{
      color: `#ffe94a`
    }}><span style={{
        animation: `bounce2 0.8s ease-in-out infinite`
      }}>🪙</span><span className="font-pixel text-xs">{coins}</span></div></div></div>;
