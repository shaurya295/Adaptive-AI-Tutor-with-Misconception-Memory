import * as React from 'react';
import * as JSXRuntime from 'react/jsx-runtime';
import { getProfile } from '../api/client';
import { DialogBox } from '../components/Dialog';
import { WizardSprite } from '../components/Sprites';
import { masteryColor } from '../data/content';
export const SpacedReviewScreen = ({
  goTo,
  studentId
}) => {
  let [n, r] = (0, React.useState)(null),
    i = new Date();
  i.setHours(0, 0, 0, 0), (0, React.useEffect)(() => {
    let e = !1;
    return getProfile(studentId || `anonymous`).then(t => {
      if (e) return;
      let n = Object.entries(t.profile.concept_mastery).filter(([, e]) => !!e.next_review).map(([e, t]) => ({
        concept: e,
        masteryPct: Math.round((t.mastery || 0) * 100),
        nextReview: new Date(t.next_review + `T00:00:00`)
      })).sort((e, t) => e.nextReview.getTime() - t.nextReview.getTime());
      r(n);
    }), () => {
      e = !0;
    };
  }, [studentId]);
  let a = e => Math.ceil((e.getTime() - i.getTime()) / 864e5),
    o = (n ?? []).filter(e => a(e.nextReview) <= 0).length;
  return <div className="game-screen scanlines" style={{
    background: `linear-gradient(to bottom, #1a0a2e, #2a1050)`,
    display: `flex`,
    flexDirection: `column`,
    alignItems: `center`,
    paddingTop: 80,
    paddingBottom: 40,
    overflowY: `auto`
  }}><div className="flex items-center gap-4 mb-6 w-full max-w-lg px-4"><button onClick={() => goTo(`mainmenu`)} className="font-pixel text-xs" style={{
        color: `#ff4fa3`,
        background: `none`,
        border: `none`,
        cursor: `pointer`
      }}>◀ BACK</button><h1 className="font-pixel" style={{
        fontSize: `clamp(0.8rem,2.5vw,1.1rem)`,
        color: `#ffe94a`,
        textShadow: `3px 3px 0 #000`
      }}>📅 REVIEW QUEUE</h1></div><p className="font-pixel text-xs mb-6 w-full max-w-lg px-4" style={{
      color: `#00ffee`
    }}>MASTERY-BASED REVIEW SCHEDULE (1 / 3 / 7 DAYS)</p>{n === null ? <p className="font-pixel text-xs" style={{
      color: `#aaa`
    }}>Loading…</p> : n.length === 0 ? <div className="w-full max-w-lg px-4 flex items-end gap-4"><WizardSprite mood="idle" size={.9} /><div className="flex-1"><DialogBox speaker="PIXEL — SCHEDULER" text="Nothing scheduled yet — chat with me in the Simple dashboard or answer a graded question here to start building your review queue!" /></div></div> : <JSXRuntime.Fragment><div className="w-full max-w-lg px-4 flex flex-col gap-3">{n.map((e, t) => {
          let n = a(e.nextReview),
            r = n <= 0,
            i = masteryColor(e.masteryPct);
          return <div className="border-4 border-black p-3 flex items-center justify-between slide-up" style={{
            background: r ? `#ff335522` : `#3d1f6e`,
            borderColor: r ? `#ff3355` : `#5b3a8e`,
            boxShadow: r ? `4px 4px 0 #000, 0 0 12px #ff335544` : `4px 4px 0 #000`,
            animationDelay: `${t * .06}s`
          }} key={e.concept}><div className="flex-1"><p className="font-pixel text-xs" style={{
                color: r ? `#ff3355` : `#f0e8ff`
              }}>{r && <span style={{
                  animation: `blink 0.5s step-end infinite`
                }}>{"⚠️ "}</span>}{e.concept}</p><div className="flex items-center gap-2 mt-1"><span className="font-pixel" style={{
                  fontSize: `7px`,
                  color: `#aaa`
                }}>{"Mastery: "}{e.masteryPct}%</span></div></div><div className="text-right">{r ? <span className="font-pixel text-xs" style={{
                color: `#ff3355`,
                animation: `blink 1s step-end infinite`
              }}>REVIEW NOW</span> : <span className="font-pixel" style={{
                fontSize: `7px`,
                color: `#00ffee`
              }}>{"in "}{n}d</span>}<div className="hp-bar-track mt-1" style={{
                width: 80,
                height: 6
              }}><div style={{
                  width: `${e.masteryPct}%`,
                  height: `100%`,
                  background: i
                }} /></div></div></div>;
        })}</div><div className="flex items-end gap-4 w-full max-w-lg px-4 mt-6"><WizardSprite mood="pointing" size={.9} /><div className="flex-1"><DialogBox speaker="PIXEL — SCHEDULER" text={`${o} item(s) due today! Higher mastery earns a longer interval before the next review — miss it and it resets to 1 day.`} /></div></div></JSXRuntime.Fragment>}</div>;
};
