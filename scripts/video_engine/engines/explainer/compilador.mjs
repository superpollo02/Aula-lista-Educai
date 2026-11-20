import fs from 'fs';
import path from 'path';
import { validateExplainerSpec } from './schema.mjs';

/**
 * Compila una especificación Explainer JSON a un archivo index.html compatible
 * con el runtime explainer, canvas 2D, subtítulos, audio y simular.cjs.
 *
 * @param {object|string} specOrPath - Objeto spec o ruta a explainer.json
 * @param {object} [options]
 * @param {Array<{start: number, dur: number}>} [options.audioMeta] - Metadatos opcionales de audio sintetizado
 * @param {string} [options.outputPath] - Ruta de salida opcional para index.html
 * @returns {string} Código HTML compilado
 */
export function compileExplainer(specOrPath, options = {}) {
  let spec = specOrPath;
  if (typeof specOrPath === 'string') {
    const raw = fs.readFileSync(specOrPath, 'utf8');
    spec = JSON.parse(raw);
  }

  // Validar con Zod
  const validated = validateExplainerSpec(spec);
  const { meta, voz, escenas } = validated;

  let audioMeta = null;
  let audioSrc = options.audioSrc || '';
  if (options.audioMeta) {
    if (Array.isArray(options.audioMeta)) {
      audioMeta = options.audioMeta;
    } else if (Array.isArray(options.audioMeta.scenes)) {
      audioMeta = options.audioMeta.scenes.map(s => ({ start: s.start, dur: s.dur, audio_dur: s.audio_dur }));
    }
    if (!audioSrc && typeof specOrPath === 'string') {
      const candidateMp3 = path.join(path.dirname(specOrPath), 'voz.mp3');
      if (fs.existsSync(candidateMp3)) audioSrc = 'voz.mp3';
    }
  } else if (escenas.every(s => typeof s.duracion === 'number')) {
    audioMeta = escenas.map(s => ({ start: s.inicio || 0, dur: s.duracion }));
  }

  const defaultPalette = {
    '--bg': '#0A1926',
    '--panel': '#0F293E',
    '--panel-2': '#163854',
    '--line': '#204E75',
    '--glass': 'rgba(10,25,38,.86)',
    '--ink': '#F0F6FC',
    '--muted': '#8DA5BE',
    '--accent': '#00C7D4',
    '--accent-2': '#4EA8DE',
    '--ok': '#06D6A0',
    '--warn': '#FF6B6B',
    '--sub-ink': '#FFFFFF',
    '--sub-edge': '#06121C',
    '--track': 'rgba(255,255,255,.22)'
  };

  const palette = Object.assign({}, defaultPalette, meta.paleta || {});
  const cssVars = Object.entries(palette)
    .map(([k, v]) => `  ${k}:${v};`)
    .join('\n');

  const fonts = meta.fuentes || {};
  const fontDisplay = fonts.display || '"Rubik",system-ui,-apple-system,sans-serif';
  const fontBody = fonts.body || '"Rubik",system-ui,-apple-system,sans-serif';
  const fontMono = fonts.mono || '"JetBrains Mono",ui-monospace,"SF Mono",Menlo,monospace';
  const fontsUrl = fonts.googleFontsUrl || 'https://fonts.googleapis.com/css2?family=Rubik:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700&display=block';

  const scriptArrayJson = JSON.stringify(escenas.map(s => s.texto), null, 2);
  const sayObjectJson = JSON.stringify(voz.say || {}, null, 2);

  // Serialización de escenas para el runtime JS
  const scenesJsCode = escenas.map((sc, i) => {
    let camJs = 'F => [[0, 0, 0, 1]]';
    if (sc.cam) {
      if (typeof sc.cam === 'string') {
        camJs = sc.cam;
      } else if (Array.isArray(sc.cam)) {
        camJs = `F => ${JSON.stringify(sc.cam)}`;
      }
    }

    let drawBody = sc.drawCode || '';
    if (!drawBody) {
      // Directivas visuales por defecto si no hay drawCode explícito
      drawBody = `
        drawBackgroundGrid(F, 0.2);
        const A = F.area, cx = A.cx, cy = A.cy;
        txt(${JSON.stringify(sc.texto)}, cx, cy, { size: 3.6, color: C.ink, w: 700 });
      `.trim();
    }

    return `    // Escena ${i + 1}: ${sc.id || 'escena-' + (i + 1)}
    {
      alt: ${JSON.stringify(sc.alt || sc.texto)},
      cam: ${camJs},
      draw(t, F) {
${indent(drawBody, 8)}
      }
    }`;
  }).join(',\n\n');

  const audioMetaJs = audioMeta
    ? `  const AUDIO_META = ${JSON.stringify(audioMeta, null, 4)};\n`
    : '';

  const sceneTimingSetup = audioMeta
    ? `  let acc = 0;
  SCENES.forEach((s, i) => {
    const e = estimate(SCRIPT[i]);
    const estSpeech = Math.max(0.1, e.dur - CONFIG.cola);
    const realSpeech = Math.max(0.1, AUDIO_META[i].audio_dur || (AUDIO_META[i].dur - 0.5));
    const scale = realSpeech / estSpeech;
    s.words = e.words.map(w => ({ w: w.w, s: +(w.s * scale).toFixed(3), e: +(w.e * scale).toFixed(3) }));
    s.dur = AUDIO_META[i].dur;
    s.start = AUDIO_META[i].start;
    s.i = i;
    s.text = SCRIPT[i];
    s.chunks = chunks(s.words);
    s.at = makeAt(s);
  });`
    : `  let acc = 0;
  SCENES.forEach((s, i) => {
    const e = estimate(SCRIPT[i]);
    s.words = e.words;
    s.dur = e.dur;
    s.start = acc;
    acc += s.dur;
    s.i = i;
    s.text = SCRIPT[i];
    s.chunks = chunks(s.words);
    s.at = makeAt(s);
  });`;

  const html = `<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>${meta.titulo}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="${fontsUrl}">
<style>
/* Estilo generado automáticamente por compilador.mjs */
:root{
${cssVars}
  --display:${fontDisplay};
  --body:${fontBody};
  --mono:${fontMono};
  color-scheme:dark;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:var(--bg)}
body{color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-underline-offset:3px}

/* Formatos: proporción y zona de subtítulos */
body{--arw:9;--arh:16;--maxw:495px;--subs-top:68%;--subs-side:7%;--subs-size:7.4cqmin}
body[data-formato="16:9"]{--arw:16;--arh:9;--maxw:1280px;--subs-top:79%;--subs-side:12%;--subs-size:5.6cqmin}
body[data-formato="1:1"]{--arw:1;--arh:1;--maxw:760px;--subs-top:75%;--subs-side:8%;--subs-size:6.4cqmin}
body[data-formato="4:5"]{--arw:4;--arh:5;--maxw:680px;--subs-top:72%;--subs-side:8%;--subs-size:6.8cqmin}

.app{min-height:100%;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:32px 40px;padding:24px 16px}

/* Cuadro */
.frame{position:relative;container-type:size;flex:none;aspect-ratio:var(--arw)/var(--arh);width:min(100%,calc((100vh - 48px) * var(--arw) / var(--arh)),var(--maxw));
  border:1px solid var(--line);border-radius:24px;overflow:hidden;background:var(--bg);box-shadow:0 18px 48px rgba(0,0,0,.5);
  -webkit-user-select:none;user-select:none;-webkit-touch-callout:none}
.frame canvas{position:absolute;inset:0;width:100%;height:100%;display:block;z-index:1}

.topbar{position:absolute;left:0;right:0;top:0;z-index:6;padding:2.6cqmin 4cqmin 0;display:flex;flex-direction:column;gap:2.6cqmin;pointer-events:none}
.bars{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(0,1fr);gap:1.2cqmin}
.bars span{position:relative;display:block;height:3px;border-radius:2px;background:var(--track);overflow:hidden}
.bars i{position:absolute;inset:0;transform-origin:left;transform:scaleX(var(--p,0));background:var(--accent)}
.toprow{display:flex;justify-content:flex-end}
.info{pointer-events:auto;width:9cqmin;height:9cqmin;border-radius:50%;border:1px solid var(--line);background:var(--glass);color:var(--ink);display:grid;place-items:center;cursor:pointer;padding:0;font:600 4cqmin/1 var(--mono)}
@media (min-width:980px){.info{display:none}}

/* Subtítulos */
.subs{position:absolute;left:var(--subs-side);right:var(--subs-side);top:var(--subs-top);z-index:4;pointer-events:none;text-align:center;text-wrap:balance;
  font-family:var(--display);font-weight:700;font-size:var(--subs-size);line-height:1.2;letter-spacing:-.01em;color:var(--sub-ink);
  background:rgba(6,18,28,.82);backdrop-filter:blur(8px);padding:2.4cqmin 3.4cqmin;border-radius:16px;border:1px solid rgba(255,255,255,.08);
  box-shadow:0 8px 24px rgba(0,0,0,.45)}
.subs .w{display:inline-block;margin-inline:.06em;transition:transform .12s ease,color .12s ease}
.subs.karaoke .w.now{color:var(--accent);transform:scale(1.06)}
.subs.pop{animation:pop .2s ease-out}
.subs.full{font-size:calc(var(--subs-size) * .68)}
@keyframes pop{from{transform:scale(.95);opacity:.4}to{transform:none;opacity:1}}

/* Toques y estados */
.taps{position:absolute;inset:0;z-index:2;cursor:pointer}
.pz,.replay{position:absolute;inset:0;z-index:5;margin:auto;display:grid;place-items:center;pointer-events:none}
.pz{width:16cqmin;height:16cqmin;border-radius:50%;border:2px solid var(--ink);background:var(--glass);color:var(--ink);transition:transform .15s ease,opacity .15s ease}
.pz svg{width:45%;height:45%;fill:currentColor;transform:translateX(5%)}
.replay{width:max-content;height:max-content;padding:2.5cqmin 4.5cqmin;border-radius:99px;border:2px solid var(--accent);background:var(--glass);color:var(--ink);font:700 3.8cqmin/1 var(--body);cursor:pointer;pointer-events:auto}
.clean .topbar,.clean .pz,.clean .replay{display:none!important}
.bare .topbar,.bare .subs{display:none!important}
.frame.frozen .subs,.frame.frozen .subs .w{animation:none!important;transition:none!important}

/* Panel lateral para desktop */
.aside{width:min(100%,440px);max-height:calc(100vh - 48px);overflow-y:auto;display:flex;flex-direction:column;gap:18px;padding-right:8px;font-size:14px}
.aside h1{font-family:var(--display);font-size:22px;line-height:1.2;margin:0;color:var(--ink);letter-spacing:-.01em}
.aside p{margin:0;color:var(--muted);line-height:1.55}
.aside h2{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:14px 0 6px}
.aside ul{margin:0;padding-left:18px;color:var(--muted)}
.aside li{margin-bottom:6px}
.actions{display:flex;gap:10px}
.act{appearance:none;border:1px solid var(--line);background:var(--panel-2);color:var(--ink);border-radius:99px;padding:9px 16px;font:700 13px/1 var(--body);cursor:pointer}
.act:hover{border-color:var(--accent)}
.act.primary{background:var(--accent);border-color:var(--accent);color:var(--bg)}
.switch{appearance:none;display:inline-flex;align-items:center;gap:10px;align-self:flex-start;border:0;background:none;padding:2px 0;color:var(--ink);font:700 14px/1 var(--body);cursor:pointer}
.switch .knob{position:relative;flex:none;width:38px;height:22px;border-radius:99px;background:var(--panel-2);border:1px solid var(--line);transition:background .15s ease}
.switch .knob::after{content:"";position:absolute;top:2px;left:2px;width:16px;height:16px;border-radius:50%;background:var(--muted);transition:transform .15s ease,background .15s ease}
.switch[aria-checked="true"] .knob{background:var(--accent);border-color:var(--accent)}
.switch[aria-checked="true"] .knob::after{transform:translateX(16px);background:var(--bg)}
.script{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:6px}
.blk{appearance:none;width:100%;text-align:left;display:grid;grid-template-columns:28px minmax(0,1fr);gap:8px;padding:9px 10px;border:1px solid transparent;border-radius:10px;background:none;color:var(--muted);font:400 14px/1.45 var(--body);cursor:pointer}
.blk .n{font-family:var(--mono);font-size:12px;padding-top:2px;color:var(--muted)}
.blk:hover{border-color:var(--line)}
.blk[aria-current="step"]{background:var(--panel-2);border-color:var(--line);color:var(--ink)}
.blk[aria-current="step"] .n{color:var(--accent)}
.sheet-head{display:flex;align-items:flex-start;justify-content:space-between;gap:12px}
.close{display:none;appearance:none;border:1px solid var(--line);background:var(--panel-2);color:var(--ink);border-radius:99px;padding:8px 14px;font:700 14px/1 var(--body);cursor:pointer}

@media (min-width:980px){
  body[data-formato="16:9"] .aside{display:block;width:min(100%,1280px);max-height:none;overflow:visible;columns:300px 3;column-gap:36px;padding-right:0}
  body[data-formato="16:9"] .aside>*{break-inside:avoid;margin-bottom:22px}
}
@media (max-width:979px){
  .aside{position:fixed;inset:0;z-index:20;width:auto;max-height:none;padding-inline:20px;padding-block:calc(env(safe-area-inset-top,0px) + 20px) calc(env(safe-area-inset-bottom,0px) + 28px);background:var(--bg);transform:translateY(102%);transition:transform .3s ease;visibility:hidden}
  .aside.open{transform:none;visibility:visible}
  .close{display:inline-block}
}
@media (max-width:699px){
  .app{padding:0}
  .frame{width:100%;border:0;border-radius:0}
  body[data-formato="9:16"] .app{display:block;height:100%;min-height:0}
  body[data-formato="9:16"] .frame{height:100%;aspect-ratio:auto}
}
body.render .app{display:block;height:100%;min-height:0;padding:0}
body.render .frame{width:100vw;height:100vh;aspect-ratio:auto;border:0;border-radius:0}
body.render .aside{display:none}
@media (prefers-reduced-motion:reduce){
  .subs.pop{animation:none}
  .subs .w,.aside,.switch .knob,.switch .knob::after{transition:none}
}
</style>
</head>
<body>
<div class="app">
  <div class="frame" id="frame" tabindex="0" aria-label="Explainer animado: ${meta.titulo}. Flechas: cambiar de escena. Espacio: pausa.">
    <canvas id="cv" role="img" aria-label=""></canvas>
    <div class="subs" id="subs" aria-live="off"></div>
    <div class="taps" id="taps"></div>
    <div class="pz" id="pz" hidden><svg viewBox="0 0 24 24"><path d="M7 4v16l13-8z"/></svg></div>
    <button class="replay" id="replay" type="button" hidden>↻ Ver de nuevo</button>
    <div class="topbar">
      <div class="bars" id="bars"></div>
      <div class="toprow">
        <button class="info" id="info" type="button" aria-label="Abrir guion y opciones">i</button>
      </div>
    </div>
  </div>
  <audio id="voz" preload="auto"></audio>

  <aside class="aside" id="aside" aria-label="Guion y opciones">
    <div class="sheet-head">
      <h1>${meta.titulo}</h1>
      <button class="close" id="close" type="button">Cerrar</button>
    </div>
    <p>${meta.descripcion || ''} Dura <span id="total">0</span> segundos.</p>
    <div class="actions">
      <button class="act" id="restart" type="button">Reiniciar</button>
      <button class="act primary" id="rec" type="button">Modo grabación</button>
    </div>
    <p>Modo grabación oculta los controles y arranca de cero. Para salir, mantené apretada la pantalla o tocá H.</p>
    <button class="switch" id="bareSw" type="button" role="switch" aria-checked="true"><span class="knob" aria-hidden="true"></span>Subtítulos y barras</button>
    <div>
      <h2>Guion por escenas</h2>
      <ol class="script" id="script"></ol>
    </div>
  </aside>
</div>

<script>
(() => {
  // ================= 1. Configuración =================
  const CONFIG = {
    formato: '${meta.formato || '9:16'}',
    subtitulos: '${meta.subtitulos || 'simples'}',
    cola: ${meta.cola ?? 0.8},
    ritmo: ${meta.ritmo ?? 1.35}
  };

  // ================= 2. Guion =================
  const SCRIPT = ${scriptArrayJson};

  const SAY = ${sayObjectJson};

  const WORDS = [];
  const AUDIO_SRC = ${JSON.stringify(audioSrc)};

  // ================= 3. Formatos =================
  const FORMATS = {
    '9:16': { ar: [9, 16], foco: .40, accion: [.08, .62], subs: [.68, .86], maxPal: 5, maxCar: 26 },
    '16:9': { ar: [16, 9], foco: .44, accion: [.07, .74], subs: [.79, .92], maxPal: 7, maxCar: 38 },
    '1:1': { ar: [1, 1], foco: .42, accion: [.07, .70], subs: [.75, .90], maxPal: 5, maxCar: 26 },
    '4:5': { ar: [4, 5], foco: .41, accion: [.07, .68], subs: [.72, .88], maxPal: 5, maxCar: 24 }
  };
  const Q = new URLSearchParams(typeof location !== 'undefined' ? location.search : '');
  const FMT_ID = FORMATS[Q.get('formato')] ? Q.get('formato') : CONFIG.formato;
  const FMT = FORMATS[FMT_ID];
  const RENDER = Q.has('render') || Q.has('t');
  document.body.dataset.formato = FMT_ID;
  if (RENDER) document.body.classList.add('render');

  // ================= 4. Tokens y utilidades =================
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const rootCS = getComputedStyle(document.documentElement);
  const tok = n => rootCS.getPropertyValue(n).trim();
  const C = {
    bg: tok('--bg') || '#0A1926',
    panel: tok('--panel') || '#0F293E',
    panel2: tok('--panel-2') || '#163854',
    line: tok('--line') || '#204E75',
    ink: tok('--ink') || '#F0F6FC',
    muted: tok('--muted') || '#8DA5BE',
    accent: tok('--accent') || '#00C7D4',
    accent2: tok('--accent-2') || '#4EA8DE',
    ok: tok('--ok') || '#06D6A0',
    warn: tok('--warn') || '#FF6B6B'
  };
  const FONT = { display: tok('--display'), body: tok('--body'), mono: tok('--mono') };

  const TAU = Math.PI * 2;
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const seg = (t, a, b) => clamp((t - a) / (b - a));
  const lerp = (a, b, k) => a + (b - a) * k;
  const ease = x => 1 - Math.pow(1 - x, 3);
  const easeIO = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  const q4 = x => x < .5 ? 8 * x ** 4 : 1 - Math.pow(-2 * x + 2, 4) / 2;
  const outExpo = x => x >= 1 ? 1 : 1 - Math.pow(2, -10 * x);
  const inExpo = x => x <= 0 ? 0 : Math.pow(2, 10 * x - 10);
  const outBack = x => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
  const pop = (t, a, d = .35) => { const k = seg(t, a, a + d); return k <= 0 ? 0 : k >= 1 ? 1 : ease(k) * (1 + .18 * Math.sin(k * Math.PI)); };
  function spring(t, zeta = .75, f = 2) {
    if (t <= 0) return 0;
    const w = TAU * f;
    if (zeta >= 1) return 1 - Math.exp(-w * t) * (1 + w * t);
    const wd = w * Math.sqrt(1 - zeta * zeta);
    return 1 - Math.exp(-zeta * w * t) * (Math.cos(wd * t) + (zeta * w / wd) * Math.sin(wd * t));
  }

  function hexRGB(hex) {
    let h = hex.replace('#', '');
    if (h.length === 3) h = h.split('').map(c => c + c).join('');
    const n = parseInt(h, 16);
    return [n >> 16 & 255, n >> 8 & 255, n & 255];
  }
  const rgba = (hex, a) => { const [r, g, b] = hexRGB(hex); return \`rgba(\${r},\${g},\${b},\${a})\`; };
  const mix = (h1, h2, k) => { const a = hexRGB(h1), b = hexRGB(h2); return \`rgb(\${a.map((v, i) => Math.round(lerp(v, b[i], k))).join(',')})\`; };
  function rng(seed) {
    return () => {
      seed |= 0; seed = seed + 0x6D2B79F5 | 0;
      let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }
  function gauss(r) {
    let u = 0, v = 0;
    while (!u) u = r();
    while (!v) v = r();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(TAU * v);
  }

  // ================= 5. Lienzo y cámara =================
  const frameEl = document.getElementById('frame');
  const cv = document.getElementById('cv');
  const ctx = cv.getContext('2d');
  const subsEl = document.getElementById('subs');
  let W = 1, H = 1, DPR = 1, ready = false;

  function resize() {
    const r = frameEl.getBoundingClientRect();
    DPR = Math.min(3, window.devicePixelRatio || 1);
    W = Math.max(1, r.width); H = Math.max(1, r.height);
    cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR);
    if (ready) paint();
  }

  function frameInfo() {
    const u = Math.min(W, H) / 100, Y = f => (f - FMT.foco) * H / u;
    const left = -W / 2 / u, right = W / 2 / u, pad = 4;
    const x0 = left + pad, x1 = right - pad, y0 = Y(FMT.accion[0]), y1 = Y(FMT.accion[1]);
    return {
      w: W / u, h: H / u, left, right, top: Y(0), bottom: Y(1), subsTop: Y(FMT.subs[0]), subsBottom: Y(FMT.subs[1]),
      area: { x0, x1, y0, y1, w: x1 - x0, h: y1 - y0, cx: (x0 + x1) / 2, cy: (y0 + y1) / 2, s: Math.min(x1 - x0, y1 - y0) },
      vertical: H > W * 1.2, horizontal: W > H * 1.2, formato: FMT_ID
    };
  }

  function track(t, K) {
    if (t <= K[0][0]) return { x: K[0][1], y: K[0][2], z: K[0][3] };
    for (let i = 0; i < K.length - 1; i++) {
      const a = K[i], b = K[i + 1];
      if (t < b[0]) { const k = q4(seg(t, a[0], b[0])); return { x: lerp(a[1], b[1], k), y: lerp(a[2], b[2], k), z: a[3] * Math.pow(b[3] / a[3], k) }; }
    }
    const l = K[K.length - 1];
    return { x: l[1], y: l[2], z: l[3] };
  }

  function beginWorld(cam) {
    const u = Math.min(W, H) / 100 * cam.z;
    ctx.save();
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    ctx.translate(W / 2, H * FMT.foco); ctx.scale(u, u); ctx.translate(-cam.x, -cam.y);
  }

  function bleed(fill, a = 1) {
    if (a <= 0) return;
    ctx.save(); ctx.setTransform(DPR, 0, 0, DPR, 0, 0); ctx.globalAlpha = a;
    if (Array.isArray(fill)) {
      const gr = ctx.createLinearGradient(0, 0, 0, H);
      gr.addColorStop(0, fill[0]); gr.addColorStop(1, fill[1]);
      ctx.fillStyle = gr;
    } else ctx.fillStyle = fill;
    ctx.fillRect(0, 0, W, H); ctx.restore();
  }

  function fixed(fn) {
    const u = Math.min(W, H) / 100;
    ctx.save(); ctx.setTransform(DPR * u, 0, 0, DPR * u, DPR * W / 2, DPR * H * FMT.foco); fn(); ctx.restore();
  }
  function scrim(a = .55) {
    if (a <= 0 || CONFIG.subtitulos === 'no') return;
    ctx.save(); ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    const y0 = H * FMT.accion[1], y1 = H * FMT.subs[0];
    const gr = ctx.createLinearGradient(0, y0, 0, y1);
    gr.addColorStop(0, rgba(C.bg, 0)); gr.addColorStop(1, rgba(C.bg, a));
    ctx.fillStyle = gr; ctx.fillRect(0, y0, W, y1 - y0);
    ctx.fillStyle = rgba(C.bg, a); ctx.fillRect(0, y1, W, H - y1);
    ctx.restore();
  }

  // ================= 6. Ayudantes de dibujo =================
  function txt(s, x, y, o = {}) {
    ctx.save();
    ctx.font = \`\${o.w || 700} \${o.size || 5}px \${o.family || FONT.display}\`;
    ctx.fillStyle = o.color || C.ink; ctx.globalAlpha *= o.a ?? 1;
    ctx.textAlign = o.align || 'center'; ctx.textBaseline = o.base || 'middle';
    ctx.fillText(s, x, y); ctx.restore();
  }
  function line(x0, y0, x1, y1) { ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x1, y1); ctx.stroke(); }
  function rrect(x, y, w, h, r) { ctx.beginPath(); if (ctx.roundRect) ctx.roundRect(x, y, w, h, r); else ctx.rect(x, y, w, h); }
  function dot(x, y, r, color, a = 1) { if (a <= 0 || r <= 0) return; ctx.save(); ctx.globalAlpha *= a; ctx.fillStyle = color; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); ctx.restore(); }

  function ring(x, y, r, a, color = C.accent, lw = .7) {
    if (a <= 0 || r <= 0) return;
    ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = color; ctx.lineWidth = lw;
    ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.stroke(); ctx.restore();
  }
  function brackets(x, y, s, a, color = C.accent) {
    if (a <= 0) return;
    const l = s * .3;
    ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = color; ctx.lineWidth = .7; ctx.lineCap = 'round';
    ctx.beginPath();
    for (const [sx, sy] of [[-1, -1], [1, -1], [1, 1], [-1, 1]]) { const px = x + sx * s, py = y + sy * s; ctx.moveTo(px, py - sy * l); ctx.lineTo(px, py); ctx.lineTo(px - sx * l, py); }
    ctx.stroke(); ctx.restore();
  }
  function arrow(x0, y0, x1, y1, a, color = C.ink, lw = .7) {
    if (a <= 0) return;
    const ang = Math.atan2(y1 - y0, x1 - x0), h = Math.max(1.4, lw * 3);
    ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = color; ctx.lineWidth = lw; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    line(x0, y0, x1, y1);
    ctx.beginPath(); ctx.moveTo(x1 - h * Math.cos(ang - .5), y1 - h * Math.sin(ang - .5)); ctx.lineTo(x1, y1); ctx.lineTo(x1 - h * Math.cos(ang + .5), y1 - h * Math.sin(ang + .5)); ctx.stroke();
    ctx.restore();
  }
  function check(x, y, r, a) {
    if (r <= 0 || a <= 0) return;
    ctx.save(); ctx.globalAlpha *= a; ctx.fillStyle = C.ok; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
    ctx.strokeStyle = C.bg; ctx.lineWidth = r * .22; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.moveTo(x - r * .42, y + r * .02); ctx.lineTo(x - r * .1, y + r * .34); ctx.lineTo(x + r * .45, y - r * .3); ctx.stroke();
    ctx.restore();
  }
  function cross(x, y, s, a, color = C.warn) {
    if (a <= 0) return;
    ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = color; ctx.lineWidth = Math.max(.5, s * .25); ctx.lineCap = 'round';
    line(x - s, y - s, x + s, y + s); line(x - s, y + s, x + s, y - s); ctx.restore();
  }
  function person(x, y, s, color = C.ink, a = 1) {
    if (s <= 0 || a <= 0) return;
    ctx.save(); ctx.globalAlpha *= a; ctx.fillStyle = color;
    ctx.beginPath(); ctx.arc(x, y - s * .45, s * .32, 0, TAU); ctx.fill();
    ctx.beginPath(); ctx.ellipse(x, y + s * .42, s * .58, s * .45, 0, Math.PI, TAU); ctx.fill();
    ctx.restore();
  }
  function bubble(x, y, s, glyph, fill = C.ink, a = 1) {
    if (s <= 0 || a <= 0) return;
    ctx.save(); ctx.globalAlpha *= a; ctx.fillStyle = fill;
    rrect(x - s, y - s * .75, s * 2, s * 1.5, s * .45); ctx.fill();
    ctx.beginPath(); ctx.moveTo(x - s * .55, y + s * .6); ctx.lineTo(x - s * .95, y + s * 1.15); ctx.lineTo(x - s * .1, y + s * .6); ctx.fill();
    ctx.restore();
    txt(glyph, x, y + s * .06, { size: s * 1.2, color: C.bg, w: 800, a });
  }
  function doc(x, y, s, a = 1, lines = 5) {
    if (s <= 0 || a <= 0) return;
    const w = s * 1.5, h = s * 2, f = s * .4, x0 = x - w / 2, y0 = y - h / 2;
    ctx.save(); ctx.globalAlpha *= a; ctx.fillStyle = C.panel; ctx.strokeStyle = C.ink; ctx.lineWidth = .6; ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x0 + w - f, y0); ctx.lineTo(x0 + w, y0 + f); ctx.lineTo(x0 + w, y0 + h); ctx.lineTo(x0, y0 + h); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.fillStyle = rgba(C.muted, .8);
    for (let i = 0; i < lines; i++) ctx.fillRect(x0 + w * .15, y0 + h * (.3 + i * .13), w * (i % 3 === 2 ? .45 : .68), Math.max(.4, s * .07));
    ctx.restore();
  }
  function laptop(x, y, s, a = 1, glow = 0) {
    if (s <= 0 || a <= 0) return;
    ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = C.ink; ctx.lineWidth = .6; ctx.lineJoin = 'round';
    ctx.fillStyle = rgba(C.accent2, .08 + .3 * glow);
    rrect(x - s, y - s * .68, s * 2, s * 1.25, s * .1); ctx.fill(); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(x - s * 1.3, y + s * .62); ctx.lineTo(x + s * 1.3, y + s * .62); ctx.lineTo(x + s * 1.15, y + s * .8); ctx.lineTo(x - s * 1.15, y + s * .8); ctx.closePath(); ctx.stroke();
    ctx.restore();
  }
  function terminal(x, y, s, a = 1) {
    if (s <= 0 || a <= 0) return;
    ctx.save(); ctx.globalAlpha *= a; ctx.fillStyle = C.panel; ctx.strokeStyle = C.accent2; ctx.lineWidth = .6;
    rrect(x - s, y - s * .72, s * 2, s * 1.44, s * .25); ctx.fill(); ctx.stroke();
    ctx.strokeStyle = C.accent; ctx.lineWidth = s * .16; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.moveTo(x - s * .55, y - s * .3); ctx.lineTo(x - s * .15, y); ctx.lineTo(x - s * .55, y + s * .3); ctx.stroke();
    line(x + s * .05, y + s * .32, x + s * .55, y + s * .32);
    ctx.restore();
  }
  function magnifier(x, y, r, a = 1) {
    if (r <= 0 || a <= 0) return;
    ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = C.ink; ctx.lineWidth = r * .18; ctx.lineCap = 'round'; ctx.fillStyle = rgba(C.accent2, .14);
    ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill(); ctx.stroke();
    line(x + r * .72, y + r * .72, x + r * 1.55, y + r * 1.55); ctx.restore();
  }
  function calendar(x, y, s, month, day, a = 1) {
    if (s <= 0 || a <= 0) return;
    ctx.save(); ctx.globalAlpha *= a; ctx.fillStyle = C.panel; ctx.strokeStyle = C.ink; ctx.lineWidth = .5;
    rrect(x - s, y - s, s * 2, s * 2, s * .22); ctx.fill(); ctx.stroke();
    ctx.fillStyle = C.accent; rrect(x - s, y - s, s * 2, s * .6, [s * .22, s * .22, 0, 0]); ctx.fill();
    ctx.restore();
    txt(month, x, y - s * .69, { size: s * .38, color: C.bg, family: FONT.mono, a });
    txt(day, x, y + s * .36, { size: s * 1.05, w: 800, a });
  }
  function clock(x, y, r, k, a = 1) {
    if (r <= 0 || a <= 0) return;
    ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = C.ink; ctx.lineWidth = r * .1;
    ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.stroke();
    ctx.fillStyle = rgba(C.accent, .85); ctx.beginPath(); ctx.moveTo(x, y); ctx.arc(x, y, r * .82, -Math.PI / 2, -Math.PI / 2 + TAU * clamp(k)); ctx.closePath(); ctx.fill();
    ctx.restore();
  }
  function bulb(x, y, s, on = 1, a = 1) {
    if (s <= 0 || a <= 0) return;
    ctx.save(); ctx.globalAlpha *= a;
    if (on > 0) { const gr = ctx.createRadialGradient(x, y - s * .2, s * .2, x, y - s * .2, s * 2.2); gr.addColorStop(0, rgba(C.accent, .45 * on)); gr.addColorStop(1, rgba(C.accent, 0)); ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(x, y - s * .2, s * 2.2, 0, TAU); ctx.fill(); }
    ctx.fillStyle = on > .5 ? C.accent : C.panel; ctx.strokeStyle = C.ink; ctx.lineWidth = s * .08;
    ctx.beginPath(); ctx.arc(x, y - s * .25, s * .62, Math.PI * .8, Math.PI * 2.2); ctx.lineTo(x + s * .3, y + s * .55); ctx.lineTo(x - s * .3, y + s * .55); ctx.closePath(); ctx.fill(); ctx.stroke();
    ctx.fillStyle = C.muted; ctx.fillRect(x - s * .3, y + s * .62, s * .6, s * .28);
    ctx.restore();
  }

  function checkBadge(x, y, r, a = 1) {
    if (r <= 0 || a <= 0) return;
    ctx.save(); ctx.globalAlpha *= a;
    ctx.fillStyle = C.ok; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
    ctx.strokeStyle = '#061D1A'; ctx.lineWidth = r * .22; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.moveTo(x - r * .42, y + r * .02); ctx.lineTo(x - r * .1, y + r * .34); ctx.lineTo(x + r * .45, y - r * .3); ctx.stroke();
    ctx.restore();
  }

  function padlock(x, y, s, closed = 1, a = 1) {
    if (s <= 0 || a <= 0) return;
    const lift = (1 - closed) * s * .45;
    ctx.save(); ctx.globalAlpha *= a; ctx.strokeStyle = C.accent; ctx.lineWidth = s * .18; ctx.lineCap = 'round';
    ctx.beginPath(); ctx.moveTo(x - s * .42, y - lift); ctx.lineTo(x - s * .42, y - s * .35 - lift);
    ctx.arc(x, y - s * .35 - lift, s * .42, Math.PI, 0); ctx.lineTo(x + s * .42, y - lift); ctx.stroke();
    ctx.fillStyle = C.accent; rrect(x - s * .7, y, s * 1.4, s * 1.05, s * .2); ctx.fill();
    ctx.fillStyle = C.bg; ctx.beginPath(); ctx.arc(x, y + s * .18, s * .14, 0, TAU); ctx.fill();
    ctx.restore();
  }

  function medicalBadge(x, y, s, a = 1) {
    if (s <= 0 || a <= 0) return;
    ctx.save(); ctx.globalAlpha *= a;
    ctx.fillStyle = C.accent;
    const w = s * .32, h = s * .95;
    rrect(x - w / 2, y - h / 2, w, h, w * .4); ctx.fill();
    rrect(x - h / 2, y - w / 2, h, w, w * .4); ctx.fill();
    ctx.restore();
  }

  function drawBackgroundGrid(F, a = 0.25) {
    const left = F.left * 1.5, right = F.right * 1.5, top = F.top * 1.5, bottom = F.bottom * 1.5;
    ctx.save(); ctx.globalAlpha = a; ctx.strokeStyle = C.line; ctx.lineWidth = 0.3;
    const step = 14;
    for (let x = Math.floor(left / step) * step; x <= right; x += step) line(x, top, x, bottom);
    for (let y = Math.floor(top / step) * step; y <= bottom; y += step) line(left, y, right, y);
    ctx.restore();
  }

  // ================= 7. Escenas =================
  const SCENES = [
${scenesJsCode}
  ];

  // ================= 8. Motor: tiempos =================
  const norm = s => String(s).toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').replace(/[^a-z0-9]/g, '');
  const N = SCENES.length;

  function estimate(text) {
    const words = [];
    let t = .25;
    for (const raw of text.split(/\\s+/).filter(Boolean)) {
      const m = raw.match(/^(.*?)([.,:;!?…]*)$/);
      const core = m[1].replace(/^[¿¡"«(]+|[")»]+$/g, '');
      const spoken = SAY[core] || core;
      const letters = spoken.replace(/[^a-záéíóúñü0-9]/gi, '').length;
      const d = clamp(.1 + letters * .038, .16, 1) * CONFIG.ritmo;
      words.push({ w: raw, s: t, e: t + d });
      t += d + (/[.!?…]/.test(m[2]) ? .42 : /[:;]/.test(m[2]) ? .26 : /,/.test(m[2]) ? .18 : .02) * CONFIG.ritmo;
    }
    return { words, dur: t + CONFIG.cola };
  }

  function chunks(words) {
    const out = [];
    let cur = [];
    words.forEach((w, i) => {
      cur.push(i);
      const len = cur.map(j => words[j].w).join(' ').length;
      if (cur.length >= FMT.maxPal || len >= FMT.maxCar || /[.,:;!?…]$/.test(w.w)) { out.push(cur); cur = []; }
    });
    if (cur.length) out.push(cur);
    return out.map(ids => ({ ids, s: words[ids[0]].s }));
  }

  function makeAt(s) {
    const cache = new Map();
    return (q, n = 1) => {
      const key = q + '#' + n;
      if (cache.has(key)) return cache.get(key);
      const parts = String(q).split(/\\s+/).map(norm).filter(Boolean);
      let hits = 0, res = null;
      for (let i = 0; i + parts.length <= s.words.length && res === null; i++) {
        if (parts.every((p, k) => norm(s.words[i + k].w).startsWith(p)) && ++hits === n) res = s.words[i].s;
      }
      if (res === null) { console.warn(\`at("\${q}") no aparece en la escena \${s.i + 1}: "\${s.text.slice(0, 50)}…"\`); res = 0; }
      cache.set(key, res);
      return res;
    };
  }

${audioMetaJs}
${sceneTimingSetup}

  const TOTAL = SCENES[N - 1].start + SCENES[N - 1].dur;
  const totalEl = document.getElementById('total');
  if (totalEl) totalEl.textContent = Math.round(TOTAL);

  // ================= 9. Motor: interfaz =================
  const barsEl = document.getElementById('bars');
  barsEl.innerHTML = SCENES.map(() => '<span><i></i></span>').join('');
  const fills = [...barsEl.querySelectorAll('i')];
  const scriptEl = document.getElementById('script');
  scriptEl.innerHTML = SCENES.map((s, i) => \`<li><button class="blk" type="button" data-i="\${i}"><span class="n">\${String(i + 1).padStart(2, '0')}</span><span>\${s.text}</span></button></li>\`).join('');
  const blks = [...scriptEl.querySelectorAll('.blk')];
  blks.forEach(b => b.addEventListener('click', () => { nav(+b.dataset.i); closeSheet(); }));
  if (CONFIG.subtitulos === 'karaoke') subsEl.classList.add('karaoke');

  const audio = document.getElementById('voz');
  const hasAudio = !RENDER && !!AUDIO_SRC && !!audio && typeof audio.play === 'function';
  if (hasAudio) audio.src = AUDIO_SRC;

  let T = 0, idx = -1, playing = !reduce && !hasAudio && !RENDER, ended = false, clean = false, bare = false, last = performance.now();
  let chunkIdx = -1, wordEls = [];
  const sceneAt = t => { let i = N - 1; while (i > 0 && SCENES[i].start > t) i--; return i; };

  function enter(i) {
    idx = i; chunkIdx = -1;
    subsEl.classList.remove('full');
    cv.setAttribute('aria-label', SCENES[i].alt);
    blks.forEach((b, j) => j === i ? b.setAttribute('aria-current', 'step') : b.removeAttribute('aria-current'));
  }

  function renderSubs(s, lt) {
    const hide = CONFIG.subtitulos === 'no' || s.noSubs;
    subsEl.style.visibility = hide ? 'hidden' : '';
    if (hide) return;
    if (reduce) {
      if (chunkIdx !== 0) { subsEl.textContent = s.text; subsEl.classList.add('full'); chunkIdx = 0; }
      return;
    }
    let ci = 0;
    for (let i = 0; i < s.chunks.length; i++) if (s.chunks[i].s <= lt + .03) ci = i;
    if (ci !== chunkIdx) {
      chunkIdx = ci;
      subsEl.innerHTML = s.chunks[ci].ids.map(j => \`<span class="w">\${s.words[j].w}</span>\`).join(' ');
      wordEls = [...subsEl.children];
      subsEl.classList.remove('pop'); void subsEl.offsetWidth; subsEl.classList.add('pop');
    }
    let cur = -1;
    s.chunks[ci].ids.forEach((j, k) => { if (s.words[j].s <= lt + .03) cur = k; });
    wordEls.forEach((el, k) => el.classList.toggle('now', k === cur));
  }

  function paint() {
    const i = sceneAt(T), s = SCENES[i];
    if (i !== idx) enter(i);
    const lt = reduce ? s.dur - .01 : T - s.start;
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
    ctx.clearRect(0, 0, W, H);
    bleed(C.bg);
    const F = Object.assign(frameInfo(), { g: reduce ? s.start : T, dur: s.dur, at: s.at, words: s.words });
    const keys = typeof s.cam === 'function' ? s.cam(F) : s.cam;
    beginWorld(keys ? track(lt, keys) : { x: 0, y: 0, z: 1 });
    s.draw(lt, F);
    ctx.restore();
    ctx.globalAlpha = 1;
    renderSubs(s, lt);
    fills.forEach((el, j) => el.style.setProperty('--p', j < i ? 1 : j > i ? 0 : clamp((T - s.start) / s.dur)));
  }

  function syncUI() {
    const pz = document.getElementById('pz');
    const replay = document.getElementById('replay');
    if (pz) pz.hidden = playing || ended;
    if (replay) replay.hidden = !ended;
  }

  function seek(t) {
    T = clamp(t, 0, TOTAL - 1e-3); ended = false;
    if (hasAudio) { try { audio.currentTime = T; } catch (e) { /* audio sin cargar */ } }
  }
  function play() {
    playing = true; ended = false;
    if (hasAudio) { try { audio.currentTime = T; } catch (e) { /* audio sin cargar */ } audio.play().catch(() => {}); }
    syncUI();
  }
  function pause() { playing = false; if (hasAudio) audio.pause(); syncUI(); }
  function nav(i) { seek(SCENES[clamp(i, 0, N - 1)].start + 1e-3); play(); }
  function toggle() { if (ended) { seek(0); play(); } else if (playing) pause(); else play(); }
  function finish() { T = TOTAL - 1e-3; pause(); ended = true; syncUI(); }
  function setClean(v) { clean = v; frameEl.classList.toggle('clean', v); }
  function setBare(v) { bare = v; frameEl.classList.toggle('bare', v); const sw = document.getElementById('bareSw'); if (sw) sw.setAttribute('aria-checked', String(!v)); }

  const bareSw = document.getElementById('bareSw');
  if (bareSw) bareSw.addEventListener('click', () => setBare(!bare));

  const taps = document.getElementById('taps');
  let lpTimer = null, lpFired = false;
  if (taps) {
    taps.addEventListener('pointerdown', () => {
      lpFired = false;
      clearTimeout(lpTimer);
      lpTimer = setTimeout(() => { lpFired = true; if (clean) setClean(false); }, 700);
    });
    taps.addEventListener('pointerup', e => {
      clearTimeout(lpTimer);
      if (lpFired) return;
      const r = taps.getBoundingClientRect(), x = (e.clientX - r.left) / r.width;
      if (x < .3) nav(idx - 1);
      else if (x > .7) { if (idx === N - 1) finish(); else nav(idx + 1); }
      else toggle();
    });
    taps.addEventListener('pointercancel', () => clearTimeout(lpTimer));
    taps.addEventListener('contextmenu', e => e.preventDefault());
  }

  const replayBtn = document.getElementById('replay');
  if (replayBtn) replayBtn.addEventListener('click', () => { seek(0); play(); });

  const aside = document.getElementById('aside');
  let wasPlaying = false;
  function openSheet() { wasPlaying = playing; pause(); if (aside) aside.classList.add('open'); const c = document.getElementById('close'); if (c) c.focus(); }
  function closeSheet() {
    if (!aside || !aside.classList.contains('open')) return;
    aside.classList.remove('open');
    if (wasPlaying && !ended) play();
  }

  const infoBtn = document.getElementById('info');
  if (infoBtn) infoBtn.addEventListener('click', openSheet);
  const closeBtn = document.getElementById('close');
  if (closeBtn) closeBtn.addEventListener('click', closeSheet);
  const restartBtn = document.getElementById('restart');
  if (restartBtn) restartBtn.addEventListener('click', () => { closeSheet(); nav(0); });
  const recBtn = document.getElementById('rec');
  if (recBtn) recBtn.addEventListener('click', () => { closeSheet(); setClean(true); nav(0); frameEl.focus(); });

  document.addEventListener('keydown', e => {
    if (e.target.closest && e.target.closest('input,textarea,select')) return;
    if (e.key === 'ArrowRight') { e.preventDefault(); nav(idx + 1); }
    else if (e.key === 'ArrowLeft') { e.preventDefault(); nav(idx - 1); }
    else if (e.key === ' ' && !(e.target instanceof HTMLButtonElement)) { e.preventDefault(); toggle(); }
    else if (e.key === 'h' || e.key === 'H') setClean(!clean);
    else if (e.key === 's' || e.key === 'S') setBare(!bare);
    else if (e.key === 'r' || e.key === 'R') nav(0);
    else if (e.key === 'Escape') closeSheet();
  });

  function frame(now) {
    const dt = Math.min(.05, (now - last) / 1000);
    last = now;
    if (playing) {
      if (hasAudio && !audio.paused) T = audio.currentTime; else T += dt;
      if (T >= TOTAL) finish();
    }
    paint();
    requestAnimationFrame(frame);
  }

  // Contrato de render
  window.__duration = TOTAL;
  window.__aspect = FMT.ar;
  window.__escenas = SCENES.map(s => ({ inicio: +s.start.toFixed(3), dur: +s.dur.toFixed(3), texto: s.text }));
  window.renderAt = t => { playing = false; T = clamp(t, 0, TOTAL - 1e-3); paint(); };

  new ResizeObserver(resize).observe(frameEl);
  resize();
  enter(0);
  syncUI();
  ready = true;

  if (RENDER) {
    setClean(true);
    frameEl.classList.add('frozen');
    if (Q.has('bare')) setBare(true);
    window.renderAt(parseFloat(Q.get('t')) || 0);
    if (document.fonts) document.fonts.ready.then(() => window.renderAt(parseFloat(Q.get('t')) || 0));
  } else {
    paint();
    requestAnimationFrame(frame);
  }
})();
</script>
</body>
</html>`;

  if (options.outputPath) {
    fs.writeFileSync(options.outputPath, html, 'utf8');
  }

  return html;
}

function indent(str, spaces) {
  const pad = ' '.repeat(spaces);
  return str.split('\n').map(line => line.trim() ? pad + line : line).join('\n');
}

// Soporte CLI directo: node compilador.mjs explainer.json [salida.html] [--audio-meta meta.json]
if (process.argv[1] && (process.argv[1].endsWith('compilador.mjs') || process.argv[1].endsWith('compilador'))) {
  const args = process.argv.slice(2);
  const jsonPath = args.find(a => !a.startsWith('--') && !a.endsWith('.html'));
  const htmlPath = args.find(a => a.endsWith('.html')) || (jsonPath ? jsonPath.replace(/\.json$/, '.html') : 'index.html');
  const metaIdx = args.indexOf('--audio-meta');
  let audioMeta = null;
  if (metaIdx >= 0 && args[metaIdx + 1]) {
    audioMeta = JSON.parse(fs.readFileSync(args[metaIdx + 1], 'utf8'));
  }

  if (!jsonPath) {
    console.error('Uso: node compilador.mjs <ruta/explainer.json> [ruta/index.html] [--audio-meta ruta/audio_meta.json]');
    process.exit(1);
  }

  try {
    compileExplainer(jsonPath, { outputPath: htmlPath, audioMeta });
    console.log(`Compilación exitosa: ${htmlPath}`);
  } catch (err) {
    console.error('Error al compilar explainer:', err.message);
    process.exit(1);
  }
}
