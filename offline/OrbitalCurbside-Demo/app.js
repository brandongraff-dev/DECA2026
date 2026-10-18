/* Orbital Curbside mission simulation.
 *
 * Frames: every position is computed in an Earth-centred inertial frame (TEME, the frame
 * TLEs and SGP4 use) and rotated into Cesium's Earth-fixed frame with Cesium's own
 * TEME->pseudo-fixed matrix.  The camera is locked to the inertial frame so orbit planes
 * look like fixed rings while Earth spins underneath -- which is exactly the view in which
 * the J2 "conveyor belt" (planes slowly twisting) is visible.
 *
 *   background objects : mean elements + secular J2 (fast, ~19k points per frame)
 *   mission targets    : satellite.js SGP4 from the 16 Oct 2026 TLEs
 *   truck              : the planner's segments (spiral / drift / spiral / ride / stay)
 */
(() => {
  "use strict";
  const MU = 398600.4418, RE = 6378.137, J2 = 1.08262668e-3;
  const DAY_MS = 86400000;
  const C = window.Cesium;
  const $ = (id) => document.getElementById(id);

  if (!C || !window.satellite) {
    $("loading").innerHTML = "<div><b>Could not start</b>The 3D engine files did not load. If you opened index.html " +
      "directly, start the demo with the launcher (it runs a tiny local web server).</div>";
    return;
  }

  // ------------------------------------------------------------------ colours
  const col = (hex, a = 1) => C.Color.fromCssColorString(hex).withAlpha(a);
  const COLORS = {
    working: col("#5d6680", 0.55), frag: col("#e34948", 0.85), derelict: col("#f2b33d", 0.9),
    target: col("#f2b33d", 1), capture: col("#ffffff", 1), removed: col("#4fc58e", 1),
    truck: col("#ff8a3d", 1), truckRing: col("#e8620c", 0.95), targetRing: col("#f2b33d", 0.38),
  };

  // ------------------------------------------------------------------ viewer
  C.Ion.defaultAccessToken = undefined;
  const viewer = new C.Viewer("globe", {
    baseLayer: C.ImageryLayer.fromProviderAsync(
      C.TileMapServiceImageryProvider.fromUrl(C.buildModuleUrl("Assets/Textures/NaturalEarthII"))),
    terrainProvider: new C.EllipsoidTerrainProvider(),
    baseLayerPicker: false, geocoder: false, homeButton: false, sceneModePicker: false,
    navigationHelpButton: false, animation: false, timeline: false, fullscreenButton: false,
    infoBox: false, selectionIndicator: false, creditContainer: document.createElement("div"),
  });
  const scene = viewer.scene;
  scene.globe.enableLighting = true;
  scene.fog.enabled = false;
  viewer.clock.shouldAnimate = false;

  const bgPoints = scene.primitives.add(new C.PointPrimitiveCollection());
  const fgPoints = scene.primitives.add(new C.PointPrimitiveCollection());
  const rings = scene.primitives.add(new C.PolylineCollection());
  const demo = { rings: scene.primitives.add(new C.PolylineCollection()), labels: scene.primitives.add(new C.LabelCollection()),
                 items: [], t0: 0, raan0: 0 };

  // ------------------------------------------------------------------ state
  const state = {
    ms: Date.UTC(2026, 9, 16, 12), speed: 60, playing: false, scene: 1, camMode: "earth",
    showPlanes: true, mission: null, missions: {}, lastReal: performance.now(), bg: null,
  };
  const M3 = new C.Matrix3(), M4 = new C.Matrix4(), JD = new C.JulianDate();
  let m = M3; // current TEME -> fixed rotation (column-major array access below)

  function updateFrame() {
    C.JulianDate.fromDate(new Date(state.ms), JD);
    viewer.clock.currentTime = JD;
    C.Transforms.computeTemeToPseudoFixedMatrix(JD, M3);
    m = M3;
  }
  const toFixed = (x, y, z, out) => {         // km TEME -> metres fixed
    out.x = (m[0] * x + m[3] * y + m[6] * z) * 1000;
    out.y = (m[1] * x + m[4] * y + m[7] * z) * 1000;
    out.z = (m[2] * x + m[5] * y + m[8] * z) * 1000;
    return out;
  };

  // ------------------------------------------------------------------ orbit maths
  function circularPos(a, i, raan, u) {
    const cO = Math.cos(raan), sO = Math.sin(raan), ci = Math.cos(i), su = Math.sin(u), cu = Math.cos(u);
    return [a * (cO * cu - sO * su * ci), a * (sO * cu + cO * su * ci), a * su * Math.sin(i)];
  }
  const norm = (v) => Math.hypot(v[0], v[1], v[2]);
  function slerpPos(p, q, w) {               // blend directions on the sphere, radii linearly
    const rp = norm(p), rq = norm(q);
    const a = p.map((x) => x / rp), b = q.map((x) => x / rq);
    const dot = Math.min(1, Math.max(-1, a[0] * b[0] + a[1] * b[1] + a[2] * b[2]));
    const th = Math.acos(dot), r = rp + (rq - rp) * w;
    if (th < 1e-6) return b.map((x) => x * r);
    const s1 = Math.sin((1 - w) * th) / Math.sin(th), s2 = Math.sin(w * th) / Math.sin(th);
    return [0, 1, 2].map((k) => (a[k] * s1 + b[k] * s2) * r);
  }
  const smooth = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : x * x * (3 - 2 * x));

  // ------------------------------------------------------------------ background field
  function buildBackground(bg) {
    const n = bg.rows.length;
    const F = (k) => new Float64Array(n);
    const B = { n, a: F(), e: F(), i: F(), W0: F(), w0: F(), M0: F(), ep: F(), nm: F(), Wd: F(), wd: F(), type: new Uint8Array(n), pts: [] };
    const counts = [0, 0, 0, 0];
    bg.rows.forEach((r, k) => {
      const [a, e, i, W, w, M, ep, t] = r;
      const p = a * (1 - e * e), nm = Math.sqrt(MU / a ** 3), f = J2 * (RE / p) ** 2 * nm;
      B.a[k] = a; B.e[k] = e; B.i[k] = i; B.W0[k] = W; B.w0[k] = w; B.M0[k] = M; B.ep[k] = ep; B.nm[k] = nm;
      B.Wd[k] = -1.5 * f * Math.cos(i); B.wd[k] = 0.75 * f * (5 * Math.cos(i) ** 2 - 1); B.type[k] = t;
      counts[t]++;
      const style = t === 0 ? [COLORS.working, 2] : t === 1 ? [COLORS.frag, 2.5] : [COLORS.derelict, 3.2];
      B.pts.push(bgPoints.add({ position: C.Cartesian3.ZERO, color: style[0], pixelSize: style[1] }));
    });
    B.counts = counts;
    return B;
  }
  const scratch = new C.Cartesian3();
  function updateBackground() {
    const B = state.bg, jd = state.ms / DAY_MS + 2440587.5;
    for (let k = 0; k < B.n; k++) {
      const dt = (jd - B.ep[k]) * 86400;
      const e = B.e[k];
      const M = B.M0[k] + B.nm[k] * dt;
      let E = M + e * Math.sin(M);
      E -= (E - e * Math.sin(E) - M) / (1 - e * Math.cos(E));
      const nu = 2 * Math.atan2(Math.sqrt(1 + e) * Math.sin(E / 2), Math.sqrt(1 - e) * Math.cos(E / 2));
      const r = B.a[k] * (1 - e * Math.cos(E));
      const p = circularPos(r, B.i[k], B.W0[k] + B.Wd[k] * dt, B.w0[k] + B.wd[k] * dt + nu);
      B.pts[k].position = toFixed(p[0], p[1], p[2], scratch);
    }
  }

  // ------------------------------------------------------------------ mission objects
  function prepareMission(ms) {
    ms.sat = {};
    ms.targets.forEach((t) => { ms.sat[t.norad] = satellite.twoline2satrec(t.tle1, t.tle2); });
    ms.stopIndex = {};
    ms.stops.forEach((s, k) => { ms.stopIndex[s.norad] = k; });
    return ms;
  }
  function targetTEME(ms, norad, t) {
    const pv = satellite.propagate(ms.sat[norad], new Date(t));
    if (!pv || !pv.position) return null;
    return { r: [pv.position.x, pv.position.y, pv.position.z], v: [pv.velocity.x, pv.velocity.y, pv.velocity.z] };
  }
  function findSegment(ms, t) {
    const S = ms.segments;
    if (t < S[0].t0) return null;
    let lo = 0, hi = S.length - 1;
    while (lo < hi) { const mid = (lo + hi + 1) >> 1; if (S[mid].t0 <= t) lo = mid; else hi = mid - 1; }
    return S[lo];
  }
  function truckState(ms, t) {
    const s = findSegment(ms, t);
    if (!s) return null;
    const dt = (Math.min(t, s.t1) - s.t0) / 1000;
    if (s.kind === "STAY") {
      const tg = targetTEME(ms, s.target, t);
      return tg && { r: tg.r, ring: ringFromRV(tg.r, tg.v), seg: s };
    }
    if (s.kind === "RIDE") {
      const own = circularPos(s.a, s.i, s.raan0 + s.raan_rate * dt, s.u0 + s.n * dt);
      const tg = targetTEME(ms, s.target, t);
      const blend = Math.min(3 * DAY_MS, 0.6 * (s.t1 - s.t0));
      const w = smooth((t - (s.t1 - blend)) / blend);
      const r = tg ? slerpPos(own, tg.r, w) : own;
      return { r, ring: { a: s.a, i: s.i, raan: s.raan0 + s.raan_rate * dt }, seg: s };
    }
    const f = Math.min(1, dt * 1000 / (s.t1 - s.t0));
    const a = s.a0 + (s.a1 - s.a0) * f, i = s.i0 + (s.i1 - s.i0) * f, W = s.raan0 + s.raan_rate * dt;
    return { r: circularPos(a, i, W, s.u0 + s.n * dt), ring: { a, i, raan: W }, seg: s };
  }
  function ringFromRV(r, v) {
    const h = [r[1] * v[2] - r[2] * v[1], r[2] * v[0] - r[0] * v[2], r[0] * v[1] - r[1] * v[0]];
    const hn = norm(h);
    const i = Math.acos(h[2] / hn), raan = Math.atan2(h[0], -h[1]);
    return { a: norm(r), i, raan };
  }
  function ringPositions(ring) {
    const out = [];
    for (let k = 0; k <= 96; k++) {
      const p = circularPos(ring.a, ring.i, ring.raan, (k / 96) * 2 * Math.PI);
      out.push(toFixed(p[0], p[1], p[2], new C.Cartesian3()));
    }
    return out;
  }

  // scene-2 demonstration: three orbits that start in the SAME plane at different altitudes
  const DEMO_ALTS = [[500, "#9ec5f4"], [960, "#3987e5"], [1500, "#256abf"]];
  function raanRateJS(a, i) { const nm = Math.sqrt(MU / a ** 3); return -1.5 * nm * J2 * (RE / a) ** 2 * Math.cos(i); }
  function buildDemo() {
    demo.rings.removeAll(); demo.labels.removeAll();
    demo.items = DEMO_ALTS.map(([h, hex]) => ({
      h, a: RE + h, i: 83 * Math.PI / 180,
      line: demo.rings.add({ positions: [C.Cartesian3.ZERO, C.Cartesian3.UNIT_X], width: 2,
        material: C.Material.fromType("Color", { color: col(hex, 0.95) }) }),
      label: demo.labels.add({ text: `${h.toLocaleString("en-US")} km`, font: "600 14px 'IBM Plex Mono', monospace",
        fillColor: col(hex, 1), outlineColor: col("#070b16", 1), outlineWidth: 3, style: C.LabelStyle.FILL_AND_OUTLINE,
        pixelOffset: new C.Cartesian2(10, -10 + 18 * DEMO_ALTS.findIndex((x) => x[0] === h)), position: C.Cartesian3.ZERO }),
    }));
  }
  function updateDemo() {
    const on = state.scene === 2;
    demo.rings.show = on; demo.labels.show = on;
    if (!on) return;
    const dt = (state.ms - demo.t0) / 1000;
    demo.items.forEach((d, k) => {
      const ring = { a: d.a, i: d.i, raan: demo.raan0 + raanRateJS(d.a, d.i) * dt };
      d.line.positions = ringPositions(ring);
      const p = circularPos(d.a, d.i, ring.raan, 0);   // label at the ring's equator crossing (its node)
      d.label.position = toFixed(p[0], p[1], p[2], new C.Cartesian3());
      const deg = ((ring.raan - demo.raan0) * 180 / Math.PI);
      d.label.text = `${d.h.toLocaleString("en-US")} km  ${deg >= 0 ? "+" : ""}${deg.toFixed(1)}°`;
    });
  }

  // mission drawables
  let truckPt = null, targetPts = [], targetRings = [], truckRing = null;
  function buildMissionDrawables(ms) {
    fgPoints.removeAll(); rings.removeAll();
    targetPts = ms.targets.map(() => fgPoints.add({ position: C.Cartesian3.ZERO, color: COLORS.target, pixelSize: 8,
      outlineColor: col("#070b16", 1), outlineWidth: 1.5 }));
    targetRings = ms.targets.map(() => rings.add({ positions: [C.Cartesian3.ZERO, C.Cartesian3.UNIT_X], width: 1.2,
      material: C.Material.fromType("Color", { color: COLORS.targetRing }) }));
    truckRing = rings.add({ positions: [C.Cartesian3.ZERO, C.Cartesian3.UNIT_X], width: 2.4,
      material: C.Material.fromType("Color", { color: COLORS.truckRing }) });
    truckPt = fgPoints.add({ position: C.Cartesian3.ZERO, color: COLORS.truck, pixelSize: 13,
      outlineColor: col("#ffffff", 0.9), outlineWidth: 2 });
    $("stopbar").innerHTML = ms.stops.map(() => "<span></span>").join("");
  }

  const fixedTruck = new C.Cartesian3();
  let truckVisible = false;
  function updateMission() {
    const ms = state.mission, t = state.ms;
    const showTruck = state.scene >= 3 && t >= ms.start_ms;
    // targets
    ms.targets.forEach((tg, k) => {
      const stop = ms.stops[k];
      const pv = targetTEME(ms, tg.norad, t);
      const pt = targetPts[k], ring = targetRings[k];
      if (!pv) { pt.show = false; ring.show = false; return; }
      let r = pv.r, color = COLORS.target, size = 8, show = state.scene >= 2;
      const pastDepart = showTruck && t >= stop.depart_ms;
      if (showTruck && t >= stop.arrive_ms && t < stop.depart_ms) {
        color = COLORS.capture; size = 10 + 3 * Math.sin(performance.now() / 160);
      } else if (pastDepart) {                       // kit fired: object falls towards the atmosphere
        const f = (t - stop.depart_ms) / (75 * DAY_MS);   // illustrative descent, not a decay model
        if (f >= 1) show = false;
        const rr = norm(r), scale = (RE + (rr - RE) * Math.pow(1 - Math.min(f, 1), 1.6)) / rr;
        r = r.map((x) => x * scale);
        color = COLORS.removed; size = 7;
      }
      pt.show = show; pt.color = color; pt.pixelSize = size;
      if (show) pt.position = toFixed(r[0], r[1], r[2], scratch);
      ring.show = show && state.showPlanes && !pastDepart;
      if (ring.show) ring.positions = ringPositions(ringFromRV(pv.r, pv.v));
    });
    // truck
    const ts = showTruck ? truckState(ms, Math.min(t, ms.end_ms)) : null;
    truckVisible = !!ts;
    truckPt.show = truckVisible;
    truckRing.show = truckVisible && state.showPlanes;
    if (ts) {
      truckPt.position = toFixed(ts.r[0], ts.r[1], ts.r[2], fixedTruck);
      if (truckRing.show) truckRing.positions = ringPositions(ts.ring);
    }
    updateReadout(ts);
  }

  // ------------------------------------------------------------------ readout
  const fmt = (x, d = 0) => x.toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
  function updateReadout(ts) {
    const ms = state.mission, t = state.ms, active = state.scene >= 3 && t >= ms.start_ms;
    const S = ms.stops;
    let removed = 0, now = -1;
    S.forEach((s, k) => { if (active && t >= s.depart_ms) removed++; if (active && t >= s.arrive_ms && t < s.depart_ms) now = k; });
    // interpolate cumulative dv / xenon along the current leg
    let dv = 0, xe = 0;
    if (active) {
      let k = S.findIndex((s) => s.arrive_ms > t);
      if (k === -1) { dv = ms.total_dv_ms; xe = ms.truck.propellant_kg; }
      else if (k > 0) {
        const a = S[k - 1], b = S[k], f = Math.max(0, Math.min(1, (t - a.depart_ms) / (b.arrive_ms - a.depart_ms)));
        dv = a.cum_dv_ms + (b.cum_dv_ms - a.cum_dv_ms) * f; xe = a.cum_prop_kg + (b.cum_prop_kg - a.cum_prop_kg) * f;
      }
    }
    $("s-removed").innerHTML = `${removed}<small> / ${S.length}</small>`;
    $("s-day").textContent = active ? fmt((t - ms.start_ms) / DAY_MS) : "–";
    $("s-dv").innerHTML = `${fmt(dv)}<small> m/s</small>`;
    $("s-xe").innerHTML = `${fmt(xe, 1)}<small> kg</small>`;
    $("s-cpr").textContent = removed ? `$${fmt(ms.economics.total_musd / removed, 1)}M` : "–";
    [...$("stopbar").children].forEach((el, k) => {
      el.className = active && t >= S[k].depart_ms ? "done" : k === now ? "now" : "";
    });
    const st = $("ro-state");
    let phase = "";
    if (!active) { st.textContent = state.scene >= 3 ? "Pre-launch" : "Standby"; st.className = "pill"; }
    else if (t >= ms.end_ms) { st.textContent = "Route complete"; st.className = "pill"; phase = `All ${S.length} objects carry deorbit kits and are falling into the atmosphere.`; }
    else { st.textContent = "Live"; st.className = "pill live"; }
    if (ts && t < ms.end_ms) {
      const s = ts.seg, nextStop = S.findIndex((x) => x.arrive_ms > t);
      const hk = (a) => fmt(a - RE);
      if (s.kind === "STAY") {
        const k = ms.stopIndex[s.target], x = S[k];
        phase = `Stop ${k + 1}: capturing ${x.name} (NORAD ${x.norad}), fitting a ${fmt(x.kit_kg)} kg deorbit kit.`;
      } else if (s.kind === "DRIFT") {
        phase = `Parked at ${hk(s.a0)} km, ${fmt(s.i0 * 180 / Math.PI, 2)}°. Waiting while Earth's bulge lines our plane up with stop ${nextStop + 1}.`;
      } else if (s.kind === "SPIRAL") {
        phase = `Electric spiral: ${hk(s.a0)} km → ${hk(s.a1)} km.`;
      } else {
        phase = `Planes aligned. Riding along and closing in on stop ${nextStop + 1}.`;
      }
    }
    if (phase) $("s-phase").textContent = phase;
    $("clock").textContent = new Date(t).toISOString().slice(0, 16).replace("T", " ") + " UTC";
  }

  function renderCompare() {
    const ms = state.mission, e = ms.economics;
    const rows = [
      { lab: "Orbital Curbside, one truck", v: e.per_removal_musd, cls: "ours" },
      { lab: "One mission per object (our same cost model)", v: e.single_object_per_removal_musd, cls: "" },
      ...e.anchors.map((a) => ({ lab: `${a.name} (public contract, per object)`, v: a.per_object_musd, cls: "anchor" })),
    ];
    const max = Math.max(...rows.map((r) => r.v));
    $("compare").innerHTML = `<div class="ro-head"><h2>Cost per removal</h2><span class="pill">US$ millions</span></div>` +
      rows.map((r) => `<div class="bar-row"><div class="lab"><span>${r.lab}</span><b>$${fmt(r.v, 1)}M</b></div>` +
        `<div class="bar ${r.cls}" style="width:${(100 * r.v / max).toFixed(1)}%"></div></div>`).join("") +
      `<p class="fine">Mission total $${fmt(e.total_musd, 0)}M for ${ms.stops.length} removals, including a rideshare ` +
      (e.launch ? `launch and a ${fmt(e.launch.climb_days, 0)}-day climb to the first stop. ` : `launch. `) + `Base-case assumptions: ` +
      `truck hardware, kit price and operations cost are estimates to be validated. Public contract values from ESA, ` +
      `JAXA/Astroscale, UK Space Agency, NASA OTPS (2023).</p>`;
  }

  // ------------------------------------------------------------------ scenes
  const NARRATION = {
    1: (ms, B) => `This is low Earth orbit on 16 Oct 2026: ${fmt(B.n)} objects from the public catalogue, moving at real speed ×60. ` +
      `Grey dots are ${fmt(B.counts[0])} working satellites. Red are ${fmt(B.counts[1])} fragments from four collisions and weapons tests. ` +
      `Gold are ${fmt(B.counts[2] + B.counts[3])} dead satellites and rocket stages. Nobody is coming to collect them. ESA tracks about 47,000 objects in total.`,
    2: (ms) => `Earth is wider at the equator. That bulge slowly twists every orbit's plane around the planet, and the twist rate depends on altitude. ` +
      `The three blue rings start in exactly the same plane at 500, 960 and 1,500 km. Watch them fan apart: the labels show how far each has turned. ` +
      `Twisting a plane with a rocket is brutally expensive. Parking at a different height and letting Earth do it costs almost nothing.`,
    3: (ms) => `${ms.title}. The orange truck parks in a "lane" where Earth twists its plane at a different speed, waits until it lines up with the next target, ` +
      `then hops over and fits a deorbit kit. Route optimised over real 2026 orbits; first stop ${new Date(ms.start_ms).toISOString().slice(0, 10)}${ms.economics.launch ? `, after a rideshare launch and a ${ms.economics.launch.climb_days}-day climb` : ''}. ` +
      `Total delta-v ${fmt(ms.total_dv_ms)} m/s, ${fmt(ms.truck.propellant_kg)} kg of xenon for the whole route.`,
    4: (ms) => `Same job, two ways. Big fixed costs (the spacecraft, the launch, the team) get split ${ms.stops.length} ways when one truck does the whole route. ` +
      `That is the business: removal priced like a garbage route, not a moon shot.`,
  };
  function setScene(n) {
    state.scene = n;
    document.querySelectorAll(".scene-btn").forEach((b) => b.setAttribute("aria-pressed", String(+b.dataset.scene === n)));
    const ms = state.mission;
    $("compare").hidden = n !== 4;
    if (n === 4) renderCompare();
    if (n === 1) { state.ms = Date.UTC(2026, 9, 16, 12); setSpeed(60); setCam("earth"); }
    if (n === 2) {
      state.ms = ms.start_ms - 120 * DAY_MS; setSpeed(172800); setCam("earth", POLE_OFFSET); state.showPlanes = true;
      demo.t0 = state.ms; demo.raan0 = 0.6;
    }
    if (n === 3) { state.ms = ms.start_ms; setSpeed(518400); setCam("earth"); }
    if (n === 4) { if (state.ms < ms.end_ms) state.ms = ms.end_ms; setSpeed(86400); }
    $("planes").setAttribute("aria-pressed", String(state.showPlanes));
    $("narration").textContent = NARRATION[n](ms, state.bg);
    setPlaying(true);
  }
  function setSpeed(s) {
    state.speed = s;
    document.querySelectorAll("[data-speed]").forEach((b) => b.setAttribute("aria-pressed", String(+b.dataset.speed === s)));
  }
  function setPlaying(p) {
    state.playing = p;
    $("play").textContent = p ? "Pause" : "Play";
    $("play").setAttribute("aria-pressed", String(p));
    state.lastReal = performance.now();
  }
  const EARTH_OFFSET = new C.Cartesian3(-2.3e7, -1.6e7, 1.25e7);
  const POLE_OFFSET = new C.Cartesian3(3.0e6, -6.0e6, 2.9e7);   // above the North Pole, slightly tilted
  function setCam(mode, offset = EARTH_OFFSET) {
    state.camMode = mode;
    $("cam-earth").setAttribute("aria-pressed", String(mode === "earth"));
    $("cam-truck").setAttribute("aria-pressed", String(mode === "truck"));
    if (mode === "earth") {
      updateFrame();
      C.Matrix4.fromRotationTranslation(M3, C.Cartesian3.ZERO, M4);
      viewer.camera.lookAtTransform(M4, offset);
    }
  }

  // ------------------------------------------------------------------ loop
  scene.preUpdate.addEventListener(() => {
    if (!state.mission) return;
    const now = performance.now();
    if (state.playing) {
      state.ms += Math.min(now - state.lastReal, 100) * state.speed;
      if (state.scene >= 3 && state.ms > state.mission.end_ms + 60 * DAY_MS && state.scene === 3) {
        state.ms = state.mission.end_ms + 60 * DAY_MS; setPlaying(false);
      }
    }
    state.lastReal = now;
    updateFrame();
    updateBackground();
    updateMission();
    updateDemo();
  });
  scene.postUpdate.addEventListener(() => {
    if (!state.mission) return;
    if (state.camMode === "truck" && truckVisible) {
      viewer.camera.lookAt(fixedTruck, new C.HeadingPitchRange(0.6, -0.45, 5.5e6));
    } else if (state.camMode === "earth") {
      C.Matrix4.fromRotationTranslation(M3, C.Cartesian3.ZERO, M4);
      const offset = C.Cartesian3.clone(viewer.camera.position);
      viewer.camera.lookAtTransform(M4, offset);
    }
  });

  // ------------------------------------------------------------------ controls
  $("play").addEventListener("click", () => setPlaying(!state.playing));
  document.querySelectorAll("[data-speed]").forEach((b) => b.addEventListener("click", () => setSpeed(+b.dataset.speed)));
  document.querySelectorAll(".scene-btn").forEach((b) => b.addEventListener("click", () => setScene(+b.dataset.scene)));
  $("cam-earth").addEventListener("click", () => setCam("earth"));
  $("cam-truck").addEventListener("click", () => {
    if (state.scene < 3) setScene(3);
    setCam("truck");
  });
  $("planes").addEventListener("click", () => {
    state.showPlanes = !state.showPlanes;
    $("planes").setAttribute("aria-pressed", String(state.showPlanes));
  });
  $("mission").addEventListener("change", (ev) => {
    state.mission = state.missions[ev.target.value];
    buildMissionDrawables(state.mission);
    $("ro-title").textContent = state.mission.product.split(":")[0];
    setScene(state.scene);
  });
  document.addEventListener("keydown", (ev) => {
    if (ev.target.tagName === "SELECT") return;
    if (ev.code === "Space") { ev.preventDefault(); setPlaying(!state.playing); }
    if (["1", "2", "3", "4"].includes(ev.key)) setScene(+ev.key);
  });

  // ------------------------------------------------------------------ boot
  const get = (p) => fetch(p).then((r) => { if (!r.ok) throw new Error(p); return r.json(); });
  Promise.all([get("data/background.json"), get("data/mission_B1.json"), get("data/mission_A1.json"),
               get("data/mission_B0.json")])
    .then(([bg, b1, a1, b0]) => {
      state.bg = buildBackground(bg);
      buildDemo();
      state.missions = { B1: prepareMission(b1), A1: prepareMission(a1), B0: prepareMission(b0) };
      state.mission = state.missions.B0;
      buildMissionDrawables(state.mission);
      $("ro-title").textContent = state.mission.product.split(":")[0];
      const hash = location.hash.replace("#", "");
      const start = { problem: 1, belt: 2, truck: 3, compare: 4 }[hash] || 1;
      setScene(start);
      $("loading").hidden = true;
    })
    .catch((err) => {
      $("loading").innerHTML = `<div><b>Could not load the orbit data</b>${String(err.message || err)}. ` +
        `Run the demo through its launcher (a local web server) rather than opening the file directly.</div>`;
    });
})();
