import os
import sys

# ── 1. Chromium 4K GPU Acceleration & Autoplay Flags ─────────────────────────
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
    "--autoplay-policy=no-user-gesture-required "
    "--no-sandbox "
    "--enable-gpu-rasterization "
    "--enable-zero-copy "
    "--ignore-gpu-blocklist"
)

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineSettings
    _WEBVIEW_OK = True
except ImportError:
    _WEBVIEW_OK = False


class NexusSplashScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        screen = QApplication.primaryScreen()
        if screen:
            self.setGeometry(screen.geometry())

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        if _WEBVIEW_OK:
            self._web = QWebEngineView()
            self._web.page().setBackgroundColor(QColor("#020308"))
            
            settings = self._web.settings()
            settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
            settings.setAttribute(QWebEngineSettings.WebAttribute.PlaybackRequiresUserGesture, False)
            
            self._web.page().titleChanged.connect(self._on_title_change)
            layout.addWidget(self._web)
            self._load_cinematic_splash()
        else:
            QTimer.singleShot(1500, self._finish)

    def _on_title_change(self, title: str):
        if "NEXUS_DONE" in title:
            self._finish()

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Space, Qt.Key.Key_Return):
            self._finish()

    def _finish(self):
        self.finished.emit()
        self.close()

    def _load_cinematic_splash(self):
        splash_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>NEXUS AI Enterprise Command Architecture</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@600;700&family=Share+Tech+Mono&family=Chakra+Petch:wght@500;700&display=swap');

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --gb: #4285F4;
      --gr: #EA4335;
      --gy: #FBBC05;
      --gg: #34A853;
      --cyan: #00F0FF;
      --bg: #020308;
    }

    html, body {
      width: 100vw; height: 100vh;
      background: var(--bg);
      color: #FFF;
      font-family: 'Chakra Petch', 'Orbitron', sans-serif;
      overflow: hidden;
      display: flex; align-items: center; justify-content: center;
      user-select: none;
    }

    #webgl-canvas {
      position: absolute; inset: 0;
      width: 100vw; height: 100vh;
      z-index: 1;
    }

    /* ── SVG Holographic HUD & Radar Calipers ── */
    .hud-overlay {
      position: absolute; inset: 0;
      z-index: 5;
      pointer-events: none;
    }

    .rot-ring-1 {
      transform-origin: center;
      animation: spinClockwise 35s linear infinite;
    }
    .rot-ring-2 {
      transform-origin: center;
      animation: spinCounterClockwise 25s linear infinite;
    }
    .rot-radar {
      transform-origin: center;
      animation: spinClockwise 6s linear infinite;
    }

    @keyframes spinClockwise { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    @keyframes spinCounterClockwise { from { transform: rotate(360deg); } to { transform: rotate(0deg); } }

    /* ── Biometric Laser Grid Scan ── */
    .laser-scanner {
      position: absolute;
      left: 0; right: 0; height: 3px;
      background: linear-gradient(90deg, transparent, var(--cyan), #FFF, var(--cyan), transparent);
      box-shadow: 0 0 25px 4px var(--cyan);
      z-index: 8;
      opacity: 0;
      pointer-events: none;
    }
    .laser-scanner.active {
      opacity: 0.85;
      animation: scanVertical 2.8s ease-in-out infinite alternate;
    }
    @keyframes scanVertical {
      0% { top: 15%; }
      100% { top: 85%; }
    }

    /* ── Top/Bottom Command Framing ── */
    .command-header, .command-footer {
      position: absolute; left: 45px; right: 45px;
      z-index: 20;
      display: flex; justify-content: space-between; align-items: center;
      font-family: 'Share Tech Mono', monospace;
      font-size: 11px;
      letter-spacing: 2px;
      color: rgba(255, 255, 255, 0.45);
      pointer-events: none;
    }
    .command-header { top: 30px; border-bottom: 1px solid rgba(66, 133, 244, 0.25); padding-bottom: 10px; }
    .command-footer { bottom: 30px; border-top: 1px solid rgba(66, 133, 244, 0.25); padding-top: 10px; }

    .org-tag {
      display: inline-flex; align-items: center; gap: 8px;
      color: var(--cyan);
      font-weight: 700;
    }
    .pulse-led {
      width: 7px; height: 7px; border-radius: 50%;
      background: var(--gg);
      box-shadow: 0 0 12px var(--gg);
      animation: ledBlink 0.9s infinite;
    }
    @keyframes ledBlink { 50% { opacity: 0.2; } }

    /* ── Central Stage Typography ── */
    .stage-center {
      position: absolute;
      top: 50%; left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
      z-index: 25;
      pointer-events: none;
      display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      width: 100%;
    }

    .org-badge {
      display: inline-block;
      font-family: 'Share Tech Mono', monospace;
      font-size: 12px;
      letter-spacing: 6px;
      color: var(--cyan);
      border: 1px solid rgba(0, 240, 255, 0.35);
      background: rgba(0, 240, 255, 0.08);
      padding: 5px 18px;
      border-radius: 2px;
      margin-bottom: 15px;
      backdrop-filter: blur(8px);
    }

    .main-title {
      font-family: 'Orbitron', sans-serif;
      font-size: 68px;
      font-weight: 900;
      letter-spacing: 16px;
      text-transform: uppercase;
      background: linear-gradient(180deg, #FFFFFF 0%, #CBD5E1 55%, var(--gb) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-shadow: 0 0 45px rgba(66, 133, 244, 0.5);
      margin-bottom: 8px;
    }

    .sub-title {
      font-family: 'Share Tech Mono', monospace;
      font-size: 14px;
      letter-spacing: 8px;
      color: var(--gy);
      text-transform: uppercase;
      text-shadow: 0 0 18px rgba(251, 188, 5, 0.7);
    }

    /* ── 4 Enterprise Module HUD Gauges ── */
    .enterprise-grid {
      position: absolute;
      inset: 85px 45px;
      pointer-events: none;
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      z-index: 18;
    }

    .node {
      position: absolute;
      width: 340px;
      background: rgba(4, 8, 20, 0.65);
      border: 1px solid rgba(66, 133, 244, 0.3);
      padding: 18px 24px;
      border-radius: 4px;
      backdrop-filter: blur(14px);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.75);
      display: flex;
      align-items: center;
      gap: 16px;
      opacity: 0;
      transform: scale(0.92);
      transition: all 0.7s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .node.active { opacity: 1; transform: scale(1); }

    .node-tl { top: 0; left: 0; border-left: 4px solid var(--gb); }
    .node-tr { top: 0; right: 0; border-right: 4px solid var(--gr); }
    .node-bl { bottom: 0; left: 0; border-left: 4px solid var(--gg); }
    .node-br { bottom: 0; right: 0; border-right: 4px solid var(--gy); }

    .dial-svg { width: 52px; height: 52px; flex-shrink: 0; }
    .dial-bg { stroke: rgba(255, 255, 255, 0.1); stroke-width: 4; fill: none; }
    .dial-bar {
      stroke-width: 4; fill: none; stroke-linecap: round;
      stroke-dasharray: 126; stroke-dashoffset: 126;
      transition: stroke-dashoffset 1.4s ease-out;
    }

    .node-info { flex: 1; }
    .node-header {
      font-family: 'Orbitron', monospace;
      font-size: 13px; font-weight: 700; letter-spacing: 2px;
      margin-bottom: 4px;
    }
    .node-desc {
      font-family: 'Share Tech Mono', monospace;
      font-size: 11px; color: rgba(255, 255, 255, 0.6);
      line-height: 1.4;
    }

    /* ── Skip Button ── */
    .skip-btn {
      position: absolute;
      bottom: 48px; right: 45px;
      z-index: 40;
      background: rgba(3, 7, 18, 0.85);
      border: 1px solid var(--cyan);
      color: var(--cyan);
      font-family: 'Orbitron', monospace;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 3px;
      padding: 12px 28px;
      border-radius: 3px;
      cursor: pointer;
      backdrop-filter: blur(16px);
      box-shadow: 0 0 25px rgba(0, 240, 255, 0.3);
      transition: all 0.3s ease;
      pointer-events: auto;
    }
    .skip-btn:hover {
      background: var(--cyan);
      color: #000;
      box-shadow: 0 0 45px rgba(0, 240, 255, 0.9);
      transform: scale(1.05);
    }
  </style>
</head>
<body>
  <canvas id="webgl-canvas"></canvas>
  <div id="laser" class="laser-scanner"></div>

  <!-- SVG Calipers & HUD Geometry -->
  <svg class="hud-overlay" viewBox="0 0 1920 1080">
    <g transform="translate(960, 540)">
      <!-- Outer Compass Degree Ring -->
      <circle class="rot-ring-1" r="320" fill="none" stroke="rgba(66, 133, 244, 0.2)" stroke-width="1.5" stroke-dasharray="8 12" />
      <circle class="rot-ring-2" r="280" fill="none" stroke="rgba(0, 240, 255, 0.35)" stroke-width="1.5" stroke-dasharray="16 28 4 28" />
      <circle r="240" fill="none" stroke="rgba(255, 255, 255, 0.1)" stroke-width="1" />

      <!-- Rotating Radar Beam -->
      <line class="rot-radar" x1="0" y1="0" x2="0" y2="-240" stroke="rgba(0, 240, 255, 0.6)" stroke-width="2" />
      
      <!-- Caliper Crosshairs -->
      <line x1="-340" y1="0" x2="-260" y2="0" stroke="var(--cyan)" stroke-width="2" />
      <line x1="260" y1="0" x2="340" y2="0" stroke="var(--cyan)" stroke-width="2" />
      <line x1="0" y1="-340" x2="0" y2="-260" stroke="var(--cyan)" stroke-width="2" />
      <line x1="0" y1="260" x2="0" y2="340" stroke="var(--cyan)" stroke-width="2" />
    </g>
  </svg>

  <div class="command-header">
    <div class="org-tag"><span class="pulse-led"></span>ORGANIZATION: NEXUS_ENTERPRISE_AI</div>
    <div>GRID: DEFENSE_LATENCY &lt; 0.8ms</div>
    <div>SECURITY: TOP_SECRET // LEVEL-0</div>
  </div>

  <div class="command-footer">
    <div>CORE: GOOGLE_CHROMA_HEX_WARP</div>
    <div>SATELLITE SYNC: ACTIVE [GNSS / 5-LAYER]</div>
    <div>STATUS: OPERATIONAL</div>
  </div>

  <div class="stage-center">
    <div id="badge-text" class="org-badge">SYSTEM INITIALIZATION</div>
    <div id="main-title" class="main-title"></div>
    <div id="sub-title" class="sub-title"></div>
  </div>

  <!-- 4 Enterprise HUD Telemetry Nodes -->
  <div class="enterprise-grid">
    <div id="node-1" class="node node-tl">
      <svg class="dial-svg" viewBox="0 0 44 44">
        <circle class="dial-bg" cx="22" cy="22" r="18" />
        <circle id="dial-1" class="dial-bar" cx="22" cy="22" r="18" stroke="var(--gb)" />
      </svg>
      <div class="node-info">
        <div class="node-header" style="color: var(--gb);">GEMINI 2.5 LIVE AUDIO</div>
        <div class="node-desc">Direct Stream: 48,000 Hz Dual-Ch<br>Status: SYNCED [99.98%]</div>
      </div>
    </div>

    <div id="node-2" class="node node-tr">
      <div class="node-info" style="text-align: right;">
        <div class="node-header" style="color: var(--gr);">5-LAYER SPATIAL MATRIX</div>
        <div class="node-desc">GNSS / IMU / BLE Multi-Sensor<br>Tracking: ARMED & LOCKED</div>
      </div>
      <svg class="dial-svg" viewBox="0 0 44 44">
        <circle class="dial-bg" cx="22" cy="22" r="18" />
        <circle id="dial-2" class="dial-bar" cx="22" cy="22" r="18" stroke="var(--gr)" />
      </svg>
    </div>

    <div id="node-3" class="node node-bl">
      <svg class="dial-svg" viewBox="0 0 44 44">
        <circle class="dial-bg" cx="22" cy="22" r="18" />
        <circle id="dial-3" class="dial-bar" cx="22" cy="22" r="18" stroke="var(--gg)" />
      </svg>
      <div class="node-info">
        <div class="node-header" style="color: var(--gg);">ESRI 3D DIGITAL TWIN</div>
        <div class="node-desc">Global Satellite Blueprint<br>Resolution: 4K MESH RASTER</div>
      </div>
    </div>

    <div id="node-4" class="node node-br">
      <div class="node-info" style="text-align: right;">
        <div class="node-header" style="color: var(--gy);">COGNITIVE REASONING</div>
        <div class="node-desc">Deep Multi-Hop Thinking Core<br>Tokens: 8,192 ALLOCATED</div>
      </div>
      <svg class="dial-svg" viewBox="0 0 44 44">
        <circle class="dial-bg" cx="22" cy="22" r="18" />
        <circle id="dial-4" class="dial-bar" cx="22" cy="22" r="18" stroke="var(--gy)" />
      </svg>
    </div>
  </div>

  <button class="skip-btn" onclick="skip()">AUTHORIZE ACCESS &#9654;&#9654;</button>

  <script>
    /* =========================================================================
       1. HOLLYWOOD MULTI-OSCILLATOR SYNTHESIZER
       ========================================================================= */
    let audioCtx = null;

    function getAudioCtx() {
      try {
        if (!audioCtx) {
          const AudioClass = window.AudioContext || window.webkitAudioContext;
          if (AudioClass) audioCtx = new AudioClass();
        }
        if (audioCtx && audioCtx.state === 'suspended') {
          audioCtx.resume().catch(() => {});
        }
      } catch (e) {}
      return audioCtx;
    }

    window.addEventListener('load', () => getAudioCtx());

    function playCinematicBraam() {
      try {
        const ctx = getAudioCtx();
        if (!ctx) return;
        const now = ctx.currentTime;

        const osc1 = ctx.createOscillator();
        const osc2 = ctx.createOscillator();
        const sub = ctx.createOscillator();
        const filter = ctx.createBiquadFilter();
        const gain = ctx.createGain();

        osc1.type = 'sawtooth'; osc1.frequency.setValueAtTime(54, now); osc1.frequency.exponentialRampToValueAtTime(30, now + 3.4);
        osc2.type = 'sawtooth'; osc2.frequency.setValueAtTime(54.6, now); osc2.frequency.exponentialRampToValueAtTime(30.4, now + 3.4);
        sub.type = 'sine'; sub.frequency.setValueAtTime(27, now); sub.frequency.exponentialRampToValueAtTime(16, now + 3.4);

        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(2600, now);
        filter.frequency.exponentialRampToValueAtTime(90, now + 3.2);
        filter.Q.value = 8;

        gain.gain.setValueAtTime(0.01, now);
        gain.gain.linearRampToValueAtTime(0.92, now + 0.15);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 3.6);

        osc1.connect(filter); osc2.connect(filter); sub.connect(filter);
        filter.connect(gain); gain.connect(ctx.destination);

        osc1.start(now); osc2.start(now); sub.start(now);
        osc1.stop(now + 3.7); osc2.stop(now + 3.7); sub.stop(now + 3.7);
      } catch(e) {}
    }

    function playLaserChirp() {
      try {
        const ctx = getAudioCtx();
        if (!ctx) return;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(3200, now);
        osc.frequency.exponentialRampToValueAtTime(600, now + 0.12);

        gain.gain.setValueAtTime(0.25, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);

        osc.connect(gain); gain.connect(ctx.destination);
        osc.start(now); osc.stop(now + 0.12);
      } catch(e) {}
    }

    function playRiser() {
      try {
        const ctx = getAudioCtx();
        if (!ctx) return;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const filter = ctx.createBiquadFilter();
        const gain = ctx.createGain();

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(90, now);
        osc.frequency.exponentialRampToValueAtTime(2400, now + 2.2);

        filter.type = 'bandpass';
        filter.frequency.setValueAtTime(250, now);
        filter.frequency.exponentialRampToValueAtTime(3400, now + 2.2);
        filter.Q.value = 5;

        gain.gain.setValueAtTime(0.01, now);
        gain.gain.linearRampToValueAtTime(0.55, now + 1.2);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 2.3);

        osc.connect(filter); filter.connect(gain); gain.connect(ctx.destination);
        osc.start(now); osc.stop(now + 2.3);
      } catch(e) {}
    }

    function speakVoice(text) {
      if (!('speechSynthesis' in window)) return;
      try {
        window.speechSynthesis.cancel();
        const utt = new SpeechSynthesisUtterance(text);
        utt.rate = 1.0;
        utt.pitch = 0.94;

        const voices = window.speechSynthesis.getVoices();
        const preferred = voices.find(v => 
          v.name.includes('Natural') || v.name.includes('Google') || v.name.includes('Neural') || v.name.includes('David') || v.name.includes('Male')
        ) || voices[0];
        if (preferred) utt.voice = preferred;

        setTimeout(() => {
          try { window.speechSynthesis.speak(utt); } catch(e) {}
        }, 120);
      } catch(e) {}
    }

    function skip() {
      if ('speechSynthesis' in window) {
        try { window.speechSynthesis.cancel(); } catch(e) {}
      }
      document.title = "NEXUS_DONE";
    }

    /* =========================================================================
       2. SCRAMBLE TEXT MATRIX DECRYPTION
       ========================================================================= */
    const GLYPHS = '0123456789ABCDEF!@#$%&*+<>{}';

    function decryptText(elementId, targetText, duration = 1200) {
      const el = document.getElementById(elementId);
      if (!el) return;
      const startTime = performance.now();
      const length = targetText.length;

      function update(now) {
        const progress = Math.min(1, (now - startTime) / duration);
        const charsRevealed = Math.floor(progress * length);
        let output = '';

        for (let i = 0; i < length; i++) {
          if (i < charsRevealed) {
            output += targetText[i];
          } else if (targetText[i] === ' ') {
            output += ' ';
          } else {
            output += GLYPHS[Math.floor(Math.random() * GLYPHS.length)];
          }
        }
        el.innerText = output;

        if (progress < 1) {
          requestAnimationFrame(update);
        } else {
          el.innerText = targetText;
        }
      }
      requestAnimationFrame(update);
    }

    /* =========================================================================
       3. 3D WEBGL RAYMARCHED HEXAGONAL QUANTUM WARP ENGINE
       ========================================================================= */
    const canvas = document.getElementById('webgl-canvas');
    const gl = canvas.getContext('webgl');

    function resizeCanvas() {
      const dpr = Math.max(2, window.devicePixelRatio || 1);
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      gl.viewport(0, 0, canvas.width, canvas.height);
    }
    window.addEventListener('resize', resizeCanvas);
    resizeCanvas();

    const vsSource = `
      attribute vec2 a_pos;
      void main() { gl_Position = vec4(a_pos, 0.0, 1.0); }
    `;

    const fsSource = `
      precision highp float;
      uniform vec2 u_res;
      uniform float u_time;
      uniform float u_stage;

      mat2 rot(float a) { float c = cos(a), s = sin(a); return mat2(c, -s, s, c); }

      // Hexagonal distance function
      float hexDist(vec2 p) {
        p = abs(p);
        float c = dot(p, normalize(vec2(1.0, 1.73)));
        c = max(c, p.x);
        return c;
      }

      void main() {
        vec2 uv = (gl_FragCoord.xy - 0.5 * u_res) / min(u_res.x, u_res.y);
        vec3 col = vec3(0.008, 0.012, 0.03);

        vec2 p = uv;
        p *= rot(u_time * 0.25);

        // Nested Hexagonal Quantum Rings
        float d1 = hexDist(p);
        float hexRing = abs(sin(d1 * 22.0 - u_time * 2.5) / 22.0);

        // Google Quad-Chroma Energy Plasma
        vec3 c_blue   = vec3(0.26, 0.52, 0.96);
        vec3 c_red    = vec3(0.92, 0.26, 0.21);
        vec3 c_yellow = vec3(0.98, 0.74, 0.02);
        vec3 c_green  = vec3(0.20, 0.66, 0.33);

        float angle = atan(p.y, p.x);
        vec3 plasma = mix(c_blue, c_red, smoothstep(-3.14, -1.0, angle));
        plasma = mix(plasma, c_yellow, smoothstep(-1.0, 1.0, angle));
        plasma = mix(plasma, c_green, smoothstep(1.0, 3.14, angle));

        float coreGlow = 0.07 / (length(uv) + 0.015);
        col += plasma * coreGlow * 0.7;
        col += plasma * (0.004 / (hexRing + 0.003)) * 0.9;

        // Stage 4 Warp Acceleration
        if (u_stage >= 4.0) {
          float tunnel = length(uv) * 16.0;
          col += vec3(0.3, 0.8, 1.0) * abs(sin(tunnel - u_time * 30.0));
        }

        gl_FragColor = vec4(col, 1.0);
      }
    `;

    function createShader(gl, type, source) {
      const shader = gl.createShader(type);
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      return shader;
    }

    const program = gl.createProgram();
    gl.attachShader(program, createShader(gl, gl.VERTEX_SHADER, vsSource));
    gl.attachShader(program, createShader(gl, gl.FRAGMENT_SHADER, fsSource));
    gl.linkProgram(program);

    const posBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, posBuffer);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
      -1, -1,  1, -1, -1,  1,
      -1,  1,  1, -1,  1,  1
    ]), gl.STATIC_DRAW);

    const aPos = gl.getAttribLocation(program, 'a_pos');
    const uRes = gl.getUniformLocation(program, 'u_res');
    const uTime = gl.getUniformLocation(program, 'u_time');
    const uStage = gl.getUniformLocation(program, 'u_stage');

    /* =========================================================================
       4. DIRECTOR SEQUENCE (4 ENTERPRISE DEFENSE PHASES)
       ========================================================================= */
    let startTime = null;
    let s1 = false, s2 = false, s3 = false, s4 = false;

    function animate(now) {
      if (!startTime) startTime = now;
      const elapsed = (now - startTime) / 1000;

      if (elapsed >= 30.0) {
        skip();
        return;
      }

      let currentStage = 1.0;
      if (elapsed >= 7.0 && elapsed < 15.0) currentStage = 2.0;
      else if (elapsed >= 15.0 && elapsed < 23.0) currentStage = 3.0;
      else if (elapsed >= 23.0) currentStage = 4.0;

      // Render WebGL
      gl.useProgram(program);
      gl.enableVertexAttribArray(aPos);
      gl.bindBuffer(gl.ARRAY_BUFFER, posBuffer);
      gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

      gl.uniform2f(uRes, canvas.width, canvas.height);
      gl.uniform1f(uTime, elapsed);
      gl.uniform1f(uStage, currentStage);

      gl.drawArrays(gl.TRIANGLES, 0, 6);

      // ── STAGE 1: NEXUS AI QUANTUM KERNEL (0s - 7s) ──
      if (elapsed < 7.0 && !s1) {
        playCinematicBraam();
        decryptText('badge-text', 'NEXUS OPERATING SYSTEM // KERNEL v6.4', 1000);
        decryptText('main-title', 'N E X U S   A I', 1400);
        decryptText('sub-title', 'MULTIMODAL AUTONOMOUS CORE // SECURE BOOT', 1600);
        speakVoice("NEXUS Multimodal Operating System initialized. Quantum core online.");
        s1 = true;
      }

      // ── STAGE 2: BIOMETRIC CLEARANCE - KAMRAN JALIL (7s - 15s) ──
      if (elapsed >= 7.0 && elapsed < 15.0 && !s2) {
        playCinematicBraam();
        playLaserChirp();
        document.getElementById('laser').classList.add('active');

        decryptText('badge-text', 'IDENTITY CLEARANCE: LEVEL-0 TOP-SECRET', 1000);
        decryptText('main-title', 'KAMRAN JALIL', 1400);
        decryptText('sub-title', 'PRINCIPAL AI SYSTEMS ARCHITECT // ROOT ACCESS VERIFIED', 1600);
        speakVoice("Identity confirmed: Kamran Jalil. Executive AI Architecture Authority verified.");
        s2 = true;
      }

      // ── STAGE 3: ENTERPRISE COMBAT & TELEMETRY SUITE (15s - 23s) ──
      if (elapsed >= 15.0 && elapsed < 23.0 && !s3) {
        document.getElementById('laser').classList.remove('active');
        playRiser();

        decryptText('badge-text', 'ENTERPRISE DEFENSE MATRIX ARMED', 1000);
        decryptText('main-title', 'ALL NODES ONLINE', 1200);
        decryptText('sub-title', 'SPATIAL TELEMETRY & DEEP REASONING CLUSTERS READY', 1500);
        speakVoice("Synchronizing multi-layer spatial telemetry, Gemini live audio, and deep reasoning matrix.");

        // Animate circular progress gauges
        document.querySelectorAll('.node').forEach((node, i) => {
          setTimeout(() => {
            node.classList.add('active');
            const dial = document.getElementById(`dial-${i + 1}`);
            if (dial) dial.style.strokeDashoffset = '15'; // 90%+ fill
          }, i * 220);
        });
        s3 = true;
      }

      // ── STAGE 4: HYPER-WARP ENGAGEMENT (23s - 30s) ──
      if (elapsed >= 23.0 && !s4) {
        playRiser();
        playCinematicBraam();

        decryptText('badge-text', 'WARP VECTOR ENGAGED', 800);
        decryptText('main-title', 'HYPERDRIVE ACTIVE', 1000);
        decryptText('sub-title', 'ALL SYSTEMS NOMINAL. WELCOME, KAMRAN JALIL.', 1200);
        speakVoice("All systems nominal. Welcome, Kamran Jalil.");
        s4 = true;
      }

      requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
  </script>
</body>
</html>
"""
        self._web.setHtml(splash_html)


# ── Testing Standalone ────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    splash = NexusSplashScreen()
    splash.showFullScreen()
    splash.finished.connect(lambda: (print("NEXUS Option 2 Splash finished!"), app.quit()))
    sys.exit(app.exec())