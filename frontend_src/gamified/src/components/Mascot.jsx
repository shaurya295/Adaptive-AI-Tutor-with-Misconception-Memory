import * as React from 'react';
import * as JSXRuntime from 'react/jsx-runtime';
import { RobotSprite } from './Sprites';
export const MASCOT_SPOTS = [{
  bottom: 24,
  right: 24,
  left: void 0
}, {
  bottom: 24,
  right: 280,
  left: void 0
}, {
  bottom: 200,
  right: 24,
  left: void 0
}, {
  bottom: 200,
  right: 280,
  left: void 0
}, {
  bottom: 80,
  right: 140,
  left: void 0
}];
export const Mascot = ({
  screen,
  wrongAnswerStreak = 0,
  spacedRepDueCount = 0,
  newBestCurve = !1
}) => {
  let [i, a] = (0, React.useState)(`idle`),
    [o, s] = (0, React.useState)(``),
    [c, u] = (0, React.useState)(!1),
    [d, f] = (0, React.useState)({
      bottom: 24,
      right: 24
    }),
    [p, m] = (0, React.useState)(!1),
    [h, g] = (0, React.useState)(!1),
    _ = (0, React.useRef)({
      mx: 0,
      my: 0,
      rb: 0,
      rr: 0
    }),
    v = (0, React.useRef)(0),
    y = (0, React.useRef)(null),
    b = {
      landing: {
        mood: `pointing`,
        msg: `▶ Press START to begin your quest!`
      },
      signin: {
        mood: `idle`,
        msg: `What's your hero name? 🎮`
      },
      mainmenu: {
        mood: `pointing`,
        msg: `Pick a mode from the menu!`
      },
      freequest: {
        mood: `pointing`,
        msg: `Try asking me something!`
      },
      lesson: {
        mood: `idle`,
        msg: `Read carefully and answer!`
      },
      reward: {
        mood: `celebrating`,
        msg: `New high score, nice! 🏆`
      },
      sessioncomplete: {
        mood: `celebrating`,
        msg: `Session done! Claim your reward!`
      },
      leaderboard: {
        mood: `idle`,
        msg: `Top scholars of the realm! ⭐`
      },
      pretest: {
        mood: `thinking`,
        msg: `Let's see what you already know!`
      },
      posttest: {
        mood: `thinking`,
        msg: `Show me what you've learned!`
      },
      evalmetrics: {
        mood: `idle`,
        msg: `Your stats are looking great! 📊`
      },
      misconceptions: {
        mood: `pointing`,
        msg: `Click a concept node to learn more!`
      },
      spacedrepeat: {
        mood: `pointing`,
        msg: `Don't forget your review items!`
      },
      progress: {
        mood: `idle`,
        msg: `Track your learning journey! 📈`
      },
      switchstudent: {
        mood: `idle`,
        msg: `Switch between player profiles!`
      }
    };
  (0, React.useEffect)(() => {
    let t = b[screen];
    if (t) {
      a(t.mood), s(t.msg), u(!0);
      let e = setTimeout(() => u(!1), 5e3);
      return () => clearTimeout(e);
    }
  }, [screen]), (0, React.useEffect)(() => {
    if (wrongAnswerStreak >= 2) {
      a(`pointing`), s(`Struggling? Try reading slowly! 💡 Use a hint!`), u(!0);
      let e = setTimeout(() => u(!1), 6e3);
      return () => clearTimeout(e);
    }
  }, [wrongAnswerStreak]), (0, React.useEffect)(() => {
    if (spacedRepDueCount > 0) {
      a(`pointing`), s(`${spacedRepDueCount} review item${spacedRepDueCount > 1 ? `s` : ``} due today! ⏰`), u(!0);
      let e = setTimeout(() => u(!1), 5e3);
      return () => clearTimeout(e);
    }
  }, [spacedRepDueCount]), (0, React.useEffect)(() => {
    if (newBestCurve) {
      a(`celebrating`), s(`New personal best on your learning curve! 🌟`), u(!0);
      let e = setTimeout(() => u(!1), 5e3);
      return () => clearTimeout(e);
    }
  }, [newBestCurve]), (0, React.useEffect)(() => {
    let e = () => {
        let t = 15e3 + Math.random() * 1e4;
        return setTimeout(() => {
          if (Date.now() - v.current > 5e3 && !p) {
            let e = MASCOT_SPOTS[Math.floor(Math.random() * MASCOT_SPOTS.length)];
            g(!0), f({
              bottom: e.bottom,
              right: e.right
            }), setTimeout(() => g(!1), 1500);
          }
          return e();
        }, t);
      },
      t = e();
    return () => clearTimeout(t);
  }, [p]);
  let x = e => {
    m(!0), v.current = Date.now(), _.current = {
      mx: e.clientX,
      my: e.clientY,
      rb: d.bottom,
      rr: d.right
    }, e.preventDefault();
  };
  (0, React.useEffect)(() => {
    if (!p) return;
    let e = e => {
        v.current = Date.now(), f({
          bottom: Math.max(0, _.current.rb - (e.clientY - _.current.my)),
          right: Math.max(0, _.current.rr - (e.clientX - _.current.mx))
        });
      },
      t = () => {
        m(!1), v.current = Date.now();
      };
    return window.addEventListener(`mousemove`, e), window.addEventListener(`mouseup`, t), () => {
      window.removeEventListener(`mousemove`, e), window.removeEventListener(`mouseup`, t);
    };
  }, [p]);
  let S = i === `idle` ? `animate-float` : i === `celebrating` ? `animate-bounce2` : ``;
  return <div ref={y} className="fixed z-[9999] select-none" style={{
    bottom: d.bottom,
    right: d.right,
    cursor: p ? `grabbing` : `grab`,
    transition: h ? `bottom 1.5s ease-in-out, right 1.5s ease-in-out` : `none`
  }} onMouseDown={x} onClick={() => u(e => !e)}>{c && o && <div className="absolute bottom-full right-0 mb-2 w-52"><div className="bg-white border-3 border-black p-2 text-xs font-body text-gray-900 leading-relaxed relative" style={{
        border: `3px solid #000`,
        boxShadow: `3px 3px 0 #000`
      }}>{o}<div className="absolute -bottom-2 right-6 w-0 h-0" style={{
          borderLeft: `6px solid transparent`,
          borderRight: `6px solid transparent`,
          borderTop: `8px solid #000`
        }} /><div className="absolute -bottom-1 right-7 w-0 h-0" style={{
          borderLeft: `5px solid transparent`,
          borderRight: `5px solid transparent`,
          borderTop: `7px solid #fff`
        }} /></div></div>}{i === `thinking` && <div className="absolute -top-8 left-1/2 -translate-x-1/2 text-2xl" style={{
      animation: `wiggle 0.4s linear infinite`
    }}>⚙️</div>}{i === `celebrating` && <JSXRuntime.Fragment>{[`✨`, `⭐`, `💫`].map((e, t) => <div className="absolute text-lg" style={{
        top: -20 - t * 10,
        left: t * 14 - 10,
        animation: `confetti ${.8 + t * .3}s ease-out ${t * .1}s infinite`
      }} key={t}>{e}</div>)}</JSXRuntime.Fragment>}<div className={`${S} ${h ? `mascot-walking` : ``}`} style={{
      filter: `drop-shadow(3px 3px 0 #000)`
    }}><RobotSprite mood={i} /></div><p className="text-center font-pixel mt-1" style={{
      fontSize: `6px`,
      color: `#00ffee`
    }}>TAP ME</p></div>;
};
