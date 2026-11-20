import { PixelButton } from '../components/PixelButton';
import { WizardSprite } from '../components/Sprites';
import { useHud } from '../api/hud';
import { isMock } from '../api/client';

// Mock mode shows the reference's badge. Real mode shows the latest badge earned, or what earns one.
function useReward() {
  const hud = useHud();
  if (isMock) return { heading: `YOU EARNED A NEW BADGE!`, badge: `FRACTIONS MASTER`, detail: `Completed: Fractions` };
  const latest = hud.badges && hud.badges[hud.badges.length - 1];
  if (latest) return { heading: `YOU EARNED A NEW BADGE!`, badge: latest, detail: `Completed: ${latest.replace(/ MASTER$/, ``).toLowerCase().replace(/(^|\s)\S/g, c => c.toUpperCase())}` };
  return { heading: `NEXT BADGE`, badge: `TOPIC MASTER`, detail: `Reach 70% mastery in any topic` };
}

export const RewardScreen = ({
  goTo
}) => {
  const reward = useReward();
  return <div className="game-screen scanlines" style={{
  background: `linear-gradient(to bottom, #2a1050, #5b3a8e)`,
  display: `flex`,
  flexDirection: `column`,
  alignItems: `center`,
  justifyContent: `center`,
  position: `relative`,
  overflow: `hidden`
}}>{Array.from({
    length: 24
  }).map((e, t) => <div className="absolute w-3 h-3" style={{
    top: `40%`,
    left: `${10 + t * 3.3 % 80}%`,
    background: [`#ff00cc`, `#00ffee`, `#ffe94a`, `#4aff91`, `#ff3355`, `#ff8c1a`][t % 6],
    animation: `confetti ${1 + t % 3 * .3}s ease-out ${t % 5 * .15}s infinite`,
    transform: `rotate(${t * 15}deg)`
  }} key={t} />)}<div className="relative z-10 flex flex-col items-center gap-4 text-center px-4"><div className="text-8xl" style={{
      animation: `bounce2 0.8s ease-in-out infinite`
    }}>🏆</div><h1 className="font-pixel" style={{
      fontSize: `clamp(1.2rem,4vw,2.2rem)`,
      color: `#ffe94a`,
      textShadow: `4px 4px 0 #000`,
      lineHeight: 1.6
    }}>GREAT JOB!</h1><p className="font-pixel text-xs" style={{
      color: `#00ffee`,
      textShadow: `2px 2px 0 #000`
    }}>{reward.heading}</p><div className="border-4 border-black p-6 flex flex-col items-center gap-3" style={{
      background: `#3d1f6e`,
      borderColor: `#ffe94a`,
      boxShadow: `6px 6px 0 #000`
    }}><div className="w-20 h-20 rounded-full flex items-center justify-center text-5xl border-4 border-black" style={{
        background: `radial-gradient(circle, #ffe94a, #ff8c1a)`,
        animation: `float 3s ease-in-out infinite`
      }}>🌟</div><p className="font-pixel text-xs" style={{
        color: `#ffe94a`
      }}>{reward.badge}</p><p className="font-body text-xs" style={{
        color: `#aaa`
      }}>{reward.detail}</p></div><WizardSprite mood="celebrate" size={1.5} className="animate-wiggle" /><div className="flex gap-4 flex-wrap justify-center mt-2"><PixelButton onClick={() => goTo(`mainmenu`)} color="#ff00cc" size="md">🏠 MENU</PixelButton><PixelButton onClick={() => goTo(`pretest`)} color="#4aff91" textColor="#000" size="md">▶ NEXT LESSON</PixelButton><PixelButton onClick={() => goTo(`leaderboard`)} color="#ffe94a" textColor="#000" size="md">🏆 LEADERBOARD</PixelButton></div></div></div>;
};
