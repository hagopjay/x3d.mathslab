// Real UI functions with explicit DOM/X_ITE adapters. This is not a browser test.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const app=fs.readFileSync(new URL('../web/app.js',import.meta.url),'utf8');
const sceneCode=app.slice(app.indexOf('function showWorld('),app.indexOf('function drawProjection('));
const busyCode=app.slice(app.indexOf('function setBusy('),app.indexOf('function stopMotion('));
assert.ok(sceneCode.includes('replaceWorldInOrder')&&busyCode.includes('disabled'));
const flush=async()=>{for(let i=0;i<8;i++)await Promise.resolve();};
function fixture(browser) {
  const nodes=new Map(), projections=[];
  const $=id=>{if(!nodes.has(id))nodes.set(id,{disabled:false,hidden:false,classList:{toggle(){}},setAttribute(){},replaceChildren(...value){this.content=value;}});return nodes.get(id);};
  const state={revision:1,worldQueue:Promise.resolve(),nativeFailed:false,projectionOnly:false,accepted:{}};
  const context=vm.createContext({state,$,document:{createTextNode:t=>t},node:t=>({tag:t}),nativeBrowser:async()=>browser,drawProjection:s=>projections.push(s.lesson)});
  vm.runInContext(sceneCode+'\n'+busyCode,context);
  return {context,state,$,projections};
}
let checks=0;
{
  let release;const gate=new Promise(r=>release=r), commits=[];
  const f=fixture({async createX3DFromString(xml){if(xml==='old')await gate;return xml;},async replaceWorld(scene){commits.push(scene);}});
  const old=f.context.showWorld({x3d:'old',sample:{lesson:'old'}},1);await flush();
  f.state.revision=2;const fresh=f.context.showWorld({x3d:'new',sample:{lesson:'new'}},2);release();
  assert.equal(await old,false);assert.equal(await fresh,true);assert.deepEqual(commits,['new']);checks++;
  console.log('PASS slow obsolete parse cannot commit over a newer request');
}
{
  let release;const gate=new Promise(r=>release=r), commits=[], parsed=[];
  const f=fixture({async createX3DFromString(xml){parsed.push(xml);return xml;},async replaceWorld(scene){if(scene==='old')await gate;commits.push(scene);}});
  const old=f.context.showWorld({x3d:'old',sample:{lesson:'old'}},1);await flush();
  f.state.revision=2;const fresh=f.context.showWorld({x3d:'new',sample:{lesson:'new'}},2);await flush();
  assert.deepEqual(parsed,['old']);release();assert.equal(await old,false);assert.equal(await fresh,true);
  assert.deepEqual(commits,['old','new']);assert.equal(commits.at(-1),'new');checks++;
  console.log('PASS an already-started obsolete native commit is serialized before the final fresh scene');
}
{
  const f=fixture({async createX3DFromString(){throw Error('intended native parser failure');}});
  assert.equal(await f.context.showWorld({x3d:'x',sample:{lesson:'linear'}},1),true);
  assert.deepEqual(f.projections,['linear']);assert.equal(f.$('projection').hidden,false);assert.equal(f.$('world').hidden,true);
  assert.ok(f.$('rendererLabel').content.includes('2D PROJECTION · NATIVE 3D UNAVAILABLE'));checks++;
  console.log('PASS failed native consumer displays the same model as an explicitly labeled projection');
}
{
  const f=fixture(null);f.context.setBusy(true);
  for(const id of ['downloadX3D','sourceDownload','saveCard','copySource','downloadManim','cameraReset','projectionToggle'])assert.equal(f.$(id).disabled,true,id);
  f.context.setBusy(false);assert.equal(f.$('cameraReset').disabled,false);assert.equal(f.$('downloadX3D').disabled,false);checks++;
  console.log('PASS pending requests disable exports and stale-scene reentry controls');
}
{
  const f=fixture(null);f.state.worldQueue=Promise.reject(Error('previous presentation job rejected'));
  assert.equal(await f.context.showWorld({x3d:'x',sample:{lesson:'integral'}},1),true);assert.deepEqual(f.projections,['integral']);checks++;
  console.log('PASS a failed queue predecessor cannot strand the next valid model');
}
console.log(checks+' UI concurrency/state controls pass with explicit DOM and native-browser adapters.');
