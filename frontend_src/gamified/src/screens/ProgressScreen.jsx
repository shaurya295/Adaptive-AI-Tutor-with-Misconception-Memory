import * as React from 'react';
import { getLearningCurve, getRollingStats, isMock } from '../api/client';
import { useHud } from '../api/hud';
import { DialogBox } from '../components/Dialog';
import { PixelButton } from '../components/PixelButton';
import { WizardSprite } from '../components/Sprites';
export const ProgressScreen = ({
  next,
  studentId
}) => {
  const hud = useHud(), coins = hud.coins;
  let [n, r] = (0, React.useState)([]),
    [i, a] = (0, React.useState)({
      rolling_accuracy: 84,
      rolling_avg_time_ms: 12400,
      streak: 7
    }),
    [o, s] = (0, React.useState)(!1),
    [c, u] = (0, React.useState)(`session`),
    [d, f] = (0, React.useState)(null);
  (0, React.useEffect)(() => {
    studentId && (s(!0), Promise.all([getLearningCurve(studentId, c), getRollingStats(studentId)]).then(([e, t]) => {
      r(e), (!isMock || t.streak > 0 || t.rolling_accuracy > 0) && a(t), s(!1);
    }));
  }, [studentId, c]);
  let p = [{
      label: `STREAK`,
      value: `🔥 ${i.streak} Days`,
      color: `#ff8c1a`
    }, {
      label: `ACCURACY`,
      value: `🎯 ${i.rolling_accuracy || 84}%`,
      color: `#00ffee`
    }, {
      label: `AVG TIME`,
      value: `⏱ ${i.rolling_avg_time_ms ? Math.round(i.rolling_avg_time_ms / 1e3) : 12}s`,
      color: `#4aff91`
    }, {
      label: `COINS`,
      value: `🪙 ${coins}`,
      color: `#ffe94a`
    }],
    m = n.length > 0 ? n : [],
    h = m.length ? Math.max(...m.map(e => e.accuracy_pct), 100) : 100,
    v = e => 30 + (m.length <= 1 ? 260 / 2 : e / (m.length - 1) * 260),
    y = e => 110 - e / h * 80,
    b = m.map((e, t) => `${v(t)},${y(e.accuracy_pct)}`).join(` `);
  const lessonPct = isMock ? 70 : Math.round(i.lesson_progress_pct ?? 0),
    tip = isMock ? `You're on a streak! Keep going and you'll earn the PHOENIX badge. Study for 20 more minutes today!`
      : i.streak > 0 ? `You're on a ${i.streak}-day streak! A few questions every day keeps it going.`
      : `Answer a question today to start a streak!`;
  return <div className="game-screen scanlines" style={{
    background: `linear-gradient(to bottom, #2a1050, #3d1f6e)`,
    display: `flex`,
    flexDirection: `column`,
    alignItems: `center`,
    paddingTop: 80,
    paddingBottom: 96,
    overflowY: `auto`
  }}><h1 className="font-pixel text-center mb-6" style={{
      fontSize: `clamp(0.9rem,2.5vw,1.3rem)`,
      color: `#ffe94a`,
      textShadow: `3px 3px 0 #000`
    }}>📊 YOUR PROGRESS</h1><div className="grid grid-cols-2 gap-4 w-full max-w-md px-4 mb-6">{p.map((e, t) => <div className="stat-card" style={{
        background: e.color + `33`,
        animation: `float 3s ${t * .2}s ease-in-out infinite`
      }} key={t}><p className="font-pixel text-xs text-white" style={{
          textShadow: `1px 1px 0 #000`
        }}>{e.label}</p><p className="font-body text-xl font-bold" style={{
          color: e.color
        }}>{e.value}</p></div>)}</div><div className="w-full max-w-md px-4 mb-6"><div className="flex justify-between font-pixel text-xs mb-1" style={{
        color: `#00ffee`
      }}><span>LESSON PROGRESS</span><span>{lessonPct}%</span></div><div className="hp-bar-track w-full"><div className="hp-bar-fill" style={{
          "--fill": `${lessonPct}%`
        }} /></div></div><div className="w-full max-w-md px-4 mb-6"><div className="flex items-center justify-between mb-3"><p className="font-pixel text-xs" style={{
          color: `#ff00cc`
        }}>📈 LEARNING CURVE</p><div className="flex gap-2">{[`session`, `day`].map(e => <button onClick={() => u(e)} className="pixel-btn font-pixel border-2 border-black px-2 py-1" style={{
            fontSize: `7px`,
            background: c === e ? `#ff00cc` : `#3d1f6e`,
            color: c === e ? `#fff` : `#aaa`,
            boxShadow: c === e ? `0 0 0 #000` : `2px 2px 0 #000`,
            transform: c === e ? `translate(2px,2px)` : `none`
          }} key={e}>{e.toUpperCase()}</button>)}</div></div><div className="border-4 border-black relative" style={{
        background: `#1a0a2e`,
        boxShadow: `6px 6px 0 #000`
      }}>{o ? <div className="flex items-center justify-center" style={{
          height: 140
        }}><span className="font-pixel text-xs" style={{
            color: `#00ffee`,
            animation: `blink 1s step-end infinite`
          }}>LOADING...</span></div> : m.length === 0 ? <div className="flex flex-col items-center justify-center gap-4 p-4" style={{
          minHeight: 140
        }}><WizardSprite mood="thinking" size={.9} /><p className="font-pixel text-xs text-center" style={{
            color: `#ff4fa3`,
            fontSize: `8px`,
            lineHeight: 2
          }}>No quest data yet,<br />brave learner!<br />Complete a lesson<br />to see your curve!</p></div> : <div className="relative" onMouseLeave={() => f(null)}><svg width="100%" viewBox="0 0 320 140" style={{
            imageRendering: `pixelated`
          }}>{[0, 25, 50, 75, 100].map(e => {
              let t = 110 - e / 100 * 80;
              return <g key={e}><line x1={30} y1={t} x2={290} y2={t} stroke="#ffffff15" strokeWidth="1" /><text x={26} y={t + 3} textAnchor="end" fill="#00ffee" fontSize="7" fontFamily="'Press Start 2P', cursive">{e}</text></g>;
            })}{m.map((e, t) => <text x={v(t)} y={132} textAnchor="middle" fill="#ffe94a" fontSize="6" fontFamily="'Press Start 2P', cursive" key={t}>{e.label}</text>)}<line x1={30} y1={30} x2={30} y2={110} stroke="#00ffee" strokeWidth="2" /><line x1={30} y1={110} x2={290} y2={110} stroke="#00ffee" strokeWidth="2" />{m.length > 1 && <polygon points={`${v(0)},110 ${b} ${v(m.length - 1)},110`} fill="#ff00cc22" />}{m.length > 1 && <polyline points={b} fill="none" stroke="#ff00cc" strokeWidth="3" strokeLinejoin="round" />}{m.map((e, t) => <g style={{
              cursor: `pointer`
            }} onMouseEnter={() => f({
              x: v(t),
              y: y(e.accuracy_pct),
              pt: e
            })} key={t}><rect x={v(t) - 5} y={y(e.accuracy_pct) - 5} width={10} height={10} fill="#ff00cc" stroke="#000" strokeWidth="2" /><rect x={v(t) - 2} y={y(e.accuracy_pct) - 2} width={4} height={4} fill="#fff" /></g>)}{d && <g><rect x={Math.min(d.x - 30, 210)} y={d.y - 38} width={100} height={34} fill="#1a0a2e" stroke="#00ffee" strokeWidth="2" /><text x={Math.min(d.x - 25, 215)} y={d.y - 24} fill="#ffe94a" fontSize="6" fontFamily="'Press Start 2P', cursive">{d.pt.label}{": "}{d.pt.accuracy_pct}%</text><text x={Math.min(d.x - 25, 215)} y={d.y - 12} fill="#00ffee" fontSize="6" fontFamily="'Press Start 2P', cursive">{"⏱ "}{Math.round(d.pt.avg_time_ms / 1e3)}s avg</text></g>}</svg></div>}<div className="absolute top-1 left-1"><span className="font-pixel" style={{
            fontSize: `6px`,
            color: `#ff00cc`
          }}>ACCURACY %</span></div></div></div><div className="flex items-end gap-4 w-full max-w-md px-4 mb-8"><WizardSprite mood="thinking" size={1.1} /><div className="flex-1"><DialogBox speaker="PIXEL TIP" text={tip} /></div></div><PixelButton onClick={next} color="#ff00cc" size="lg">CONTINUE ▶</PixelButton></div>;
};
