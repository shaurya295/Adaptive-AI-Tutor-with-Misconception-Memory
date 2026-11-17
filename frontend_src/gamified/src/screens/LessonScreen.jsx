import * as React from 'react';
import { getHint, recordAttempt } from '../api/mock';
import { DialogBox } from '../components/Dialog';
import { PixelButton } from '../components/PixelButton';
import { QuestionTimer } from '../components/QuestionTimer';
import { WizardSprite } from '../components/Sprites';
import { LESSON_QUESTION, LESSON_SCRIPT } from '../data/content';
import { answerQuestion, finishSession, isMock, loadLesson, startSession } from '../api/client';
import { useHud } from '../api/hud';
export const LessonScreen = ({
  next,
  studentId,
  onWrongStreak,
  onUpdateRisk
}) => {
  // Real mode: the lesson the tutor picked (dialog + questions); mock mode: the reference's script and one question.
  const hud = useHud();
  const [lesson, setLesson] = React.useState(isMock ? { lesson_index: 1, lesson_total: 5, dialog: LESSON_SCRIPT, questions: LESSON_QUESTION } : null);
  const [qi, setQi] = React.useState(0);
  const [key, setKey] = React.useState(null);
  const [busy, setBusy] = React.useState(false);
  const [error, setError] = React.useState(null);
  const sessionRef = React.useRef(null);
  React.useEffect(() => {
    if (isMock) return;
    loadLesson().then(l => { setLesson(l); return startSession(`lesson`, l.concept); })
      .then(r => { if (r) sessionRef.current = r.session_id; }).catch(e => setError(e.message));
  }, []);
  const SCRIPT = lesson ? lesson.dialog : LESSON_SCRIPT;
  let [i, a] = (0, React.useState)(0),
    [o, s] = (0, React.useState)(null),
    [c, u] = (0, React.useState)(!1),
    d = (0, React.useRef)(0),
    f = (0, React.useRef)(0),
    p = (0, React.useRef)(0),
    m = (0, React.useRef)(0),
    [g, _] = (0, React.useState)(null),
    [v, b] = (0, React.useState)(!1),
    x = lesson ? lesson.questions[Math.min(qi, lesson.questions.length - 1)] : LESSON_QUESTION[0],
    K = key ?? x.correct,
    S = i >= SCRIPT.length - 1,
    C = e => {
      b(!0), getHint({
        student_id: studentId || `anonymous`,
        concept: x.concept,
        question: x.text,
        student_answer: e,
        correct_answer: x.correct
      }).then(e => _(e.hint_text)).finally(() => b(!1));
    };
  (0, React.useEffect)(() => {
    S && !o && (d.current = performance.now());
  }, [S, o]), (0, React.useEffect)(() => {
    let e = () => {
      document.hidden && S && !o && (p.current += 1, onUpdateRisk?.(p.current, m.current));
    };
    return document.addEventListener(`visibilitychange`, e), () => document.removeEventListener(`visibilitychange`, e);
  }, [S, o, onUpdateRisk]);
  const gradeLesson = (picked, ms) => {
    setBusy(true);
    answerQuestion(x, picked, ms, sessionRef.current).then(res => {
      setKey(res.correctAnswer);
      picked == null ? u(!0) : s(picked);
      res.correct ? (f.current = 0, onWrongStreak(0)) : (f.current += 1, onWrongStreak(f.current), _(res.feedback || null));
    }).catch(err => { picked == null ? u(!0) : s(picked); _(`⚠️ ${err.message}`); }).finally(() => setBusy(false));
  };
  const nextQuestion = () => {
    if (!isMock && lesson && qi + 1 < lesson.questions.length) {
      setQi(q => q + 1), s(null), u(!1), _(null), setKey(null), d.current = performance.now();
      return;
    }
    isMock || finishSession(sessionRef.current).catch(() => {});
    next();
  };
  let w = e => {
    if (o || c || busy) return;
    let i = Math.round(performance.now() - d.current),
      a = e === x.correct;
    i < 1500 && (m.current += 1, onUpdateRisk?.(p.current, m.current));
    if (!isMock) return gradeLesson(e, i);
    s(e), a ? (f.current = 0, onWrongStreak(0)) : (f.current += 1, onWrongStreak(f.current), C(e)), recordAttempt({
      student_id: studentId || `anonymous`,
      concept: x.concept,
      question_id: x.id,
      correct: a,
      time_taken_ms: i,
      hint_used: !1
    });
  };
  if (!lesson) return <div className="game-screen scanlines" style={{ background: `linear-gradient(to bottom, #2a1050, #3d1f6e)`, display: `flex`, alignItems: `center`, justifyContent: `center` }}><p className="font-pixel text-xs" style={{ color: `#00ffee` }}>{error ? `⚠ ${error}` : `LOADING LESSON...`}</p></div>;
  return <div className="game-screen scanlines" style={{
    background: `linear-gradient(to bottom, #2a1050, #3d1f6e)`,
    display: `flex`,
    flexDirection: `column`,
    position: `relative`
  }}><div className="absolute top-0 left-0 right-0 h-20" style={{
      background: `repeating-linear-gradient(0deg,transparent 0,transparent 15px,rgba(0,0,0,0.15) 15px,rgba(0,0,0,0.15) 16px), repeating-linear-gradient(90deg,transparent 0,transparent 31px,rgba(0,0,0,0.15) 31px,rgba(0,0,0,0.15) 32px)`,
      backgroundColor: `#5b3a8e`
    }} /><div className="flex-1 flex flex-col items-center justify-center pt-20 pb-6 px-4"><div className="w-full max-w-md mb-4"><div className="flex justify-between font-pixel text-xs mb-1" style={{
          color: `#00ffee`
        }}><span>LESSON {lesson.lesson_index}/{lesson.lesson_total}</span><span>XP: {isMock ? 120 : hud.xp}</span></div><div className="hp-bar-track w-full"><div className="hp-bar-fill" style={{
            "--fill": `${isMock ? 40 : Math.round(100 * qi / lesson.questions.length)}%`
          }} /></div></div><div className="flex items-end gap-4 w-full max-w-2xl mb-6"><div className="flex-shrink-0"><WizardSprite mood={i === SCRIPT.length - 1 ? `thinking` : `idle`} size={1.2} /></div><div className="flex-1"><DialogBox speaker="PIXEL — AI TUTOR" text={SCRIPT[Math.min(i, SCRIPT.length - 1)]} onNext={i < SCRIPT.length - 1 ? () => a(e => e + 1) : void 0} /></div></div>{S && <div className="w-full max-w-2xl"><QuestionTimer key={qi} timeLimitSec={30} paused={!!(o || c)} onTimeout={() => {
          if (!isMock) return gradeLesson(null, 3e4);
          u(!0), C(`(no answer — time ran out)`), recordAttempt({
            student_id: studentId || `anonymous`,
            concept: x.concept,
            question_id: x.id,
            correct: !1,
            time_taken_ms: 3e4,
            hint_used: !1
          });
        }} /><div className="border-4 border-black p-4 mb-4" style={{
          background: `#1a0a2e`
        }}><p className="font-pixel text-xs mb-4" style={{
            color: `#ffe94a`,
            textShadow: `2px 2px 0 #000`
          }}>{"❓ "}{x.text}</p><div className="grid grid-cols-2 gap-3">{x.options.map(e => {
              let t = `#5b3a8e`;
              return (o || c) && (e === K ? t = `#4aff91` : e === o && (t = `#ff3355`)), <PixelButton onClick={() => w(e)} color={t} size="md" className="w-full" disabled={!!(o || c)} key={e}>{e}</PixelButton>;
            })}</div></div>{(o || c) && <div className="flex items-center gap-4 mb-4 slide-up"><WizardSprite mood={o === K ? `celebrate` : `thinking`} size={.8} /><div className="flex-1 border-4 border-black bg-white p-3"><p className="font-body text-sm text-gray-900">{c ? `⏰ Time's up! The answer was: ${K}` : o === K ? `🎉 Correct! +${isMock ? 50 : 10} XP!` : `❌ Not quite! The correct answer is ${K}. Keep going!`}</p></div></div>}{(o && o !== K || c) && <div className="flex items-start gap-4 mb-4 slide-up"><div className="text-xl" aria-hidden={!0}>🤖</div><div className="flex-1 border-4 border-black p-3" style={{
            background: `#fff7d6`
          }}>{v ? <p className="font-body text-sm text-gray-700 italic">Pixel is thinking it through…</p> : <p className="font-body text-sm text-gray-900">{g}</p>}</div></div>}{(o || c) && <div className="flex justify-center mt-4"><PixelButton onClick={nextQuestion} color="#ff00cc" size="lg">NEXT ▶</PixelButton></div>}</div>}</div><div className="ground h-12" /></div>;
};
