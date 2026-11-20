// Rewrites compiled React calls back into JSX.
//
//   (0,T.jsx)(`div`, {className: `x`, children: [a, b]}, key)   ->   <div className="x" key={key}>{a}{b}</div>
//
// Only jsx()/jsxs() calls on the given runtime namespace are touched; every other character of
// the source is kept as it is. Used once, to turn the code recovered from the UI reference's
// compiled bundle into editable source.
//
//   node tools/unjsx.mjs <input.js> <output.jsx> [runtimeNamespace=T]
import { readFileSync, writeFileSync } from 'node:fs';
import { parseAst } from 'vite';

const [, , input, output, NS = 'T'] = process.argv;
const code = readFileSync(input, 'utf8');
const ast = parseAst(code, { lang: 'js' });

const isNode = (v) => v && typeof v === 'object' && typeof v.type === 'string';
function children(node) {
  const out = [];
  for (const [k, v] of Object.entries(node)) {
    if (k === 'start' || k === 'end') continue;
    if (Array.isArray(v)) v.forEach((x) => isNode(x) && out.push(x));
    else if (isNode(v)) out.push(v);
  }
  return out;
}

// (0,T.jsx) or T.jsx  ->  'jsx' | 'jsxs' | null
function runtimeFn(callee) {
  let c = callee;
  if (c.type === 'ParenthesizedExpression') c = c.expression;
  if (c.type === 'SequenceExpression' && c.expressions.length === 2) c = c.expressions[1];
  if (c.type === 'MemberExpression' && !c.computed && c.object.type === 'Identifier' && c.object.name === NS &&
      ['jsx', 'jsxs'].includes(c.property.name)) return c.property.name;
  return null;
}
const isJsxCall = (n) => n.type === 'CallExpression' && runtimeFn(n.callee) && n.arguments.length >= 2;

// Outermost jsx calls inside `node` (not nested in another jsx call).
function outerCalls(node, acc = []) {
  if (isJsxCall(node)) { acc.push(node); return acc; }
  for (const c of children(node)) outerCalls(c, acc);
  return acc;
}

// Source of `node` with every jsx call inside it rewritten.
function src(node) {
  const calls = outerCalls(node).filter((c) => c !== node).sort((a, b) => a.start - b.start);
  if (isJsxCall(node)) return toJsx(node);
  let out = '', pos = node.start;
  for (const c of calls) { out += code.slice(pos, c.start) + toJsx(c); pos = c.end; }
  return out + code.slice(pos, node.end);
}

const aliases = new Map();        // lower-case component names need a capitalised alias in JSX
function tagName(node) {
  if (node.type === 'Literal' && typeof node.value === 'string') return node.value;
  if (node.type === 'TemplateLiteral' && node.expressions.length === 0) return node.quasis[0].value.cooked;
  if (node.type === 'Identifier') {
    if (/^[A-Z]/.test(node.name)) return node.name;
    const alias = 'C_' + node.name;
    aliases.set(alias, node.name);
    return alias;
  }
  if (node.type === 'MemberExpression' && !node.computed) return code.slice(node.start, node.end);
  return null;
}

const staticString = (n) =>
  n.type === 'Literal' && typeof n.value === 'string' ? n.value
  : n.type === 'TemplateLiteral' && n.expressions.length === 0 ? n.quasis[0].value.cooked
  : null;

function attr(name, value) {
  const s = staticString(value);
  if (s !== null && !/["\\\n\r]/.test(s) && !s.includes('&')) return `${name}="${s}"`;
  if (s !== null) return `${name}={${JSON.stringify(s)}}`;
  return `${name}={${src(value)}}`;
}

function child(n) {
  if (isJsxCall(n)) return toJsx(n);
  const s = staticString(n);
  if (s !== null) {
    const safe = s.length && !/[{}<>&\n\r]/.test(s) && s === s.trim();
    return safe ? s : `{${JSON.stringify(s)}}`;
  }
  return `{${src(n)}}`;
}

function toJsx(call) {
  const [tagNode, props, keyNode] = call.arguments;
  const tag = tagName(tagNode);
  if (!tag) throw new Error(`Unsupported tag at ${tagNode.start}: ${code.slice(tagNode.start, tagNode.end)}`);
  const attrs = [];
  let kids = [];
  if (props.type === 'ObjectExpression') {
    for (const p of props.properties) {
      if (p.type === 'SpreadElement') { attrs.push(`{...${src(p.argument)}}`); continue; }
      if (p.computed || p.kind !== 'init' || p.method) throw new Error(`Unsupported prop at ${p.start}`);
      const name = p.key.type === 'Identifier' ? p.key.name : String(p.key.value);
      if (name === 'children') {
        kids = p.value.type === 'ArrayExpression' ? p.value.elements.map(child) : [child(p.value)];
      } else {
        attrs.push(attr(name, p.value));
      }
    }
  } else {
    attrs.push(`{...${src(props)}}`);
  }
  if (keyNode) attrs.push(`key={${src(keyNode)}}`);
  const open = `<${tag}${attrs.length ? ' ' + attrs.join(' ') : ''}`;
  return kids.length ? `${open}>${kids.join('')}</${tag}>` : `${open} />`;
}

let result = src(ast);
if (aliases.size) {
  const marker = '(0,u.createRoot)';
  const at = result.lastIndexOf(marker);
  if (at < 0) throw new Error('render call not found');
  const decl = 'const ' + [...aliases].map(([a, n]) => `${a} = ${n}`).join(', ') + ';\n';
  result = result.slice(0, at) + '\n// JSX treats lower-case tags as HTML elements, so the minified component names get capitalised aliases.\n' + decl + result.slice(at);
}
writeFileSync(output, result);
console.log(`converted ${outerCalls(ast).length} top-level jsx expressions; ${aliases.size} component aliases; ${code.length} -> ${result.length} chars`);
