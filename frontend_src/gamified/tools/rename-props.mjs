// Second readability pass over the split files: destructured names take the name of their
// key, e.g. ({goTo: e}) => ... e(`menu`)  becomes  ({goTo}) => ... goTo(`menu`).
// Scope-aware (Babel), so other variables named `e` are untouched. Skips any rename that
// would clash with a name already visible in that scope.
//
//   node tools/rename-props.mjs src/**/*.js*
import { readFileSync, writeFileSync } from 'node:fs';
import { parse } from '@babel/parser';
import traverseModule from '@babel/traverse';
import { generate } from '@babel/generator';
import * as t from '@babel/types';

const traverse = traverseModule.default || traverseModule;
let total = 0;
for (const file of process.argv.slice(2)) {
  const code = readFileSync(file, 'utf8');
  const ast = parse(code, { sourceType: 'module', plugins: ['jsx'] });
  let renamed = 0;
  traverse(ast, {
    ObjectPattern(path) {
      for (const prop of path.get('properties')) {
        if (!prop.isObjectProperty() || prop.node.computed || !t.isIdentifier(prop.node.key)) continue;
        const want = prop.node.key.name;
        let valuePath = prop.get('value');
        if (valuePath.isAssignmentPattern()) valuePath = valuePath.get('left');
        if (!valuePath.isIdentifier()) continue;
        const have = valuePath.node.name;
        if (have === want) continue;
        const scope = valuePath.scope;
        const binding = scope.getBinding(have);
        if (!binding || binding.identifier !== valuePath.node) continue;
        // the new name must not already mean something anywhere this binding is used
        if (scope.hasBinding(want) || binding.referencePaths.some((r) => r.scope.hasBinding(want))) continue;
        scope.rename(have, want);
        if (prop.node.value === valuePath.node || t.isAssignmentPattern(prop.node.value)) prop.node.shorthand = !t.isAssignmentPattern(prop.node.value) && true;
        renamed++;
      }
    },
  });
  writeFileSync(file, generate(ast, { jsescOption: { minimal: true } }, code).code + '\n');
  total += renamed;
  if (renamed) console.log(`${file}: ${renamed}`);
}
console.log('renamed', total);
