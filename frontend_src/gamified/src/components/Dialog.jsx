import * as React from 'react';
export const Typewriter = ({
  text,
  speed = 40,
  onDone
}) => {
  let [r, i] = (0, React.useState)(``);
  return (0, React.useEffect)(() => {
    i(``);
    let r = 0,
      a = setInterval(() => {
        r < text.length ? i(text.slice(0, ++r)) : (clearInterval(a), onDone?.());
      }, speed);
    return () => clearInterval(a);
  }, [text, speed]), <span>{r}<span style={{
      animation: `blink 1s step-end infinite`
    }}>▌</span></span>;
};
export const DialogBox = ({
  speaker = ``,
  text = ``,
  onNext
}) => <div className="relative ml-4"><div className="bg-white border-4 border-black p-4" style={{
    boxShadow: `6px 6px 0 #000`
  }}>{speaker && <p className="font-pixel text-xs mb-2 pb-1" style={{
      color: `#5b3a8e`,
      borderBottom: `2px solid #eee`
    }}>{speaker}</p>}<p className="font-body text-sm text-gray-900 leading-relaxed"><Typewriter text={text} /></p>{onNext && <button onClick={onNext} className="absolute bottom-2 right-3 font-pixel text-xs" style={{
      color: `#5b3a8e`,
      animation: `bounce2 0.8s ease-in-out infinite`,
      background: `none`,
      border: `none`,
      cursor: `pointer`
    }}>▼</button>}</div><div className="absolute top-5" style={{
    left: -12,
    borderTop: `8px solid transparent`,
    borderBottom: `8px solid transparent`,
    borderRight: `12px solid #000`
  }} /><div className="absolute top-6" style={{
    left: -8,
    borderTop: `6px solid transparent`,
    borderBottom: `6px solid transparent`,
    borderRight: `10px solid #fff`
  }} /></div>;
