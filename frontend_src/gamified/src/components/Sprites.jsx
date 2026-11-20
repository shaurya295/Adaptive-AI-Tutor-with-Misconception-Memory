import * as JSXRuntime from 'react/jsx-runtime';
export const WizardSprite = ({
  mood = `idle`,
  size = 1,
  className = ``
}) => {
  let r = mood === `celebrate` ? `#ffe94a` : mood === `thinking` ? `#00ffee` : `#ff4fa3`;
  return <svg width={64 * size} height={80 * size} viewBox="0 0 64 80" className={className} style={{
    imageRendering: `pixelated`
  }}><rect x="20" y="0" width="24" height="4" fill="#ff00cc" /><rect x="24" y="4" width="16" height="4" fill="#ff00cc" /><rect x="24" y="8" width="16" height="4" fill="#ff00cc" /><rect x="24" y="12" width="16" height="4" fill="#ff00cc" /><rect x="16" y="16" width="32" height="4" fill="#ff00cc" /><rect x="30" y="4" width="4" height="4" fill="#ffe94a" /><rect x="16" y="20" width="32" height="24" fill="#ffd9aa" /><rect x="22" y="26" width="6" height="6" fill="#1a0a2e" /><rect x="36" y="26" width="6" height="6" fill="#1a0a2e" /><rect x="24" y="27" width="2" height="2" fill="#fff" /><rect x="38" y="27" width="2" height="2" fill="#fff" />{mood === `celebrate` ? <JSXRuntime.Fragment><rect x="24" y="36" width="16" height="4" fill="#ff3355" /><rect x="26" y="34" width="2" height="2" fill="#fff" /><rect x="36" y="34" width="2" height="2" fill="#fff" /></JSXRuntime.Fragment> : <rect x="26" y="36" width="12" height="3" fill="#c07040" />}<rect x="12" y="44" width="40" height="24" fill="#5b3a8e" /><rect x="12" y="44" width="40" height="4" fill="#ff00cc" /><rect x="28" y="52" width="8" height="12" fill="#ff00cc" /><rect x="0" y="44" width="12" height="8" fill="#5b3a8e" /><rect x="52" y="44" width="12" height="8" fill="#5b3a8e" /><rect x="0" y="52" width="10" height="8" fill="#ffd9aa" /><rect x="54" y="52" width="10" height="8" fill="#ffd9aa" /><rect x="56" y="40" width="4" height="20" fill="#c8a050" /><rect x="54" y="36" width="8" height="8" fill={r} style={{
      animation: `startwink 1.5s ease-in-out infinite`
    }} /><rect x="16" y="68" width="12" height="12" fill="#3d1f6e" /><rect x="36" y="68" width="12" height="12" fill="#3d1f6e" /><rect x="14" y="76" width="14" height="4" fill="#000" /><rect x="36" y="76" width="14" height="4" fill="#000" /></svg>;
};
export const RobotSprite = ({
  mood
}) => {
  let t = mood === `celebrating` ? `#ffe94a` : mood === `thinking` ? `#00ffee` : mood === `pointing` ? `#ff4fa3` : `#00ffee`;
  return <svg width="56" height="72" viewBox="0 0 56 72" style={{
    imageRendering: `pixelated`
  }}><rect x="26" y="0" width="4" height="8" fill="#aaa" /><rect x="22" y="0" width="12" height="4" fill="#888" /><rect x="24" y="-4" width="8" height="6" fill={t} style={{
      animation: `blink 2s step-end infinite`
    }} /><rect x="8" y="8" width="40" height="28" fill="#4a4a6a" /><rect x="8" y="8" width="40" height="4" fill="#333" /><rect x="8" y="32" width="40" height="4" fill="#333" /><rect x="12" y="14" width="32" height="14" fill="#1a1a2e" /><rect x="14" y="16" width="12" height="10" fill={t} style={{
      opacity: .9
    }} /><rect x="30" y="16" width="12" height="10" fill={t} style={{
      opacity: .9
    }} /><rect x="15" y="17" width="4" height="4" fill="#fff" style={{
      opacity: .6
    }} /><rect x="31" y="17" width="4" height="4" fill="#fff" style={{
      opacity: .6
    }} /><rect x="16" y="28" width="24" height="6" fill="#333" />{mood === `celebrating` ? [0, 4, 8, 12, 16, 20].map(e => <rect x={16 + e} y={30} width="3" height="3" fill={e % 2 == 0 ? `#ffe94a` : `#ff00cc`} key={e} />) : [0, 6, 12, 18].map(e => <rect x={18 + e} y={30} width="3" height="3" fill="#555" key={e} />)}<rect x="10" y="36" width="36" height="24" fill="#3a3a5a" /><rect x="10" y="36" width="36" height="4" fill="#555" /><rect x="16" y="42" width="24" height="12" fill="#2a2a4a" /><rect x="18" y="44" width="6" height="6" fill={t} style={{
      opacity: .7
    }} /><rect x="28" y="44" width="6" height="6" fill="#ff00cc" style={{
      opacity: .7
    }} /><rect x="36" y="44" width="4" height="8" fill="#888" /><rect x="0" y="38" width="10" height="6" fill="#3a3a5a" /><rect x="46" y="38" width="10" height="6" fill="#3a3a5a" /><rect x="0" y="44" width="8" height="8" fill="#555" /><rect x="48" y="44" width="8" height="8" fill="#555" />{mood === `pointing` && <rect x="-4" y="44" width="8" height="4" fill="#ffe94a" />}<rect x="14" y="60" width="10" height="10" fill="#2a2a4a" /><rect x="32" y="60" width="10" height="10" fill="#2a2a4a" /><rect x="12" y="68" width="12" height="4" fill="#000" /><rect x="32" y="68" width="12" height="4" fill="#000" /></svg>;
};
