import * as THREE from 'three';

const FLAP_V = 10.5;
const GRAVITY = -26;
const GROUND_Y = -35;
const PLANE_X = -18;
const TURB_TIME = 1.0;

const state = {
  mode: 'menu',
  speed: 16,
  vy: 0,
  y: 6,
  score: 0,
  best: parseInt(localStorage.getItem('nexaos_best') || '0'),
  turbUntil: 0,
  time: 0,
  shake: 0,
  dead: false,
};

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(50, innerWidth / innerHeight, 0.1, 600);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
document.body.appendChild(renderer.domElement);

scene.fog = new THREE.Fog(0xdfeaf2, 130, 320);
scene.background = makeSkyTexture();

const hemi = new THREE.HemisphereLight(0xbfd8ff, 0x5a7a4a, 0.9);
scene.add(hemi);
const sun = new THREE.DirectionalLight(0xfff2d9, 2.4);
sun.position.set(40, 70, 40);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -70;
sun.shadow.camera.right = 70;
sun.shadow.camera.top = 80;
sun.shadow.camera.bottom = -50;
sun.shadow.camera.far = 220;
scene.add(sun);
scene.add(sun.target);

function makeSkyTexture() {
  const c = document.createElement('canvas');
  c.width = 2; c.height = 512;
  const g = c.getContext('2d');
  const grad = g.createLinearGradient(0, 0, 0, 512);
  grad.addColorStop(0, '#79aede');
  grad.addColorStop(0.55, '#a9cdec');
  grad.addColorStop(1, '#e9f1f8');
  g.fillStyle = grad;
  g.fillRect(0, 0, 2, 512);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function makeGroundTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 1024;
  const g = c.getContext('2d');
  g.fillStyle = '#4c8a3f';
  g.fillRect(0, 0, 1024, 1024);
  const patches = ['#5a9a4a', '#3f7a35', '#568f42', '#b9a35c', '#7f9a4e', '#446f38'];
  for (let i = 0; i < 60; i++) {
    g.fillStyle = patches[(Math.random() * patches.length) | 0];
    g.globalAlpha = 0.55;
    const w = 80 + Math.random() * 260;
    const h = 60 + Math.random() * 200;
    g.fillRect(Math.random() * 1024, Math.random() * 1024, w, h);
  }
  g.globalAlpha = 1;
  for (const y of [180, 640, 880]) {
    g.fillStyle = '#55595e';
    g.fillRect(0, y, 1024, 16);
    g.fillStyle = '#e8d55a';
    for (let x = 0; x < 1024; x += 48) g.fillRect(x, y + 6, 26, 3);
  }
  for (const x of [300, 760]) {
    g.fillStyle = '#55595e';
    g.fillRect(x, 0, 10, 1024);
  }
  g.globalAlpha = 0.08;
  for (let i = 0; i < 3000; i++) {
    g.fillStyle = Math.random() > 0.5 ? '#fff' : '#000';
    g.fillRect(Math.random() * 1024, Math.random() * 1024, 2, 2);
  }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = tex.wrapT = THREE.RepeatWrapping;
  tex.repeat.set(8, 5);
  return tex;
}

const groundTex = makeGroundTexture();
const ground = new THREE.Mesh(
  new THREE.PlaneGeometry(640, 400),
  new THREE.MeshStandardMaterial({ map: groundTex, roughness: 1 })
);
ground.rotation.x = -Math.PI / 2;
ground.position.set(0, GROUND_Y, -130);
ground.receiveShadow = true;
scene.add(ground);

function makeCloudTexture() {
  const c = document.createElement('canvas');
  c.width = c.height = 256;
  const g = c.getContext('2d');
  const blob = (x, y, r, col) => {
    const grad = g.createRadialGradient(x, y, 0, x, y, r);
    grad.addColorStop(0, col);
    grad.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = grad;
    g.fillRect(x - r, y - r, r * 2, r * 2);
  };
  blob(128, 140, 90, 'rgba(255,255,255,.9)');
  for (let i = 0; i < 7; i++) blob(60 + Math.random() * 136, 90 + Math.random() * 90, 34 + Math.random() * 30, 'rgba(255,255,255,.85)');
  for (let i = 0; i < 4; i++) blob(70 + Math.random() * 116, 165 + Math.random() * 30, 26 + Math.random() * 20, 'rgba(185,205,225,.5)');
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

const cloudTex = makeCloudTexture();
const cloudMat = new THREE.SpriteMaterial({ map: cloudTex, transparent: true, depthWrite: false });

function makeCloudCluster(kind) {
  const group = new THREE.Group();
  const n = 3 + (Math.random() * 3 | 0);
  for (let i = 0; i < n; i++) {
    const s = new THREE.Sprite(cloudMat.clone());
    const sc = 10 + Math.random() * 10;
    s.scale.set(sc, sc * 0.62, 1);
    s.position.set((Math.random() - 0.5) * 14, (Math.random() - 0.5) * 5, (Math.random() - 0.5) * 4);
    group.add(s);
  }
  group.userData.kind = kind;
  return group;
}

const plane = buildPlane();
plane.position.set(PLANE_X, 6, 0);
scene.add(plane);

function buildPlane() {
  const g = new THREE.Group();
  const yellow = new THREE.MeshStandardMaterial({ color: 0xf2c21c, metalness: 0.35, roughness: 0.35 });
  const red = new THREE.MeshStandardMaterial({ color: 0xd42b1e, metalness: 0.4, roughness: 0.4 });
  const dark = new THREE.MeshStandardMaterial({ color: 0x26313d, metalness: 0.7, roughness: 0.15 });

  const fus = new THREE.Mesh(new THREE.CapsuleGeometry(0.9, 3.4, 8, 16), yellow);
  fus.rotation.z = Math.PI / 2;
  g.add(fus);

  const nose = new THREE.Mesh(new THREE.CylinderGeometry(0.95, 0.85, 0.6, 16), yellow);
  nose.rotation.z = -Math.PI / 2;
  nose.position.set(2.4, 0, 0);
  g.add(nose);

  const prop = new THREE.Group();
  const hub = new THREE.Mesh(new THREE.SphereGeometry(0.28, 12, 12), red);
  prop.add(hub);
  for (const a of [0, Math.PI / 2]) {
    const blade = new THREE.Mesh(new THREE.BoxGeometry(0.09, 3, 0.22), red);
    blade.rotation.x = a;
    prop.add(blade);
  }
  prop.position.set(2.85, 0, 0);
  prop.userData.isProp = true;
  g.add(prop);

  const cockpit = new THREE.Mesh(new THREE.SphereGeometry(0.72, 16, 12), dark);
  cockpit.scale.set(1.25, 0.75, 0.9);
  cockpit.position.set(0.35, 0.6, 0);
  g.add(cockpit);

  const wing = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.13, 7.2), yellow);
  wing.position.set(0.25, 0.35, 0);
  g.add(wing);
  for (const z of [-3.6, 3.6]) {
    const tip = new THREE.Mesh(new THREE.BoxGeometry(1.7, 0.16, 0.7), red);
    tip.position.set(0.25, 0.35, z);
    g.add(tip);
  }
  const stripe = new THREE.Mesh(new THREE.BoxGeometry(1.72, 0.14, 0.5), red);
  stripe.position.set(0.25, 0.35, 0.9);
  g.add(stripe);

  const fin = new THREE.Mesh(new THREE.BoxGeometry(0.13, 1.5, 1.6), yellow);
  fin.position.set(-2.15, 1.05, 0);
  g.add(fin);
  const finTip = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.35, 1.6), red);
  finTip.position.set(-2.15, 1.75, 0);
  g.add(finTip);
  const stab = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.1, 3.0), yellow);
  stab.position.set(-2.2, 0.25, 0);
  g.add(stab);

  for (const z of [-0.9, 0.9]) {
    const strut = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.7, 0.1), dark);
    strut.position.set(0.4, -0.85, z);
    g.add(strut);
    const wheel = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.32, 0.2, 14), dark);
    wheel.rotation.x = Math.PI / 2;
    wheel.position.set(0.4, -1.2, z);
    g.add(wheel);
  }

  g.traverse(o => { if (o.isMesh) { o.castShadow = true; } });
  return g;
}

const mountains = [];
const hills = [];
const clouds = [];
const trees = [];
const farPeaks = [];
const farClouds = [];

const rockMat = new THREE.MeshStandardMaterial({ color: 0x8d8f94, roughness: 1, flatShading: true });
const rockMat2 = new THREE.MeshStandardMaterial({ color: 0x6f7175, roughness: 1, flatShading: true });
const snowMat = new THREE.MeshStandardMaterial({ color: 0xf4f8fb, roughness: 0.85, flatShading: true });
const farMat = new THREE.MeshStandardMaterial({ color: 0x6b7686, roughness: 1, flatShading: true });
const treeMats = [
  new THREE.MeshStandardMaterial({ color: 0x2e6b2f, roughness: 1, flatShading: true }),
  new THREE.MeshStandardMaterial({ color: 0x3c7d33, roughness: 1, flatShading: true }),
  new THREE.MeshStandardMaterial({ color: 0x2a5f2a, roughness: 1, flatShading: true }),
];
const trunkMat = new THREE.MeshStandardMaterial({ color: 0x7a4a21, roughness: 1 });

function makeMountain(h) {
  const g = new THREE.Group();
  const baseR = 11 + Math.random() * 4;
  const base = new THREE.Mesh(new THREE.ConeGeometry(baseR, h, 7), Math.random() > 0.5 ? rockMat : rockMat2);
  base.position.y = h / 2;
  base.castShadow = true;
  g.add(base);
  const snow = new THREE.Mesh(new THREE.ConeGeometry(baseR * 0.42, h * 0.32, 7), snowMat);
  snow.position.y = h - h * 0.15;
  snow.castShadow = true;
  g.add(snow);
  g.userData = { type: 'mountain', h, baseR };
  return g;
}

function makeHill() {
  const g = new THREE.Group();
  const h = 8 + Math.random() * 14;
  const base = new THREE.Mesh(new THREE.ConeGeometry(9 + Math.random() * 6, h, 6), rockMat2);
  base.position.y = h / 2;
  base.castShadow = true;
  g.add(base);
  const grass = new THREE.Mesh(new THREE.ConeGeometry(6 + Math.random() * 4, h * 0.75, 6), treeMats[(Math.random() * 3) | 0]);
  grass.position.y = h * 0.45;
  g.add(grass);
  g.userData = { type: 'hill' };
  return g;
}

function makeTree() {
  const g = new THREE.Group();
  const s = 0.7 + Math.random() * 0.9;
  const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.25, 0.35, 1.6, 6), trunkMat);
  trunk.position.y = 0.8;
  g.add(trunk);
  for (let i = 0; i < 2; i++) {
    const cone = new THREE.Mesh(new THREE.ConeGeometry(1.4 - i * 0.4, 2.2 - i * 0.5, 7), treeMats[(Math.random() * 3) | 0]);
    cone.position.y = 1.9 + i * 1.2;
    cone.castShadow = true;
    g.add(cone);
  }
  g.scale.setScalar(s);
  g.userData = { type: 'tree' };
  return g;
}

function placeMountains() {
  let x = PLANE_X + 55;
  for (let i = 0; i < 4; i++) {
    x += 28 + Math.random() * 18;
    const m = makeMountain(28 + Math.random() * 34);
    m.position.set(x, GROUND_Y, (Math.random() - 0.5) * 6);
    scene.add(m);
    mountains.push(m);
  }
  return x;
}

function spawnMountainAfter(prevX) {
  const x = prevX + 28 + Math.random() * 18;
  const m = makeMountain(28 + Math.random() * 34);
  m.position.set(x, GROUND_Y, (Math.random() - 0.5) * 6);
  scene.add(m);
  return m;
}

function fill(list, n, factory, area) {
  for (let i = 0; i < n; i++) {
    const o = factory();
    o.position.set(PLANE_X - 120 + Math.random() * area, 0, area === 60 ? 0 : -220 + Math.random() * 230);
    o.position.z = o.userData.type === 'tree' ? -20 - Math.random() * 190 : o.position.z;
    if (o.userData.type !== 'mountain') o.position.y = GROUND_Y;
    scene.add(o);
    list.push(o);
  }
}

let nextCloudX = PLANE_X + 70;
function spawnCloudAt(x) {
  const c = makeCloudCluster('obstacle');
  const h = 7 + Math.random() * 3;
  c.position.set(x, -4 + Math.random() * 26, -2 - Math.random() * 10);
  c.userData.box = { w: 15 + Math.random() * 6, h };
  scene.add(c);
  return c;
}

for (let i = 0; i < 4; i++) {
  nextCloudX += 34 + Math.random() * 22;
  clouds.push(spawnCloudAt(nextCloudX));
}

const bg = new THREE.Group();
scene.add(bg);
for (let i = 0; i < 10; i++) {
  const p = new THREE.Mesh(new THREE.ConeGeometry(26 + Math.random() * 26, 40 + Math.random() * 55, 6), farMat);
  p.position.set(PLANE_X - 160 + i * 34 + Math.random() * 15, GROUND_Y - 2, -230 - Math.random() * 90);
  bg.add(p);
  farPeaks.push(p);
}
for (let i = 0; i < 14; i++) {
  const s = new THREE.Sprite(cloudMat.clone());
  const sc = 16 + Math.random() * 18;
  s.scale.set(sc, sc * 0.6, 1);
  s.position.set(PLANE_X - 160 + Math.random() * 340, 20 + Math.random() * 40, -80 - Math.random() * 140);
  s.material.opacity = 0.85;
  bg.add(s);
  farClouds.push(s);
}

fill(hills, 6, makeHill, 360);
fill(trees, 40, makeTree, 360);

const menuTl = gsap.timeline({ repeat: -1, yoyo: true });
menuTl.to(plane.position, { y: 8.5, duration: 1.4, ease: 'sine.inOut' });

const scoreEl = document.getElementById('score');
const bestEl = document.getElementById('best');
const hintEl = document.getElementById('hint');
const menuEl = document.getElementById('menu');
const overEl = document.getElementById('gameover');
const finalScoreEl = document.getElementById('finalScore');
const finalBestEl = document.getElementById('finalBest');
bestEl.textContent = 'Record : ' + state.best;

function flap() {
  if (state.dead || state.time < state.turbUntil) return;
  state.vy = FLAP_V;
  gsap.fromTo(plane.rotation, { z: plane.rotation.z }, { z: 0.5, duration: 0.12, yoyo: true, repeat: 1, overwrite: 'auto' });
}

function startGame() {
  state.mode = 'play';
  state.vy = FLAP_V * 0.6;
  state.score = 0;
  state.y = 6;
  state.dead = false;
  scoreEl.textContent = '0';
  gsap.to(menuEl, { autoAlpha: 0, duration: 0.4, onComplete: () => menuEl.style.display = 'none' });
  gsap.fromTo(scoreEl, { opacity: 0, y: -30 }, { opacity: 1, y: 0, duration: 0.5 });
  gsap.to(hintEl, { opacity: 0, delay: 2.5, duration: 0.5 });
  menuTl.kill();
}

function restart() {
  location.reload();
}

function gameOver() {
  if (state.dead) return;
  state.dead = true;
  state.shake = 1.4;
  gsap.to(hintEl, { opacity: 0, duration: 0.2 });
  gsap.to(plane.rotation, { z: -2.6, x: 0.6, duration: 1.1, ease: 'power2.in' });
  gsap.delayedCall(1.15, () => {
    if (state.score > state.best) {
      state.best = state.score;
      localStorage.setItem('nexaos_best', state.best);
    }
    bestEl.textContent = 'Record : ' + state.best;
    finalScoreEl.textContent = state.score;
    finalBestEl.textContent = state.best;
    overEl.style.display = 'flex';
    gsap.fromTo(overEl, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.4 });
    gsap.fromTo(overEl.querySelectorAll('h2,.stats,button'), { y: 40, opacity: 0 }, { y: 0, opacity: 1, stagger: 0.12, duration: 0.5, ease: 'back.out(1.6)' });
  });
}

addEventListener('keydown', e => {
  if (e.code === 'Space') {
    e.preventDefault();
    if (state.mode === 'menu') startGame();
    else if (!state.dead) flap();
  }
});
renderer.domElement.addEventListener('pointerdown', () => {
  if (state.mode === 'menu') startGame();
  else if (!state.dead) flap();
});
document.getElementById('btnPlay').addEventListener('click', startGame);
document.getElementById('btnRestart').addEventListener('click', restart);

function recycle(list, maxX, respawn) {
  for (let i = 0; i < list.length; i++) {
    const o = list[i];
    o.position.x -= state.speed * dt;
    if (o.position.x < maxX) respawn(o);
  }
}

function respawnHill(o) { o.position.x = PLANE_X + 260 + Math.random() * 120; o.position.z = -20 - Math.random() * 190; }
function respawnTree(o) { o.position.x = PLANE_X + 260 + Math.random() * 120; o.position.z = -20 - Math.random() * 190; }
function respawnCloud(o) {
  o.position.x = Math.max(nextCloudX, PLANE_X + 260) + 14 + Math.random() * 22;
  nextCloudX = o.position.x;
  o.position.y = -4 + Math.random() * 26;
  o.userData.box.h = 7 + Math.random() * 3;
  o.userData.passed = false;
  o.scale.setScalar(1);
}

let dt = 0;
const clock = new THREE.Clock();

function animate() {
  requestAnimationFrame(animate);
  dt = Math.min(clock.getDelta(), 0.05);
  state.time += dt;

  const playing = state.mode === 'play' && !state.dead;

  if (playing || state.dead) {
    state.speed = Math.min(16 + state.score * 0.25, 30);

    if (playing) {
      if (state.time < state.turbUntil) state.vy = Math.min(state.vy - 34 * dt, -9);
      else state.vy += GRAVITY * dt;
      state.y += state.vy * dt;
      if (state.y > 38) { state.y = 38; state.vy = Math.min(state.vy, 0); }
      if (state.y < GROUND_Y + 12) gameOver();
    } else {
      state.vy += GRAVITY * dt;
      state.y += state.vy * dt;
    }
    plane.position.y = state.y;
    plane.position.x = PLANE_X;
    if (!state.dead) plane.rotation.z = THREE.MathUtils.clamp(state.vy * 0.045, -0.35, 0.55);

    plane.children.forEach(ch => { if (ch.userData.isProp) ch.rotation.x += dt * 42; });

    groundTex.offset.x -= (state.speed * dt) / 80;

    for (const m of mountains) {
      m.position.x -= state.speed * dt;
      if (playing && !m.userData.passed && m.position.x < PLANE_X - 3) {
        m.userData.passed = true;
        state.score++;
        scoreEl.textContent = state.score;
        gsap.fromTo(scoreEl, { scale: 1.35 }, { scale: 1, duration: 0.3 });
      }
      if (m.position.x < PLANE_X - 200) {
        const nm = spawnMountainAfter(Math.max(...mountains.map(o => o.position.x)));
        nm.userData.passed = false;
        scene.remove(m);
        mountains.splice(mountains.indexOf(m), 1);
        mountains.push(nm);
        m.geometry.dispose();
        break;
      }
    }

    for (const m of mountains) {
      if (!playing || state.dead) break;
      const u = m.userData;
      const t = THREE.MathUtils.clamp((state.y - GROUND_Y) / u.h, 0, 1);
      const halfW = u.baseR * (1 - t) * 0.85 + 1;
      if (state.y < GROUND_Y + u.h + 0.5 && Math.abs(PLANE_X - m.position.x) < halfW) gameOver();
    }

    recycle(hills, PLANE_X - 200, respawnHill);
    recycle(trees, PLANE_X - 200, respawnTree);

    for (const c of clouds) {
      c.position.x -= state.speed * dt;
      if (playing && !c.userData.passed && c.position.x < PLANE_X - 3) {
        c.userData.passed = true;
      }
      if (c.position.x < PLANE_X - 200) respawnCloud(c);
    }

    for (const c of clouds) {
      if (!playing || state.dead || state.time < state.turbUntil) break;
      const b = c.userData.box;
      if (Math.abs(PLANE_X - c.position.x) < b.w / 2 + 1.5 && Math.abs(state.y - c.position.y) < b.h / 2 + 1.5) {
        state.turbUntil = state.time + TURB_TIME;
        state.shake = 1;
        gsap.fromTo(c.scale, { x: 1, y: 1 }, { x: 1.15, y: 0.85, duration: 0.18, yoyo: true, repeat: 3, overwrite: true });
        gsap.fromTo(plane.rotation, { z: plane.rotation.z }, { z: -0.7, duration: 0.12, yoyo: true, repeat: 5, overwrite: 'auto' });
      }
    }

    for (const p of farPeaks) {
      p.position.x -= state.speed * dt * 0.15;
      if (p.position.x < PLANE_X - 240) p.position.x += 460 + Math.random() * 40;
    }
    for (const s of farClouds) {
      s.position.x -= state.speed * dt * 0.4;
      if (s.position.x < PLANE_X - 240) { s.position.x += 500; s.position.y = 20 + Math.random() * 40; }
    }
  }

  const targetY = THREE.MathUtils.clamp(state.y, -18, 34);
  camera.position.x += (PLANE_X + 14 - camera.position.x) * Math.min(1, dt * 3);
  camera.position.y += (targetY + 9 - camera.position.y) * Math.min(1, dt * 3);
  camera.position.z = 58;
  if (state.shake > 0) {
    camera.position.x += (Math.random() - 0.5) * state.shake * 1.6;
    camera.position.y += (Math.random() - 0.5) * state.shake * 1.6;
    state.shake -= dt * 2.2;
  }
  sun.position.set(PLANE_X + 60, targetY + 60, 40);
  sun.target.position.set(PLANE_X, state.y, 0);

  camera.lookAt(PLANE_X + 4, targetY - 8, -14);

  renderer.render(scene, camera);
}

camera.position.set(PLANE_X + 14, 16, 58);
animate();

gsap.fromTo('#menu h1', { y: -60, opacity: 0 }, { y: 0, opacity: 1, duration: 0.8, ease: 'back.out(1.4)' });
gsap.fromTo('#menu p, #btnPlay', { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.6, stagger: 0.15, delay: 0.3 });
