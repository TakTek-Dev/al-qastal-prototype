// Run the visual-QA probe on many pages at many widths through Chrome DevTools Protocol.
// node --experimental-websocket tools/qa.mjs <base-url> <probe.js> <out.json> [widths] [pages...]
// The loader is marked as seen so the probe measures the settled page.
import { spawn } from 'node:child_process';
import { mkdtempSync, readFileSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const [base, probeFile, out, widths = '375,768,1280,1920', ...pages] = process.argv.slice(2);
const probe = readFileSync(probeFile, 'utf8');
const port = 9500 + Math.floor(Math.random() * 300);
const proc = spawn('C:/Program Files/Google/Chrome/Application/chrome.exe', ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${mkdtempSync(join(tmpdir(), 'aq-qa-'))}`, '--hide-scrollbars', 'about:blank'], { stdio: 'ignore' });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
let ws, id = 0; const pending = new Map(); let errs = [];
const send = (method, params = {}) => new Promise((res, rej) => { const i = ++id; pending.set(i, { res, rej }); ws.send(JSON.stringify({ id: i, method, params })); });
const results = {};
try {
  let t; for (let k = 0; k < 50 && !t; k++) { try { t = (await (await fetch(`http://127.0.0.1:${port}/json`)).json()).find((x) => x.type === 'page'); } catch {} await sleep(150); }
  ws = new WebSocket(t.webSocketDebuggerUrl); await new Promise((r) => ws.addEventListener('open', r));
  ws.addEventListener('message', (ev) => { const m = JSON.parse(ev.data);
    if (m.id && pending.has(m.id)) { const p = pending.get(m.id); pending.delete(m.id); m.error ? p.rej(new Error(m.error.message)) : p.res(m.result); }
    if (m.method === 'Runtime.exceptionThrown') errs.push('EXC ' + m.params.exceptionDetails.exception?.description);
    if (m.method === 'Runtime.consoleAPICalled' && m.params.type === 'error') errs.push('console ' + m.params.args.map((a) => a.value).join(' '));
    if (m.method === 'Network.responseReceived' && m.params.response.status >= 400) errs.push(m.params.response.status + ' ' + m.params.response.url); });
  await send('Runtime.enable'); await send('Network.enable'); await send('Page.enable');
  await send('Page.addScriptToEvaluateOnNewDocument', { source: "try{sessionStorage.setItem('aq-in','1')}catch(e){}" });
  for (const w of widths.split(',').map(Number)) {
    await send('Emulation.setDeviceMetricsOverride', { width: w, height: w < 768 ? 812 : 900, deviceScaleFactor: 1, mobile: w < 768 });
    for (const p of pages) {
      errs = [];
      await send('Page.navigate', { url: base + p }); await sleep(3500);
      const r = await send('Runtime.evaluate', { expression: probe, awaitPromise: true, returnByValue: true, replMode: true });
      results[`${p}@${w}`] = { ...(r.result.value || { error: r.exceptionDetails?.text }), errors: errs };
    }
  }
  writeFileSync(out, JSON.stringify(results, null, 1));
  console.log('probed', Object.keys(results).length);
} finally { try { ws.close(); } catch {} proc.kill(); }
