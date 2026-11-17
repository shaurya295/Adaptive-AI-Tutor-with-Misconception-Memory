import * as React from 'react';
export const PixelButton = ({
  children,
  color = `#ff00cc`,
  textColor = `#fff`,
  onClick,
  className = ``,
  size = `md`,
  glow = !1,
  disabled = !1
}) => {
  let [c, u] = (0, React.useState)(!1);
  return <button className={`pixel-btn font-pixel border-4 border-black ${{
    sm: `text-xs px-4 py-2`,
    md: `text-sm px-6 py-3`,
    lg: `text-base px-8 py-4`
  }[size]} inline-block select-none ${className}`} disabled={disabled} style={{
    background: disabled ? `#444` : color,
    color: disabled ? `#888` : textColor,
    boxShadow: c ? `0 0 0 #000` : glow ? `5px 5px 0 #000, 0 0 18px ${color}88` : `5px 5px 0 #000`,
    transform: c ? `translate(5px,5px)` : `translate(0,0)`,
    transition: `transform 0.08s, box-shadow 0.08s`,
    cursor: disabled ? `not-allowed` : `pointer`
  }} onMouseDown={() => !disabled && u(!0)} onMouseUp={() => u(!1)} onMouseLeave={() => u(!1)} onClick={disabled ? void 0 : onClick}>{children}</button>;
};
