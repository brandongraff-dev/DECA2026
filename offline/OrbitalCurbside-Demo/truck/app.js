// Orbital Curbside: concept model of the truck and its journey to the first stop.
// Everything is sized from data/truck.json (engine/scripts/export_model.py), which
// comes from the route and launch results. Units in the close-up scenes: metres.
import * as THREE from './lib/three.module.min.js';
import { OrbitControls } from './lib/OrbitControls.js';
import { RoomEnvironment } from './lib/RoomEnvironment.js';
import { EffectComposer } from './lib/EffectComposer.js';
import { RenderPass } from './lib/RenderPass.js';
import { UnrealBloomPass } from './lib/UnrealBloomPass.js';
import { OutputPass } from './lib/OutputPass.js';
import { loadEarthTextures, makeRealEarth, setEarthSun } from './earth.js';

const $ = (id) => document.getElementById(id);
const fmt = (x, d = 0) => Number(x).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
const smooth = (x) => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (f, a, b) => clamp((f - a) / (b - a), 0, 1);                 // progress of f inside [a, b]
const pulse = (dt, len) => (dt < 0 || dt > len ? 0 : Math.sin(Math.PI * dt / len));
const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
function mulberry(a) { return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

const COL = { truck: 0xe8620c, xenon: 0x8c7cff, kit: 0xf2b33d };
const SUN_DIR = new THREE.Vector3(0.55, 0.62, 0.56).normalize();

// ------------------------------------------------------------------ renderer + post-processing
const host = $('stage');
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, logarithmicDepthBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.95;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
host.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x020306);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

const camera = new THREE.PerspectiveCamera(38, 1, 0.05, 40000);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const bloom = new UnrealBloomPass(new THREE.Vector2(512, 512), 0.32, 0.4, 0.93);
composer.addPass(bloom);
composer.addPass(new OutputPass());

// the Sun, with shadows over the close-up working area
const sun = new THREE.DirectionalLight(0xfff3e2, 3.1);
sun.position.copy(SUN_DIR).multiplyScalar(40);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -12, right: 12, top: 12, bottom: -12, near: 1, far: 90 });
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 0.02;
scene.add(sun, sun.target);
// earthshine: bluish light from below, faint dark sky above
const earthshine = new THREE.HemisphereLight(0x0a0c14, 0x3d6fb0, 0.75);
scene.add(earthshine);

// stars
(function stars() {
  const n = 3000, pos = new Float32Array(n * 3), rng = mulberry(7);
  for (let k = 0; k < n; k++) {
    const u = rng() * 2 - 1, th = rng() * Math.PI * 2, r = 30000, s = Math.sqrt(1 - u * u);
    pos.set([r * s * Math.cos(th), r * u, r * s * Math.sin(th)], k * 3);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  scene.add(new THREE.Points(g, new THREE.PointsMaterial({ color: 0xc9d2e8, size: 1.4, sizeAttenuation: false, transparent: true, opacity: 0.7, depthWrite: false })));
})();

// ------------------------------------------------------------------ procedural textures
function canvasTex(w, h, draw, srgb = true, repeat) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  if (repeat) { t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(repeat[0], repeat[1]); }
  return t;
}
// multi-layer insulation: crinkled facets, taped seams and stitched panel edges
const mliColor = canvasTex(1024, 1024, (g, w, h) => {
  const r = mulberry(3);
  g.fillStyle = '#c69a3c'; g.fillRect(0, 0, w, h);
  for (let k = 0; k < 2600; k++) {
    const x = r() * w, y = r() * h, s = 8 + r() * 46, v = r();
    g.fillStyle = v < 0.5 ? `rgba(255,226,140,${0.10 + 0.25 * r()})` : `rgba(70,45,10,${0.08 + 0.22 * r()})`;
    g.beginPath(); g.moveTo(x, y);
    for (let j = 0; j < 4; j++) g.lineTo(x + (r() - 0.5) * s * 2, y + (r() - 0.5) * s * 2);
    g.closePath(); g.fill();
  }
  g.strokeStyle = 'rgba(60,40,10,0.55)'; g.lineWidth = 3;
  for (let k = 1; k < 4; k++) { g.beginPath(); g.moveTo(k * w / 4, 0); g.lineTo(k * w / 4 + (r() - 0.5) * 12, h); g.stroke(); }
  g.fillStyle = 'rgba(205,205,200,0.85)';                  // aluminised tape strips
  for (let k = 0; k < 7; k++) g.fillRect(r() * w, r() * h, 18 + r() * 60, 7);
  g.strokeStyle = 'rgba(40,28,8,0.6)'; g.lineWidth = 2; g.setLineDash([3, 5]);
  g.strokeRect(10, 10, w - 20, h - 20);
});
const mliBump = canvasTex(1024, 1024, (g, w, h) => {
  const r = mulberry(5);
  g.fillStyle = '#808080'; g.fillRect(0, 0, w, h);
  for (let k = 0; k < 3200; k++) {
    const x = r() * w, y = r() * h, s = 6 + r() * 40, v = Math.floor(70 + r() * 110);
    g.fillStyle = `rgb(${v},${v},${v})`;
    g.beginPath(); g.moveTo(x, y);
    for (let j = 0; j < 4; j++) g.lineTo(x + (r() - 0.5) * s * 2, y + (r() - 0.5) * s * 2);
    g.closePath(); g.fill();
  }
}, false);
// white radiator panels with a fine grid of mounting lines
const radTex = canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = '#e9e8e2'; g.fillRect(0, 0, w, h);
  g.strokeStyle = 'rgba(120,120,120,0.25)'; g.lineWidth = 2;
  for (let k = 1; k < 8; k++) { g.beginPath(); g.moveTo(k * w / 8, 0); g.lineTo(k * w / 8, h); g.stroke(); }
  g.strokeStyle = 'rgba(90,90,90,0.5)'; g.lineWidth = 6; g.strokeRect(3, 3, w - 6, h - 6);
});
// solar cells: dark-blue cells, silver interconnects, bus bars
const cellTex = canvasTex(1024, 1024, (g, w, h) => {
  g.fillStyle = '#b9bec8'; g.fillRect(0, 0, w, h);
  const nx = 12, ny = 16, gap = 3, r = mulberry(11);
  for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
    const x = i * w / nx + gap, y = j * h / ny + gap, cw = w / nx - 2 * gap, ch = h / ny - 2 * gap;
    const d = 0.9 + 0.2 * r();
    const grd = g.createLinearGradient(x, y, x + cw, y + ch);
    grd.addColorStop(0, `rgb(${22 * d},${38 * d},${78 * d})`); grd.addColorStop(1, `rgb(${10 * d},${18 * d},${44 * d})`);
    g.fillStyle = grd; g.fillRect(x, y, cw, ch);
    g.fillStyle = 'rgba(200,210,230,0.35)';
    for (let b = 1; b < 5; b++) g.fillRect(x, y + b * ch / 5, cw, 1);
    g.fillStyle = 'rgba(220,225,235,0.6)'; g.fillRect(x + cw / 2 - 1, y, 2, ch);
  }
});
// weathered paint for a decades-old rocket stage: sun-faded white, grime streaks, panel lines
function stagePaint(seed) {
  return canvasTex(1024, 1024, (g, w, h) => {
    const r = mulberry(seed);
    g.fillStyle = '#d7d4cb'; g.fillRect(0, 0, w, h);
    for (let k = 0; k < 400; k++) {
      g.fillStyle = `rgba(${120 + r() * 60},${110 + r() * 50},${90 + r() * 40},${0.04 + 0.06 * r()})`;
      g.beginPath(); g.ellipse(r() * w, r() * h, 20 + r() * 120, 10 + r() * 60, r() * 3, 0, Math.PI * 2); g.fill();
    }
    for (let k = 0; k < 140; k++) {
      const x = r() * w; g.fillStyle = `rgba(70,62,50,${0.03 + 0.07 * r()})`; g.fillRect(x, r() * h * 0.5, 2 + r() * 6, h * (0.2 + r() * 0.6));
    }
    g.strokeStyle = 'rgba(60,55,50,0.45)'; g.lineWidth = 2;
    for (let k = 0; k < 24; k++) { const x = k * w / 24; g.beginPath(); g.moveTo(x, 0); g.lineTo(x, h); g.stroke(); }
    for (let k = 1; k < 6; k++) { const y = k * h / 6; g.lineWidth = 4; g.beginPath(); g.moveTo(0, y); g.lineTo(w, y); g.stroke(); }
    g.fillStyle = 'rgba(30,30,30,0.85)';
    g.fillRect(0, h * 0.06, w, h * 0.035);
    for (let k = 0; k < 6; k++) g.fillRect(w * (0.1 + 0.15 * k), h * 0.45, w * 0.05, h * 0.012);
  });
}
const carbonTex = canvasTex(256, 256, (g) => {
  g.fillStyle = '#1d1f23'; g.fillRect(0, 0, 256, 256);
  for (let i = 0; i < 16; i++) for (let j = 0; j < 16; j++) { g.fillStyle = (i + j) % 2 ? '#2a2d33' : '#16181c'; g.fillRect(i * 16, j * 16, 16, 16); }
}, true, [3, 2]);
const nozzleTex = canvasTex(64, 512, (g, w, h) => {
  const grd = g.createLinearGradient(0, 0, 0, h);
  grd.addColorStop(0, '#5a4a3a'); grd.addColorStop(0.35, '#8a7356'); grd.addColorStop(0.7, '#6d7684'); grd.addColorStop(1, '#3a3f48');
  g.fillStyle = grd; g.fillRect(0, 0, w, h);
});
const softDot = canvasTex(128, 128, (g, w) => {
  const grd = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2);
  grd.addColorStop(0, 'rgba(255,255,255,1)'); grd.addColorStop(0.35, 'rgba(255,255,255,0.55)'); grd.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grd; g.fillRect(0, 0, w, w);
});
const plumeTex = canvasTex(64, 256, (g, w, h) => {
  const grd = g.createLinearGradient(0, h, 0, 0);
  grd.addColorStop(0, 'rgba(255,255,255,1)'); grd.addColorStop(0.12, 'rgba(255,255,255,0.8)'); grd.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grd; g.fillRect(0, 0, w, h);
});

const M = {
  mli: new THREE.MeshStandardMaterial({ map: mliColor, bumpMap: mliBump, bumpScale: 1.6, metalness: 0.85, roughness: 0.32 }),
  mliBlack: new THREE.MeshStandardMaterial({ color: 0x1a1a1c, bumpMap: mliBump, bumpScale: 1.2, metalness: 0.7, roughness: 0.4 }),
  mliSilver: new THREE.MeshStandardMaterial({ color: 0xc8ccd2, bumpMap: mliBump, bumpScale: 1.2, metalness: 0.95, roughness: 0.25 }),
  radiator: new THREE.MeshStandardMaterial({ map: radTex, roughness: 0.6, metalness: 0.02 }),
  white: new THREE.MeshStandardMaterial({ color: 0xe9e8e3, roughness: 0.5, metalness: 0.05 }),
  dark: new THREE.MeshStandardMaterial({ color: 0x2a2d33, roughness: 0.5, metalness: 0.6 }),
  black: new THREE.MeshStandardMaterial({ color: 0x0e0f12, roughness: 0.6, metalness: 0.3 }),
  steel: new THREE.MeshStandardMaterial({ color: 0x9aa0a9, roughness: 0.3, metalness: 0.95 }),
  alu: new THREE.MeshStandardMaterial({ color: 0xc5c9cf, roughness: 0.38, metalness: 0.9 }),
  cells: new THREE.MeshPhysicalMaterial({ map: cellTex, roughness: 0.32, metalness: 0.4, clearcoat: 1, clearcoatRoughness: 0.06 }),
  cellBack: new THREE.MeshStandardMaterial({ color: 0xd9d7cf, roughness: 0.75 }),
  orange: new THREE.MeshStandardMaterial({ color: COL.truck, roughness: 0.45, metalness: 0.1 }),
  carbon: new THREE.MeshStandardMaterial({ map: carbonTex, roughness: 0.45, metalness: 0.3 }),
  nozzle: new THREE.MeshStandardMaterial({ map: nozzleTex, roughness: 0.42, metalness: 0.85, side: THREE.DoubleSide }),
  nozzleIn: new THREE.MeshStandardMaterial({ color: 0x1b1a19, roughness: 0.8, metalness: 0.3, side: THREE.BackSide }),
  tank: new THREE.MeshStandardMaterial({ color: 0x9aa3b5, roughness: 0.3, metalness: 0.8 }),
  thrusterRing: new THREE.MeshStandardMaterial({ color: 0x15161b, emissive: COL.xenon, emissiveIntensity: 0, roughness: 0.4 }),
  led: new THREE.MeshStandardMaterial({ color: 0x111111, emissive: 0xff3b1f, emissiveIntensity: 2.2 }),
  lens: new THREE.MeshPhysicalMaterial({ color: 0x0a1020, roughness: 0.05, metalness: 0.2, clearcoat: 1 }),
};
function additive(color, opacity, map = plumeTex) {
  return new THREE.MeshBasicMaterial({ color, map, transparent: true, opacity, blending: THREE.AdditiveBlending, depthWrite: false, side: THREE.DoubleSide, toneMapped: false });
}
function lathe(points, segs, mat) {
  return new THREE.Mesh(new THREE.LatheGeometry(points.map(([r, y]) => new THREE.Vector2(r, y)), segs), mat);
}
function bell(rThroat, rExit, len, n = 14) {           // a contoured rocket nozzle profile
  const pts = [];
  for (let k = 0; k <= n; k++) { const t = k / n; pts.push([rThroat + (rExit - rThroat) * Math.pow(t, 0.62), -len * t]); }
  return pts;
}
function tube(points, radius, mat) {
  const curve = new THREE.CatmullRomCurve3(points.map((p) => new THREE.Vector3(...p)));
  return new THREE.Mesh(new THREE.TubeGeometry(curve, 40, radius, 8, false), mat);
}
function shadowAll(obj) { obj.traverse((o) => { if (o.isMesh && o.material.blending !== THREE.AdditiveBlending) { o.castShadow = true; o.receiveShadow = true; } }); }

// ------------------------------------------------------------------ the truck
// Frame: +Z forward (capture end), -Z aft (thrusters), wings along +/-X, +Y up (antenna side).
const BUS = { w: 1.5, h: 1.35, l: 1.8 };
const MAG = { r: 0.92, len: 0.78, z0: BUS.l / 2 };
const truck = new THREE.Group();
const parts = {};
const xrayHide = [];

function mesh(geo, mat, parent, pos, rot) {
  const m = new THREE.Mesh(geo, mat);
  if (pos) m.position.set(...pos);
  if (rot) m.rotation.set(...rot);
  (parent || truck).add(m);
  return m;
}
function anchor(name, parent, pos) { const o = new THREE.Object3D(); o.position.set(...pos); parent.add(o); parts[name] = o; return o; }

function buildTruck(D) {
  // bus: gold MLI with a black MLI band, white radiators, aluminium longerons
  const shell = mesh(new THREE.BoxGeometry(BUS.w, BUS.h, BUS.l), M.mli); xrayHide.push(shell);
  const band = mesh(new THREE.BoxGeometry(BUS.w + 0.012, 0.22, BUS.l + 0.012), M.mliBlack, null, [0, -BUS.h / 2 + 0.16, 0]); xrayHide.push(band);
  for (const s of [1, -1]) xrayHide.push(mesh(new THREE.BoxGeometry(BUS.w * 0.86, 0.02, BUS.l * 0.8), M.radiator, null, [0, s * (BUS.h / 2 + 0.011), 0]));
  for (const x of [-1, 1]) for (const y of [-1, 1]) mesh(new THREE.BoxGeometry(0.04, 0.04, BUS.l + 0.02), M.alu, null, [x * BUS.w / 2, y * BUS.h / 2, 0]);
  for (const x of [-1, 1]) for (const z of [-1, 1]) mesh(new THREE.BoxGeometry(0.04, BUS.h, 0.04), M.alu, null, [x * BUS.w / 2, 0, z * BUS.l / 2]);
  // launch adapter (Marman) ring on -Y, where it bolted to the rideshare plate
  mesh(new THREE.CylinderGeometry(0.47, 0.47, 0.06, 48, 1, true), M.alu, null, [0, -BUS.h / 2 - 0.03, -0.1]);
  mesh(new THREE.TorusGeometry(0.47, 0.022, 8, 48), M.steel, null, [0, -BUS.h / 2 - 0.06, -0.1], [Math.PI / 2, 0, 0]);

  // inside: xenon tank sized from the propellant mass (~1.6 kg/L supercritical storage [ASSUMPTION])
  const xeKg = D.mass.xenon_kg * 1.1, vol = xeKg / 1600;
  const tankR = 0.36, tankL = Math.max(0.2, (vol - (4 / 3) * Math.PI * tankR ** 3) / (Math.PI * tankR ** 2));
  const tank = new THREE.Group(); truck.add(tank); tank.position.set(0, 0.08, -0.15);
  mesh(new THREE.CylinderGeometry(tankR, tankR, tankL, 32), M.tank, tank, [0, 0, 0], [Math.PI / 2, 0, 0]);
  for (const s of [1, -1]) mesh(new THREE.SphereGeometry(tankR, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), M.tank, tank, [0, 0, s * tankL / 2], [s * Math.PI / 2, 0, 0]);
  tank.scale.setScalar(Math.min(1, (BUS.l * 0.62) / (tankL + 2 * tankR)));
  anchor('xenon', tank, [0, tankR, 0]);
  for (const x of [-0.45, 0.45]) mesh(new THREE.BoxGeometry(0.32, 0.22, 0.42), M.dark, null, [x, -0.38, -0.55]);
  for (let k = 0; k < 4; k++) mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.07, 24), M.steel, null, [-0.45 + 0.3 * k, -0.42, 0.45]);

  // two Hall thrusters on gimbal brackets, each with its external cathode
  const thr = [];
  const hallProfile = [[0.12, 0], [0.175, -0.02], [0.18, -0.14], [0.165, -0.17], [0.07, -0.17], [0.06, -0.05], [0.0, -0.05]];
  for (const x of [-0.38, 0.38]) {
    const g = new THREE.Group(); truck.add(g); g.position.set(x, -0.05, -BUS.l / 2);
    mesh(new THREE.BoxGeometry(0.42, 0.04, 0.14), M.alu, g, [0, -0.2, -0.05]);
    for (const s of [1, -1]) mesh(new THREE.BoxGeometry(0.04, 0.38, 0.12), M.alu, g, [s * 0.19, 0, -0.06]);
    const body = lathe(hallProfile, 40, M.dark); body.rotation.x = -Math.PI / 2; g.add(body);
    const ring = mesh(new THREE.RingGeometry(0.08, 0.15, 48), M.thrusterRing, g, [0, 0, -0.172], [0, Math.PI, 0]);
    mesh(new THREE.CylinderGeometry(0.045, 0.045, 0.02, 24), M.steel, g, [0, 0, -0.175], [Math.PI / 2, 0, 0]);
    mesh(new THREE.CylinderGeometry(0.018, 0.018, 0.18, 12), M.steel, g, [0.2, 0.12, -0.12], [Math.PI / 2 - 0.4, 0, -0.5]);
    const plume = mesh(new THREE.ConeGeometry(0.5, 3.2, 40, 1, true), additive(COL.xenon, 0), g, [0, 0, -1.78], [-Math.PI / 2, 0, 0]);
    const core = mesh(new THREE.ConeGeometry(0.16, 1.4, 32, 1, true), additive(0xdcd6ff, 0), g, [0, 0, -0.88], [-Math.PI / 2, 0, 0]);
    thr.push({ ring, plume, core });
  }
  for (const x of [-0.38, 0.38]) truck.add(tube([[0, -0.1, -0.7], [x * 0.5, -0.25, -0.85], [x, -0.24, -BUS.l / 2 - 0.02], [x, -0.18, -BUS.l / 2 - 0.08]], 0.012, M.steel));
  anchor('thrusters', truck, [0, -0.05, -BUS.l / 2 - 0.2]);

  // small steering (RCS) thrusters at the top corners, with puff sprites
  const rcs = [];
  for (const x of [-1, 1]) for (const z of [-1, 1]) {
    const q = new THREE.Group(); truck.add(q); q.position.set(x * (BUS.w / 2 + 0.02), BUS.h / 2 - 0.1, z * (BUS.l / 2 - 0.12));
    mesh(new THREE.BoxGeometry(0.08, 0.08, 0.08), M.dark, q);
    for (const d of [[x, 0, 0], [0, 1, 0], [0, 0, z]]) {
      const n = mesh(new THREE.ConeGeometry(0.022, 0.05, 10, 1, true), M.steel, q, [d[0] * 0.06, d[1] * 0.06, d[2] * 0.06]);
      n.quaternion.setFromUnitVectors(new THREE.Vector3(0, -1, 0), new THREE.Vector3(...d));
    }
    const puff = new THREE.Sprite(new THREE.SpriteMaterial({ map: softDot, color: 0xffffff, transparent: true, opacity: 0, depthWrite: false }));
    puff.position.set(x * 0.25, 0.1, z * 0.25); puff.scale.setScalar(0.5); q.add(puff);
    rcs.push(puff);
  }

  // antenna, star trackers, cameras/lidar
  const dish = new THREE.Group(); truck.add(dish); dish.position.set(0.35, BUS.h / 2 + 0.03, -0.45);
  mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.35, 12), M.alu, dish, [0, 0.17, 0]);
  mesh(new THREE.SphereGeometry(0.32, 40, 14, 0, Math.PI * 2, 0, 0.55), M.white, dish, [0, 0.62, 0], [Math.PI, 0, 0]);
  mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.18, 10), M.alu, dish, [0, 0.44, 0]);
  anchor('radio', dish, [0, 0.45, 0]);
  for (const z of [-0.2, 0.15]) {
    const st = new THREE.Group(); truck.add(st); st.position.set(-0.5, BUS.h / 2 + 0.02, z); st.rotation.z = 0.5;
    mesh(new THREE.BoxGeometry(0.12, 0.08, 0.12), M.dark, st);
    const baffle = lathe([[0.04, 0], [0.04, 0.05], [0.08, 0.16], [0.075, 0.16], [0.035, 0.05]], 24, M.black); baffle.position.y = 0.04; st.add(baffle);
  }
  const eye = new THREE.Group(); truck.add(eye); eye.position.set(-0.45, BUS.h / 2 - 0.05, BUS.l / 2 + 0.05);
  mesh(new THREE.BoxGeometry(0.22, 0.18, 0.2), M.mliBlack, eye);
  mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.06, 24), M.alu, eye, [0, 0, 0.12], [Math.PI / 2, 0, 0]);
  mesh(new THREE.CircleGeometry(0.045, 24), M.lens, eye, [0, 0, 0.152]);
  mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.065, 24), M.dark, eye, [0.07, 0.04, 0.12], [Math.PI / 2, 0, 0]);
  anchor('eyes', eye, [0, 0.1, 0.1]);

  // solar wings: 4 framed panels each, accordion-folded against the sides when stowed
  const wings = [];
  const PW = 1.15, PH = 1.55;
  for (const s of [1, -1]) {
    const root = new THREE.Group(); truck.add(root); root.position.set(s * (BUS.w / 2 + 0.02), 0.05, -0.1);
    mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.1, 20), M.dark, root, [0, 0, 0], [0, 0, Math.PI / 2]);
    const yoke = new THREE.Group(); root.add(yoke);
    for (const z of [-0.35, 0.35]) mesh(new THREE.BoxGeometry(0.55, 0.03, 0.03), M.alu, yoke, [s * 0.275, 0, z * 0.5]);
    const hinge0 = new THREE.Group(); root.add(hinge0); hinge0.position.set(s * 0.55, 0, 0);
    let parent = hinge0; const hinges = [hinge0];
    for (let k = 0; k < 4; k++) {
      const p = new THREE.Group(); parent.add(p);
      if (k > 0) { p.position.set(s * PW, 0, 0); hinges.push(p); }
      mesh(new THREE.BoxGeometry(PW - 0.03, 0.022, PH), M.cellBack, p, [s * PW / 2, -0.004, 0]);
      mesh(new THREE.PlaneGeometry(PW - 0.07, PH - 0.06), M.cells, p, [s * PW / 2, 0.0085, 0], [-Math.PI / 2, 0, 0]);
      for (const z of [-PH / 2, PH / 2]) mesh(new THREE.BoxGeometry(PW - 0.03, 0.03, 0.025), M.alu, p, [s * PW / 2, 0, z]);
      for (const xx of [0.015, PW - 0.015]) mesh(new THREE.BoxGeometry(0.025, 0.03, PH), M.alu, p, [s * xx, 0, 0]);
      parent = p;
    }
    wings.push({ s, root, yoke, hinges });
    if (s > 0) anchor('wings', hinges[2], [s * PW * 0.5, 0.05, 0]);
  }

  // kit magazine: a framed carousel of ten kits ahead of the bus
  const mag = new THREE.Group(); truck.add(mag); mag.position.set(0, 0, MAG.z0);
  mesh(new THREE.CylinderGeometry(0.34, 0.34, MAG.len, 32), M.mliBlack, mag, [0, 0, MAG.len / 2], [Math.PI / 2, 0, 0]);
  for (const z of [0.04, MAG.len - 0.04]) mesh(new THREE.TorusGeometry(MAG.r, 0.03, 10, 72), M.alu, mag, [0, 0, z]);
  for (let k = 0; k < 10; k++) {
    const a = (k / 10) * Math.PI * 2;
    mesh(new THREE.BoxGeometry(0.035, 0.035, MAG.len), M.alu, mag, [Math.cos(a) * (MAG.r - 0.2), Math.sin(a) * (MAG.r - 0.2), MAG.len / 2]);
    const spoke = mesh(new THREE.BoxGeometry(MAG.r - 0.34, 0.03, 0.03), M.alu, mag, [Math.cos(a) * (MAG.r + 0.34) / 2, Math.sin(a) * (MAG.r + 0.34) / 2, MAG.len - 0.04]);
    spoke.rotation.z = a;
  }
  const kits = [];
  const kmax = Math.max(...D.mass.kits_kg);
  D.mass.kits_kg.forEach((kg, k) => {
    const a = ((k + 0.5) / 10) * Math.PI * 2;
    const kit = makeKit(kg, kmax);
    kit.position.set(Math.cos(a) * MAG.r, Math.sin(a) * MAG.r, MAG.len / 2);
    kit.rotation.z = a;
    kit.userData.home = { pos: kit.position.clone(), rot: kit.rotation.clone(), parent: mag };
    mag.add(kit); kits.push(kit);
  });
  anchor('kits', mag, [0, MAG.r + 0.3, MAG.len / 2]);
  // telescoping boom that pushes a kit onto the target (three nested tubes)
  const boom = new THREE.Group(); mag.add(boom); boom.position.set(0, -0.2, MAG.len);
  const booms = [0.07, 0.055, 0.04].map((r, k) => mesh(new THREE.CylinderGeometry(r, r, 1, 20), [M.alu, M.steel, M.alu][k], boom, [0, 0, 0], [Math.PI / 2, 0, 0]));

  // capture arm on the nose
  const arm = makeArm(); arm.base.position.set(0.25, 0.2, MAG.len); mag.add(arm.base);
  anchor('arm', arm.wrist, [0, 0.12, 0]);
  anchor('bus', truck, [-BUS.w / 2, 0.2, 0.2]);
  shadowAll(truck);
  scene.add(truck);
  return { wings, thr, kits, mag, arm, tank, rcs, boom, booms };
}

// a deorbit kit: composite motor case, contoured nozzle, latch ring with three claws, avionics box + status light
function makeKit(kg, kmax) {
  const g = new THREE.Group();
  const len = 0.36 + 0.32 * (kg / kmax), r = 0.17;
  const body = new THREE.Mesh(new THREE.CylinderGeometry(r, r, len, 32), M.carbon); body.rotation.x = Math.PI / 2; g.add(body);
  for (const z of [len / 2 - 0.02, -len / 2 + 0.02]) {
    const dome = new THREE.Mesh(new THREE.CylinderGeometry(r * 0.98, r, 0.04, 32), M.alu); dome.rotation.x = Math.PI / 2; dome.position.z = z; g.add(dome);
  }
  const band = new THREE.Mesh(new THREE.CylinderGeometry(r + 0.006, r + 0.006, 0.06, 32), M.orange); band.rotation.x = Math.PI / 2; band.position.z = len * 0.22; g.add(band);
  const latch = new THREE.Mesh(new THREE.TorusGeometry(r * 0.85, 0.02, 10, 32), M.steel); latch.position.z = len / 2 + 0.05; g.add(latch);
  const claws = [];
  for (let k = 0; k < 3; k++) {
    const h = new THREE.Group(); h.rotation.z = k * Math.PI * 2 / 3; h.position.z = len / 2 + 0.05; g.add(h);
    const pivot = new THREE.Group(); pivot.position.set(0, r * 0.85, 0); h.add(pivot);
    const c = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.03, 0.12), M.dark); c.position.z = 0.06; pivot.add(c);
    claws.push(pivot);
  }
  const box = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.08, 0.1), M.mliSilver); box.position.set(0, r + 0.03, len * 0.3); g.add(box);
  const led = new THREE.Mesh(new THREE.SphereGeometry(0.014, 10, 8), M.led.clone()); led.position.set(0.04, r + 0.075, len * 0.3); g.add(led);
  const noz = lathe(bell(0.045, 0.11, 0.18), 32, M.nozzle); noz.rotation.x = -Math.PI / 2; noz.position.z = -len / 2; g.add(noz);
  const fire = new THREE.Mesh(new THREE.ConeGeometry(0.2, 2.2, 28, 1, true), additive(0xffb060, 0)); fire.rotation.x = -Math.PI / 2; fire.position.z = -len / 2 - 1.28; g.add(fire);
  const core = new THREE.Mesh(new THREE.ConeGeometry(0.08, 0.7, 20, 1, true), additive(0xfff1d6, 0)); core.rotation.x = -Math.PI / 2; core.position.z = -len / 2 - 0.52; g.add(core);
  g.userData = { len, fire, core, claws, led };
  shadowAll(g);
  return g;
}

// arm: base yaw, shoulder and elbow pitch, wrist with camera, work light and a three-finger gripper
function makeArm() {
  const L1 = 1.2, L2 = 1.05;
  const base = new THREE.Group();
  const yaw = new THREE.Group(); base.add(yaw);
  const turret = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.16, 0.14, 24), M.white); turret.rotation.x = Math.PI / 2; turret.position.z = 0.07; yaw.add(turret);
  const shoulder = new THREE.Group(); shoulder.position.z = 0.16; yaw.add(shoulder);
  const joint = (parent, r) => {
    const j = new THREE.Mesh(new THREE.CylinderGeometry(r, r, r * 1.6, 24), M.white); j.rotation.z = Math.PI / 2; parent.add(j);
    const ring = new THREE.Mesh(new THREE.CylinderGeometry(r * 1.02, r * 1.02, r * 0.3, 24), M.dark); ring.rotation.z = Math.PI / 2; parent.add(ring);
  };
  joint(shoulder, 0.1);
  const link1 = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.065, L1, 20), M.white); link1.position.y = L1 / 2; shoulder.add(link1);
  const cable1 = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, L1 * 0.9, 8), M.dark); cable1.position.set(0.07, L1 / 2, 0); shoulder.add(cable1);
  const elbow = new THREE.Group(); elbow.position.y = L1; shoulder.add(elbow);
  joint(elbow, 0.085);
  const link2 = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.055, L2, 20), M.white); link2.position.y = L2 / 2; elbow.add(link2);
  const wrist = new THREE.Group(); wrist.position.y = L2; elbow.add(wrist);
  wrist.add(new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.075, 0.1, 20), M.dark));
  const cam = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.05, 0.05), M.dark); cam.position.set(0.09, 0.03, 0); wrist.add(cam);
  const light = new THREE.SpotLight(0xfff5e8, 0, 9, 0.5, 0.6, 1.2); light.position.set(0.09, 0.06, 0); wrist.add(light);
  const lt = new THREE.Object3D(); lt.position.set(0.09, 2, 0); wrist.add(lt); light.target = lt;
  const fingers = [];
  for (let k = 0; k < 3; k++) {
    const f = new THREE.Group(); f.rotation.y = (k / 3) * Math.PI * 2; wrist.add(f);
    const hinge = new THREE.Group(); hinge.position.set(0.06, 0.05, 0); f.add(hinge);
    const bone = new THREE.Mesh(new THREE.BoxGeometry(0.028, 0.17, 0.04), M.orange); bone.position.y = 0.085; hinge.add(bone);
    const tip = new THREE.Mesh(new THREE.BoxGeometry(0.028, 0.05, 0.04), M.dark); tip.position.set(-0.02, 0.17, 0); tip.rotation.z = 0.6; hinge.add(tip);
    fingers.push(hinge);
  }
  return { base, yaw, shoulder, elbow, wrist, fingers, light, L1, L2 };
}
function armReach(arm, target, grip) {          // target in the arm-base frame
  arm.yaw.rotation.z = Math.atan2(-target.x, target.y);
  const r = Math.hypot(target.x, target.y), z = target.z - 0.16;
  const d = clamp(Math.hypot(r, z), 0.25, arm.L1 + arm.L2 - 1e-3);
  const elbow = Math.acos(clamp((d * d - arm.L1 ** 2 - arm.L2 ** 2) / (2 * arm.L1 * arm.L2), -1, 1));
  const sh = Math.atan2(z, r) + Math.atan2(arm.L2 * Math.sin(elbow), arm.L1 + arm.L2 * Math.cos(elbow));
  arm.shoulder.rotation.x = sh;
  arm.elbow.rotation.x = -elbow;
  arm.wrist.rotation.x = 0;
  arm.fingers.forEach((f) => { f.rotation.z = -0.1 - 0.6 * (1 - grip); });
}
function armStow(arm, grip = 0.6) {
  arm.yaw.rotation.z = 0.5; arm.shoulder.rotation.x = 0.2; arm.elbow.rotation.x = 2.75; arm.wrist.rotation.x = 0.15;
  arm.fingers.forEach((f) => { f.rotation.z = -0.1 - 0.6 * (1 - grip); });
}
function setWings(T, d) {
  const e = smooth(d);
  for (const w of T.wings) {
    w.hinges.forEach((h, k) => {
      if (k === 0) h.rotation.z = w.s * (1 - e) * (Math.PI / 2);
      else h.rotation.z = w.s * (k % 2 ? -1 : 1) * (1 - e) * Math.PI * 0.985;
    });
    w.yoke.scale.x = Math.max(0.05, e);
    w.hinges[0].position.x = w.s * (0.06 + 0.49 * e);
  }
}
function setThrust(T, on) {
  for (const t of T.thr) {
    t.ring.material.emissiveIntensity = 3.0 * on;
    t.plume.material.opacity = 0.28 * on;
    t.core.material.opacity = 0.6 * on;
  }
}
function setRcs(T, t, events) {            // events: [[time, index], ...]; index -1 = all four
  T.rcs.forEach((p, k) => {
    let o = 0;
    for (const [te, i] of events) if (i === k || i === -1) o = Math.max(o, pulse(t - te, 0.35));
    p.material.opacity = 0.85 * o; p.scale.setScalar(0.25 + 0.6 * o);
  });
}
function setXray(on) {
  for (const m of xrayHide) {
    m.material = m.material.clone();
    m.material.transparent = on; m.material.opacity = on ? 0.14 : 1; m.material.depthWrite = !on;
    m.castShadow = !on;
  }
}

// ------------------------------------------------------------------ a spent rocket stage (sized from data)
function makeStage(S) {
  const g = new THREE.Group();
  const R = S.diameter_m / 2, L = S.length_m;
  const heatMap = canvasTex(8, 256, (c, w, h) => {                    // re-entry heating: hottest at the leading (nose) end
    const grd = c.createLinearGradient(0, h, 0, 0); grd.addColorStop(0, '#000'); grd.addColorStop(0.55, '#200'); grd.addColorStop(1, '#fff');
    c.fillStyle = grd; c.fillRect(0, 0, w, h);
  });
  const paint = new THREE.MeshStandardMaterial({ map: stagePaint(31), roughness: 0.78, metalness: 0.12, emissive: 0xff6a20, emissiveIntensity: 0, emissiveMap: heatMap });
  const tankL = L * 0.62, mid = L * 0.12;
  const body = new THREE.Mesh(new THREE.CylinderGeometry(R, R, tankL, 64), paint); body.position.y = mid; g.add(body);
  for (let k = 0; k <= 4; k++) {                                         // weld rings
    const w = new THREE.Mesh(new THREE.TorusGeometry(R * 1.003, 0.018, 8, 64), M.alu); w.rotation.x = Math.PI / 2;
    w.position.y = mid - tankL / 2 + (k / 4) * tankL; g.add(w);
  }
  // forward end: equipment bay with MLI patches, payload-adapter cone and the grapple ring
  const top = mid + tankL / 2;
  const bay = new THREE.Mesh(new THREE.CylinderGeometry(R * 0.98, R, 0.35, 64), M.mliBlack); bay.position.y = top + 0.175; g.add(bay);
  for (let k = 0; k < 3; k++) {
    const a = k * 2.1, p = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.22, 0.05), M.mli);
    p.position.set(Math.cos(a) * R * 1.0, top + 0.18, Math.sin(a) * R * 1.0); p.lookAt(0, top + 0.18, 0); g.add(p);
  }
  const ringR = Math.max(0.35, R * 0.48);
  const cone = new THREE.Mesh(new THREE.CylinderGeometry(ringR, R * 0.96, 0.45, 64, 1, true), M.alu); cone.position.y = top + 0.575; g.add(cone);
  const plate = new THREE.Mesh(new THREE.CircleGeometry(ringR, 48), M.dark); plate.rotation.x = -Math.PI / 2; plate.position.y = top + 0.8; g.add(plate);
  const ring = new THREE.Mesh(new THREE.TorusGeometry(ringR, 0.035, 12, 64), M.steel); ring.rotation.x = Math.PI / 2; ring.position.y = top + 0.8; g.add(ring);
  for (let k = 0; k < 24; k++) { const b = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, 0.03, 6), M.dark); const a = k * Math.PI / 12; b.position.set(Math.cos(a) * ringR, top + 0.83, Math.sin(a) * ringR); g.add(b); }
  // aft end: skirt, thrust frame, engine with turbopump and a contoured bell, attitude-control pods
  const bot = mid - tankL / 2;
  const skirt = new THREE.Mesh(new THREE.CylinderGeometry(R, R * 0.97, 0.5, 64, 1, true), paint); skirt.position.y = bot - 0.25; g.add(skirt);
  for (let k = 0; k < 6; k++) {
    const a = k * Math.PI / 3;
    g.add(tube([[Math.cos(a) * R * 0.85, bot - 0.45, Math.sin(a) * R * 0.85], [Math.cos(a) * 0.25, bot - 0.9, Math.sin(a) * 0.25]], 0.025, M.alu));
  }
  const chamber = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.2, 0.45, 32), M.steel); chamber.position.y = bot - 1.0; g.add(chamber);
  const pump = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.32, 0.22), M.dark); pump.position.set(0.32, bot - 0.95, 0); g.add(pump);
  const nozLen = Math.min(1.4, L * 0.18), exitR = Math.min(R * 0.7, 0.75);
  const noz = lathe(bell(0.14, exitR, nozLen), 48, M.nozzle); noz.position.y = bot - 1.22; g.add(noz);
  const nozIn = lathe(bell(0.135, exitR - 0.01, nozLen), 48, M.nozzleIn); nozIn.position.y = bot - 1.22; g.add(nozIn);
  for (const s of [1, -1]) {
    const pod = new THREE.Mesh(new THREE.BoxGeometry(0.22, 0.3, 0.18), M.dark); pod.position.set(s * (R + 0.08), bot - 0.1, 0); g.add(pod);
    const pn = lathe(bell(0.015, 0.04, 0.07, 6), 12, M.nozzle); pn.position.set(s * (R + 0.08), bot - 0.25, 0); g.add(pn);
  }
  const dock = new THREE.Object3D(); dock.position.y = top + 0.82; g.add(dock);
  // plasma sheath for re-entry: glowing shells around the leading (nose) end and a long trailing wake
  const sheath = new THREE.Group(); g.add(sheath);
  const glows = [];
  for (let k = 0; k < 14; k++) {                                         // soft glow: bright at the nose, fading down the wake
    const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: softDot, color: k < 2 ? 0xffe2b8 : 0xff7a2a, transparent: true, opacity: 0,
      blending: THREE.AdditiveBlending, depthWrite: false, toneMapped: false }));
    s.position.y = top + 0.9 - k * L * 0.32;
    s.scale.setScalar(R * (k < 2 ? 4.2 : 3.4 - k * 0.12));
    s.userData.base = Math.pow(0.86, k) * (k < 2 ? 1 : 0.7);
    sheath.add(s); glows.push(s);
  }
  g.userData = { dock, ringR, top: top + 0.8, paint, sheath: glows, length: L, radius: R };
  shadowAll(g);
  return g;
}

// ------------------------------------------------------------------ Earth: a globe (journey) and a backdrop (close-ups)
const RE_KM = 6378.137;
function updateAtmo(earthGroup) { setEarthSun(earthGroup, SUN_DIR); }   // NASA Earth (earth.js): world-space sun
const world = new THREE.Group(); world.visible = false; scene.add(world);
let globe, backdrop;
function geo(latDeg, lonDeg, r = 1) {
  const p = latDeg * Math.PI / 180, l = lonDeg * Math.PI / 180;
  return new THREE.Vector3(r * Math.cos(p) * Math.cos(l), r * Math.sin(p), -r * Math.cos(p) * Math.sin(l));
}
function orbitPoint(raanDeg, incDeg, u, r) {
  const O = raanDeg * Math.PI / 180, i = incDeg * Math.PI / 180, x = Math.cos(u), y = Math.sin(u);
  const X = x * Math.cos(O) - y * Math.cos(i) * Math.sin(O), Y = x * Math.sin(O) + y * Math.cos(i) * Math.cos(O), Z = y * Math.sin(i);
  return new THREE.Vector3(r * X, r * Z, -r * Y);
}
function ring(raan, inc, r, color, opacity, dashed) {
  const pts = [];
  for (let k = 0; k <= 256; k++) pts.push(orbitPoint(raan, inc, (k / 256) * Math.PI * 2, r));
  const g = new THREE.BufferGeometry().setFromPoints(pts);
  const mat = dashed ? new THREE.LineDashedMaterial({ color, transparent: true, opacity, dashSize: 0.03, gapSize: 0.02 })
    : new THREE.LineBasicMaterial({ color, transparent: true, opacity });
  const line = new THREE.Line(g, mat);
  if (dashed) line.computeLineDistances();
  return line;
}
function glowDot(color, size) {
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: softDot, color, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending, toneMapped: false }));
  s.scale.setScalar(size);
  return s;
}

// ------------------------------------------------------------------ smoke particles (computed from time, so the timeline can be scrubbed)
function makeSmoke(n, color = 0xc4beb5, additiveBlend = false) {
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(n * 3), 3));
  geo.setAttribute('alpha', new THREE.BufferAttribute(new Float32Array(n), 1));
  geo.setAttribute('size', new THREE.BufferAttribute(new Float32Array(n), 1));
  const mat = new THREE.ShaderMaterial({
    transparent: true, depthWrite: false, blending: additiveBlend ? THREE.AdditiveBlending : THREE.NormalBlending, toneMapped: !additiveBlend,
    uniforms: { map: { value: softDot }, color: { value: new THREE.Color(color) }, scale: { value: 600 } },
    vertexShader: `attribute float alpha; attribute float size; varying float vA; uniform float scale;
      void main(){ vA = alpha; vec4 mv = modelViewMatrix * vec4(position,1.0); gl_PointSize = size * scale / -mv.z; gl_Position = projectionMatrix * mv; }`,
    fragmentShader: `uniform sampler2D map; uniform vec3 color; varying float vA;
      void main(){ vec4 t = texture2D(map, gl_PointCoord); gl_FragColor = vec4(color, t.a * vA); }`,
  });
  const pts = new THREE.Points(geo, mat); pts.frustumCulled = false;
  return pts;
}

// ------------------------------------------------------------------ labels, spec card
const PART_INFO = (D) => [
  { key: 'kits', name: 'Deorbit kits ×10', mass: `${fmt(D.mass.kits_total_kg)} kg`,
    note: `Ten small solid rocket motors, one per object. Each latches onto a dead object and lowers its orbit so it burns up. Heavier objects need bigger kits (${fmt(Math.min(...D.mass.kits_kg))}–${fmt(Math.max(...D.mass.kits_kg))} kg). Together they are ${fmt(100 * D.mass.kits_total_kg / D.mass.launch_kg)}% of launch mass.` },
  { key: 'arm', name: 'Capture arm', mass: '',
    note: 'Grabs the ring where the stage once held its satellite, and holds it while a kit is attached. Capturing a tumbling stage has not been demonstrated yet; we plan to partner on this part.' },
  { key: 'thrusters', name: 'Hall thrusters ×2', mass: '',
    note: `${D.truck.thrusters}. They push gently but for months, using about a fifth of the propellant a chemical engine would.` },
  { key: 'xenon', name: 'Xenon tank', mass: `${fmt(D.mass.xenon_kg)} kg`,
    note: 'Propellant for the climb after launch and the whole route, plus a reserve to dispose of the truck at the end.' },
  { key: 'wings', name: 'Solar wings', mass: '',
    note: `About ${D.truck.power_kw} kW to run both thrusters and the spacecraft. Folded flat for launch, opened once in orbit.` },
  { key: 'eyes', name: 'Cameras + lidar', mass: '', note: 'Measure the target’s spin and distance during the last few metres of approach.' },
  { key: 'radio', name: 'Antenna', mass: '', note: 'Talks to ground stations: tracking, commands and pictures of every capture.' },
  { key: 'bus', name: 'Spacecraft body', mass: `${fmt(D.mass.dry_kg)} kg dry`,
    note: 'Structure, power electronics, reaction wheels, computers and small steering thrusters, wrapped in gold insulation. The dry mass includes the arm, thrusters and wings.' },
];
const labelEls = {};
function buildLabels(D) {
  const ul = $('parts'), box = $('labels');
  PART_INFO(D).forEach((p, k) => {
    const li = document.createElement('li');
    const b = document.createElement('button');
    b.innerHTML = `<span class="n">${k + 1}</span><span>${p.name}</span><span class="m">${p.mass}</span>`;
    b.addEventListener('click', () => selectPart(p, b));
    li.appendChild(b); ul.appendChild(li);
    const el = document.createElement('div'); el.className = 'lbl';
    el.innerHTML = `<i>${k + 1}</i><span>${p.name}</span>`;
    box.appendChild(el); labelEls[p.key] = el;
  });
}
let flyTarget = null;
function selectPart(p, btn) {
  document.querySelectorAll('.parts button').forEach((x) => x.setAttribute('aria-pressed', String(x === btn)));
  $('partNote').textContent = p.note;
  const a = parts[p.key];
  if (a) { const w = new THREE.Vector3(); a.getWorldPosition(w); flyTarget = w; }
}
const tmpV = new THREE.Vector3();
function updateLabels(show) {
  for (const [key, el] of Object.entries(labelEls)) {
    const a = parts[key];
    if (!show || !a || !truck.visible) { el.style.opacity = 0; continue; }
    a.getWorldPosition(tmpV);
    const behind = tmpV.clone().sub(controls.target).dot(camera.position.clone().sub(controls.target)) < 0;
    tmpV.project(camera);
    if (tmpV.z > 1) { el.style.opacity = 0; continue; }
    el.style.left = `${(tmpV.x * 0.5 + 0.5) * innerWidth}px`;
    el.style.top = `${(-tmpV.y * 0.5 + 0.5) * innerHeight}px`;
    el.style.opacity = '';
    el.classList.toggle('dim', behind);
  }
}
function buildSpecs(D) {
  const m = D.mass;
  $('mTotal').innerHTML = `${fmt(m.launch_kg)} <small>kg</small>`;
  const rows = [['Deorbit kits ×10', m.kits_total_kg, 'var(--kit)'], ['Spacecraft (dry)', m.dry_kg, 'var(--ink-2)'], ['Xenon', m.xenon_kg, 'var(--xenon)']];
  $('mBar').innerHTML = rows.map(([, v, c]) => `<span style="width:${(100 * v / m.launch_kg).toFixed(1)}%;background:${c}"></span>`).join('');
  $('mLegend').innerHTML = rows.map(([n, v, c]) => `<i style="background:${c}"></i><span>${n}</span><span class="v">${fmt(v)} kg</span>`).join('');
  const sp = [
    ['Route', D.route.name], ['Stops', `${D.route.stops}`], ['On route', `${fmt(D.route.days)} days`],
    ['Ride to orbit', D.launch.short], ['Climb after launch', `${fmt(D.insertion.days)} days, ${fmt(D.insertion.dv_ms)} m/s`],
    ['Engines', '2 Hall thrusters'], ['Power', `≈${D.truck.power_kw} kW (assumed)`], ['Cost per removal', `$${fmt(D.cost.per_removal_musd, 1)}M (model)`],
  ];
  $('specs').innerHTML = sp.map(([a, b]) => `<dt>${a}</dt><dd>${b}</dd>`).join('');
  $('specNote').textContent = D.note;
}

// ------------------------------------------------------------------ journey
let T, D, stage, journey, plate, smoke, sparks, kitLight;
function buildJourney() {
  const ins = D.insertion;
  const r0 = 1 + ins.from_alt_km / RE_KM, r1 = 1 + ins.to_alt_km / RE_KM;
  const VAN = { lat: 34.63, lon: -120.61 };                        // Vandenberg SLC-4E
  const iS = ins.from_inc_deg * Math.PI / 180, sinU = Math.sin(VAN.lat * Math.PI / 180) / Math.sin(iS);
  const uV = Math.PI - Math.asin(clamp(sinU, -1, 1));
  const raan0 = VAN.lon - Math.atan2(Math.cos(iS) * Math.sin(uV), Math.cos(uV)) * 180 / Math.PI;
  const raan1 = raan0 + D.insertion.raan_shift_deg;
  const grp = new THREE.Group(); world.add(grp);
  const ssoRing = ring(raan0, ins.from_inc_deg, r0, 0x9aa3b5, 0.55, true); grp.add(ssoRing);
  const tgtRing = ring(raan1, ins.to_inc_deg, r1, COL.kit, 0.75, true); grp.add(tgtRing);
  const revs = 36, N = revs * 120, pts = [];
  for (let k = 0; k <= N; k++) {
    const f = k / N;
    pts.push(orbitPoint(lerp(raan0, raan1, f), lerp(ins.from_inc_deg, ins.to_inc_deg, f), uV + f * revs * Math.PI * 2, lerp(r0, r1, f)));
  }
  const spiral = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: COL.truck, transparent: true, opacity: 0.55 }));
  spiral.geometry.setDrawRange(0, 0); grp.add(spiral);
  const pad = geo(VAN.lat, VAN.lon, 1.0), asc = [];
  for (let k = 0; k <= 120; k++) {
    const f = k / 120;
    asc.push(orbitPoint(raan0, ins.from_inc_deg, uV + f * 0.55, 1).normalize().multiplyScalar(lerp(1.0, r0, Math.sqrt(f))));
  }
  asc[0].copy(pad);
  const ascLine = new THREE.Line(new THREE.BufferGeometry().setFromPoints(asc), new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.9 }));
  ascLine.geometry.setDrawRange(0, 0); grp.add(ascLine);
  const rocket = glowDot(0xffe2b0, 0.05); grp.add(rocket);
  const dot = glowDot(COL.truck, 0.06); grp.add(dot);
  const others = [];
  for (let k = 1; k < D.route.stops; k++) {
    const rr = ring(raan1 + D.route.stop_raan_offsets_deg[k], D.route.stop_inc_deg[k], 1 + D.route.stop_alt_km[k] / RE_KM, COL.kit, 0, false);
    grp.add(rr); others.push(rr);
  }
  // re-entry: a fireball with a fading trail, descending through the atmosphere seen over the limb
  const entry = new THREE.Group(); grp.add(entry);
  const trail = [];
  for (let k = 0; k < 60; k++) { const s = glowDot(k < 4 ? 0xfff1d0 : 0xff8a3d, 0.02); entry.add(s); trail.push(s); }
  return { grp, ssoRing, tgtRing, spiral, ascLine, asc, rocket, dot, others, revs, N, pts, raan0, raan1, uV, r0, r1, entry, trail };
}

const CH = () => [
  { key: 'launch', dur: 7, eyebrow: '1 · Launch', title: D.launch.title, text: D.launch.text },
  { key: 'deploy', dur: 7, eyebrow: '2 · Separate and unfold', title: 'Off the rideshare, wings out',
    text: `The truck springs off its launch plate, then unfolds two solar wings (about ${D.truck.power_kw} kW).` },
  { key: 'climb', dur: 12, eyebrow: '3 · Climb and line up', title: `${fmt(D.insertion.days)} days of gentle thrust`,
    text: Math.abs(D.insertion.to_inc_deg - D.insertion.from_inc_deg) > 5
      ? `The rideshare leaves us tilted ${fmt(D.insertion.from_inc_deg, 1)}°. The target stages are tilted ${fmt(D.insertion.to_inc_deg, 1)}°. Earth’s bulge can swing an orbit around the pole but cannot change its tilt, so the thrusters do it: ${fmt(D.insertion.dv_ms)} m/s and ${fmt(D.insertion.xenon_kg)} kg of xenon.`
      : `The first stage is already in the band the rideshare goes to. The truck spirals up from ${fmt(D.insertion.from_alt_km)} km to ${fmt(D.insertion.to_alt_km)} km and tilts ${fmt(Math.abs(D.insertion.to_inc_deg - D.insertion.from_inc_deg), 1)}° while Earth’s bulge swings its orbit into line: ${fmt(D.insertion.dv_ms)} m/s and ${fmt(D.insertion.xenon_kg)} kg of xenon.` },
  { key: 'approach', dur: 13, eyebrow: '4 · Meet the first stage', title: D.stage.name,
    text: `About ${fmt(D.stage.length_m, 1)} m long, ${fmt(D.stage.mass_kg)} kg, slowly tumbling. The truck waits at a safe distance, measures the spin with cameras and lidar, then closes in and circles with the stage so that, to the truck, it looks still.` },
  { key: 'tag', dur: 15, eyebrow: '5 · Tag it', title: 'Grab, stop the spin, latch a kit',
    text: 'The arm grabs the ring where the stage once held its satellite. Small thruster puffs stop the spin. A boom pushes one kit onto the ring; its latches close and its light turns green. Then the arm lets go and the truck backs off.' },
  { key: 'deorbit', dur: 13, eyebrow: '6 · Send it down', title: 'Burn, then burn up',
    text: `From a safe distance the kit fires for under a minute. That lowers the stage’s lowest point to ${D.kit.perigee_km} km, where air drag takes over. Weeks to months later it plunges into the atmosphere at 7.8 km/s, wrapped in glowing plasma, and burns up.` },
  { key: 'driveon', dur: 8, eyebrow: '7 · Drive on', title: `Stop 1 of ${D.route.stops} done`,
    text: `The truck parks at a new height, lets Earth’s bulge line up the next orbit, and hops over. The whole route takes ${fmt(D.route.days)} days. Cost per removal: about $${fmt(D.cost.per_removal_musd, 1)}M in our model, launch included.` },
];
let chapters, totalDur, jt = 0, playing = true, mode = 'truck';

function setGauges(labels, values) {
  const g = $('gauges').children;
  for (let k = 0; k < 4; k++) { g[k].querySelector('b').textContent = values[k]; g[k].querySelector('span').textContent = labels[k]; }
}
function setMode(m) {
  mode = m;
  $('mTruck').setAttribute('aria-pressed', String(m === 'truck'));
  $('mJourney').setAttribute('aria-pressed', String(m === 'journey'));
  $('truckToggles').hidden = m !== 'truck';
  $('partsWrap').hidden = m !== 'truck';
  $('partNote').hidden = m !== 'truck';
  $('right').hidden = m !== 'truck' || innerWidth <= 760;
  $('chapter').hidden = m !== 'journey';
  $('timeline').hidden = m !== 'journey';
  $('tagline').textContent = m === 'truck' ? 'The truck: one electric spacecraft that carries ten deorbit kits.' : `From the launch pad to the first stop, by ${D.launch.short.toLowerCase()}.`;
  controls.autoRotate = m === 'truck' && !reduceMotion;
  controls.autoRotateSpeed = 0.5;
  if (m === 'truck') { resetTruckPose(); setTruckView(); }
  else { jt = 0; playing = true; $('play').textContent = '❚❚'; }
}
function resetTruckPose() {
  world.visible = false; truck.visible = true; backdrop.visible = true;
  truck.position.set(0, 0, 0); truck.quaternion.identity();
  stage.visible = false; plate.visible = false; smoke.visible = false; kitLight.intensity = 0;
  setWings(T, $('tWings').getAttribute('aria-pressed') === 'true' ? 1 : 0);
  setThrust(T, $('tFire').getAttribute('aria-pressed') === 'true' ? 1 : 0);
  setRcs(T, 0, []);
  armStow(T.arm); T.arm.light.intensity = 0;
  T.booms.forEach((b) => { b.visible = false; });
  T.kits.forEach(restoreKit);
  placeBackdrop(new THREE.Vector3(0, 0, 0));
  controls.enabled = true;
}
function setTruckView() {
  if (innerWidth <= 760) { camera.position.set(10.5, 6.5, 12); controls.target.set(0, 1.4, 0.5); }
  else { camera.position.set(7, 3.4, 7.8); controls.target.set(-0.7, -0.2, 1.1); }
  controls.minDistance = 4; controls.maxDistance = 60;
}
function restoreKit(kit) {
  const h = kit.userData.home;
  if (kit.parent !== h.parent) h.parent.add(kit);
  kit.position.copy(h.pos); kit.rotation.copy(h.rot); kit.visible = true;
  kit.userData.fire.material.opacity = 0; kit.userData.core.material.opacity = 0;
  kit.userData.claws.forEach((c) => { c.rotation.x = 0.7; });
  kit.userData.led.material.emissive.setHex(0xff3b1f);
}
// the close-up Earth: a 1:1000 globe whose surface sits ~800 m (800 km) below the action
function placeBackdrop(center) { backdrop.position.set(center.x, center.y - 7180, center.z - 1200); backdrop.userData.atmo.visible = true; }
function buildTicks() {
  const box = $('ticks');
  box.style.gridTemplateColumns = chapters.map((c) => `${c.dur}fr`).join(' ');
  chapters.forEach((c, k) => {
    const b = document.createElement('button');
    b.innerHTML = `<div class="rail"><i></i></div>${c.eyebrow.replace(/^\d · /, '')}`;
    b.addEventListener('click', () => { jt = chapters.slice(0, k).reduce((s, x) => s + x.dur, 0) + 0.01; });
    box.appendChild(b);
  });
}

// stage attitude over the close-up chapters: a slow tumble that the truck later stops
const SPIN_AXIS = new THREE.Vector3(0.35, 1, 0.25).normalize();
const SPIN_RATE = 0.06;                                  // rad per animation second
const STAGE_Q0 = new THREE.Quaternion().setFromEuler(new THREE.Euler(Math.PI / 2 + 0.35, 0.2, 0.1));
function spinStops() { const a = chapters[3].dur; return [a + chapters[4].dur * 0.22, a + chapters[4].dur * 0.45]; }
function spinAngle(tc) {                                  // tc: seconds since the approach chapter began
  const [s0, s1] = spinStops();
  if (tc <= s0) return SPIN_RATE * tc;
  const d = Math.min(tc, s1) - s0, Td = s1 - s0;
  return SPIN_RATE * s0 + SPIN_RATE * (d - d * d / (2 * Td));   // rate ramps to zero: detumble
}
function stageQuat(tc) { return new THREE.Quaternion().setFromAxisAngle(SPIN_AXIS, spinAngle(tc)).multiply(STAGE_Q0); }
const TRUCK_FACING = new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), new THREE.Vector3(0, -1, 0));
function truckCoRotating(q, gap) {
  // the truck sits on the stage's nose axis, magazine facing the grapple ring, turning with the stage
  const off = new THREE.Vector3(0, stage.userData.top + gap + MAG.len + BUS.l / 2, 0).applyQuaternion(q);
  return { off, rot: q.clone().multiply(TRUCK_FACING) };
}

const vA = new THREE.Vector3(), vB = new THREE.Vector3(), qA = new THREE.Quaternion();
function journeyFrame(t) {
  let k = 0, acc = 0;
  while (k < chapters.length - 1 && t >= acc + chapters[k].dur) { acc += chapters[k].dur; k++; }
  const c = chapters[k], f = clamp((t - acc) / c.dur, 0, 1), tl = t - acc;
  if (journey.lastK !== k) {
    journey.lastK = k;
    $('chEyebrow').textContent = c.eyebrow; $('chTitle').textContent = c.title; $('chText').textContent = c.text;
    [...$('ticks').children].forEach((b, j) => b.setAttribute('aria-current', String(j === k)));
  }
  [...$('ticks').children].forEach((b, j) => { const done = j < k ? 1 : j > k ? 0 : f; b.querySelector('i').style.width = `${(100 * done).toFixed(1)}%`; });
  const J = journey, ins = D.insertion;
  const earthView = c.key === 'launch' || c.key === 'climb' || c.key === 'driveon';
  world.visible = earthView; truck.visible = !earthView; backdrop.visible = !earthView;
  stage.visible = !earthView && (c.key === 'approach' || c.key === 'tag' || c.key === 'deorbit');
  plate.visible = c.key === 'deploy';
  smoke.visible = c.key === 'deorbit' && f <= 0.62;
  sparks.visible = c.key === 'deorbit' && f > 0.62;
  stage.userData.paint.emissiveIntensity = 0; stage.userData.sheath.forEach((m) => { m.material.opacity = 0; });
  kitLight.intensity = 0;
  controls.enabled = false; controls.autoRotate = false;

  if (k <= 2 || c.key === 'driveon') {
    let day = 0, alt = ins.from_alt_km, inc = ins.from_inc_deg, xe = 0;
    if (c.key === 'launch') alt = ins.from_alt_km * smooth(f * 1.3);
    if (k >= 2) { const p = c.key === 'climb' ? smooth(f) : 1; day = ins.days * p; alt = lerp(ins.from_alt_km, ins.to_alt_km, p); inc = lerp(ins.from_inc_deg, ins.to_inc_deg, p); xe = ins.xenon_kg * p; }
    setGauges(['days since launch', 'altitude, km', 'tilt, °', 'xenon used, kg'], [fmt(day), fmt(alt), fmt(inc, 1), fmt(xe)]);
  }

  if (earthView) {
    T.kits.forEach(restoreKit);
    if (c.key === 'driveon' || c.key === 'deorbit') T.kits[0].visible = false;
    J.ssoRing.material.opacity = c.key === 'launch' ? 0.55 * smooth(f * 2 - 0.6) : c.key === 'deorbit' ? 0 : 0.35;
    J.tgtRing.material.opacity = c.key === 'launch' || c.key === 'deorbit' ? 0 : 0.8;
    J.ascLine.visible = c.key === 'launch'; J.rocket.visible = c.key === 'launch';
    J.spiral.visible = c.key === 'climb' || c.key === 'driveon';
    J.spiral.material.opacity = c.key === 'driveon' ? lerp(0.55, 0.12, smooth(f * 2)) : 0.55;
    J.others.forEach((r, j) => { r.material.opacity = c.key === 'driveon' ? 0.7 * smooth(f * 3 - j * 0.15) : 0; });
    J.entry.visible = c.key === 'deorbit';
    J.dot.visible = c.key !== 'launch' && c.key !== 'deorbit';
    if (c.key === 'launch') {
      const n = Math.floor(smooth(f) * (J.asc.length - 1));
      J.ascLine.geometry.setDrawRange(0, n + 1); J.rocket.position.copy(J.asc[n]);
      camera.position.copy(geo(18, -100, lerp(3.5, 3.9, f))); controls.target.copy(geo(18, -100, 0.15));
    } else if (c.key === 'climb') {
      const e = smooth(f), n = Math.floor(e * J.N);
      J.spiral.geometry.setDrawRange(0, n + 1); J.dot.position.copy(J.pts[n]);
      camera.position.copy(geo(lerp(25, 45, e), -100 + 60 * e, lerp(3.4, 3.9, e))); controls.target.set(0, 0, 0);
    } else if (c.key === 'deorbit') {
      // re-entry, weeks later, seen from orbit just above the limb
      const g = seg(f, 0.62, 1);
      const lat = 10, lon0 = -40;
      const start = geo(lat, lon0, 1.03), end = geo(lat - 4, lon0 + 9, 1.002);
      J.trail.forEach((s, j) => {
        const u = clamp(g * 1.15 - j * 0.012, 0, 1);
        s.position.copy(start).lerp(end, u);
        const hot = smooth((u - 0.15) / 0.3) * (u < 0.98 ? 1 : 0);
        s.material.opacity = hot * (1 - j / J.trail.length);
        s.scale.setScalar((j < 4 ? 0.012 : 0.007) * (1 + 1.5 * hot) * (1 - 0.5 * j / J.trail.length));
      });
      camera.position.copy(geo(lat + 4, lon0 - 38, 1.42)); controls.target.copy(geo(lat - 2, lon0 + 6, 1.03));
      setGauges(['weeks after the burn', 'altitude, km', 'speed, km/s', 'status'], [fmt(lerp(3, 9, g)), fmt(lerp(120, 60, g)), fmt(7.8, 1), g > 0.5 ? 'burning up' : 'entering']);
    } else {
      J.spiral.geometry.setDrawRange(0, J.N + 1);
      J.dot.position.copy(orbitPoint(J.raan1, ins.to_inc_deg, J.uV + J.revs * Math.PI * 2 + f * Math.PI * 1.2, J.r1));
      camera.position.copy(geo(lerp(45, 60, f), lerp(-40, 10, f), lerp(3.9, 4.6, f))); controls.target.set(0, 0, 0);
    }
    camera.lookAt(controls.target);
    updateAtmo(globe);
    return;
  }

  // ---------------- close-ups (metres) ----------------
  T.arm.light.intensity = 0;
  setRcs(T, 0, []);
  T.booms.forEach((b) => { b.visible = false; });
  if (c.key === 'deploy') {
    T.kits.forEach(restoreKit); setThrust(T, 0); armStow(T.arm);
    const sep = smooth(f / 0.35);
    truck.quaternion.identity(); truck.position.set(0, 0.2 + sep * 1.6, 0);
    setWings(T, smooth((f - 0.35) / 0.6));
    setRcs(T, tl, [[2.8, -1]]);
    placeBackdrop(truck.position);
    camera.position.set(lerp(9, 7, f), lerp(1.2, 3.2, f), lerp(8, 9.5, f)); camera.lookAt(0, 0.8 + sep, 0.5);
    setGauges(['days since launch', 'altitude, km', 'tilt, °', 'wings'], ['0', fmt(ins.from_alt_km), fmt(ins.from_inc_deg, 1), f > 0.9 ? 'open' : 'opening']);
    updateAtmo(backdrop);
    return;
  }
  setWings(T, 1);
  const tc = c.key === 'approach' ? tl : c.key === 'tag' ? chapters[3].dur + tl : chapters[3].dur + chapters[4].dur + tl;
  const q = stageQuat(tc);
  stage.position.set(0, 0, 0); stage.quaternion.copy(q);
  placeBackdrop(new THREE.Vector3(0, 0, 0));
  stage.updateMatrixWorld();
  const dockW = new THREE.Vector3(); stage.userData.dock.getWorldPosition(dockW);
  const axis = new THREE.Vector3(0, 1, 0).applyQuaternion(q);           // stage nose direction
  const grapple = () => dockW.clone().add(new THREE.Vector3(stage.userData.ringR, 0, 0).applyQuaternion(q));
  const kit = T.kits[0];

  if (c.key === 'approach') {
    T.kits.forEach(restoreKit); armStow(T.arm); setThrust(T, 0);
    // 0-0.35 hold ~25 m away; 0.35-0.75 close in while starting to turn with the stage; 0.75-1 final metres
    const hold = new THREE.Vector3(3, 2.2, 26);
    const co = truckCoRotating(q, lerp(5, 1.5, smooth(seg(f, 0.75, 1))));
    const m = smooth(seg(f, 0.35, 0.75));
    truck.position.copy(hold).lerp(co.off, m);
    qA.setFromUnitVectors(new THREE.Vector3(0, 0, 1), vA.copy(truck.position).multiplyScalar(-1).normalize());
    truck.quaternion.copy(qA).slerp(co.rot, m);
    setRcs(T, tl, [[1.5, 0], [4.8, 2], [6.1, 1], [7.4, 3], [9.2, -1], [10.6, 0], [11.5, 2]]);
    T.arm.light.intensity = 25 * smooth(seg(f, 0.5, 0.6));
    const reach = smooth(seg(f, 0.82, 1));
    if (reach > 0) {
      truck.updateMatrixWorld();
      armReach(T.arm, new THREE.Vector3(0.1, 0.5, 0.5).lerp(T.arm.base.worldToLocal(grapple()), reach), 0);
    }
    const range = Math.max(0, truck.position.distanceTo(new THREE.Vector3()) - stage.userData.top - MAG.len - BUS.l / 2);
    setGauges(['range to stage, m', 'stage spin, °/s', 'turning with it', 'arm'], [fmt(range, 1), '2.5', m > 0.95 ? 'yes' : 'no', reach > 0 ? 'reaching' : 'stowed']);
    const mid = vB.copy(truck.position).multiplyScalar(0.5);
    const sep = truck.position.length();
    const perp = new THREE.Vector3().crossVectors(truck.position, new THREE.Vector3(0, 1, 0)).normalize();
    camera.position.copy(mid).addScaledVector(perp, -(sep * 0.75 + 9)).add(new THREE.Vector3(0, 3.5 + sep * 0.1, 0));
    camera.lookAt(mid.x, mid.y - 0.5, mid.z);
    updateAtmo(backdrop);
    return;
  }

  const co = truckCoRotating(q, 1.5);
  if (c.key === 'tag') {
    // 0-0.15 grip; 0.15-0.45 detumble; 0.45-0.78 kit out, onto the ring, latch, boom back; 0.78-0.85 release; 0.85-1 back off
    const back = smooth(seg(f, 0.85, 1)) * 4;
    truck.position.copy(co.off).addScaledVector(axis, back); truck.quaternion.copy(co.rot);
    truck.updateMatrixWorld();
    setThrust(T, 0);
    setRcs(T, tl, [[2.5, 0], [3.1, 3], [3.8, 1], [4.6, 2], [5.4, 0], [6.0, 3], [12.9, -1], [13.6, -1]]);
    const grip = smooth(seg(f, 0.04, 0.15)) * (1 - smooth(seg(f, 0.78, 0.84)));
    const reach = 1 - smooth(seg(f, 0.8, 0.95));
    armReach(T.arm, new THREE.Vector3(0.1, 0.5, 0.5).lerp(T.arm.base.worldToLocal(grapple()), reach), grip);
    T.arm.light.intensity = 25;
    const out = smooth(seg(f, 0.45, 0.55)), push = smooth(seg(f, 0.55, 0.66)), latch = smooth(seg(f, 0.66, 0.7)), retract = smooth(seg(f, 0.7, 0.78));
    const boomLen = 0.15 + 1.35 * push * (1 - retract);
    T.booms.forEach((b, j) => { b.visible = out > 0 && retract < 1; const L = Math.max(0.001, boomLen * (1 - j * 0.28)); b.scale.y = L; b.position.z = L / 2; });
    if (out > 0) {
      if (kit.parent !== scene) scene.add(kit);
      const home = new THREE.Vector3(); kit.userData.home.parent.localToWorld(home.copy(kit.userData.home.pos));
      const boomTip = new THREE.Vector3(0, -0.2, MAG.len + 0.15).applyMatrix4(T.mag.matrixWorld);
      const onRing = dockW.clone().addScaledVector(axis, kit.userData.len / 2 + 0.09);
      kit.position.copy(home).lerp(boomTip, out).lerp(onRing, push);
      kit.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), axis.clone().multiplyScalar(-1));
      kit.userData.claws.forEach((cl) => { cl.rotation.x = 0.7 * (1 - latch); });
      kit.userData.led.material.emissive.setHex(latch > 0.9 ? 0x3dff7a : 0xff3b1f);
    } else restoreKit(kit);
    const [s0, s1] = spinStops();
    const spinNow = 2.5 * (1 - seg(tc, s0, s1));
    setGauges(['stage spin, °/s', 'gripper', 'kit', 'backing off, m'], [fmt(spinNow, 1), grip > 0.5 ? 'closed' : 'open', latch > 0.9 ? 'latched' : out > 0 ? 'moving' : 'in magazine', fmt(back, 1)]);
    const view = dockW.clone().addScaledVector(axis, 1.6 + back * 0.5);
    const side = new THREE.Vector3(1, 0.3, 0).cross(axis).normalize();
    camera.position.copy(view).addScaledVector(side, 9.5).addScaledVector(axis, -1.5).add(new THREE.Vector3(0, 2.6, 0)); camera.lookAt(view);
    updateAtmo(backdrop);
    return;
  }

  if (f > 0.62) { reentryFrame(seg(f, 0.62, 1), t, kit); return; }
  // deorbit, close-up part (f < 0.62): truck holds back; the kit fires; stage + kit accelerate away trailing smoke
  const g = seg(f, 0, 0.62);
  truck.position.copy(co.off).addScaledVector(axis, 4 + 10 * g); truck.quaternion.copy(co.rot);
  setThrust(T, 0); armStow(T.arm);
  const ign = 0.18, burnT = Math.max(0, g - ign);
  stage.position.copy(axis).multiplyScalar(-0.5 * 9 * burnT * burnT); stage.updateMatrixWorld();
  stage.userData.dock.getWorldPosition(dockW);
  if (kit.parent !== scene) scene.add(kit);
  kit.position.copy(dockW).addScaledVector(axis, kit.userData.len / 2 + 0.09);
  kit.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), axis.clone().multiplyScalar(-1));
  kit.userData.claws.forEach((cl) => { cl.rotation.x = 0; });
  kit.userData.led.material.emissive.setHex(0x3dff7a);
  const burning = g > ign ? 1 : 0;
  const flick = 0.85 + 0.15 * Math.sin(t * 47) * Math.sin(t * 31);
  kit.userData.fire.material.opacity = 0.9 * burning * flick;
  kit.userData.core.material.opacity = burning;
  kitLight.color.setHex(0xffa860);
  kitLight.position.copy(kit.position).addScaledVector(axis, kit.userData.len / 2 + 0.5);
  kitLight.intensity = burning * 60 * flick;
  // smoke: particle i leaves the (moving) nozzle at its birth time and drifts outward along +axis
  const pos = smoke.geometry.attributes.position, al = smoke.geometry.attributes.alpha, sz = smoke.geometry.attributes.size;
  const n = al.count, rng = mulberry(99);
  for (let i = 0; i < n; i++) {
    const born = ign + (i / n) * 0.82, age = g - born;
    const sx = rng() - 0.5, sy = rng() - 0.5, sz2 = rng() - 0.5;
    if (age < 0) { al.array[i] = 0; continue; }
    const bt = born - ign;
    const base = vA.copy(axis).multiplyScalar(-0.5 * 9 * bt * bt + stage.userData.top + kit.userData.len + 0.3);
    const outD = 2.5 + age * 22;
    pos.setXYZ(i, base.x + axis.x * outD + sx * age * 9, base.y + axis.y * outD + sy * age * 9, base.z + axis.z * outD + sz2 * age * 9);
    al.array[i] = clamp(0.55 * (1 - age / 0.5), 0, 0.55);
    sz.array[i] = 0.6 + age * 14;
  }
  pos.needsUpdate = true; al.needsUpdate = true; sz.needsUpdate = true;
  const bf = Math.min(burnT, 0.42) / 0.42;
  setGauges(['burn, s', 'speed change, m/s', 'lowest point, km', 'stage'], [fmt(bf * 50), fmt(bf * 95), fmt(lerp(D.insertion.to_alt_km, D.kit.perigee_km, smooth(bf))), burning ? 'heading down' : 'kit armed']);
  const mid = stage.position.clone().addScaledVector(axis, 2);
  camera.position.copy(mid).add(new THREE.Vector3(-16, 6, 12)); camera.lookAt(mid);
  updateAtmo(backdrop);
}

// re-entry, weeks after the burn: the stage plunges through ~80 km, wrapped in plasma, shedding sparks
function reentryFrame(g, t, kit) {
  truck.visible = false;
  const S = stage.userData;
  const vel = new THREE.Vector3(1, -0.18, 0.12).normalize();             // direction of travel
  stage.position.set(0, 0, 0);
  stage.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), vel);   // nose (with the spent kit) leads
  stage.rotateY(t * 0.4);
  stage.updateMatrixWorld();
  backdrop.position.set(0, -6378 - 420, -1500);                           // Earth below; we are above most of the air,
  backdrop.userData.atmo.visible = false;                                  // so the sky stays black
  backdrop.rotation.x = 0.35 + 0.02 * g;
  const dockW = new THREE.Vector3(); S.dock.getWorldPosition(dockW);
  if (kit.parent !== scene) scene.add(kit);
  kit.position.copy(dockW).addScaledVector(vel, kit.userData.len / 2 + 0.09);
  kit.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), vel.clone().multiplyScalar(-1));
  kit.userData.fire.material.opacity = 0; kit.userData.core.material.opacity = 0;
  const heat = smooth(seg(g, 0.05, 0.45)), flick = 0.85 + 0.15 * Math.sin(t * 53) * Math.sin(t * 29);
  S.paint.emissiveIntensity = 3.0 * heat;
  S.sheath.forEach((sp, k) => { sp.material.opacity = sp.userData.base * heat * (k < 2 ? flick : 1); });
  kitLight.position.copy(dockW).addScaledVector(vel, 1.2);
  kitLight.color.setHex(0xff8a40); kitLight.intensity = 90 * heat * flick;
  // sparks and melted bits streaming back from the hot end
  const pos = sparks.geometry.attributes.position, al = sparks.geometry.attributes.alpha, sz = sparks.geometry.attributes.size;
  const rng = mulberry(7), n = al.count;
  for (let i = 0; i < n; i++) {
    const phase = rng(), sx = rng() - 0.5, sy = rng() - 0.5, sz2 = rng() - 0.5, spd = 8 + rng() * 22;
    const age = ((g * 6 + phase) % 1);
    const p = dockW.clone().addScaledVector(vel, -age * spd).add(new THREE.Vector3(sx, sy, sz2).multiplyScalar(age * 3 + S.radius * 0.8));
    pos.setXYZ(i, p.x, p.y, p.z);
    al.array[i] = heat * (1 - age) * (0.4 + 0.6 * rng());
    sz.array[i] = 0.15 + 0.5 * rng() * (1 - age);
  }
  pos.needsUpdate = true; al.needsUpdate = true; sz.needsUpdate = true;
  setGauges(['weeks after the burn', 'altitude, km', 'speed, km/s', 'status'], [fmt(lerp(4, 9, g)), fmt(lerp(95, 65, g)), fmt(7.8, 1), heat > 0.6 ? 'burning up' : 'heating']);
  // chase camera: behind and beside the stage, looking forward along its path, horizon below
  const camPos = new THREE.Vector3(-10, 3.2, 8.5).add(new THREE.Vector3(Math.sin(t * 13) * 0.04, Math.sin(t * 17) * 0.04, 0));
  camera.position.copy(camPos); camera.lookAt(1.5, -1.8, 0);
  updateAtmo(backdrop);
}

// ------------------------------------------------------------------ boot
function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false); composer.setSize(w, h);
  camera.aspect = w / h; camera.updateProjectionMatrix();
  if (mode === 'truck') $('right').hidden = w <= 760;
}
addEventListener('resize', resize);
let wingAnim = null;
function bindUI() {
  $('mTruck').onclick = () => setMode('truck');
  $('mJourney').onclick = () => setMode('journey');
  const tog = (id, fn) => { const b = $(id); b.onclick = () => { const on = b.getAttribute('aria-pressed') !== 'true'; b.setAttribute('aria-pressed', String(on)); fn(on); }; };
  tog('tLabels', () => {});
  tog('tXray', setXray);
  tog('tWings', (on) => { wingAnim = { from: on ? 0 : 1, to: on ? 1 : 0, t: 0 }; });
  tog('tFire', (on) => setThrust(T, on ? 1 : 0));
  $('play').onclick = () => { playing = !playing; $('play').textContent = playing ? '❚❚' : '▶'; $('play').setAttribute('aria-label', playing ? 'Pause' : 'Play'); };
  addEventListener('keydown', (e) => { if (e.key === ' ' && mode === 'journey') { e.preventDefault(); $('play').click(); } });
}
const clock = new THREE.Clock();
function loop() {
  const dt = Math.min(clock.getDelta(), 0.05);
  if (mode === 'truck') {
    if (wingAnim) { wingAnim.t = Math.min(1, wingAnim.t + dt / 1.6); setWings(T, lerp(wingAnim.from, wingAnim.to, wingAnim.t)); if (wingAnim.t >= 1) wingAnim = null; }
    if (flyTarget) { controls.target.lerp(flyTarget, 0.08); if (controls.target.distanceTo(flyTarget) < 0.01) flyTarget = null; }
    if ($('tFire').getAttribute('aria-pressed') === 'true') { const p = 0.85 + 0.15 * Math.sin(clock.elapsedTime * 9); T.thr.forEach((x) => { x.plume.material.opacity = 0.28 * p; }); }
    backdrop.rotation.x = 0.35 + clock.elapsedTime * 0.004;
    controls.update();
    updateAtmo(backdrop);
    updateLabels($('tLabels').getAttribute('aria-pressed') === 'true');
  } else {
    if (playing) jt += dt * (reduceMotion ? 0.6 : 1);
    if (jt >= totalDur) jt = 0;
    backdrop.rotation.x = 0.35 + jt * 0.004;
    journeyFrame(jt);
    updateLabels(false);
  }
  composer.render();
  requestAnimationFrame(loop);
}

async function boot() {
  try {
    D = await (await fetch('data/truck.json')).json();
    const tex = await loadEarthTextures('textures/');                     // NASA Blue Marble, Black Marble, clouds
    T = buildTruck(D);
    globe = makeRealEarth(1, tex, { atmo: 1.025 }); world.add(globe);
    backdrop = makeRealEarth(6378, tex, { atmo: 1.016 }); scene.add(backdrop);
    backdrop.rotation.set(0.35, 2.2, 0);
    stage = makeStage(D.stage); stage.visible = false; scene.add(stage);
    plate = new THREE.Group();
    plate.add(new THREE.Mesh(new THREE.CylinderGeometry(1.4, 1.4, 0.12, 64), M.alu));
    for (let k = 0; k < 5; k++) { const a = k * 1.25 + 0.6; const sat = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.6, 0.45), k % 2 ? M.mliBlack : M.mli); sat.position.set(Math.cos(a) * 1.0, 0.36, Math.sin(a) * 1.0); plate.add(sat); }
    plate.position.set(0, -0.62, 0); plate.visible = false; shadowAll(plate); scene.add(plate);
    smoke = makeSmoke(420); smoke.visible = false; scene.add(smoke);
    sparks = makeSmoke(500, 0xffa050, true); sparks.visible = false; scene.add(sparks);
    kitLight = new THREE.PointLight(0xffa860, 0, 25, 1.6); scene.add(kitLight);
    chapters = CH(); totalDur = chapters.reduce((s, c) => s + c.dur, 0);
    journey = buildJourney(); journey.lastK = -1;
    buildLabels(D); buildSpecs(D); buildTicks(); bindUI();
    resize(); setMode(location.hash === '#journey' ? 'journey' : 'truck');
    $('loading').hidden = true;
    window.__ready = true;
    loop();
  } catch (e) {
    $('err').textContent = 'The model could not load. Open it through the demo launcher (Start Demo.bat), not by double-clicking the file. Details: ' + e.message;
    console.error(e);
  }
}
window.__setJourney = (t) => { setMode('journey'); playing = false; jt = t; };
window.__setMode = setMode;
window.__chapters = () => chapters.map((c) => [c.key, c.dur]);
boot();
