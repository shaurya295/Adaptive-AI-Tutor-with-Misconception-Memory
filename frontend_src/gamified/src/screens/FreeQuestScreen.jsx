import * as React from 'react';
import { PixelButton } from '../components/PixelButton';
import { WizardSprite } from '../components/Sprites';
import { QUEST_CATEGORIES } from '../data/content';
export const FreeQuestScreen = ({
  goTo,
  setRobotMood
}) => {
  let [n, r] = (0, React.useState)(``),
    [i, a] = (0, React.useState)(``),
    [o, s] = (0, React.useState)(!1),
    [c, u] = (0, React.useState)(null),
    [d, f] = (0, React.useState)([]),
    p = (0, React.useRef)(null),
    m = (0, React.useCallback)(e => {
      s(!0), setRobotMood(`thinking`), a(``);
      let n = {
          default: `Great question, hero! "${e}" — Here's what I know: This topic connects to many areas of learning. In essence, understanding the fundamentals will help you level up in this quest. Keep asking great questions and your knowledge XP will grow!`,
          math: `Excellent math quest! For "${e}": Start by identifying what you know, then set up your equation. Work step by step, and always double-check your answer. Math is like unlocking a puzzle — each step reveals the next!`,
          science: `Science quest activated! For "${e}": Science begins with observation. Form a hypothesis, test it, and analyze results. The universe is full of wonders waiting for you to discover!`,
          history: `History scroll opened! For "${e}": History teaches us patterns. Great civilizations rose by cooperation and fell by division. Understanding the past arms you for the future!`
        },
        r = n[c?.toLowerCase() || `default`] ?? n.default,
        i = 0,
        o = setInterval(() => {
          i < r.length ? a(r.slice(0, ++i)) : (clearInterval(o), s(!1), setRobotMood(`celebrating`), f(t => [...t, {
            q: e,
            a: r
          }]), setTimeout(() => setRobotMood(`idle`), 3e3));
        }, 25);
    }, [c, setRobotMood]),
    h = () => {
      n.trim() && (m(n.trim()), r(``));
    };
  return <div className="game-screen scanlines" style={{
    background: `linear-gradient(to bottom, #1a0a2e, #2a1050)`,
    display: `flex`,
    flexDirection: `column`,
    alignItems: `center`,
    paddingTop: 80,
    paddingBottom: 40,
    overflowY: `auto`
  }}><div className="flex items-center gap-4 mb-6"><button onClick={() => goTo(`mainmenu`)} className="font-pixel text-xs" style={{
        color: `#ff4fa3`,
        background: `none`,
        border: `none`,
        cursor: `pointer`
      }}>◀ BACK</button><h1 className="font-pixel text-center" style={{
        fontSize: `clamp(0.9rem,3vw,1.4rem)`,
        color: `#ffe94a`,
        textShadow: `3px 3px 0 #000`
      }}>✨ FREE QUEST</h1></div><div className="w-full max-w-2xl px-4 flex flex-col gap-5"><div><p className="font-pixel text-xs mb-3" style={{
          color: `#00ffee`
        }}>SELECT QUEST TYPE:</p><div className="flex flex-wrap gap-2">{QUEST_CATEGORIES.map(e => <button onClick={() => u(c === e.label ? null : e.label)} className="pixel-btn font-pixel text-xs border-2 border-black px-3 py-1" style={{
            background: c === e.label ? e.color : `#3d1f6e`,
            color: c === e.label ? `#000` : `#fff`,
            boxShadow: c === e.label ? `0 0 0 #000` : `3px 3px 0 #000`,
            transform: c === e.label ? `translate(3px,3px)` : `none`
          }} key={e.label}>{e.label}</button>)}</div></div><div className="border-4 border-black" style={{
        background: `linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)`,
        boxShadow: `6px 6px 0 #000`
      }}><div className="flex items-center gap-2 px-3 py-2 border-b-2 border-black" style={{
          background: `#0f0f1a`
        }}><div className="w-3 h-3 rounded-full" style={{
            background: `#ff3355`,
            border: `2px solid #000`
          }} /><div className="w-3 h-3 rounded-full" style={{
            background: `#ffe94a`,
            border: `2px solid #000`
          }} /><div className="w-3 h-3 rounded-full" style={{
            background: `#4aff91`,
            border: `2px solid #000`
          }} /><span className="font-pixel text-xs ml-2" style={{
            color: `#00ffee`
          }}>QUEST_INPUT.exe</span></div><div className="p-4"><p className="font-pixel text-xs mb-2" style={{
            color: `#4aff91`
          }}>{"> TYPE YOUR QUEST:"}</p><div className="relative"><textarea ref={p} value={n} onChange={e => r(e.target.value)} onKeyDown={e => {
              e.key === `Enter` && !e.shiftKey && (e.preventDefault(), h());
            }} rows={3} placeholder="e.g. Why is the sky blue? What is algebra? Explain DNA..." className="w-full bg-transparent font-body text-sm p-2 outline-none resize-none" style={{
              border: `2px solid #00ffee`,
              color: `#f0e8ff`,
              caretColor: `#00ffee`,
              boxShadow: `0 0 8px #00ffee44`
            }} /><span className="absolute bottom-3 right-3 text-xs" style={{
              color: `#00ffee`,
              animation: `blink 1s step-end infinite`
            }}>▌</span></div><div className="flex justify-between items-center mt-3"><span className="font-pixel text-xs" style={{
              color: `#555`
            }}>ENTER to cast • SHIFT+ENTER for newline</span><PixelButton onClick={h} color={o ? `#555` : `#ff00cc`} size="sm" glow={!o}>{o ? `⏳ CASTING...` : `🔮 CAST SPELL`}</PixelButton></div></div></div>{(i || o) && <div className="flex items-start gap-4"><div className="flex-shrink-0"><WizardSprite mood={o ? `thinking` : `idle`} size={1} />{o && <div className="text-center mt-1" style={{
            animation: `wiggle 0.4s linear infinite`,
            fontSize: 20
          }}>⚙️</div>}</div><div className="flex-1"><div className="bg-white border-4 border-black p-4" style={{
            boxShadow: `6px 6px 0 #000`
          }}><p className="font-pixel text-xs mb-2 pb-1" style={{
              color: `#5b3a8e`,
              borderBottom: `2px solid #eee`
            }}>PIXEL — AI TUTOR</p><p className="font-body text-sm text-gray-900 leading-relaxed">{i}{o && <span style={{
                animation: `blink 1s step-end infinite`
              }}>▌</span>}</p></div></div></div>}{d.length > 0 && <div><p className="font-pixel text-xs mb-3" style={{
          color: `#ff4fa3`
        }}>⚔ QUEST LOG:</p><div className="flex flex-col gap-2 max-h-40 overflow-y-auto">{d.slice(-3).reverse().map((e, t) => <div className="border-2 border-black p-2 cursor-pointer" style={{
            background: `#3d1f6e`,
            boxShadow: `2px 2px 0 #000`
          }} onClick={() => a(e.a)} key={t}><p className="font-pixel text-xs" style={{
              color: `#00ffee`
            }}>{"▶ "}{e.q}</p></div>)}</div></div>}</div></div>;
};
