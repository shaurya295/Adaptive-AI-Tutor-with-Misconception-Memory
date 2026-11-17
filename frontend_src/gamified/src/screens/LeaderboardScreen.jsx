import * as React from 'react';
import * as JSXRuntime from 'react/jsx-runtime';
import { PixelButton } from '../components/PixelButton';
import { COMPANIONS, LEADERBOARD, RANK_STYLES, TICKER_ITEMS } from '../data/content';
import { getLeaderboard, isMock } from '../api/client';

const avatarOf = id => COMPANIONS.find(c => c.id === id)?.emoji || `🧙`;
const WINDOWS = { week: `7d`, alltime: `all`, friends: `all` };
export const LeaderboardScreen = ({
  goTo,
  profiles,
  activeProfileId
}) => {
  let [r, i] = (0, React.useState)(`alltime`);
  // Real mode: real players from the server, ranked by XP (owner's decision G3).
  const [entries, setEntries] = React.useState(null);
  React.useEffect(() => {
    if (isMock) return;
    getLeaderboard(WINDOWS[r]).then(d => setEntries(d.entries)).catch(() => setEntries([]));
  }, [r]);
  const localIds = new Set(profiles.map(p => p.id));
  const realRows = (entries || [])
    .filter(e => r !== `friends` || e.is_me || localIds.has(e.student_id))
    .map((e, idx) => ({ rank: idx + 1, name: e.name, xp: e.xp, streak: e.streak, badge: e.badge, avatar: avatarOf(e.avatar), isMe: e.is_me }));
  const rows = isMock ? LEADERBOARD : realRows;
  const ticker = isMock ? TICKER_ITEMS : realRows.length
    ? realRows.flatMap(e => [`${e.name} has ${e.xp.toLocaleString()} XP! ⭐`, ...(e.streak > 1 ? [`${e.name} is on a ${e.streak}-day streak! 🔥`] : [])])
    : [`Answer a question to get on the board! ⭐`];
  (0, React.useEffect)(() => {
    let e = setInterval(() => {}, 3e3);
    return () => clearInterval(e);
  }, []);
  let a = [{
      key: `week`,
      label: `7 DAYS`,
      color: `#00ffee`
    }, {
      key: `alltime`,
      label: `ALL TIME`,
      color: `#ff00cc`
    }, {
      key: `friends`,
      label: `FRIENDS`,
      color: `#4aff91`
    }],
    o = !isMock ? realRows.filter(e => e.isMe).map(e => ({ ...e, isLocal: !0, isActive: !0 })) : profiles.map((e, t) => ({
      rank: 11 + t,
      name: e.name.toUpperCase(),
      xp: 1240 + t * 300,
      streak: 7,
      badge: `🔥`,
      avatar: COMPANIONS.find(t => t.id === e.avatarId)?.emoji || `🧙`,
      isLocal: !0,
      isActive: e.id === activeProfileId
    }));
  return <div className="game-screen scanlines" style={{
    background: `linear-gradient(to bottom, #1a0a2e, #2a1050)`,
    display: `flex`,
    flexDirection: `column`,
    alignItems: `center`,
    paddingTop: 80,
    paddingBottom: 40,
    overflowY: `auto`
  }}><div className="w-full border-b-4 border-black mb-6 overflow-hidden" style={{
      background: `#1a0a2e`,
      padding: `6px 0`
    }}><div style={{
        animation: `cloudmove 8s linear infinite`,
        whiteSpace: `nowrap`,
        display: `inline-block`
      }}>{[...ticker, ...ticker].map((e, t) => <span className="font-pixel text-xs mx-8" style={{
          color: t % 2 == 0 ? `#ffe94a` : `#ff4fa3`
        }} key={t}>{"★ "}{e}</span>)}</div></div><div className="flex items-center gap-4 mb-6"><button onClick={() => goTo(`mainmenu`)} className="font-pixel text-xs" style={{
        color: `#ff4fa3`,
        background: `none`,
        border: `none`,
        cursor: `pointer`
      }}>◀ BACK</button><h1 className="font-pixel text-center" style={{
        fontSize: `clamp(0.9rem,3vw,1.4rem)`,
        color: `#ffe94a`,
        textShadow: `4px 4px 0 #000`
      }}>🏆 TOP SCHOLARS 🏆</h1></div><div className="flex gap-3 mb-6">{a.map(e => <button onClick={() => i(e.key)} className="pixel-btn font-pixel text-xs border-3 border-black px-4 py-2" style={{
        border: `3px solid #000`,
        background: r === e.key ? e.color : `#3d1f6e`,
        color: r === e.key ? `#000` : `#fff`,
        boxShadow: r === e.key ? `0 0 0 #000` : `4px 4px 0 #000`,
        transform: r === e.key ? `translate(4px,4px)` : `none`
      }} key={e.key}>{e.label}</button>)}</div><div className="w-full max-w-lg px-4 flex flex-col gap-2"><div className="grid grid-cols-12 gap-1 font-pixel text-xs mb-2 px-2" style={{
        color: `#00ffee`
      }}><span className="col-span-1">#</span><span className="col-span-1" /><span className="col-span-4">NAME</span><span className="col-span-3 text-right">XP</span><span className="col-span-2 text-right">🔥</span><span className="col-span-1 text-right" /></div>{rows.map(e => {
        let t = RANK_STYLES[e.rank];
        return <div className="grid grid-cols-12 gap-1 items-center border-4 border-black px-2 py-2" style={{
          background: t ? t.bg + `33` : `#3d1f6e`,
          boxShadow: t ? `4px 4px 0 #000, 0 0 16px ${t.glow}` : `3px 3px 0 #000`,
          border: t ? `4px solid ${t.bg}` : `4px solid #000`
        }} key={e.rank}><div className="col-span-1 font-pixel text-xs text-center" style={{
            color: t ? t.bg : `#aaa`
          }}>{t ? t.icon : e.rank}</div><div className="col-span-1 text-center text-xl" style={{
            animation: t ? `float 3s ease-in-out infinite` : `none`
          }}>{e.avatar}</div><div className="col-span-4 font-pixel text-xs truncate" style={{
            color: t ? `#ffe94a` : `#f0e8ff`
          }}>{e.name}{t && <span className="ml-1" style={{
              color: t.bg
            }}>★</span>}</div><div className="col-span-3 font-pixel text-xs text-right" style={{
            color: `#4aff91`
          }}>{e.xp.toLocaleString()}</div><div className="col-span-2 font-pixel text-xs text-right" style={{
            color: `#ff8c1a`
          }}>{e.streak}d</div><div className="col-span-1 text-center text-sm">{e.badge}</div></div>;
      })}{o.length > 0 && <JSXRuntime.Fragment><div className="flex items-center gap-2 my-2"><div className="flex-1 border-t-2 border-black border-dashed" /><span className="font-pixel text-xs" style={{
            color: `#555`
          }}>• LOCAL PLAYERS •</span><div className="flex-1 border-t-2 border-black border-dashed" /></div>{o.map(e => <div className="grid grid-cols-12 gap-1 items-center border-4 border-black px-2 py-2" style={{
          background: e.isActive ? `#ff00cc33` : `#2a1050`,
          boxShadow: e.isActive ? `4px 4px 0 #000, 0 0 16px #ff00cc44` : `3px 3px 0 #000`,
          borderColor: e.isActive ? `#ff00cc` : `#000`
        }} key={e.rank}><div className="col-span-1 font-pixel text-xs text-center" style={{
            color: e.isActive ? `#ff00cc` : `#aaa`
          }}>{e.rank}</div><div className="col-span-1 text-center text-xl">{e.avatar}</div><div className="col-span-4 font-pixel text-xs" style={{
            color: e.isActive ? `#ffe94a` : `#f0e8ff`
          }}>{e.name}{" "}{e.isActive && <span style={{
              color: `#ff4fa3`,
              animation: `blink 1s step-end infinite`
            }}>◀</span>}</div><div className="col-span-3 font-pixel text-xs text-right" style={{
            color: `#4aff91`
          }}>{e.xp.toLocaleString()}</div><div className="col-span-2 font-pixel text-xs text-right" style={{
            color: `#ff8c1a`
          }}>{e.streak}d</div><div className="col-span-1 text-center text-sm">{e.badge}</div></div>)}</JSXRuntime.Fragment>}<div className="flex items-center gap-2 my-2"><div className="flex-1 border-t-2 border-black border-dashed" /><span className="font-pixel text-xs" style={{
          color: `#555`
        }}>• • •</span><div className="flex-1 border-t-2 border-black border-dashed" /></div></div><div className="mt-8 flex gap-4"><PixelButton onClick={() => goTo(`pretest`)} color="#ff00cc" size="md">▶ STUDY MORE</PixelButton><PixelButton onClick={() => goTo(`freequest`)} color="#ffe94a" textColor="#000" size="md" glow={!0}>✨ FREE QUEST</PixelButton></div></div>;
};
