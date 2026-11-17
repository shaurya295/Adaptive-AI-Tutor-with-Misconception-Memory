// Turns the single recovered file (src/reference/app.jsx) into named modules:
// renames every top-level binding to a meaningful name (scope-aware, so local variables
// that happen to share a minified name are left alone), then writes one file per group
// with the imports each needs. Run once; the board checks the result is pixel-identical.
//
//   node tools/split.mjs
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, relative } from 'node:path';
import { parse } from '@babel/parser';
import traverseModule from '@babel/traverse';
import { generate } from '@babel/generator';

const traverse = traverseModule.default || traverseModule;

// old name -> [new name, file]
const MAP = {
  d: ['delay', 'src/api/mock.js'], f: ['todayIso', 'src/api/mock.js'], p: ['daysFromNowIso', 'src/api/mock.js'],
  m: ['mockAttempts', 'src/api/mock.js'], h: ['recordAttempt', 'src/api/mock.js'], g: ['getLearningCurve', 'src/api/mock.js'],
  _: ['getRollingStats', 'src/api/mock.js'], v: ['mockHintsByConcept', 'src/api/mock.js'], y: ['getHint', 'src/api/mock.js'],
  b: ['mockPrerequisites', 'src/api/mock.js'], x: ['mockMastery', 'src/api/mock.js'], S: ['getConceptGraph', 'src/api/mock.js'],
  C: ['getProfile', 'src/api/mock.js'],
  ee: ['PixelCloud', 'src/components/Scenery.jsx'], E: ['PixelBuilding', 'src/components/Scenery.jsx'],
  D: ['WizardSprite', 'src/components/Sprites.jsx'], te: ['RobotSprite', 'src/components/Sprites.jsx'],
  ne: ['MASCOT_SPOTS', 'src/components/Mascot.jsx'], re: ['Mascot', 'src/components/Mascot.jsx'],
  O: ['PixelButton', 'src/components/PixelButton.jsx'], ie: ['Typewriter', 'src/components/Dialog.jsx'],
  ae: ['Hud', 'src/components/Hud.jsx'], oe: ['DialogBox', 'src/components/Dialog.jsx'],
  k: ['QuestionTimer', 'src/components/QuestionTimer.jsx'], ge: ['QuizEngine', 'src/components/QuizEngine.jsx'],
  A: ['LandingScreen', 'src/screens/LandingScreen.jsx'], se: ['SignInScreen', 'src/screens/SignInScreen.jsx'],
  ce: ['MainMenuScreen', 'src/screens/MainMenuScreen.jsx'], le: ['WelcomeScreen', 'src/screens/WelcomeScreen.jsx'],
  ue: ['COMPANIONS', 'src/data/content.js'], de: ['AvatarSelectScreen', 'src/screens/AvatarSelectScreen.jsx'],
  j: ['HOW_IT_WORKS', 'src/data/content.js'], fe: ['HowItWorksScreen', 'src/screens/HowItWorksScreen.jsx'],
  pe: ['PRETEST_QUESTIONS', 'src/data/content.js'], me: ['LESSON_QUESTION', 'src/data/content.js'],
  he: ['POSTTEST_QUESTIONS', 'src/data/content.js'], _e: ['PreTestScreen', 'src/screens/QuizScreens.jsx'],
  ve: ['LESSON_SCRIPT', 'src/data/content.js'], ye: ['LessonScreen', 'src/screens/LessonScreen.jsx'],
  be: ['PostTestScreen', 'src/screens/QuizScreens.jsx'], xe: ['ProgressScreen', 'src/screens/ProgressScreen.jsx'],
  Se: ['SessionCompleteScreen', 'src/screens/SessionCompleteScreen.jsx'], Ce: ['RewardScreen', 'src/screens/RewardScreen.jsx'],
  we: ['QUEST_CATEGORIES', 'src/data/content.js'], Te: ['FreeQuestScreen', 'src/screens/FreeQuestScreen.jsx'],
  Ee: ['LEADERBOARD', 'src/data/content.js'], De: ['RANK_STYLES', 'src/data/content.js'], Oe: ['TICKER_ITEMS', 'src/data/content.js'],
  ke: ['LeaderboardScreen', 'src/screens/LeaderboardScreen.jsx'], Ae: ['EvalMetricsScreen', 'src/screens/EvalMetricsScreen.jsx'],
  je: ['TOPICS', 'src/data/content.js'], Me: ['masteryColor', 'src/data/content.js'], Ne: ['explainConcept', 'src/data/content.js'],
  Pe: ['MisconceptionsScreen', 'src/screens/MisconceptionsScreen.jsx'], Fe: ['SpacedReviewScreen', 'src/screens/SpacedReviewScreen.jsx'],
  Ie: ['SwitchStudentScreen', 'src/screens/SwitchStudentScreen.jsx'], Le: ['SCREEN_FLOW', 'src/App.jsx'], Re: ['App', 'src/App.jsx'],
};
const LIB = { l: 'React', u: 'ReactDOMClient', T: 'JSXRuntime' };
const HEADERS = {
  'src/api/mock.js': 'Mock backend from the UI reference: every call resolves locally after a short delay.\n// Stage 3 replaces these with real API calls of the same shape.',
  'src/data/content.js': 'Fixed content and small helpers used by the screens.',
};

const code = readFileSync('src/reference/app.jsx', 'utf8');
const ast = parse(code, { sourceType: 'module', plugins: ['jsx'] });

let program;
traverse(ast, { Program(path) { program = path; path.stop(); } });
const scope = program.scope;

// 1. JSX aliases (C_x = x) are no longer needed once components have capitalised names.
for (const [name, binding] of Object.entries(scope.bindings)) {
  if (!name.startsWith('C_')) continue;
  const target = name.slice(2);
  const newName = MAP[target]?.[0];
  if (!newName) throw new Error(`alias ${name} has no mapping`);
  for (const ref of binding.referencePaths) ref.node.name = newName;
  binding.path.remove();
}
// 2. Scope-aware renames of every top-level binding and the library namespaces.
scope.crawl();
for (const [oldName, [newName]] of Object.entries(MAP)) {
  if (!scope.hasOwnBinding(oldName)) throw new Error(`no top-level binding ${oldName}`);
  scope.rename(oldName, newName);
}
for (const [oldName, newName] of Object.entries(LIB)) if (scope.hasOwnBinding(oldName)) scope.rename(oldName, newName);
scope.crawl();
// JSX references renamed through the aliases still need the import bindings to see them.
const unmapped = Object.keys(scope.bindings).filter(
  (n) => !Object.values(MAP).some(([nn]) => nn === n) && !Object.values(LIB).includes(n) && n !== 'initialScreen',
);
if (unmapped.length) throw new Error('unmapped top-level bindings: ' + unmapped.join(', '));

// 3. Collect each top-level declaration with its file and dependencies.
const fileOf = Object.fromEntries(Object.values(MAP).map(([n, f]) => [n, f]));
const decls = [];          // {name, file, node, deps:Set}
let renderStatement = null;
for (const stmt of program.get('body')) {
  if (stmt.isImportDeclaration()) continue;
  if (stmt.isVariableDeclaration()) {
    for (const d of stmt.get('declarations')) decls.push({ name: d.node.id.name, path: d, kind: stmt.node.kind });
  } else if (stmt.isFunctionDeclaration()) {
    decls.push({ name: stmt.node.id.name, path: stmt, kind: 'function' });
  } else {
    renderStatement = stmt;
  }
}
const all = new Set(decls.map((d) => d.name));
for (const d of decls) {
  d.file = fileOf[d.name];
  d.deps = new Set();
  d.path.traverse({
    'Identifier|JSXIdentifier'(p) {
      const n = p.node.name;
      if ((all.has(n) || Object.values(LIB).includes(n) || n === 'initialScreen') && p.scope.getBinding(n)?.scope === scope) d.deps.add(n);
    },
  });
  d.deps.delete(d.name);
}

// 4. Write the files.
const files = new Map();
for (const d of decls) {
  if (!files.has(d.file)) files.set(d.file, []);
  files.get(d.file).push(d);
}
const gen = (node) => generate(node, { retainLines: false, comments: true, jsescOption: { minimal: true } }).code;
for (const [file, list] of files) {
  const own = new Set(list.map((d) => d.name));
  const needs = new Map();
  let usesReact = false, usesRuntime = false, usesScreenParam = false;
  for (const d of list) for (const dep of d.deps) {
    if (dep === 'React') usesReact = true;
    else if (dep === 'JSXRuntime') usesRuntime = true;
    else if (dep === 'initialScreen') usesScreenParam = true;
    else if (!own.has(dep)) {
      const f = fileOf[dep];
      if (!needs.has(f)) needs.set(f, new Set());
      needs.get(f).add(dep);
    }
  }
  const rel = (to) => { let r = relative(dirname(file), to).replace(/\.jsx?$/, ''); return r.startsWith('.') ? r : './' + r; };
  const lines = [];
  if (HEADERS[file]) lines.push('// ' + HEADERS[file]);
  if (usesReact) lines.push("import * as React from 'react';");
  if (usesRuntime) lines.push("import * as JSXRuntime from 'react/jsx-runtime';");
  if (usesScreenParam) lines.push(`import { initialScreen } from '${rel('src/screen-param.js')}';`);
  for (const [f, names] of [...needs].sort()) lines.push(`import { ${[...names].sort().join(', ')} } from '${rel(f)}';`);
  lines.push('');
  for (const d of list) {
    const node = d.kind === 'function' ? d.path.node : { type: 'VariableDeclaration', kind: d.kind === 'var' ? 'const' : d.kind, declarations: [d.path.node] };
    lines.push('export ' + gen(node) + '\n');
  }
  mkdirSync(dirname(file), { recursive: true });
  writeFileSync(file, lines.join('\n'));
  console.log(`${file}: ${list.map((d) => d.name).join(', ')}`);
}
console.log('render statement:', gen(renderStatement.node));
