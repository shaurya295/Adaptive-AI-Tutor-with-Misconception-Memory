import * as React from 'react';
import { initialScreen } from './screen-param';
import { Hud } from './components/Hud';
import { useHud } from './api/hud';
import { getMe, guestSignIn, isMock, signOut, updateMe } from './api/client';
import { Mascot } from './components/Mascot';
import { AvatarSelectScreen } from './screens/AvatarSelectScreen';
import { EvalMetricsScreen } from './screens/EvalMetricsScreen';
import { FreeQuestScreen } from './screens/FreeQuestScreen';
import { HowItWorksScreen } from './screens/HowItWorksScreen';
import { LandingScreen } from './screens/LandingScreen';
import { LeaderboardScreen } from './screens/LeaderboardScreen';
import { LessonScreen } from './screens/LessonScreen';
import { MainMenuScreen } from './screens/MainMenuScreen';
import { MisconceptionsScreen } from './screens/MisconceptionsScreen';
import { ProgressScreen } from './screens/ProgressScreen';
import { PostTestScreen, PreTestScreen } from './screens/QuizScreens';
import { RewardScreen } from './screens/RewardScreen';
import { SessionCompleteScreen } from './screens/SessionCompleteScreen';
import { SignInScreen } from './screens/SignInScreen';
import { SpacedReviewScreen } from './screens/SpacedReviewScreen';
import { SwitchStudentScreen } from './screens/SwitchStudentScreen';
import { WelcomeScreen } from './screens/WelcomeScreen';
export const SCREEN_FLOW = [`landing`, `signin`, `mainmenu`, `welcome`, `avatarselect`, `howitworks`, `pretest`, `lesson`, `posttest`, `progress`, `sessioncomplete`, `reward`];
export function App() {
  let [e, t] = (0, React.useState)(initialScreen(`landing`)),
    hud = useHud(),
    n = hud.coins,
    r = hud.xp_pct,
    [dueCount, setDueCount] = React.useState(isMock ? 2 : 0),
    [, i] = (0, React.useState)(`idle`),
    [a, o] = (0, React.useState)([]),
    [s, c] = (0, React.useState)(``),
    [u, d] = (0, React.useState)(``),
    [f, p] = (0, React.useState)(`wizard`),
    [m, h] = (0, React.useState)(null),
    [g, _] = (0, React.useState)(5),
    [v, y] = (0, React.useState)(0),
    [b, x] = (0, React.useState)(0),
    S = Math.min(100, v * 15 + b * 20),
    [C, w] = (0, React.useState)(0),
    ee = (0, React.useCallback)((e, t) => {
      y(e), x(t);
    }, []);
  (0, React.useEffect)(() => {
    if (!isMock) {
      // Real mode: whoever is signed in (from the Simple dashboard or an earlier game) goes straight to the menu.
      getMe().then(me => {
        if (!me) return;
        o(t => t.find(t => t.id === me.student_id) ? t : [...t, { id: me.student_id, name: me.display_name, avatarId: me.companion_id || `wizard` }]);
        c(me.student_id), d(me.display_name), me.companion_id && p(me.companion_id), setDueCount(me.due_count);
        t(initialScreen(`mainmenu`));
      }).catch(() => {});
      return;
    }
    let e = new URLSearchParams(window.location.search).get(`student_id`) || localStorage.getItem(`mentora_student_id`);
    if (!e) return;
    localStorage.setItem(`mentora_student_id`, e);
    let n = e.split(`@`)[0],
      r = {
        id: e,
        name: e,
        avatarId: `wizard`
      };
    o(t => t.find(t => t.id === e) ? t : [...t, r]), c(e), d(n), t(initialScreen(`mainmenu`));
  }, []);
  let E = () => {
      let n = SCREEN_FLOW.indexOf(e);
      n >= 0 && n < SCREEN_FLOW.length - 1 && t(SCREEN_FLOW[n + 1]);
    },
    D = e => t(e),
    te = ![`landing`, `signin`].includes(e),
    ne = e => {
      d(e);
      if (!isMock) {
        guestSignIn(e).then(res => {
          o(r => [...r.filter(x => x.id !== res.student_id), { id: res.student_id, name: e, avatarId: f }]);
          c(res.student_id);
          getMe();
        }).catch(() => {});
        return;
      }
      let t = `${e.toLowerCase().replace(/\s+/g, `-`)}-${Date.now()}`,
        n = {
          id: t,
          name: e,
          avatarId: f
        };
      o(r => {
        let i = r.find(t => t.name.toLowerCase() === e.toLowerCase());
        return i ? (c(i.id), r) : (c(t), [...r, n]);
      });
    },
    O = e => {
      isMock || updateMe({ companion_id: e }).catch(() => {});
      p(e), o(t => t.map(t => t.id === s ? {
        ...t,
        avatarId: e
      } : t));
    },
    ie = (e, t) => {
      h(e), _(t), E();
    },
    oe = (e, t) => {},
    k = a.find(e => e.id === s)?.name || u || `anonymous`;
  return <div style={{
    minHeight: `100vh`,
    background: `#1a0a2e`
  }}>{te && <Hud coins={n} level={hud.level} xp={r} goTo={D} playerName={u} />}<div style={{
      paddingTop: te ? 48 : 0
    }}>{e === `landing` && <LandingScreen next={E} />}{e === `signin` && <SignInScreen next={E} back={() => t(`landing`)} onSetName={ne} />}{e === `mainmenu` && <MainMenuScreen goTo={D} />}{e === `welcome` && <WelcomeScreen next={E} />}{e === `avatarselect` && <AvatarSelectScreen next={E} onSelect={O} />}{e === `howitworks` && <HowItWorksScreen next={E} />}{e === `pretest` && <PreTestScreen studentId={k} onComplete={ie} onUpdateRisk={ee} />}{e === `lesson` && <LessonScreen next={E} studentId={k} onWrongStreak={w} onUpdateRisk={ee} />}{e === `posttest` && <PostTestScreen studentId={k} preScore={m} preTotal={g} onComplete={oe} onUpdateRisk={ee} />}{e === `progress` && <ProgressScreen next={E} studentId={k} />}{e === `sessioncomplete` && <SessionCompleteScreen next={E} />}{e === `reward` && <RewardScreen goTo={D} />}{e === `freequest` && <FreeQuestScreen goTo={D} setRobotMood={i} />}{e === `leaderboard` && <LeaderboardScreen goTo={D} profiles={a} activeProfileId={s} />}{e === `evalmetrics` && <EvalMetricsScreen goTo={D} sessionRiskScore={S} />}{e === `misconceptions` && <MisconceptionsScreen goTo={D} studentId={k} />}{e === `spacedrepeat` && <SpacedReviewScreen goTo={D} studentId={k} />}{e === `switchstudent` && <SwitchStudentScreen goTo={D} profiles={isMock ? a : a.filter(x => x.id === s)} activeProfileId={s} onSwitch={e => {
        c(e);
        let t = a.find(t => t.id === e);
        t && d(t.name);
      }} onAddNew={() => isMock ? D(`signin`) : signOut().catch(() => {}).finally(() => D(`signin`))} />}</div><Mascot screen={e} wrongAnswerStreak={C} spacedRepDueCount={dueCount} newBestCurve={!1} /></div>;
}
// JSX treats lower-case tags as HTML elements, so the minified component names get capitalised aliases.
