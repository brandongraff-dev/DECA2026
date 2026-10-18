// Orbital Curbside: concept model of the truck and its journey to the first stop.
// Everything is sized from data/truck.json, which engine/scripts/export_model.py
// writes from the route and launch results. Units in the truck view: metres.
import * as THREE from './lib/three.module.min.js';
import { OrbitControls } from './lib/OrbitControls.js';
import { RoomEnvironment } from './lib/RoomEnvironment.js';

const $ = (id) => document.getElementById(id);
const fmt = (x, d = 0) => Number(x).toLocaleString('en-US', { minimumFractionDigits: d, maximumFractionDigits: d });
const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
const smooth = (x) => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
const lerp = (a, b, t) => a + (b - a) * t;
const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const COL = { foil: 0xc9a14a, white: 0xe6e5df, dark: 0x2a2d33, steel: 0x8c9099, truck: 0xe8620c,
  xenon: 0x8c7cff, kit: 0xf2b33d, stage: 0x7f847a, cell: 0x15233f };

// ------------------------------------------------------------------ renderer
const host = $('stage');
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
host.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x05070b);
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.35;

const camera = new THREE.PerspectiveCamera(38, 1, 0.05, 2000);
const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.08;
controls.minDistance = 4;
controls.maxDistance = 60;

const sun = new THREE.DirectionalLight(0xfff4e6, 3.2);
sun.position.set(8, 10, 6);
scene.add(sun);
scene.add(new THREE.HemisphereLight(0x8aa6ff, 0x1a1408, 0.35));
const fill = new THREE.DirectionalLight(0x6f86c9, 0.5);
fill.position.set(-6, -3, -8);
scene.add(fill);

// stars: fixed points on a big sphere
(function stars() {
  const n = 2600, pos = new Float32Array(n * 3), rng = mulberry(7);
  for (let k = 0; k < n; k++) {
    const u = rng() * 2 - 1, th = rng() * Math.PI * 2, r = 900, s = Math.sqrt(1 - u * u);
    pos.set([r * s * Math.cos(th), r * u, r * s * Math.sin(th)], k * 3);
  }
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  scene.add(new THREE.Points(g, new THREE.PointsMaterial({ color: 0xc9d2e8, size: 1.6, sizeAttenuation: false, transparent: true, opacity: 0.8 })));
})();

function mulberry(a) { return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

// ------------------------------------------------------------------ procedural textures
function canvasTex(w, h, draw, srgb = true) {
  const c = document.createElement('canvas'); c.width = w; c.height = h;
  draw(c.getContext('2d'), w, h);
  const t = new THREE.CanvasTexture(c);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 4;
  return t;
}
// crinkled multi-layer insulation: random facets, used as a bump map
const foilBump = canvasTex(512, 512, (g, w, h) => {
  const r = mulberry(3);
  g.fillStyle = '#808080'; g.fillRect(0, 0, w, h);
  for (let k = 0; k < 900; k++) {
    const x = r() * w, y = r() * h, s = 10 + r() * 40, v = Math.floor(90 + r() * 90);
    g.fillStyle = `rgb(${v},${v},${v})`;
    g.beginPath(); g.moveTo(x, y);
    for (let j = 0; j < 4; j++) g.lineTo(x + (r() - 0.5) * s * 2, y + (r() - 0.5) * s * 2);
    g.closePath(); g.fill();
  }
}, false);
foilBump.wrapS = foilBump.wrapT = THREE.RepeatWrapping;
// solar cells: navy cells with silver gaps and bus bars
const cellTex = canvasTex(512, 512, (g, w, h) => {
  g.fillStyle = '#c9cdd4'; g.fillRect(0, 0, w, h);
  const nx = 8, ny = 8, gap = 5;
  for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
    const x = i * w / nx + gap, y = j * h / ny + gap, cw = w / nx - 2 * gap, ch = h / ny - 2 * gap;
    const grd = g.createLinearGradient(x, y, x + cw, y + ch);
    grd.addColorStop(0, '#1b2c52'); grd.addColorStop(1, '#0d1730');
    g.fillStyle = grd; g.fillRect(x, y, cw, ch);
    g.fillStyle = 'rgba(200,210,230,0.35)';
    for (let b = 1; b < 4; b++) g.fillRect(x, y + b * ch / 4, cw, 1);
  }
});
// plume: soft gradient along the cone (white at the nozzle, fading out)
const plumeTex = canvasTex(64, 256, (g, w, h) => {
  const grd = g.createLinearGradient(0, h, 0, 0);
  grd.addColorStop(0, 'rgba(255,255,255,1)'); grd.addColorStop(0.15, 'rgba(255,255,255,0.75)');
  grd.addColorStop(1, 'rgba(255,255,255,0)');
  g.fillStyle = grd; g.fillRect(0, 0, w, h);
});

const M = {
  foil: new THREE.MeshStandardMaterial({ color: 0xe0b552, metalness: 0.6, roughness: 0.4, bumpMap: foilBump, bumpScale: 0.9, emissive: 0x3a2808, emissiveIntensity: 0.35 }),
  foilDark: new THREE.MeshStandardMaterial({ color: 0x3a3a3c, metalness: 0.9, roughness: 0.35, bumpMap: foilBump, bumpScale: 1.0 }),
  white: new THREE.MeshStandardMaterial({ color: COL.white, roughness: 0.55, metalness: 0.05 }),
  dark: new THREE.MeshStandardMaterial({ color: COL.dark, roughness: 0.5, metalness: 0.6 }),
  steel: new THREE.MeshStandardMaterial({ color: COL.steel, roughness: 0.35, metalness: 0.9 }),
  cells: new THREE.MeshStandardMaterial({ map: cellTex, roughness: 0.28, metalness: 0.35 }),
  cellBack: new THREE.MeshStandardMaterial({ color: 0xdedcd4, roughness: 0.7 }),
  orange: new THREE.MeshStandardMaterial({ color: COL.truck, roughness: 0.45, metalness: 0.1 }),
  kit: new THREE.MeshStandardMaterial({ color: 0xf0efe9, roughness: 0.5, metalness: 0.05 }),
  stage: new THREE.MeshStandardMaterial({ color: COL.stage, roughness: 0.72, metalness: 0.25 }),
  xenonTank: new THREE.MeshStandardMaterial({ color: 0x9aa3b5, roughness: 0.3, metalness: 0.8 }),
  thrusterRing: new THREE.MeshStandardMaterial({ color: 0x1b1c22, emissive: COL.xenon, emissiveIntensity: 0.0, roughness: 0.4 }),
};
function plumeMat(color, opacity) {
  return new THREE.MeshBasicMaterial({ color, map: plumeTex, transparent: true, opacity, blending: THREE.AdditiveBlending,
    depthWrite: false, side: THREE.DoubleSide });
}

// ------------------------------------------------------------------ the truck
// Frame: +Z forward (capture end), -Z aft (thrusters), wings along +/-X, +Y is "up" (antenna side).
const BUS = { w: 1.5, h: 1.35, l: 1.8 };
const MAG = { r: 0.92, len: 0.78, z0: BUS.l / 2 };       // kit magazine (carousel) ahead of the bus
const truck = new THREE.Group();
const parts = {};                                        // name -> anchor Object3D for labels
const xrayHide = [];                                     // shells that turn see-through

function mesh(geo, mat, parent, pos, rot) {
  const m = new THREE.Mesh(geo, mat);
  if (pos) m.position.set(...pos);
  if (rot) m.rotation.set(...rot);
  (parent || truck).add(m);
  return m;
}
function anchor(name, parent, pos) {
  const o = new THREE.Object3D(); o.position.set(...pos); parent.add(o); parts[name] = o; return o;
}

function buildTruck(D) {
  // bus: gold multi-layer insulation, white radiators on +/-Y
  const shell = mesh(new THREE.BoxGeometry(BUS.w, BUS.h, BUS.l), M.foil);
  xrayHide.push(shell);
  for (const s of [1, -1]) {
    const rad = mesh(new THREE.BoxGeometry(BUS.w * 0.86, 0.02, BUS.l * 0.8), M.white, null, [0, s * (BUS.h / 2 + 0.011), 0]);
    xrayHide.push(rad);
  }
  // frame edges
  const edge = new THREE.LineSegments(new THREE.EdgesGeometry(new THREE.BoxGeometry(BUS.w + 0.01, BUS.h + 0.01, BUS.l + 0.01)),
    new THREE.LineBasicMaterial({ color: 0x5b4a20, transparent: true, opacity: 0.6 }));
  truck.add(edge);
  // launch adapter ring on -Y (bolts to the rideshare plate)
  mesh(new THREE.TorusGeometry(0.42, 0.035, 10, 40), M.steel, null, [0, -BUS.h / 2 - 0.04, -0.1], [Math.PI / 2, 0, 0]);

  // inside (visible in "see inside"): xenon tank sized from the propellant mass, power units, wheels
  // xenon stored supercritical at ~1.6 kg/L [ASSUMPTION typical COPV storage density]
  const xeKg = D.mass.xenon_kg * 1.1;
  const vol = xeKg / 1600;                         // m^3
  const tankR = 0.36, tankL = Math.max(0.2, (vol - (4 / 3) * Math.PI * tankR ** 3) / (Math.PI * tankR ** 2));
  const tank = new THREE.Group(); truck.add(tank); tank.position.set(0, 0.05, -0.15);
  mesh(new THREE.CylinderGeometry(tankR, tankR, tankL, 32), M.xenonTank, tank, [0, 0, 0], [Math.PI / 2, 0, 0]);
  for (const s of [1, -1]) mesh(new THREE.SphereGeometry(tankR, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2), M.xenonTank, tank, [0, 0, s * tankL / 2], [s * Math.PI / 2, 0, 0]);
  tank.scale.setScalar(Math.min(1, (BUS.l * 0.62) / (tankL + 2 * tankR)));   // keep it inside the bus
  anchor('xenon', tank, [0, tankR, 0]);
  for (const x of [-0.45, 0.45]) mesh(new THREE.BoxGeometry(0.32, 0.22, 0.42), M.dark, null, [x, -0.38, -0.55]);    // power units
  for (let k = 0; k < 4; k++) mesh(new THREE.CylinderGeometry(0.11, 0.11, 0.07, 24), M.steel, null, [-0.45 + 0.3 * k, -0.42, 0.45]); // wheels

  // two Hall thrusters on the aft face
  const thr = [];
  for (const x of [-0.38, 0.38]) {
    const g = new THREE.Group(); truck.add(g); g.position.set(x, -0.05, -BUS.l / 2);
    mesh(new THREE.CylinderGeometry(0.16, 0.18, 0.16, 32), M.dark, g, [0, 0, -0.08], [Math.PI / 2, 0, 0]);
    const ring = mesh(new THREE.RingGeometry(0.075, 0.13, 40), M.thrusterRing, g, [0, 0, -0.165], [0, Math.PI, 0]);
    mesh(new THREE.CylinderGeometry(0.035, 0.035, 0.05, 16), M.steel, g, [0, 0, -0.17], [Math.PI / 2, 0, 0]);
    const plume = mesh(new THREE.ConeGeometry(0.42, 2.6, 32, 1, true), plumeMat(COL.xenon, 0.0), g, [0, 0, -1.47], [-Math.PI / 2, 0, 0]);
    const core = mesh(new THREE.ConeGeometry(0.16, 1.3, 24, 1, true), plumeMat(0xd9d4ff, 0.0), g, [0, 0, -0.82], [-Math.PI / 2, 0, 0]);
    thr.push({ ring, plume, core });
  }
  anchor('thrusters', truck, [0, -0.05, -BUS.l / 2 - 0.2]);

  // antenna + sensors
  const dish = new THREE.Group(); truck.add(dish); dish.position.set(0.35, BUS.h / 2 + 0.05, -0.45);
  mesh(new THREE.CylinderGeometry(0.03, 0.03, 0.35, 12), M.steel, dish, [0, 0.17, 0]);
  mesh(new THREE.SphereGeometry(0.32, 32, 12, 0, Math.PI * 2, 0, 0.55), M.white, dish, [0, 0.62, 0], [Math.PI, 0, 0]);
  anchor('radio', dish, [0, 0.45, 0]);
  const eye = new THREE.Group(); truck.add(eye); eye.position.set(-0.45, BUS.h / 2 - 0.05, BUS.l / 2 + 0.05);
  mesh(new THREE.BoxGeometry(0.22, 0.18, 0.2), M.dark, eye);
  mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.06, 20), M.steel, eye, [0, 0, 0.12], [Math.PI / 2, 0, 0]);
  mesh(new THREE.CylinderGeometry(0.05, 0.05, 0.065, 20), M.dark, eye, [0.07, 0, 0.12], [Math.PI / 2, 0, 0]);
  anchor('eyes', eye, [0, 0.1, 0.1]);

  // solar wings: 4 panels each, accordion-folded against the sides when stowed
  const wings = [];
  const PW = 1.15, PH = 1.55;
  for (const s of [1, -1]) {
    const root = new THREE.Group(); truck.add(root); root.position.set(s * (BUS.w / 2 + 0.02), 0.05, -0.1);
    const yoke = mesh(new THREE.BoxGeometry(0.55, 0.04, 0.04), M.steel, root, [s * 0.275, 0, 0]);
    const hinge0 = new THREE.Group(); root.add(hinge0); hinge0.position.set(s * 0.55, 0, 0);
    let parent = hinge0; const hinges = [hinge0];
    for (let k = 0; k < 4; k++) {
      const p = new THREE.Group(); parent.add(p);
      if (k > 0) { p.position.set(s * PW, 0, 0); hinges.push(p); }
      mesh(new THREE.BoxGeometry(PW - 0.03, 0.025, PH), M.cellBack, p, [s * PW / 2, -0.004, 0]);
      const face = mesh(new THREE.PlaneGeometry(PW - 0.05, PH - 0.04), M.cells, p, [s * PW / 2, 0.0095, 0], [-Math.PI / 2, 0, 0]);
      parent = p;
    }
    wings.push({ s, root, yoke, hinges });
    if (s > 0) anchor('wings', hinges[2], [s * PW * 0.5, 0.05, 0]);
  }

  // kit magazine: a ring of deorbit kits ahead of the bus, sized from the real kit masses
  const mag = new THREE.Group(); truck.add(mag); mag.position.set(0, 0, MAG.z0);
  mesh(new THREE.CylinderGeometry(0.34, 0.34, MAG.len, 28), M.dark, mag, [0, 0, MAG.len / 2], [Math.PI / 2, 0, 0]);
  mesh(new THREE.TorusGeometry(MAG.r, 0.025, 8, 60), M.steel, mag, [0, 0, 0.05]);
  mesh(new THREE.TorusGeometry(MAG.r, 0.025, 8, 60), M.steel, mag, [0, 0, MAG.len - 0.05]);
  for (let k = 0; k < 10; k++) {
    const a = (k / 10) * Math.PI * 2;
    mesh(new THREE.BoxGeometry(0.03, 0.03, MAG.len), M.steel, mag, [Math.cos(a) * (MAG.r - 0.18), Math.sin(a) * (MAG.r - 0.18), MAG.len / 2]);
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

  // capture arm on the nose of the magazine
  const arm = makeArm(); arm.base.position.set(0, 0, MAG.len); mag.add(arm.base);
  anchor('arm', arm.wrist, [0, 0.12, 0]);
  anchor('bus', truck, [-BUS.w / 2, 0.2, 0.2]);
  scene.add(truck);
  return { wings, thr, kits, mag, arm, tank };
}

// a deorbit kit: solid motor + clamp band + nozzle; length scales with its mass
function makeKit(kg, kmax) {
  const g = new THREE.Group();
  const len = 0.36 + 0.32 * (kg / kmax), r = 0.17;
  const body = new THREE.Mesh(new THREE.CylinderGeometry(r, r, len, 24), M.kit); body.rotation.x = Math.PI / 2; g.add(body);
  const band = new THREE.Mesh(new THREE.CylinderGeometry(r + 0.006, r + 0.006, 0.07, 24), M.orange); band.rotation.x = Math.PI / 2; band.position.z = len * 0.3; g.add(band);
  const clamp = new THREE.Mesh(new THREE.TorusGeometry(r * 0.75, 0.025, 8, 24), M.dark); clamp.position.z = len / 2 + 0.03; g.add(clamp);
  const noz = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.11, 0.16, 20, 1, true), M.dark); noz.rotation.x = Math.PI / 2; noz.position.z = -len / 2 - 0.07; g.add(noz);
  const fire = new THREE.Mesh(new THREE.ConeGeometry(0.16, 1.6, 20, 1, true), plumeMat(0xffa24a, 0)); fire.rotation.x = -Math.PI / 2; fire.position.z = -len / 2 - 0.95; g.add(fire);
  g.userData = { len, fire };
  return g;
}

// two-link arm: base yaw, shoulder pitch, elbow pitch, wrist + three-finger gripper
function makeArm() {
  const L1 = 1.15, L2 = 1.0;
  const base = new THREE.Group();
  const yaw = new THREE.Group(); base.add(yaw);
  const turret = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.15, 0.12, 20), M.dark); turret.rotation.x = Math.PI / 2; turret.position.z = 0.06; yaw.add(turret);
  const shoulder = new THREE.Group(); shoulder.position.z = 0.14; yaw.add(shoulder);
  const s1 = new THREE.Mesh(new THREE.SphereGeometry(0.1, 16, 12), M.steel); shoulder.add(s1);
  const link1 = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.065, L1, 16), M.white); link1.position.y = L1 / 2; shoulder.add(link1);
  const elbow = new THREE.Group(); elbow.position.y = L1; shoulder.add(elbow);
  elbow.add(new THREE.Mesh(new THREE.SphereGeometry(0.085, 16, 12), M.steel));
  const link2 = new THREE.Mesh(new THREE.CylinderGeometry(0.045, 0.055, L2, 16), M.white); link2.position.y = L2 / 2; elbow.add(link2);
  const wrist = new THREE.Group(); wrist.position.y = L2; elbow.add(wrist);
  wrist.add(new THREE.Mesh(new THREE.CylinderGeometry(0.075, 0.075, 0.09, 16), M.dark));
  const fingers = [];
  for (let k = 0; k < 3; k++) {
    const f = new THREE.Group(); f.rotation.y = (k / 3) * Math.PI * 2; wrist.add(f);
    const hinge = new THREE.Group(); hinge.position.set(0.06, 0.05, 0); f.add(hinge);
    const bone = new THREE.Mesh(new THREE.BoxGeometry(0.025, 0.16, 0.035), M.orange); bone.position.y = 0.08; hinge.add(bone);
    fingers.push(hinge);
  }
  return { base, yaw, shoulder, elbow, wrist, fingers, L1, L2 };
}

// planar 2-link inverse kinematics: point the arm at a target given in the arm base frame
function armReach(arm, target, grip) {
  const yawAng = Math.atan2(target.x, target.y);
  arm.yaw.rotation.z = -yawAng;
  const r = Math.hypot(target.x, target.y), z = target.z - 0.14;
  const d = clamp(Math.hypot(r, z), 0.2, arm.L1 + arm.L2 - 1e-3);
  const cosE = (d * d - arm.L1 ** 2 - arm.L2 ** 2) / (2 * arm.L1 * arm.L2);
  const elbow = Math.acos(clamp(cosE, -1, 1));
  const phi = Math.atan2(z, r);
  const sh = phi + Math.atan2(arm.L2 * Math.sin(elbow), arm.L1 + arm.L2 * Math.cos(elbow));
  // links point along local +Y; a positive turn about X tilts +Y toward +Z (forward)
  arm.shoulder.rotation.x = sh;
  arm.elbow.rotation.x = -elbow;
  arm.wrist.rotation.x = 0;
  arm.fingers.forEach((f) => { f.rotation.z = -0.15 - 0.55 * (1 - grip); });
}
function armStow(arm, grip = 0.6) {
  arm.yaw.rotation.z = 0;
  arm.shoulder.rotation.x = 0.25;
  arm.elbow.rotation.x = 2.7;
  arm.wrist.rotation.x = 0.2;
  arm.fingers.forEach((f) => { f.rotation.z = -0.15 - 0.55 * (1 - grip); });
}

function setWings(T, d) {             // d = 0 stowed, 1 deployed
  const e = smooth(d);
  for (const w of T.wings) {
    w.hinges.forEach((h, k) => {
      if (k === 0) h.rotation.z = w.s * (1 - e) * (Math.PI / 2);
      else h.rotation.z = w.s * (k % 2 ? -1 : 1) * (1 - e) * Math.PI * 0.985;
    });
    w.yoke.scale.x = Math.max(0.05, e);
    w.yoke.position.x = w.s * 0.275 * e;
    w.hinges[0].position.x = w.s * (0.04 + 0.51 * e);
  }
}
function setThrust(T, on) {
  for (const t of T.thr) {
    t.ring.material.emissiveIntensity = 2.6 * on;
    t.plume.material.opacity = 0.32 * on;
    t.core.material.opacity = 0.55 * on;
  }
}
function setXray(on) {
  for (const m of xrayHide) {
    m.material = m.material.clone();
    m.material.transparent = on; m.material.opacity = on ? 0.14 : 1; m.material.depthWrite = !on;
  }
}

// ------------------------------------------------------------------ an SL-8 stage (Kosmos-3M second stage)
function makeStage(S) {
  const g = new THREE.Group();
  const R = S.diameter_m / 2, L = S.length_m;
  const body = new THREE.Mesh(new THREE.CylinderGeometry(R, R, L * 0.82, 40), M.stage); g.add(body);
  const nose = new THREE.Mesh(new THREE.CylinderGeometry(R * 0.55, R, L * 0.08, 40), M.stage); nose.position.y = L * 0.45; g.add(nose);
  const plate = new THREE.Mesh(new THREE.CylinderGeometry(R * 0.55, R * 0.55, 0.05, 40), M.dark); plate.position.y = L * 0.49; g.add(plate);
  const skirt = new THREE.Mesh(new THREE.CylinderGeometry(R, R * 0.9, L * 0.06, 40, 1, true), M.dark); skirt.position.y = -L * 0.44; g.add(skirt);
  const noz = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.55, 0.9, 30, 1, true), M.steel); noz.position.y = -L * 0.47 - 0.25; g.add(noz);
  for (let k = 0; k < 4; k++) {
    const rib = new THREE.Mesh(new THREE.BoxGeometry(0.06, L * 0.8, 0.06), M.dark);
    const a = k * Math.PI / 2; rib.position.set(Math.cos(a) * R, 0, Math.sin(a) * R); g.add(rib);
  }
  // where the kit clamps: the nose plate
  const dock = new THREE.Object3D(); dock.position.y = L * 0.5 + 0.02; g.add(dock);
  g.userData.dock = dock;
  return g;
}

// ------------------------------------------------------------------ the Earth view (1 unit = Earth radius)
const RE_KM = 6378.137;
const world = new THREE.Group(); world.visible = false; scene.add(world);
let earth;
function buildWorld(tex) {
  tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  earth = new THREE.Mesh(new THREE.SphereGeometry(1, 96, 64), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.95, metalness: 0 }));
  world.add(earth);
  const atm = new THREE.Mesh(new THREE.SphereGeometry(1.025, 64, 48), new THREE.MeshBasicMaterial({ color: 0x5fa5ff, transparent: true, opacity: 0.12, side: THREE.BackSide, blending: THREE.AdditiveBlending, depthWrite: false }));
  world.add(atm);
}
// geographic -> three (Y = north), matching the equirectangular texture on SphereGeometry
function geo(latDeg, lonDeg, r = 1) {
  const p = latDeg * Math.PI / 180, l = lonDeg * Math.PI / 180;
  return new THREE.Vector3(r * Math.cos(p) * Math.cos(l), r * Math.sin(p), -r * Math.cos(p) * Math.sin(l));
}
// orbit point (Earth-fixed schematic): node longitude raanDeg, tilt incDeg, argument of latitude u
function orbitPoint(raanDeg, incDeg, u, r) {
  const O = raanDeg * Math.PI / 180, i = incDeg * Math.PI / 180;
  const x = Math.cos(u), y = Math.sin(u);
  const X = x * Math.cos(O) - y * Math.cos(i) * Math.sin(O);
  const Y = x * Math.sin(O) + y * Math.cos(i) * Math.cos(O);
  const Z = y * Math.sin(i);
  return new THREE.Vector3(r * X, r * Z, -r * Y);
}
function ring(raan, inc, r, color, opacity, dashed) {
  const pts = [];
  for (let k = 0; k <= 256; k++) pts.push(orbitPoint(raan, inc, (k / 256) * Math.PI * 2, r));
  const g = new THREE.BufferGeometry().setFromPoints(pts);
  const mat = dashed
    ? new THREE.LineDashedMaterial({ color, transparent: true, opacity, dashSize: 0.03, gapSize: 0.02 })
    : new THREE.LineBasicMaterial({ color, transparent: true, opacity });
  const line = new THREE.Line(g, mat);
  if (dashed) line.computeLineDistances();
  return line;
}
function glowDot(color, size) {
  const t = canvasTex(64, 64, (g, w) => {
    const grd = g.createRadialGradient(w / 2, w / 2, 0, w / 2, w / 2, w / 2);
    grd.addColorStop(0, 'rgba(255,255,255,1)'); grd.addColorStop(0.3, 'rgba(255,255,255,0.8)'); grd.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = grd; g.fillRect(0, 0, w, w);
  });
  const s = new THREE.Sprite(new THREE.SpriteMaterial({ map: t, color, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending }));
  s.scale.setScalar(size);
  return s;
}

// ------------------------------------------------------------------ labels
const PART_INFO = (D) => [
  { key: 'kits', name: 'Deorbit kits ×10', mass: `${fmt(D.mass.kits_total_kg)} kg`,
    note: `Ten small solid rocket motors, one per object. Each clamps onto a dead object and lowers its orbit so it burns up. Heavier objects need bigger kits (${fmt(Math.min(...D.mass.kits_kg))}–${fmt(Math.max(...D.mass.kits_kg))} kg). Together they are ${fmt(100 * D.mass.kits_total_kg / D.mass.launch_kg)}% of launch mass.` },
  { key: 'arm', name: 'Capture arm', mass: '',
    note: 'Grabs a fixture on the dead object and holds it steady while a kit is attached. Capturing a tumbling stage has not been demonstrated yet; we plan to partner on this part.' },
  { key: 'thrusters', name: 'Hall thrusters ×2', mass: '',
    note: `${D.truck.thrusters}. They push gently but for months, using about a fifth of the propellant a chemical engine would.` },
  { key: 'xenon', name: 'Xenon tank', mass: `${fmt(D.mass.xenon_kg)} kg`,
    note: `Propellant for the whole job${D.insertion.dv_ms > 50 ? ', including the climb and tilt change after launch' : ''}, plus a reserve to dispose of the truck at the end.` },
  { key: 'wings', name: 'Solar wings', mass: '',
    note: `About ${D.truck.power_kw} kW to run both thrusters and the spacecraft. Folded flat for launch, opened once in orbit.` },
  { key: 'eyes', name: 'Cameras + lidar', mass: '', note: 'Measure the target’s spin and distance during the last few metres of approach.' },
  { key: 'radio', name: 'Antenna', mass: '', note: 'Talks to ground stations: tracking, commands and pictures of every capture.' },
  { key: 'bus', name: 'Spacecraft body', mass: `${fmt(D.mass.dry_kg)} kg dry`,
    note: 'Structure, power electronics, reaction wheels and computers, wrapped in gold insulation. The dry mass includes the arm, thrusters and wings.' },
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
function selectPart(p, btn) {
  document.querySelectorAll('.parts button').forEach((x) => x.setAttribute('aria-pressed', String(x === btn)));
  $('partNote').textContent = p.note;
  const a = parts[p.key];
  if (a) { const w = new THREE.Vector3(); a.getWorldPosition(w); flyTarget = w; }
}
let flyTarget = null;
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

// ------------------------------------------------------------------ spec card
function buildSpecs(D) {
  const m = D.mass;
  $('mTotal').innerHTML = `${fmt(m.launch_kg)} <small>kg</small>`;
  const rows = [['Deorbit kits ×10', m.kits_total_kg, 'var(--kit)'], ['Spacecraft (dry)', m.dry_kg, 'var(--ink-2)'], ['Xenon', m.xenon_kg, 'var(--xenon)']];
  $('mBar').innerHTML = rows.map(([, v, c]) => `<span style="width:${(100 * v / m.launch_kg).toFixed(1)}%;background:${c}"></span>`).join('');
  $('mLegend').innerHTML = rows.map(([n, v, c]) => `<i style="background:${c}"></i><span>${n}</span><span class="v">${fmt(v)} kg</span>`).join('');
  const sp = [
    ['Route', D.route.name], ['Stops', `${D.route.stops}`], ['On route', `${fmt(D.route.days)} days`],
    ['Ride to orbit', D.launch.short], ['Climb + tilt', D.insertion.dv_ms > 50 ? `${fmt(D.insertion.days)} days, ${fmt(D.insertion.dv_ms)} m/s` : 'none'],
    ['Engines', '2 Hall thrusters'], ['Power', `≈${D.truck.power_kw} kW (assumed)`], ['Cost per removal', `$${fmt(D.cost.per_removal_musd, 1)}M (model)`],
  ];
  $('specs').innerHTML = sp.map(([a, b]) => `<dt>${a}</dt><dd>${b}</dd>`).join('');
  $('specNote').textContent = D.note;
}

// ------------------------------------------------------------------ journey
let T, D, stage, journey;
function buildJourney() {
  const ins = D.insertion;
  const r0 = 1 + ins.from_alt_km / RE_KM, r1 = 1 + ins.to_alt_km / RE_KM;
  const VAN = { lat: 34.63, lon: -120.61 };                       // Vandenberg SLC-4E
  // node longitude that puts the SSO ring over Vandenberg on a southbound pass
  const iS = ins.from_inc_deg * Math.PI / 180, sinU = Math.sin(VAN.lat * Math.PI / 180) / Math.sin(iS);
  const uV = Math.PI - Math.asin(clamp(sinU, -1, 1));
  const raan0 = VAN.lon - Math.atan2(Math.cos(iS) * Math.sin(uV), Math.cos(uV)) * 180 / Math.PI;
  const raan1 = raan0 + D.insertion.raan_shift_deg;
  const grp = new THREE.Group(); world.add(grp);
  const ssoRing = ring(raan0, ins.from_inc_deg, r0, 0x9aa3b5, 0.55, true); grp.add(ssoRing);
  const tgtRing = ring(raan1, ins.to_inc_deg, r1, COL.kit, 0.75, true); grp.add(tgtRing);
  // the climb: many revolutions while altitude and tilt change smoothly (a helix that leans over)
  const revs = 36, N = revs * 120, pts = [];
  for (let k = 0; k <= N; k++) {
    const f = k / N, e = f;
    pts.push(orbitPoint(lerp(raan0, raan1, e), lerp(ins.from_inc_deg, ins.to_inc_deg, e), uV + f * revs * Math.PI * 2, lerp(r0, r1, e)));
  }
  const spiralGeo = new THREE.BufferGeometry().setFromPoints(pts);
  const spiral = new THREE.Line(spiralGeo, new THREE.LineBasicMaterial({ color: COL.truck, transparent: true, opacity: 0.55 }));
  spiral.geometry.setDrawRange(0, 0); grp.add(spiral);
  // ascent arc from the pad to orbit insertion (a quarter of the way around, schematic)
  const pad = geo(VAN.lat, VAN.lon, 1.0);
  const asc = [];
  for (let k = 0; k <= 120; k++) {
    const f = k / 120;
    const p = orbitPoint(raan0, ins.from_inc_deg, uV + f * 0.55, 1).normalize();
    const h = lerp(1.0, r0, Math.sqrt(f));
    asc.push(p.multiplyScalar(h));
  }
  asc[0].copy(pad);
  const ascLine = new THREE.Line(new THREE.BufferGeometry().setFromPoints(asc), new THREE.LineBasicMaterial({ color: 0xffffff, transparent: true, opacity: 0.9 }));
  ascLine.geometry.setDrawRange(0, 0); grp.add(ascLine);
  const rocket = glowDot(0xffffff, 0.06); grp.add(rocket);
  const dot = glowDot(COL.truck, 0.07); grp.add(dot);
  // other stops on the route: their rings, faint
  const others = [];
  for (let k = 1; k < D.route.stops; k++) {
    const rr = ring(raan1 + D.route.stop_raan_offsets_deg[k], D.route.stop_inc_deg[k], 1 + D.route.stop_alt_km[k] / RE_KM, COL.kit, 0.0, false);
    grp.add(rr); others.push(rr);
  }
  return { grp, ssoRing, tgtRing, spiral, ascLine, asc, rocket, dot, others, revs, N, pts, raan0, raan1, uV, r0, r1 };
}

const CH = () => [
  { key: 'launch', dur: 7, eyebrow: '1 · Launch', title: D.launch.title,
    text: D.launch.text },
  { key: 'deploy', dur: 7, eyebrow: '2 · Separate and unfold', title: 'Off the rideshare, wings out',
    text: `The truck springs off its launch plate, then unfolds two solar wings (about ${D.truck.power_kw} kW). Everything else stays folded until it reaches the first stop.` },
  { key: 'climb', dur: 13, eyebrow: '3 · Climb and tilt', title: D.insertion.dv_ms > 50 ? `${fmt(D.insertion.days)} days of gentle thrust` : 'A short climb',
    text: D.insertion.dv_ms > 50
      ? `The rideshare leaves us tilted ${fmt(D.insertion.from_inc_deg, 1)}°. The target stages are tilted ${fmt(D.insertion.to_inc_deg, 1)}°. Earth’s bulge can swing an orbit around the pole but cannot change its tilt, so the thrusters do it: ${fmt(D.insertion.dv_ms)} m/s and ${fmt(D.insertion.xenon_kg)} kg of xenon, spiralling up as they turn.`
      : `The rideshare drops us in almost the same orbit as the targets. A short electric climb (${fmt(D.insertion.dv_ms)} m/s) and some drifting line us up.` },
  { key: 'approach', dur: 9, eyebrow: '4 · Meet the first stage', title: `${D.stage.name}`,
    text: `About ${fmt(D.stage.length_m, 1)} m long and ${fmt(D.stage.mass_kg)} kg, slowly tumbling. The truck matches its spin with cameras and lidar, then reaches out with the arm.` },
  { key: 'tag', dur: 9, eyebrow: '5 · Tag it', title: 'Clamp on a deorbit kit',
    text: 'The arm holds the stage still while one kit slides out of the magazine and clamps onto the stage’s nose. Then the arm lets go and the truck backs away.' },
  { key: 'deorbit', dur: 7, eyebrow: '6 · Send it down', title: 'The kit fires',
    text: `A short burn lowers the stage’s lowest point to ${D.kit.perigee_km} km. Air drag does the rest: it re-enters and burns up within months.` },
  { key: 'driveon', dur: 8, eyebrow: '7 · Drive on', title: `Stop 1 of ${D.route.stops} done`,
    text: `The truck parks at a new height, lets Earth’s bulge line up the next orbit, and hops over. The whole route takes ${fmt(D.route.days)} days. Cost per removal: about $${fmt(D.cost.per_removal_musd, 1)}M in our model.` },
];
let chapters, totalDur, jt = 0, playing = true, mode = 'truck';

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
  $('tagline').textContent = m === 'truck' ? 'The truck: one electric spacecraft that carries ten deorbit kits.' : `From the launch pad to the first stop, ${D.launch.short.toLowerCase()}.`;
  controls.autoRotate = m === 'truck' && !reduceMotion;
  controls.autoRotateSpeed = 0.6;
  if (m === 'truck') { resetTruckPose(); setTruckView(); }
  else { jt = 0; playing = true; $('play').textContent = '❚❚'; }
}
function resetTruckPose() {
  world.visible = false; truck.visible = true; truck.position.set(0, 0, 0); truck.rotation.set(0, 0, 0); truck.scale.setScalar(1);
  if (stage) stage.visible = false;
  if (plate) plate.visible = false;
  setWings(T, $('tWings').getAttribute('aria-pressed') === 'true' ? 1 : 0);
  setThrust(T, $('tFire').getAttribute('aria-pressed') === 'true' ? 1 : 0);
  armStow(T.arm);
  T.kits.forEach(restoreKit);
  controls.enabled = true;
}
function setTruckView() {
  camera.near = 0.05; camera.far = 2000; camera.updateProjectionMatrix();
  if (innerWidth <= 760) { camera.position.set(10.5, 6.5, 12); controls.target.set(0, 1.4, 0.5); }
  else { camera.position.set(7, 3.8, 7.8); controls.target.set(-0.7, -0.2, 1.1); } controls.minDistance = 4; controls.maxDistance = 60;
}
function restoreKit(kit) {
  const h = kit.userData.home;
  if (kit.parent !== h.parent) h.parent.add(kit);
  kit.position.copy(h.pos); kit.rotation.copy(h.rot); kit.visible = true;
  kit.userData.fire.material.opacity = 0;
}

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

let plate;          // the rideshare plate the truck leaves
const camTmp = new THREE.Vector3();
function journeyFrame(t) {
  // which chapter, and how far through it
  let k = 0, acc = 0;
  while (k < chapters.length - 1 && t >= acc + chapters[k].dur) { acc += chapters[k].dur; k++; }
  const c = chapters[k], f = clamp((t - acc) / c.dur, 0, 1);
  if (journey.lastK !== k) {
    journey.lastK = k;
    $('chEyebrow').textContent = c.eyebrow; $('chTitle').textContent = c.title; $('chText').textContent = c.text;
    [...$('ticks').children].forEach((b, j) => b.setAttribute('aria-current', String(j === k)));
  }
  [...$('ticks').children].forEach((b, j) => {
    const done = j < k ? 1 : j > k ? 0 : f; b.querySelector('i').style.width = `${(100 * done).toFixed(1)}%`;
  });
  const J = journey, ins = D.insertion;
  const earthView = c.key === 'launch' || c.key === 'climb' || c.key === 'driveon';
  world.visible = earthView;
  truck.visible = !earthView;
  stage.visible = c.key === 'approach' || c.key === 'tag' || c.key === 'deorbit';
  plate.visible = c.key === 'deploy';
  controls.enabled = false;
  controls.autoRotate = false;

  // gauges
  let day = 0, alt = ins.from_alt_km, inc = ins.from_inc_deg, xe = 0;
  if (c.key === 'launch') { alt = ins.from_alt_km * smooth(f * 1.3); inc = ins.from_inc_deg; }
  if (k >= 2) { const p = c.key === 'climb' ? smooth(f) : 1; day = ins.days * p; alt = lerp(ins.from_alt_km, ins.to_alt_km, p); inc = lerp(ins.from_inc_deg, ins.to_inc_deg, p); xe = ins.xenon_kg * p; }
  if (c.key === 'driveon') { day = ins.days + D.route.days * smooth(f) * 0.1; }
  $('gDay').textContent = fmt(day); $('gAlt').textContent = fmt(alt); $('gInc').textContent = fmt(inc, 1); $('gXe').textContent = fmt(xe);

  if (earthView) {
    T.kits.forEach(restoreKit);
    if (c.key === 'driveon') T.kits[0].visible = false;
    camera.near = 0.01; camera.far = 2000; camera.updateProjectionMatrix();
    J.ssoRing.material.opacity = c.key === 'launch' ? 0.55 * smooth(f * 2 - 0.6) : 0.35;
    J.tgtRing.material.opacity = c.key === 'launch' ? 0 : 0.8;
    J.ascLine.visible = c.key === 'launch';
    J.rocket.visible = c.key === 'launch';
    J.spiral.visible = c.key !== 'launch';
    J.spiral.material.opacity = c.key === 'driveon' ? lerp(0.55, 0.12, smooth(f * 2)) : 0.55;
    J.others.forEach((r, j) => { r.material.opacity = c.key === 'driveon' ? 0.7 * smooth(f * 3 - j * 0.15) : 0; });
    const camDir = geo(10, -95, 1);
    if (c.key === 'launch') {
      const n = Math.floor(smooth(f) * (J.asc.length - 1));
      J.ascLine.geometry.setDrawRange(0, n + 1);
      J.rocket.position.copy(J.asc[n]);
      J.dot.visible = false;
      const look = geo(18, -100, 1);
      camera.position.copy(look.multiplyScalar(lerp(3.5, 3.9, f)));
      controls.target.copy(geo(18, -100, 0.15));
    } else if (c.key === 'climb') {
      const e = smooth(f);
      const n = Math.floor(e * J.N);
      J.spiral.geometry.setDrawRange(0, n + 1);
      J.dot.visible = true; J.dot.position.copy(J.pts[n]);
      const ang = -100 + 60 * e;
      camera.position.copy(geo(lerp(25, 45, e), ang, lerp(3.4, 3.9, e)));
      controls.target.set(0, 0, 0);
    } else {
      J.spiral.geometry.setDrawRange(0, J.N + 1);
      J.dot.visible = true;
      const u = J.uV + J.revs * Math.PI * 2 + f * Math.PI * 1.2;
      J.dot.position.copy(orbitPoint(J.raan1, ins.to_inc_deg, u, J.r1));
      camera.position.copy(geo(lerp(45, 60, f), lerp(-40, 10, f), lerp(3.9, 4.6, f)));
      controls.target.set(0, 0, 0);
    }
    camera.lookAt(controls.target);
    world.rotation.y = 0;
    return;
  }

  // close-up chapters (metres)
  camera.near = 0.05; camera.updateProjectionMatrix();
  armStow(T.arm);
  if (c.key === 'deploy') {
    T.kits.forEach(restoreKit);
    setThrust(T, 0);
    const sep = smooth(f / 0.35);
    truck.position.set(0, 0.2 + sep * 1.6, 0); truck.rotation.set(0, 0, 0);
    setWings(T, smooth((f - 0.35) / 0.6));
    camTmp.set(lerp(9, 7, f), lerp(1.5, 3.5, f), lerp(8, 9.5, f));
    camera.position.copy(camTmp); camera.lookAt(0, 0.8 + sep, 0.5);
    return;
  }
  setWings(T, 1);
  // stage sits at the origin, slowly tumbling; the truck comes in along +Z toward its nose
  const S = D.stage, tumble = 0.12;
  stage.position.set(0, 0, 0);
  const dockW = new THREE.Vector3();
  if (c.key === 'approach') {
    T.kits.forEach(restoreKit);
    setThrust(T, f < 0.6 ? 0.6 : 0);
    stage.rotation.set(Math.PI / 2 + 0.3 * (1 - f), 0.4 + t * tumble * (1 - f), 0);
    const dist = lerp(14, 1.7, smooth(f));
    truck.rotation.set(0, Math.PI, 0);
    truck.position.set(0.15, -0.35, S.length_m / 2 + dist + MAG.len + BUS.l / 2);
    const reach = smooth((f - 0.6) / 0.4);
    stage.updateMatrixWorld(); stage.userData.dock.getWorldPosition(dockW);
    if (reach > 0) {
      truck.updateMatrixWorld();
      const local = T.arm.base.worldToLocal(dockW.clone());
      const stow = new THREE.Vector3(0, 0.5, 0.6);
      armReach(T.arm, stow.lerp(local, reach), reach);
    }
    camera.position.set(lerp(-9, -7, f), lerp(3, 2.2, f), lerp(5, 9, f));
    camera.lookAt(0, 0, S.length_m / 2 + dist * 0.5);
    return;
  }
  // tag + deorbit: stage held still, truck docked at a fixed stand-off
  stage.rotation.set(Math.PI / 2, 0.4, 0);
  const stand = S.length_m / 2 + 1.7 + MAG.len + BUS.l / 2;
  truck.rotation.set(0, Math.PI, 0);
  stage.updateMatrixWorld(); stage.userData.dock.getWorldPosition(dockW);
  const kit = T.kits[0];
  if (c.key === 'tag') {
    setThrust(T, 0);
    truck.position.set(0.15, -0.35, stand + smooth((f - 0.75) / 0.25) * 2.0);
    truck.updateMatrixWorld();
    const hold = smooth(1 - (f - 0.7) / 0.15);
    const local = T.arm.base.worldToLocal(dockW.clone().add(new THREE.Vector3(0.35, 0.3, 0)));
    armReach(T.arm, new THREE.Vector3(0, 0.5, 0.6).lerp(local, hold), hold);
    // kit 0 travels from its slot to the stage's nose plate
    const g = smooth((f - 0.15) / 0.5);
    if (kit.parent !== scene) { scene.add(kit); }
    const home = new THREE.Vector3(); kit.userData.home.parent.localToWorld(home.copy(kit.userData.home.pos));
    const dest = dockW.clone().add(new THREE.Vector3(0, 0, kit.userData.len / 2 + 0.04));
    const mid = home.clone().lerp(dest, 0.5).add(new THREE.Vector3(0, 0.9, 0));
    const p = home.clone().lerp(mid, g).lerp(mid.clone().lerp(dest, g), g);
    kit.position.copy(p);
    kit.rotation.set(0, Math.PI * g + (1 - g) * Math.PI, 0);
    kit.userData.fire.material.opacity = 0;
    camera.position.set(-6.5, 3, stand - 1.5);
    camera.lookAt(0, 0.2, S.length_m / 2 + 1.4);
    return;
  }
  if (c.key === 'deorbit') {
    truck.position.set(0.15, -0.35 + smooth(f) * 3.5, stand + 2.0 + f * 2);
    setThrust(T, 0.7);
    const burn = f < 0.55 ? smooth(f / 0.1) : smooth(1 - (f - 0.55) / 0.1);
    kit.position.copy(dockW).add(new THREE.Vector3(0, 0, kit.userData.len / 2 + 0.04));
    kit.rotation.set(0, Math.PI, 0);
    kit.userData.fire.material.opacity = 0.8 * burn;
    // stage + kit sink away (toward Earth, -Y) and shrink with distance
    const drop = smooth((f - 0.3) / 0.7);
    stage.position.set(0, -drop * 9, -drop * 6);
    kit.position.add(stage.position);
    camera.position.set(-9, 4, 10);
    camera.lookAt(0, -drop * 3, 2);
  }
}

// ------------------------------------------------------------------ boot
function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix();
  if (mode === 'truck') $('right').hidden = w <= 760;
}
addEventListener('resize', resize);

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
let wingAnim = null;

const clock = new THREE.Clock();
function loop() {
  const dt = Math.min(clock.getDelta(), 0.05);
  if (mode === 'truck') {
    if (wingAnim) { wingAnim.t = Math.min(1, wingAnim.t + dt / 1.6); setWings(T, lerp(wingAnim.from, wingAnim.to, wingAnim.t)); if (wingAnim.t >= 1) wingAnim = null; }
    if (flyTarget) { controls.target.lerp(flyTarget, 0.08); if (controls.target.distanceTo(flyTarget) < 0.01) flyTarget = null; }
    const pulse = $('tFire').getAttribute('aria-pressed') === 'true' ? 0.85 + 0.15 * Math.sin(clock.elapsedTime * 9) : 0;
    if (pulse) T.thr.forEach((t) => { t.plume.material.opacity = 0.32 * pulse; });
    controls.update();
    updateLabels($('tLabels').getAttribute('aria-pressed') === 'true');
  } else {
    if (playing) jt += dt * (reduceMotion ? 0.6 : 1);
    if (jt >= totalDur) jt = 0;
    journeyFrame(jt);
    updateLabels(false);
  }
  renderer.render(scene, camera);
  requestAnimationFrame(loop);
}

async function boot() {
  try {
    D = await (await fetch('data/truck.json')).json();
    const tex = await new THREE.TextureLoader().loadAsync('textures/earth.jpg');
    T = buildTruck(D);
    buildWorld(tex);
    stage = makeStage(D.stage); stage.visible = false; scene.add(stage);
    plate = new THREE.Group();
    const pl = new THREE.Mesh(new THREE.CylinderGeometry(1.4, 1.4, 0.12, 48), M.steel); plate.add(pl);
    for (let k = 0; k < 5; k++) { const a = k * 1.25 + 0.6; const sat = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.6, 0.45), k % 2 ? M.foilDark : M.white); sat.position.set(Math.cos(a) * 1.0, 0.36, Math.sin(a) * 1.0); plate.add(sat); }
    plate.position.set(0, -0.62, 0); plate.visible = false; scene.add(plate);
    journey = buildJourney(); journey.lastK = -1;
    chapters = CH(); totalDur = chapters.reduce((s, c) => s + c.dur, 0);
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
// test hook: jump the journey to a time (seconds) or switch mode
window.__setJourney = (t) => { setMode('journey'); playing = false; jt = t; };
window.__setMode = setMode;
boot();
