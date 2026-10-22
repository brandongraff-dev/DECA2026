// A realistic Earth for Orbital Curbside: NASA Blue Marble by day, city lights by night,
// real cloud cover, a warm band at the day/night line and a glowing atmosphere rim.
// Imagery: NASA Visible Earth (Blue Marble Next Generation, Black Marble 2012, cloud composite), public domain.
import * as THREE from './lib/three.module.min.js';

const GROUND_VERT = `
varying vec2 vUv; varying vec3 vN;
void main(){ vUv = uv; vN = normalize(mat3(modelMatrix) * normal); gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0); }`;
const GROUND_FRAG = `
uniform sampler2D dayMap; uniform sampler2D nightMap; uniform sampler2D cloudMap; uniform vec3 sunDir; uniform float nightGain;
varying vec2 vUv; varying vec3 vN;
void main(){
  float d = dot(normalize(vN), normalize(sunDir));
  vec3 day = pow(texture2D(dayMap, vUv).rgb, vec3(2.2));
  vec3 nt = texture2D(nightMap, vUv).rgb;
  // Black Marble tints oceans blue; keep only the warm city lights
  vec3 night = vec3(1.0, 0.72, 0.42) * pow(smoothstep(0.16, 0.85, nt.r), 1.6);
  float cloud = texture2D(cloudMap, vUv).r;
  float lit = smoothstep(-0.08, 0.25, d) * (0.25 + 0.75 * clamp(d, 0.0, 1.0));
  vec3 col = day * lit * 1.35;
  col += night * nightGain * (1.0 - smoothstep(-0.22, 0.04, d)) * (1.0 - 0.7 * cloud);
  col += vec3(1.0, 0.42, 0.16) * exp(-pow(d / 0.06, 2.0)) * 0.015;
  gl_FragColor = vec4(col, 1.0);
}`;
const CLOUD_FRAG = `
uniform sampler2D cloudMap; uniform vec3 sunDir;
varying vec2 vUv; varying vec3 vN;
void main(){
  float d = dot(normalize(vN), normalize(sunDir));
  float a = texture2D(cloudMap, vUv).r;
  a = smoothstep(0.18, 0.95, a) * 0.92;
  float lit = smoothstep(-0.12, 0.3, d);
  vec3 c = mix(vec3(0.02, 0.025, 0.04), vec3(0.78), lit) + vec3(1.0, 0.45, 0.2) * exp(-pow(d / 0.07, 2.0)) * 0.1;
  gl_FragColor = vec4(c, a * (0.25 + 0.75 * lit));
}`;
const ATMO_VERT = `
varying vec3 vN; varying vec3 vP; varying vec3 vNW;
void main(){ vN = normalize(normalMatrix * normal); vNW = normalize(mat3(modelMatrix) * normal);
  vec4 p = modelViewMatrix * vec4(position,1.0); vP = p.xyz; gl_Position = projectionMatrix * p; }`;
const ATMO_FRAG = `
uniform vec3 sunDir; uniform float power; uniform float strength; uniform vec3 tint;
varying vec3 vN; varying vec3 vP; varying vec3 vNW;
void main(){
  vec3 v = normalize(-vP);
  float rim = pow(1.0 - abs(dot(vN, v)), power);
  float d = dot(vNW, normalize(sunDir));
  float lit = smoothstep(-0.2, 0.3, d);
  vec3 col = mix(vec3(1.0, 0.45, 0.2), tint, smoothstep(-0.08, 0.15, d));
  gl_FragColor = vec4(col * rim * lit * strength, rim * lit);
}`;

export async function loadEarthTextures(base = 'textures/') {
  const L = new THREE.TextureLoader();
  const [day, night, clouds] = await Promise.all(['earth_day.jpg', 'earth_night.jpg', 'clouds.jpg'].map((f) => L.loadAsync(base + f)));
  for (const t of [day, night, clouds]) { t.colorSpace = THREE.NoColorSpace; t.anisotropy = 8; }
  return { day, night, clouds };
}

// radius in scene units; sunDir in world space (updated each frame by setEarthSun)
export function makeRealEarth(radius, tex, { segments = 160, nightGain = 2.2, atmo = 1.015 } = {}) {
  const sun = { value: new THREE.Vector3(1, 0, 0) };
  const g = new THREE.Group();
  const ground = new THREE.Mesh(new THREE.SphereGeometry(radius, segments, segments * 0.75), new THREE.ShaderMaterial({
    vertexShader: GROUND_VERT, fragmentShader: GROUND_FRAG,
    uniforms: { dayMap: { value: tex.day }, nightMap: { value: tex.night }, cloudMap: { value: tex.clouds }, sunDir: sun, nightGain: { value: nightGain } } }));
  const clouds = new THREE.Mesh(new THREE.SphereGeometry(radius * 1.004, segments, segments * 0.75), new THREE.ShaderMaterial({
    vertexShader: GROUND_VERT, fragmentShader: CLOUD_FRAG, transparent: true, depthWrite: false,
    uniforms: { cloudMap: { value: tex.clouds }, sunDir: sun } }));
  const mk = (r, side, power, strength) => new THREE.Mesh(new THREE.SphereGeometry(r, segments, segments * 0.75), new THREE.ShaderMaterial({
    vertexShader: ATMO_VERT, fragmentShader: ATMO_FRAG, side, transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    uniforms: { sunDir: sun, power: { value: power }, strength: { value: strength }, tint: { value: new THREE.Color(0.32, 0.6, 1.0) } } }));
  const shell = mk(radius * atmo, THREE.BackSide, 3.2, 1.6);
  const halo = mk(radius * 1.006, THREE.FrontSide, 4.5, 0.6);
  g.add(ground, clouds, shell, halo);
  g.userData = { sun, ground, clouds, atmo: shell, halo };
  return g;
}
export function setEarthSun(earth, sunDirWorld) { earth.userData.sun.value.copy(sunDirWorld).normalize(); }
