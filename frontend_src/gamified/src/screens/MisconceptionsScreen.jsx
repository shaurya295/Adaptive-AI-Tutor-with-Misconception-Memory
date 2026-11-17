import * as React from 'react';
import { getConceptGraph } from '../api/mock';
import { DialogBox } from '../components/Dialog';
import { WizardSprite } from '../components/Sprites';
import { TOPICS, explainConcept, masteryColor } from '../data/content';
export const MisconceptionsScreen = ({
  goTo,
  studentId
}) => {
  let [n, r] = (0, React.useState)(TOPICS[0]),
    [i, a] = (0, React.useState)(null),
    [o, s] = (0, React.useState)(!0),
    [c, u] = (0, React.useState)(null);
  (0, React.useEffect)(() => {
    let e = !1;
    return s(!0), u(null), getConceptGraph(n, studentId || `anonymous`).then(t => {
      e || (a(t), s(!1));
    }), () => {
      e = !0;
    };
  }, [n, studentId]);
  let d = i?.nodes.find(e => e.is_focus) ?? null,
    f = i?.nodes.filter(e => !e.is_focus) ?? [],
    p = 460 / (f.length + 1),
    m = e => {
      if (e.is_focus) return 190;
      let t = f.indexOf(e);
      return p * (t + 1) - 40;
    };
  return <div className="game-screen scanlines" style={{
    background: `linear-gradient(to bottom, #1a0a2e, #2a1050)`,
    display: `flex`,
    flexDirection: `column`,
    alignItems: `center`,
    paddingTop: 80,
    paddingBottom: 40,
    overflowY: `auto`
  }}><div className="flex items-center gap-4 mb-2 w-full max-w-2xl px-4"><button onClick={() => goTo(`mainmenu`)} className="font-pixel text-xs" style={{
        color: `#ff4fa3`,
        background: `none`,
        border: `none`,
        cursor: `pointer`
      }}>◀ BACK</button><h1 className="font-pixel" style={{
        fontSize: `clamp(0.8rem,2.5vw,1.1rem)`,
        color: `#ffe94a`,
        textShadow: `3px 3px 0 #000`
      }}>🧠 MISCONCEPTION MAP</h1></div><div className="flex gap-2 mb-4 flex-wrap justify-center px-4">{TOPICS.map(e => <button onClick={() => r(e)} className="font-pixel" style={{
        fontSize: `7px`,
        padding: `6px 10px`,
        border: `3px solid #000`,
        cursor: `pointer`,
        background: e === n ? `#ffe94a` : `#3d1f6e`,
        color: e === n ? `#000` : `#f0e8ff`
      }} key={e}>{e.toUpperCase()}</button>)}</div><div className="flex gap-4 mb-4">{[[`#4aff91`, `MASTERED 70%+`], [`#ffe94a`, `DEVELOPING 40-69%`], [`#ff3355`, `WEAK <40%`]].map(([e, t]) => <div className="flex items-center gap-1" key={t}><div style={{
          width: 12,
          height: 12,
          background: e,
          border: `2px solid #000`
        }} /><span className="font-pixel" style={{
          fontSize: `6px`,
          color: `#aaa`
        }}>{t}</span></div>)}</div><div className="border-4 border-black mb-4" style={{
      background: `#1a0a2e`,
      boxShadow: `6px 6px 0 #000`,
      maxWidth: 480,
      width: `100%`,
      margin: `0 16px 16px`,
      minHeight: 220
    }}>{o ? <p className="font-pixel text-xs text-center py-16" style={{
        color: `#00ffee`
      }}>Loading graph…</p> : i?.neo4j_available ? f.length === 0 ? <p className="font-body text-sm text-center py-16 px-6" style={{
        color: `#aaa`
      }}>{"No prerequisites on record for "}{n}{" yet."}</p> : <svg viewBox="0 0 460 230" style={{
        width: `100%`,
        imageRendering: `pixelated`
      }}>{d && f.map(e => <polyline points={`230,56 230,68 ${m(e) + 40},68 ${m(e) + 40},160`} fill="none" stroke="#5b3a8e" strokeWidth="3" key={e.name + `-edge`} />)}{i.nodes.map(e => {
          let t = Math.round((e.mastery || 0) * 100),
            n = masteryColor(t),
            r = m(e),
            i = e.is_focus ? 40 : 160,
            a = c?.name === e.name;
          return <g style={{
            cursor: `pointer`
          }} onClick={() => u(a ? null : e)} key={e.name}>{a && <rect x={r - 6} y={i - 6} width={92} height={36} fill={n} opacity={.25} />}<rect x={r} y={i} width={80} height={28} fill="#2a1050" stroke={n} strokeWidth={a ? 4 : 2} /><rect x={r} y={i} width={80} height={4} fill={n} /><text x={r + 4} y={i + 16} style={{
              fontSize: `6px`,
              fontFamily: `'Press Start 2P', cursive`,
              fill: `#fff`
            }}>{e.name.length > 10 ? e.name.slice(0, 9) + `…` : e.name}</text><text x={r + 4} y={i + 25} style={{
              fontSize: `6px`,
              fontFamily: `'Press Start 2P', cursive`,
              fill: n
            }}>{t}%</text></g>;
        })}</svg> : <p className="font-body text-sm text-center py-16 px-6" style={{
        color: `#aaa`
      }}>🔌 Neo4j isn't connected right now, so the prerequisite graph is empty. Mastery and quizzes still work — this screen just needs the graph database live.</p>}</div>{c ? <div className="flex items-end gap-4 w-full max-w-2xl px-4 slide-up"><WizardSprite mood="pointing" size={.9} /><div className="flex-1"><DialogBox speaker={`${c.name} — ${Math.round((c.mastery || 0) * 100)}% MASTERED`} text={explainConcept(c.name, Math.round((c.mastery || 0) * 100), c.is_focus)} /></div></div> : <div className="flex items-end gap-4 w-full max-w-2xl px-4"><WizardSprite mood="idle" size={.9} /><div className="flex-1"><DialogBox speaker="PIXEL — AI TUTOR" text="Pick a topic above, then click any concept node to see your real mastery on it!" /></div></div>}</div>;
};
