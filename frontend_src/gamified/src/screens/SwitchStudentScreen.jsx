import { PixelButton } from '../components/PixelButton';
import { WizardSprite } from '../components/Sprites';
import { COMPANIONS } from '../data/content';
export const SwitchStudentScreen = ({
  goTo,
  profiles,
  activeProfileId,
  onSwitch,
  onAddNew
}) => <div className="game-screen scanlines" style={{
  background: `linear-gradient(to bottom, #2a1050, #3d1f6e)`,
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
      fontSize: `clamp(0.8rem,2.5vw,1.2rem)`,
      color: `#ffe94a`,
      textShadow: `3px 3px 0 #000`
    }}>👥 SWITCH STUDENT</h1></div><div className="w-full max-w-lg px-4 flex flex-col gap-4">{profiles.length === 0 ? <div className="border-4 border-black p-8 text-center" style={{
      background: `#1a0a2e`,
      boxShadow: `6px 6px 0 #000`
    }}><WizardSprite mood="thinking" size={.9} className="mx-auto mb-4" /><p className="font-pixel text-xs" style={{
        color: `#aaa`,
        lineHeight: 2
      }}>NO PROFILES YET!<br />CREATE ONE BELOW.</p></div> : profiles.map(t => {
      let i = COMPANIONS.find(e => e.id === t.avatarId),
        a = t.id === activeProfileId;
      return <button onClick={() => {
        onSwitch(t.id), goTo(`mainmenu`);
      }} className="pixel-btn border-4 border-black p-4 flex items-center gap-4 text-left w-full" style={{
        background: a ? `#ff00cc33` : `#3d1f6e`,
        boxShadow: a ? `0 0 0 #000, 0 0 16px #ff00cc44` : `5px 5px 0 #000`,
        transform: a ? `translate(5px,5px)` : `translate(0,0)`,
        borderColor: a ? `#ff00cc` : `#000`
      }} key={t.id}><span className="text-4xl">{i?.emoji || `🧙`}</span><div className="flex-1"><p className="font-pixel text-xs" style={{
            color: a ? `#ffe94a` : `#f0e8ff`
          }}>{t.name}</p><p className="font-pixel mt-1" style={{
            fontSize: `7px`,
            color: `#aaa`
          }}>{i?.name || `WIZARD`}{" CLASS"}</p></div>{a && <span className="font-pixel text-xs" style={{
          color: `#ff00cc`,
          animation: `blink 1s step-end infinite`
        }}>ACTIVE</span>}</button>;
    })}<PixelButton onClick={onAddNew} color="#4aff91" textColor="#000" size="lg" className="w-full">➕ ADD NEW PLAYER</PixelButton></div></div>;
