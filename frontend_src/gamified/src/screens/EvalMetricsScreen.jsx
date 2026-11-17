import { DialogBox } from '../components/Dialog';
import { WizardSprite } from '../components/Sprites';
export const EvalMetricsScreen = ({
  goTo,
  sessionRiskScore
}) => {
  let n = sessionRiskScore < 33 ? {
    label: `LOW`,
    color: `#4aff91`
  } : sessionRiskScore < 66 ? {
    label: `MEDIUM`,
    color: `#ffe94a`
  } : {
    label: `HIGH`,
    color: `#ff3355`
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
      }}>📈 EVAL METRICS</h1></div><p className="font-pixel text-xs mb-6 w-full max-w-2xl px-4" style={{
      color: `#ff4fa3`
    }}>TEACHER / ANALYST VIEW</p><div className="w-full max-w-2xl px-4 mb-6"><div className="border-4 border-black p-4 slide-up" style={{
        background: `#1a0a2e`,
        boxShadow: `6px 6px 0 #000`,
        borderColor: n.color
      }}><div className="flex items-center justify-between mb-3"><p className="font-pixel text-xs" style={{
            color: n.color
          }}>🛡️ CHEATING RISK SIGNAL</p><span className="font-pixel text-xs" style={{
            color: n.color,
            animation: sessionRiskScore > 66 ? `blink 0.5s step-end infinite` : `none`
          }}>{n.label}</span></div><div className="hp-bar-track w-full" style={{
          height: 16
        }}><div className="hp-bar-fill-risk" style={{
            "--fill": `${sessionRiskScore}%`,
            animation: `hpbar 1s ease-out forwards`
          }} /></div><div className="flex justify-between font-pixel mt-2" style={{
          fontSize: `7px`,
          color: `#555`
        }}><span>0 — LOW RISK</span><span>100 — HIGH RISK</span></div><p className="font-pixel mt-2" style={{
          fontSize: `7px`,
          color: `#aaa`
        }}>Based on tab-switching, answer speed, and paste events</p></div></div><div className="grid grid-cols-2 gap-4 w-full max-w-2xl px-4 mb-6">{[{
        label: `ACCURACY`,
        value: `84%`,
        trend: `▲`,
        trendDir: `up`,
        color: `#00ffee`,
        icon: `🎯`,
        sub: `last 20 attempts`
      }, {
        label: `HINT USAGE`,
        value: `23%`,
        trend: `▼`,
        trendDir: `down`,
        color: `#ffe94a`,
        icon: `💡`,
        sub: `of questions`
      }, {
        label: `AVG SPEED`,
        value: `12.4s`,
        trend: `▲`,
        trendDir: `up`,
        color: `#4aff91`,
        icon: `⏱`,
        sub: `per answer`
      }, {
        label: `MISCONCEPTIONS`,
        value: `3`,
        trend: `▼`,
        trendDir: `good`,
        color: `#ff8c1a`,
        icon: `🧠`,
        sub: `recurring`
      }, {
        label: `CONFIDENCE`,
        value: `76%`,
        trend: `▲`,
        trendDir: `up`,
        color: `#ff00cc`,
        icon: `💪`,
        sub: `trend upward`
      }, {
        label: `ESCALATIONS`,
        value: `2`,
        trend: `▼`,
        trendDir: `good`,
        color: `#ff3355`,
        icon: `⚠️`,
        sub: `this session`
      }].map((e, t) => <div className="border-4 border-black p-4 slide-up" style={{
        background: e.color + `15`,
        boxShadow: `6px 6px 0 #000`,
        animationDelay: `${t * .05}s`
      }} key={t}><div className="flex items-start justify-between mb-2"><div><p className="font-pixel mb-1" style={{
              fontSize: `7px`,
              color: `#aaa`
            }}>{e.label}</p><p className="font-body text-2xl font-bold" style={{
              color: e.color
            }}>{e.icon}{" "}{e.value}</p></div><span className={`font-pixel text-sm ${e.trendDir === `up` || e.trendDir === `good` ? `trend-up` : `trend-down`}`}>{e.trend}</span></div><p className="font-pixel" style={{
          fontSize: `7px`,
          color: `#555`
        }}>{e.sub}</p></div>)}</div><div className="flex items-end gap-4 w-full max-w-2xl px-4"><WizardSprite mood="thinking" size={.9} /><div className="flex-1"><DialogBox speaker="ANALYSIS" text="Overall performance is trending upward! Hint usage is decreasing which shows growing confidence. Keep monitoring misconception recurrence." /></div></div></div>;
};
