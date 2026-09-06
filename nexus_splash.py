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
            self._web.page().setBackgroundColor(QColor("#03050D"))
            
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
  <title>NEXUS AI 4K Quantum Core</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@600;700&family=Space+Grotesk:wght@400;700&family=Share+Tech+Mono&display=swap');

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --gb: #4285F4;
      --gr: #EA4335;
      --gy: #FBBC05;
      --gg: #34A853;
      --cyan: #00F0FF;
      --bg: #03050D;
    }

    html, body {
      width: 100vw; height: 100vh;
      background: var(--bg);
      color: #FFF;
      font-family: 'Orbitron', 'Rajdhani', sans-serif;
      overflow: hidden;
      display: flex; align-items: center; justify-content: center;
      user-select: none;
    }

    #webgl-canvas {
      position: absolute; inset: 0;
      width: 100vw; height: 100vh;
      z-index: 1;
    }

    .ui-layer {
      position: absolute; inset: 0;
      z-index: 10;
      pointer-events: none;
      display: flex; flex-direction: column;
      justify-content: space-between;
      padding: 35px 55px;
    }

    /* Ambient Cinema Gradients */
    .anamorphic-flare {
      position: absolute;
      top: 50%; left: 0; right: 0;
      height: 2px;
      background: linear-gradient(90deg, transparent 0%, rgba(0, 240, 255, 0.8) 25%, rgba(66, 133, 244, 1) 50%, rgba(251, 188, 5, 0.8) 75%, transparent 100%);
      box-shadow: 0 0 45px 8px rgba(66, 133, 244, 0.6);
      transform: translateY(-50%);
      z-index: 2;
      opacity: 0.4;
      animation: pulseFlare 4s ease-in-out infinite;
    }

    @keyframes pulseFlare {
      0%, 100% { opacity: 0.25; transform: translateY(-50%) scaleY(1); }
      50% { opacity: 0.6; transform: translateY(-50%) scaleY(2.2); }
    }

    /* Top & Bottom Status Bars */
    .hud-header, .hud-footer {
      display: flex; justify-content: space-between; align-items: center;
      font-family: 'Share Tech Mono', monospace;
      font-size: 11px;
      letter-spacing: 3px;
      color: rgba(255, 255, 255, 0.5);
      border-bottom: 1px solid rgba(66, 133, 244, 0.15);
      padding-bottom: 12px;
    }
    .hud-footer {
      border-bottom: none;
      border-top: 1px solid rgba(66, 133, 244, 0.15);
      padding-top: 12px;
      padding-bottom: 0;
    }

    .badge {
      display: inline-flex; align-items: center; gap: 8px;
      background: rgba(66, 133, 244, 0.12);
      border: 1px solid rgba(66, 133, 244, 0.3);
      padding: 4px 12px;
      border-radius: 3px;
      color: var(--cyan);
    }
    .badge-dot {
      width: 6px; height: 6px; border-radius: 50%;
      background: var(--gg);
      box-shadow: 0 0 10px var(--gg);
      animation: blink 1s infinite;
    }
    @keyframes blink { 50% { opacity: 0.3; } }

    /* Central Hologram Stage */
    .center-stage {
      position: absolute;
      top: 50%; left: 50%;
      transform: translate(-50%, -50%);
      text-align: center;
      z-index: 15;
      display: flex; flex-direction: column;
      align-items: center; justify-content: center;
      width: 100%;
    }

    .title-glitch {
      font-size: 64px;
      font-weight: 900;
      letter-spacing: 18px;
      text-transform: uppercase;
      background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 40%, var(--cyan) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-shadow: 0 0 50px rgba(0, 240, 255, 0.45);
      margin-bottom: 10px;
    }

    .subtitle-badge {
      font-family: 'Share Tech Mono', monospace;
      font-size: 13px;
      letter-spacing: 8px;
      color: var(--gy);
      text-transform: uppercase;
      margin-top: 5px;
      text-shadow: 0 0 15px rgba(251, 188, 5, 0.6);
    }

    /* 4-Corner Holographic Cyberdeck Panels */
    .telemetry-grid {
      position: absolute;
      inset: 80px 55px;
      pointer-events: none;
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      z-index: 12;
    }

    .panel {
      position: absolute;
      width: 320px;
      background: rgba(6, 11, 24, 0.55);
      border: 1px solid rgba(66, 133, 244, 0.25);
      padding: 18px 22px;
      border-radius: 6px;
      backdrop-filter: blur(14px);
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
      transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
      opacity: 0;
      transform: translateY(20px);
    }
    .panel.visible {
      opacity: 1;
      transform: translateY(0);
    }

    .panel-tl { top: 0; left: 0; border-left: 3px solid var(--gb); }
    .panel-tr { top: 0; right: 0; border-right: 3px solid var(--gr); text-align: right; }
    .panel-bl { bottom: 0; left: 0; border-left: 3px solid var(--gg); }
    .panel-br { bottom: 0; right: 0; border-right: 3px solid var(--gy); text-align: right; }

    .panel-title {
      font-family: 'Orbitron', monospace;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 2px;
      margin-bottom: 6px;
    }
    .panel-desc {
      font-family: 'Share Tech Mono', monospace;
      font-size: 11px;
      color: rgba(255, 255, 255, 0.6);
      line-height: 1.5;
    }

    /* Skip Button */
    .skip-btn {
      position: absolute;
      bottom: 50px; right: 55px;
      z-index: 30;
      background: rgba(6, 11, 25, 0.85);
      border: 1px solid var(--cyan);
      color: var(--cyan);
      font-family: 'Orbitron', monospace;
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 3px;
      padding: 12px 28px;
      border-radius: 4px;
      cursor: pointer;
      backdrop-filter: blur(16px);
      box-shadow: 0 0 30px rgba(0, 240, 255, 0.25);
      transition: all 0.3s ease;
      pointer-events: auto;
    }
    .skip-btn:hover {
      background: var(--cyan);
      color: #000;
      box-shadow: 0 0 50px rgba(0, 240, 255, 0.9);
      transform: scale(1.06);
    }
  </style>
</head>
<body>
  <canvas id="webgl-canvas"></canvas>
  <div class="anamorphic-flare"></div>

  <div class="ui-layer">
    <div class="hud-header">
      <div class="badge"><span class="badge-dot"></span>NEXUS_CORE :: ACTIVE</div>
      <div>FREQUENCY: 48.0 kHz ULTRA-HD</div>
      <div>NEURAL CLEARANCE: LEVEL_0</div>
    </div>

    <div class="hud-footer">
      <div>QUANTUM CORE: GOOGLE MULTI-CHROMA ENGINE</div>
      <div>TARGET: SYSTEM_INIT_READY</div>
    </div>
  </div>

  <div class="center-stage">
    <div id="main-title" class="title-glitch"></div>
    <div id="sub-title" class="subtitle-badge"></div>
  </div>

  <div class="telemetry-grid">
    <div id="panel-1" class="panel panel-tl">
      <div class="panel-title" style="color: var(--gb);">[01] LIVE AUDIO STREAM</div>
      <div class="panel-desc">Gemini 2.5 Low-Latency Pipeline<br>Status: SYNCED (48,000 Hz)</div>
    </div>
    <div id="panel-2" class="panel panel-tr">
      <div class="panel-title" style="color: var(--gr);">[02] 5-LAYER TRACKER</div>
      <div class="panel-desc">GNSS / IMU / BLE Matrix<br>Redundancy: ARMED & CALIBRATED</div>
    </div>
    <div id="panel-3" class="panel panel-bl">
      <div class="panel-title" style="color: var(--gg);">[03] ESRI 3D DIGITAL TWIN</div>
      <div class="panel-desc">Global Satellite Blueprint Mesh<br>Engine: READY [4K RASTER]</div>
    </div>
    <div id="panel-4" class="panel panel-br">
      <div class="panel-title" style="color: var(--gy);">[04] COGNITIVE REASONING</div>
      <div class="panel-desc">Deep Multi-Hop Thinking Core<br>Budget: 8,192 Tokens Allocated</div>
    </div>
  </div>

  <button class="skip-btn" onclick="skip()">INITIALIZE NOW &#9654;&#9654;</button>

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

        osc1.type = 'sawtooth';
        osc1.frequency.setValueAtTime(58, now);
        osc1.frequency.exponentialRampToValueAtTime(32, now + 3.2);

        osc2.type = 'sawtooth';
        osc2.frequency.setValueAtTime(58.6, now);
        osc2.frequency.exponentialRampToValueAtTime(32.4, now + 3.2);

        sub.type = 'sine';
        sub.frequency.setValueAtTime(29, now);
        sub.frequency.exponentialRampToValueAtTime(18, now + 3.2);

        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(2800, now);
        filter.frequency.exponentialRampToValueAtTime(100, now + 3.0);
        filter.Q.value = 7;

        gain.gain.setValueAtTime(0.01, now);
        gain.gain.linearRampToValueAtTime(0.9, now + 0.15);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 3.4);

        osc1.connect(filter); osc2.connect(filter); sub.connect(filter);
        filter.connect(gain); gain.connect(ctx.destination);

        osc1.start(now); osc2.start(now); sub.start(now);
        osc1.stop(now + 3.5); osc2.stop(now + 3.5); sub.stop(now + 3.5);
      } catch(e) {}
    }

    function playCyberClick() {
      try {
        const ctx = getAudioCtx();
        if (!ctx) return;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(2400 + Math.random() * 800, now);
        osc.frequency.exponentialRampToValueAtTime(800, now + 0.04);

        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.04);

        osc.connect(gain); gain.connect(ctx.destination);
        osc.start(now); osc.stop(now + 0.04);
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
        osc.frequency.setValueAtTime(100, now);
        osc.frequency.exponentialRampToValueAtTime(2200, now + 2.0);

        filter.type = 'bandpass';
        filter.frequency.setValueAtTime(200, now);
        filter.frequency.exponentialRampToValueAtTime(3200, now + 2.0);
        filter.Q.value = 5;

        gain.gain.setValueAtTime(0.01, now);
        gain.gain.linearRampToValueAtTime(0.5, now + 1.2);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 2.1);

        osc.connect(filter); filter.connect(gain); gain.connect(ctx.destination);
        osc.start(now); osc.stop(now + 2.1);
      } catch(e) {}
    }

    function speakVoice(text) {
      if (!('speechSynthesis' in window)) return;
      try {
        window.speechSynthesis.cancel();
        const utt = new SpeechSynthesisUtterance(text);
        utt.rate = 1.0;
        utt.pitch = 0.95;

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
       2. SCRAMBLE TEXT MATRIX DECRYPTION ENGINE
       ========================================================================= */
    const CHARS = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#@*<>_+=';

    function decryptText(elementId, finalText, duration = 1200) {
      const el = document.getElementById(elementId);
      if (!el) return;
      const startTime = performance.now();
      const length = finalText.length;

      function update(currentTime) {
        const progress = Math.min(1, (currentTime - startTime) / duration);
        const revealedCount = Math.floor(progress * length);
        let result = '';

        for (let i = 0; i < length; i++) {
          if (i < revealedCount) {
            result += finalText[i];
          } else if (finalText[i] === ' ') {
            result += ' ';
          } else {
            result += CHARS[Math.floor(Math.random() * CHARS.length)];
          }
        }
        el.innerText = result;
        if (Math.random() > 0.4) playCyberClick();

        if (progress < 1) {
          requestAnimationFrame(update);
        } else {
          el.innerText = finalText;
        }
      }
      requestAnimationFrame(update);
    }

    /* =========================================================================
       3. 3D WEBGL VOLUMETRIC QUANTUM PLASMA CORE (FROM SCRATCH)
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
      void main() {
        gl_Position = vec4(a_pos, 0.0, 1.0);
      }
    `;

    // 4K Raymarched Quantum Singularity with Google 4-Color Plasma
    const fsSource = `
      precision highp float;
      uniform vec2 u_res;
      uniform float u_time;
      uniform float u_stage;

      mat2 rot(float a) {
        float c = cos(a), s = sin(a);
        return mat2(c, -s, s, c);
      }

      void main() {
        vec2 uv = (gl_FragCoord.xy - 0.5 * u_res) / min(u_res.x, u_res.y);
        vec3 col = vec3(0.015, 0.025, 0.05);

        // Dynamic 3D Quantum Gyroscope
        float t = u_time * 0.8;
        vec2 p = uv;
        p *= rot(t * 0.4);

        float len = length(p);
        float ring1 = abs(sin(len * 18.0 - t * 3.0) / 18.0);
        float ring2 = abs(sin(len * 28.0 + t * 4.0) / 28.0);
        
        // Google Quad-Color Tendrils
        vec3 c_blue   = vec3(0.26, 0.52, 0.96);
        vec3 c_red    = vec3(0.92, 0.26, 0.21);
        vec3 c_yellow = vec3(0.98, 0.74, 0.02);
        vec3 c_green  = vec3(0.20, 0.66, 0.33);

        float angle = atan(p.y, p.x);
        vec3 plasma = mix(c_blue, c_red, smoothstep(-3.14, -1.0, angle));
        plasma = mix(plasma, c_yellow, smoothstep(-1.0, 1.0, angle));
        plasma = mix(plasma, c_green, smoothstep(1.0, 3.14, angle));

        float core = 0.08 / (len + 0.01);
        col += plasma * core * 0.6;
        col += plasma * (0.003 / (ring1 + 0.002)) * 0.8;
        col += vec3(0.0, 0.94, 1.0) * (0.002 / (ring2 + 0.002)) * 0.6;

        // Hyperdrive Implosion in Stage 4
        if (u_stage >= 4.0) {
          float warp = length(uv) * 12.0;
          col += vec3(0.4, 0.8, 1.0) * abs(sin(warp - u_time * 25.0));
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
       4. DIRECTOR CHOREOGRAPHY (4 DISTINCT 4K PHASES)
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

      // Determine active stage
      let currentStage = 1.0;
      if (elapsed >= 7.0 && elapsed < 15.0) currentStage = 2.0;
      else if (elapsed >= 15.0 && elapsed < 23.0) currentStage = 3.0;
      else if (elapsed >= 23.0) currentStage = 4.0;

      // Render WebGL Quantum Shader
      gl.useProgram(program);
      gl.enableVertexAttribArray(aPos);
      gl.bindBuffer(gl.ARRAY_BUFFER, posBuffer);
      gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);

      gl.uniform2f(uRes, canvas.width, canvas.height);
      gl.uniform1f(uTime, elapsed);
      gl.uniform1f(uStage, currentStage);

      gl.drawArrays(gl.TRIANGLES, 0, 6);

      // ── STAGE 1: NEXUS AI QUANTUM CORE (0s - 7s) ──
      if (elapsed < 7.0 && !s1) {
        playCinematicBraam();
        decryptText('main-title', 'N E X U S   A I', 1400);
        decryptText('sub-title', 'MULTIMODAL NEURAL CORE // v6.0', 1600);
        speakVoice("NEXUS Multimodal Operating System Core initialized.");
        s1 = true;
      }

      // ── STAGE 2: ARCHITECT KAMRAN JALIL CLEARANCE (7s - 15s) ──
      if (elapsed >= 7.0 && elapsed < 15.0 && !s2) {
        playCinematicBraam();
        playRiser();
        decryptText('main-title', 'KAMRAN JALIL', 1400);
        decryptText('sub-title', 'PRINCIPAL AI SYSTEMS ARCHITECT // ALPHA CLEARANCE', 1600);
        speakVoice("Architect signature verified: Kamran Jalil.");
        s2 = true;
      }

      // ── STAGE 3: 4-CORNER TACTICAL CYBERDECK (15s - 23s) ──
      if (elapsed >= 15.0 && elapsed < 23.0 && !s3) {
        playRiser();
        decryptText('main-title', 'SYSTEM ARMED', 1000);
        decryptText('sub-title', '5-LAYER SPATIAL REDUNDANCY & DEEP REASONING READY', 1400);
        speakVoice("Initializing multi-layer spatial telemetry and deep reasoning matrix.");

        // Animate floating panels
        document.querySelectorAll('.panel').forEach((p, idx) => {
          setTimeout(() => p.classList.add('visible'), idx * 250);
        });
        s3 = true;
      }

      // ── STAGE 4: HYPERDRIVE LAUNCH (23s - 30s) ──
      if (elapsed >= 23.0 && !s4) {
        playRiser();
        playCinematicBraam();
        decryptText('main-title', 'HYPERDRIVE ENGAGED', 800);
        decryptText('sub-title', 'ALL SYSTEMS NOMINAL. WELCOME, KAMRAN.', 1000);
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
    splash.finished.connect(lambda: (print("NEXUS Splash Completed!"), app.quit()))
    sys.exit(app.exec())