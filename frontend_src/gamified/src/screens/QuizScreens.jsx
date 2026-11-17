import * as React from 'react';
import { PixelButton } from '../components/PixelButton';
import { QuizEngine } from '../components/QuizEngine';
import { WizardSprite } from '../components/Sprites';
import { POSTTEST_QUESTIONS, PRETEST_QUESTIONS } from '../data/content';
export const PreTestScreen = ({
  studentId,
  onComplete,
  onUpdateRisk
}) => <QuizEngine title="📋 PRE-TEST" questions={PRETEST_QUESTIONS} studentId={studentId} onComplete={onComplete} timeLimitSec={30} onUpdateRisk={onUpdateRisk} />;
export const PostTestScreen = ({
  studentId,
  preScore,
  preTotal,
  onComplete,
  onUpdateRisk
}) => {
  let [a, o] = (0, React.useState)(!1),
    [s, c] = (0, React.useState)(0),
    [u, d] = (0, React.useState)(POSTTEST_QUESTIONS.length),
    f = (e, t) => {
      c(e), d(t), o(!0), onComplete(e, t);
    };
  if (!a) return <QuizEngine title="🏁 POST-TEST" questions={POSTTEST_QUESTIONS} studentId={studentId} onComplete={f} timeLimitSec={30} onUpdateRisk={onUpdateRisk} />;
  let p = preScore === null ? 0 : Math.round(preScore / preTotal * 100),
    m = Math.round(s / u * 100),
    h = m - p;
  return <div className="game-screen scanlines starfield" style={{
    background: `#1a0a2e`,
    display: `flex`,
    flexDirection: `column`,
    alignItems: `center`,
    justifyContent: `center`,
    padding: `80px 16px 40px`
  }}><h1 className="font-pixel text-center mb-6" style={{
      fontSize: `clamp(0.9rem,3vw,1.4rem)`,
      color: `#ffe94a`,
      textShadow: `3px 3px 0 #000`
    }}>📊 LEARNING GAIN</h1><div className="border-4 border-black p-6 w-full max-w-sm mb-6 slide-up" style={{
      background: `#3d1f6e`,
      borderColor: `#ffe94a`,
      boxShadow: `6px 6px 0 #000`
    }}><div className="grid grid-cols-3 gap-4 text-center mb-4"><div className="border-4 border-black p-3" style={{
          background: `#2a1050`,
          boxShadow: `4px 4px 0 #000`
        }}><p className="font-pixel text-xs mb-2" style={{
            color: `#00ffee`
          }}>PRE</p><p className="font-body text-2xl font-bold" style={{
            color: `#ff4fa3`
          }}>{p}%</p><p className="font-pixel text-xs mt-1" style={{
            color: `#aaa`
          }}>{preScore}/{preTotal}</p></div><div className="flex items-center justify-center"><span className="font-pixel text-xl" style={{
            color: h >= 0 ? `#4aff91` : `#ff3355`
          }}>{h >= 0 ? `▲` : `▼`}</span></div><div className="border-4 border-black p-3" style={{
          background: `#2a1050`,
          boxShadow: `4px 4px 0 #000`
        }}><p className="font-pixel text-xs mb-2" style={{
            color: `#00ffee`
          }}>POST</p><p className="font-body text-2xl font-bold" style={{
            color: `#4aff91`
          }}>{m}%</p><p className="font-pixel text-xs mt-1" style={{
            color: `#aaa`
          }}>{s}/{u}</p></div></div><div className="border-4 border-black p-3 text-center" style={{
        background: h >= 0 ? `#4aff9133` : `#ff335533`,
        borderColor: h >= 0 ? `#4aff91` : `#ff3355`,
        boxShadow: `4px 4px 0 #000`
      }}><p className="font-pixel text-xs" style={{
          color: h >= 0 ? `#4aff91` : `#ff3355`
        }}>{h >= 0 ? `🎉` : `📚`}{" LEARNING GAIN: "}{h >= 0 ? `+` : ``}{h}%</p></div></div><WizardSprite mood={h >= 0 ? `celebrate` : `thinking`} size={1.3} className="animate-float" /><div className="mt-6"><PixelButton onClick={() => {}} color="#ff00cc" size="lg" glow={!0}>▶ CLAIM REWARD</PixelButton></div></div>;
};
