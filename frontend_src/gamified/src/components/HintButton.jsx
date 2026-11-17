// Buy a clue before answering (owner's decision G2): costs coins, shown in the same pale
// "Pixel" panel as the reference's hint box. Real mode only; the hint after a wrong answer stays free.
import * as React from 'react';
import { PixelButton } from './PixelButton';
import { buyHint } from '../api/client';
import { useHud } from '../api/hud';

const HINT_COST = 5;

export function HintButton({ questionId }) {
  const hud = useHud();
  const [clue, setClue] = React.useState(null);
  const [busy, setBusy] = React.useState(false);
  const buy = () => {
    setBusy(true);
    buyHint(questionId).then(r => setClue(r.clue)).catch(e => setClue(`⚠ ${e.message}`)).finally(() => setBusy(false));
  };
  return <div className="flex flex-col items-center gap-3 mb-4">{clue ? <div className="w-full border-4 border-black p-3" style={{
      background: `#fff7d6`,
      boxShadow: `4px 4px 0 #000`
    }}><p className="font-body text-sm text-gray-900">{`💡 ${clue}`}</p></div> : <PixelButton onClick={buy} color="#ffe94a" textColor="#000" size="sm" disabled={busy || hud.coins < HINT_COST}>{hud.coins < HINT_COST ? `💡 HINT · NEED ${HINT_COST} 🪙` : `💡 HINT · ${HINT_COST} 🪙`}</PixelButton>}</div>;
}
