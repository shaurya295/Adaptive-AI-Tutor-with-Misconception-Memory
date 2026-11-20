import { delay } from '../api/mock';
export const PixelCloud = ({
  x = 0,
  y = 0,
  scale = 1,
  color = `#f0e8ff`,
  delay: i = `0s`
}) => <g transform={`translate(${x},${y}) scale(${scale})`} style={{
  animation: `cloudmove 18s ${i} linear infinite`
}}><rect x="16" y="8" width="48" height="8" fill={color} /><rect x="8" y="16" width="64" height="8" fill={color} /><rect x="4" y="24" width="72" height="8" fill={color} /><rect x="0" y="32" width="80" height="8" fill={color} /><rect x="4" y="40" width="72" height="8" fill={color} /><rect x="16" y="48" width="48" height="8" fill={color} /></g>;
export const PixelBuilding = ({
  x = 0,
  color = `#5b3a8e`,
  w = 40,
  h = 80
}) => <g transform={`translate(${x},0)`}><rect x={0} y={200 - h} width={w} height={h} fill={color} /><rect x={0} y={200 - h} width={w} height={4} fill="#000" />{[0, 1, 2].map(e => [0, 1].map(t => <rect x={6 + t * 14} y={200 - h + 10 + e * 20} width={8} height={8} fill={(e * 2 + t) % 3 == 0 ? `#1a0a2e` : `#ffe94a`} key={`w-${e}-${t}`} />))}</g>;
