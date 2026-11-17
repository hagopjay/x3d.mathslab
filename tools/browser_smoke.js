// Headless browser smoke for the static (Pyodide) and server transports.
// usage: NODE_PATH=$(npm root -g) node tools/browser_smoke.js <url> [out.json] [shots-dir]
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [url, out, shots] = [process.argv[2], process.argv[3], process.argv[4]];
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: 1440, height: 900 } })).newPage();
  const errors = [], report = { url, chromium: browser.version(), playwright: require('playwright/package.json').version, lessons: [], checks: {} };
  page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text()); });
  page.on('pageerror', (e) => errors.push('pageerror: ' + e.message));
  const t0 = Date.now();
  await page.goto(url, { waitUntil: 'load' });
  const native = () => page.waitForFunction(() => /NATIVE X3D/.test(document.getElementById('rendererLabel')?.textContent || ''), null, { timeout: 180000 });
  await native();
  report.first_native_scene_s = (Date.now() - t0) / 1000;
  report.python_runtime = await page.evaluate(() => document.body.dataset.transport === 'pyodide' ? window.MathLabStatic.runtimeVersion() : null).catch(() => null);
  report.transport = await page.evaluate(() => document.body.dataset.transport || 'server');
  const buttons = page.locator('nav button');
  const n = await buttons.count();
  report.checks.lessons_in_nav = n;
  for (let i = 0; i < n; i++) {
    const t1 = Date.now();
    await buttons.nth(i).click();
    await page.waitForTimeout(400);
    await native();
    await page.waitForFunction(() => !document.querySelector('[aria-busy="true"]') && !document.body.classList.contains('busy'), null, { timeout: 60000 }).catch(() => {});
    await page.waitForTimeout(1500);
    const row = await page.evaluate(() => {
      const b = document.getElementById('world')?.browser;
      const scene = b?.currentScene;
      return { title: document.querySelector('h1,h2')?.textContent.trim(), nodes: scene?.rootNodes?.length ?? null,
        metrics: [...document.querySelectorAll('.metric, [class*=metric]')].length,
        model: document.body.innerText.match(/MODEL [0-9a-f]+/)?.[0] || null };
    });
    row.ms = Date.now() - t1;
    report.lessons.push(row);
    if (shots) { fs.mkdirSync(shots, { recursive: true }); await page.screenshot({ path: `${shots}/lesson-${i + 1}.png` }); }
  }
  // parameter change moves the model identity
  const before = await page.evaluate(() => document.body.innerText.match(/MODEL [0-9a-f]+/)?.[0]);
  const slider = page.locator('input[type=range]').first();
  await slider.focus(); await page.keyboard.press('ArrowRight'); await page.keyboard.press('ArrowRight');
  await page.waitForTimeout(2500);
  const after = await page.evaluate(() => document.body.innerText.match(/MODEL [0-9a-f]+/)?.[0]);
  report.checks.parameter_change_changes_model_id = { before, after, changed: before !== after };
  // Manim source download
  const dl = page.waitForEvent('download', { timeout: 20000 }).catch(() => null);
  await page.getByRole('tab', { name: 'Source' }).click().catch(() => page.getByText('Source', { exact: true }).first().click());
  await page.waitForTimeout(500);
  const btn = page.locator('#downloadManim');
  if (await btn.count()) { await btn.click(); const d = await dl; if (d) { const p = await d.path(); const src = fs.readFileSync(p, 'utf8'); report.checks.manim_source = { filename: d.suggestedFilename(), bytes: src.length, has_scene_class: /class \w+\(.*Scene\)/.test(src) }; } else report.checks.manim_source = 'no download'; }
  report.console_errors = errors.slice(0, 10);
  report.elapsed_s = (Date.now() - t0) / 1000;
  const text = JSON.stringify(report, null, 1);
  console.log(text);
  if (out) fs.writeFileSync(out, text);
  await browser.close();
})();
