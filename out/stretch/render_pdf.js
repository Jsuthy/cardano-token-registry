// node render_pdf.js in.html out.pdf  (headless Chromium print-to-PDF)
let pw; try { pw = require('playwright'); } catch { pw = require('/opt/node22/lib/node_modules/playwright'); }
(async () => { const b = await pw.chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + require('path').resolve(process.argv[2])); await p.pdf({ path: process.argv[3], format: 'Letter', printBackground: true, margin: { top: '0.3in', bottom: '0.3in', left: '0.3in', right: '0.3in' } });
  await b.close(); })();
