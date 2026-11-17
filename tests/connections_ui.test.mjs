// Exercise authored conceptual bridges through the actual UI functions.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';

const app = fs.readFileSync(new URL('../web/app.js', import.meta.url), 'utf8');
const functions = app.slice(app.indexOf('function collectionMatches('), app.indexOf('function resetPrediction('));
class Element {
  constructor(tag) {
    this.tagName = tag; this.children = []; this.attributes = {};
    this.style = {}; this.dataset = {}; this.value = ''; this.focused = false;
  }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute(k, v) { this.attributes[k] = v; }
  focus() { this.focused = true; }
  get childElementCount() { return this.children.length; }
}
const nodes = new Map();
const $ = id => { if (!nodes.has(id)) nodes.set(id, new Element('div')); return nodes.get(id); };
const node = (tag, cls, text) => {
  const el = new Element(tag); el.className = cls; el.textContent = text; return el;
};
const source = {
  id: 'heat', title: 'Heat and roughness', level: 'Undergraduate 1', parameters: [],
  axes: 'Horizontal: position x. Vertical: temperature u. Depth: elapsed time.',
  connections: [
    { lesson: 'waves', why: 'Compare oscillation with exponential modal decay.' },
    { lesson: 'waves', why: 'Duplicate destination is deliberately omitted.' },
    { lesson: 'missing', why: 'A lesson from a future edition.' },
    { lesson: 'heat', why: 'Do not link the current scene to itself.' },
  ],
};
const target = { id: 'waves', title: 'Standing waves', shortName: 'Waves and nodes',
  level: 'Undergraduate 1', parameters: [] };
const state = { lessons: [source, target], lesson: source, mode: 'story' };
const chosen = [], panels = [];
const context = vm.createContext({ state, $, node, URL, domains: {}, shortNames: {},
  choose: id => { chosen.push(id); state.lesson = state.lessons.find(l => l.id === id); },
  changePanel: mode => { panels.push(mode); state.mode = mode; },
});
vm.runInContext(functions, context);

context.buildLearningTools();
assert.equal($('sceneAxes').textContent, source.axes);
assert.equal($('sceneAxes').hidden, false);
assert.equal($('connectionsSection').hidden, false);
assert.equal($('lessonConnections').children.length, 1, 'Only distinct, available destinations appear');
const button = $('lessonConnections').children[0].children[0];
assert.equal(button.type, 'button');
assert.equal(button.children[0].textContent, 'Continue with Waves and nodes →');
assert.equal(button.children[1].textContent, source.connections[0].why);

$('lessonSearch').value = 'heat';
$('levelFilter').value = 'Grade 10–12';
button.onclick();
assert.deepEqual(chosen, ['waves']);
assert.deepEqual(panels, ['story'], 'Following a bridge preserves the Understand tab');
assert.equal($('lessonSearch').value, '', 'Conflicting search does not conceal destination');
assert.equal($('levelFilter').value, '', 'Conflicting level filter is cleared');
assert.equal($('lessonTitle').focused, true, 'Keyboard focus moves to the new lesson heading');
assert.equal($('lessonNav').children[1].attributes['aria-current'], 'true');

context.buildLearningTools();
assert.equal($('sceneAxes').textContent, '');
assert.equal($('sceneAxes').hidden, true, 'Coordinate hints do not leak between scenes');
assert.equal($('lessonConnections').children.length, 0);
assert.equal($('connectionsSection').hidden, true);
$('lessonSearch').value = 'waves';
$('levelFilter').value = 'Undergraduate 1';
context.followConnection('waves');
assert.equal($('lessonSearch').value, 'waves', 'A compatible search is preserved');
assert.equal($('levelFilter').value, 'Undergraduate 1');
const before = chosen.length;
context.followConnection('missing');
assert.equal(chosen.length, before, 'Unavailable connection is a no-op');

const html = fs.readFileSync(new URL('../web/index.html', import.meta.url), 'utf8');
assert.match(html, /id="lessonTitle" tabindex="-1"/);
assert.match(html, /id="connectionsSection"[^>]+aria-labelledby="connectionsHeading"/);
assert.match(html, /id="sceneAxes"[^>]+aria-label="Coordinate guide/);
assert.match(app, /Insight-Expeditions\.html/);
console.log('PASS coordinate hints, valid conceptual bridges, filter visibility, reading-mode continuity and keyboard focus');
