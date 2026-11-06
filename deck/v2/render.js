// node render.js out_dir slide1 slide2 ...  -> PNG per slide (1920x1080)
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const [out, ...ids] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  for (const id of ids) {
    const body = fs.readFileSync(path.join(__dirname, 'slides', id + '.html'), 'utf8');
    fs.writeFileSync(path.join(__dirname, '_tmp.html'), `<!doctype html><meta charset=utf-8><link rel=stylesheet href="theme.css"><body>${body}</body>`);
    await pg.goto('file://' + path.join(__dirname, '_tmp.html')); await pg.evaluate(() => document.fonts.ready); await pg.waitForTimeout(300);
    await pg.locator('section').screenshot({ path: path.join(out, id + '.png') });
  }
  fs.unlinkSync(path.join(__dirname, '_tmp.html')); await b.close();
})();
