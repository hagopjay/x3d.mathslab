// Catalog-driven learning tools, exercised with a small DOM adapter.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const app = fs.readFileSync(new URL('../web/app.js', import.meta.url), 'utf8');
const functions = app.slice(app.indexOf('function collectionMatches('), app.indexOf('function resetPrediction('));
class Element {
  constructor(tag) { this.tagName = tag; this.children = []; this.attributes = {}; this.style = {}; this.dataset = {}; }
  append(...children) { this.children.push(...children); }
  replaceChildren(...children) { this.children = children; }
  setAttribute(k, v) { this.attributes[k] = v; }
  get childElementCount() { return this.children.filter(c => c instanceof Element).length; }
  querySelector(selector) {
    const match = selector.match(/data-preset="(\d+)"/);
    return this.children.find(c => match && c.dataset.preset === match[1]) || null;
  }
}
const nodes = new Map();
const $ = id => { if (!nodes.has(id)) nodes.set(id, new Element('div')); return nodes.get(id); };
const node = (tag, cls, text) => { const el = new Element(tag); el.className = cls; el.textContent = text; return el; };
const lesson = {
  id: 'test', title: 'A Projected Vector', domain: 'LINEAR ALGEBRA', level: 'Undergraduate',
  prerequisites: ['Dot products'],
  parameters: [{ id: 'a', default: 1 }, { id: 'b', default: 2 }],
  presets: [{ title: 'A surprising limit', params: { a: 3 }, why: 'Look at the residual.' }],
  legend: [{ label: 'Residual vector', color: '#ff9977' }],
  resources: [{ title: 'Primary source', url: 'https://example.edu/notes', note: 'Read section 2.' },
    { title: 'Unsafe scheme', url: 'javascript:alert(1)' }],
};
let chosen;
const state = { lessons: [lesson, { id: 'old', title: 'An older idea', tagline: 'Still searchable', parameters: [] }], lesson };
const context = vm.createContext({ state, $, node, URL, domains: {}, shortNames: {},
  defaults: l => Object.fromEntries(l.parameters.map(p => [p.id, p.default])),
  choose: (id, params) => { chosen = { id, params }; context.buildLearningTools(); },
  document: { querySelectorAll: () => $('lessonPresets').children },
});
vm.runInContext(functions, context);
assert.equal(context.collectionMatches(lesson, 'linear dot', ''), true);
assert.equal(context.collectionMatches(lesson, 'linear', 'Undergraduate'), true);
assert.equal(context.collectionMatches(lesson, '', 'High school'), false);
assert.equal(context.collectionMatches(lesson, 'matrices', ''), false);
context.buildLearningTools();
assert.equal($('learningProfile').children[0].textContent, 'Undergraduate');
assert.equal($('sceneLegend').children[0].children[1].textContent, 'Residual vector');
assert.equal($('sceneLegend').children[0].children[0].style.backgroundColor, '#ff9977');
assert.equal($('lessonResources').children.length, 1, 'Only HTTPS reading links are offered');
const link = $('lessonResources').children[0].children[0];
assert.equal(link.target, '_blank');
assert.equal(link.rel, 'noopener noreferrer');
context.applyPreset(0);
assert.equal(chosen.id, 'test');
assert.equal(chosen.params.a, 3);
assert.equal(chosen.params.b, 2, 'Partial presets merge with declared defaults');
assert.equal($('presetNote').textContent, 'Look at the residual.');
assert.equal($('lessonPresets').children[0].attributes['aria-pressed'], 'true');
context.clearPreset();
assert.equal($('lessonPresets').children[0].attributes['aria-pressed'], 'false');
state.lesson = state.lessons[1];
context.buildLearningTools();
for (const id of ['sceneLegend', 'presetSection', 'resourcesSection']) assert.equal($(id).hidden, true, id);
assert.equal($('learningProfile').children.length, 0, 'Metadata does not leak from a previous lesson');
$('lessonSearch').value = 'missing';
context.buildNav();
assert.equal($('collectionStatus').textContent, '0 of 2 experiments');
assert.equal($('lessonNav').children[0].className, 'collection-empty');
$('lessonSearch').value = '';
context.buildNav();
assert.equal($('lessonNav').children.length, 2, 'Older catalog entries remain discoverable');
console.log('PASS collection search/filter, partial preset semantics, legends, safe resources, metadata reset, empty results');
