import * as React from 'react';
import { getHint, recordAttempt } from '../api/mock';
import { DialogBox } from './Dialog';
import { PixelButton } from './PixelButton';
import { QuestionTimer } from './QuestionTimer';
import { WizardSprite } from './Sprites';
export const QuizEngine = ({
  title,
  questions,
  studentId,
  onComplete,
  timeLimitSec = 30,
  onUpdateRisk
}) => {
  let [o, s] = (0, React.useState)(0),
    [c, u] = (0, React.useState)(null),
    [d, f] = (0, React.useState)(0),
    [p, m] = (0, React.useState)(!1),
    [g, _] = (0, React.useState)(!1),
    v = (0, React.useRef)(performance.now()),
    b = (0, React.useRef)(0),
    x = (0, React.useRef)(0),
    [S, C] = (0, React.useState)(null),
    [w, ee] = (0, React.useState)(!1),
    E = questions[o];
  (0, React.useEffect)(() => {
    u(null), m(!1), C(null), ee(!1), v.current = performance.now();
  }, [o]);
  let te = e => {
    ee(!0), getHint({
      student_id: studentId || `anonymous`,
      concept: E.concept,
      question: E.text,
      student_answer: e,
      correct_answer: E.correct
    }).then(e => C(e.hint_text)).finally(() => ee(!1));
  };
  (0, React.useEffect)(() => {
    let e = () => {
      document.hidden && !c && (b.current += 1, onUpdateRisk?.(b.current, x.current));
    };
    return document.addEventListener(`visibilitychange`, e), () => document.removeEventListener(`visibilitychange`, e);
  }, [c, onUpdateRisk]);
  let ne = e => {
    if (c || p) return;
    let t = Math.round(performance.now() - v.current),
      r = e === E.correct;
    t < 1500 && (x.current += 1, onUpdateRisk?.(b.current, x.current)), u(e), r ? f(e => e + 1) : te(e), recordAttempt({
      student_id: studentId || `anonymous`,
      concept: E.concept,
      question_id: E.id,
      correct: r,
      time_taken_ms: t,
      hint_used: !1
    });
  };
  return g ? null : <div className="game-screen scanlines" style={{
    background: `linear-gradient(to bottom, #2a1050, #3d1f6e)`,
    display: `flex`,
    flexDirection: `column`,
    alignItems: `center`,
    paddingTop: 80,
    paddingBottom: 40,
    overflowY: `auto`
  }}><div className="w-full max-w-2xl px-4"><div className="flex justify-between items-center mb-4"><h1 className="font-pixel text-xs" style={{
          color: `#ffe94a`,
          textShadow: `2px 2px 0 #000`
        }}>{title}</h1><span className="font-pixel text-xs" style={{
          color: `#00ffee`
        }}>{"Q "}{o + 1}/{questions.length}</span></div><div className="hp-bar-track w-full mb-4" style={{
        height: 12
      }}><div className="hp-bar-fill" style={{
          "--fill": `${o / questions.length * 100}%`
        }} /></div><QuestionTimer timeLimitSec={timeLimitSec} paused={!!(c || p)} onTimeout={() => {
        m(!0), te(`(no answer — time ran out)`), recordAttempt({
          student_id: studentId || `anonymous`,
          concept: E.concept,
          question_id: E.id,
          correct: !1,
          time_taken_ms: timeLimitSec * 1e3,
          hint_used: !1
        });
      }} /><div className="flex items-end gap-4 mb-6"><div className="flex-shrink-0"><WizardSprite mood={p ? `thinking` : c ? c === E.correct ? `celebrate` : `thinking` : `idle`} size={1.1} /></div><div className="flex-1"><DialogBox speaker="PIXEL — AI TUTOR" text={E.text} /></div></div><div className="grid grid-cols-2 gap-3 mb-4">{E.options.map(e => {
          let t = `#5b3a8e`;
          return (c || p) && (e === E.correct ? t = `#4aff91` : e === c && (t = `#ff3355`)), <PixelButton onClick={() => ne(e)} color={t} size="md" className="w-full" disabled={!!(c || p)} key={e}>{e}</PixelButton>;
        })}</div>{(c || p) && <div className="flex items-center gap-3 mb-4 slide-up"><WizardSprite mood={c === E.correct ? `celebrate` : `thinking`} size={.7} /><div className="flex-1 border-4 border-black bg-white p-3" style={{
          boxShadow: `4px 4px 0 #000`
        }}><p className="font-body text-sm text-gray-900">{p ? `⏰ Time's up! The answer was: ${E.correct}` : c === E.correct ? `🎉 Correct! +1 point!` : `❌ Not quite! Answer: ${E.correct}`}</p></div></div>}{c && c !== E.correct || p ? <div className="flex items-start gap-3 mb-4 slide-up"><div className="text-xl" aria-hidden={!0}>🤖</div><div className="flex-1 border-4 border-black p-3" style={{
          background: `#fff7d6`,
          boxShadow: `4px 4px 0 #000`
        }}>{w ? <p className="font-body text-sm text-gray-700 italic">Pixel is thinking it through…</p> : <p className="font-body text-sm text-gray-900">{S}</p>}</div></div> : null}{(c || p) && <div className="flex justify-center"><PixelButton onClick={() => {
          o + 1 >= questions.length ? (_(!0), onComplete(d + +(c === E.correct), questions.length)) : s(e => e + 1);
        }} color="#ff00cc" size="lg">{o + 1 >= questions.length ? `FINISH ▶` : `NEXT ▶`}</PixelButton></div>}</div></div>;
};
