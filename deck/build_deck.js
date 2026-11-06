// Build the Orbital Curbside pitch deck from deck/slides/*.html (order in deck.json).
//
// Outputs (in deck/):
//   OrbitalCurbside_deck.html   offline presenter: arrow keys / click to advance, F = full screen,
//                               plays assets/demo_pickup.mp4 on the demo slide. Needs no internet.
//   OrbitalCurbside_deck.pdf    1920x1080 (16:9) pages for upload to DECA. The demo slide shows a still.
//   speaker_notes.md            word-for-word script for every slide
//   (with --png DIR)            one 1920x1080 PNG per slide, used by make_pptx.py
//
// Run from the repo root:  node deck/build_deck.js [--png DIR]
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const HERE = __dirname;
const deck = JSON.parse(fs.readFileSync(path.join(HERE, 'deck.json'), 'utf8'));
const pngArg = process.argv.indexOf('--png');
const pngDir = pngArg > 0 ? path.resolve(process.argv[pngArg + 1]) : null;
const VIDEO = 'assets/demo_pickup.mp4';
const hasVideo = fs.existsSync(path.join(HERE, VIDEO));

const unescape = (s) => s.replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&quot;/g, '"').replace(/&#39;/g, "'");
const slides = deck.order.map((id) => fs.readFileSync(path.join(HERE, 'slides', id + '.html'), 'utf8'));

// ---- speaker notes
const notes = [`# ${deck.title}: speaker notes\n`,
  'Word-for-word scripts. Text in [brackets] is a stage cue, not spoken. "Q&A backup" lines are for judge questions.\n'];
deck.order.forEach((id, i) => {
  const m = slides[i].match(/<aside>([\s\S]*?)<\/aside>/);
  notes.push(`\n## Slide ${i + 1}: ${id}\n\n${m ? unescape(m[1]).trim() : '(no notes)'}\n`);
});
fs.writeFileSync(path.join(HERE, 'speaker_notes.md'), notes.join(''));

// ---- presenter (offline)
const PRESENTER = `
<style>
html,body{margin:0;height:100%;background:#000;overflow:hidden}
#stage{position:absolute;left:50%;top:50%;width:1920px;height:1080px;transform-origin:0 0}
#stage>section{position:absolute;left:0;top:0;display:none}
#stage>section.on{display:block}
#hint{position:fixed;left:16px;bottom:12px;font:14px 'Schibsted Grotesk',Arial,sans-serif;color:#6B6964;transition:opacity 1s}
</style>
<script>
const VIDEO = ${JSON.stringify(hasVideo ? VIDEO : '')};
let i = 0, S;
function fit(){ const k = Math.min(innerWidth/1920, innerHeight/1080);
  document.getElementById('stage').style.transform = 'scale('+k+') translate(-50%,-50%)'; }
function show(n){
  i = Math.max(0, Math.min(S.length-1, n));
  S.forEach((s,k)=>{ s.classList.toggle('on', k===i); const v=s.querySelector('video[data-video]'); if(v && k!==i){ v.pause(); } });
  const v = S[i].querySelector('video[data-video]');
  if (v && VIDEO) {
    const poster = S[i].querySelector('img[data-poster]');
    v.style.display='block'; if (poster) poster.style.visibility='hidden'; const sc=S[i].querySelector('.scrim-l'); if (sc) sc.style.display='none';
    v.currentTime = 0; v.play().catch(()=>{ v.style.display='none'; if (poster) poster.style.visibility='visible'; if (sc) sc.style.display=''; });
  }
  history.replaceState(null,'','#'+(i+1));
}
addEventListener('DOMContentLoaded',()=>{
  S=[...document.querySelectorAll('#stage>section')];
  S.forEach(s=>{ const v=s.querySelector('video[data-video]'); if(v && VIDEO){ v.src=VIDEO; v.loop=true;
    v.addEventListener('error',()=>{ v.style.display='none'; const p=s.querySelector('img[data-poster]'); if(p) p.style.visibility='visible'; const c=s.querySelector('.scrim-l'); if(c) c.style.display=''; }); } });
  fit(); show((parseInt(location.hash.slice(1))||1)-1);
  setTimeout(()=>{document.getElementById('hint').style.opacity=0},4000);
});
addEventListener('resize',fit);
addEventListener('keydown',e=>{
  if(['ArrowRight','ArrowDown','PageDown',' ','Enter'].includes(e.key)){e.preventDefault();show(i+1);}
  else if(['ArrowLeft','ArrowUp','PageUp','Backspace'].includes(e.key)){e.preventDefault();show(i-1);}
  else if(e.key==='Home') show(0); else if(e.key==='End') show(S.length-1);
  else if(e.key==='f'||e.key==='F'){ document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen(); }
});
addEventListener('click',e=>{ show(e.clientX < innerWidth/4 ? i-1 : i+1); });
</script>`;
const head = (extra) => `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>${deck.title}</title>
<link rel="stylesheet" href="theme.css">${extra}</head>`;
fs.writeFileSync(path.join(HERE, 'OrbitalCurbside_deck.html'),
  head(PRESENTER) + `<body><div id="stage">${slides.join('\n')}</div>
<p id="hint">→ / click: next · ← : back · F: full screen</p></body></html>`);

// ---- PDF + PNGs (rendered from a print page next to theme.css so relative paths resolve)
(async () => {
  const printPath = path.join(HERE, '_print.html');
  fs.writeFileSync(printPath, head(`<style>@page{size:1920px 1080px;margin:0} body{margin:0;background:#000}
section{page-break-after:always;break-after:page}</style>`) + `<body>${slides.join('\n')}</body></html>`);
  const b = await chromium.launch();
  const pg = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await pg.goto('file://' + printPath, { waitUntil: 'load' });
  await pg.evaluate(() => document.fonts.ready);
  const missing = await pg.evaluate(() => [...document.images].filter((im) => !im.naturalWidth).map((im) => im.getAttribute('src')));
  if (missing.length) throw new Error('missing images: ' + missing.join(', '));
  if (!(await pg.evaluate(() => document.fonts.check('800 40px "Schibsted Grotesk"')))) throw new Error('Schibsted Grotesk did not load');
  await pg.pdf({ path: path.join(HERE, 'OrbitalCurbside_deck.pdf'), width: '1920px', height: '1080px', printBackground: true, preferCSSPageSize: true });
  if (pngDir) {
    fs.mkdirSync(pngDir, { recursive: true });
    const secs = await pg.$$('section');
    for (let k = 0; k < secs.length; k++) await secs[k].screenshot({ path: path.join(pngDir, `slide${String(k + 1).padStart(2, '0')}.png`) });
  }
  await b.close();
  fs.unlinkSync(printPath);
  console.log(`built ${slides.length} slides; video ${hasVideo ? 'embedded' : 'missing (still image only)'}`);
})().catch((e) => { console.error(e); process.exit(1); });
