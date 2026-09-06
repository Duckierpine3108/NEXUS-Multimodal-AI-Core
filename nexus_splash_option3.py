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
            self._web.page().setBackgroundColor(QColor("#04060E"))
            
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
  <title>NEXUS AI - Synaptic Particle Matrix</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;500;800&family=Space+Grotesk:wght@400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');

    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --gb: #4285F4;
      --gr: #EA4335;
      --gy: #FBBC05;
      --gg: #34A853;
      --cyan: #00F0FF;
      --bg: #04060E;
    }

    html, body {
      width: 100vw; height: 100vh;
      background: var(--bg);
      color: #FFF;
      font-family: 'Plus Jakarta Sans', sans-serif;
      overflow: hidden;
      display: flex; align-items: center; justify-content: center;
      user-select: none;
    }

    #canvas {
      position: absolute; inset: 0;
      width: 100vw; height: 100vh;
      z-index: 1;
    }

    /* Spatial Ambient Glow */
    .ambient-glow {
      position: absolute;
      width: 650px; height: 650px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(66, 133, 244, 0.18) 0%, rgba(0, 240, 255, 0.08) 45%, transparent 70%);
      filter: blur(80px);
      z-index: 2;
      pointer-events: none;
      animation: pulseGlow 6s ease-in-out infinite alternate;
    }
    @keyframes pulseGlow {
      0% { transform: scale(0.9) translate(-50%, -50%); opacity: 0.6; }
      100% { transform: scale(1.25) translate(-50%, -50%); opacity: 0.95; }
    }
    .ambient-glow { top: 50%; left: 50%; transform: translate(-50%, -50%); }

    /* Minimalist Top/Bottom Telemetry Headers */
    .top-bar, .bottom-bar {
      position: absolute; left: 60px; right: 60px;
      z-index: 20;
      display: flex; justify-content: space-between; align-items: center;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      letter-spacing: 2.5px;
      color: rgba(255, 255, 255, 0.4);
      pointer-events: none;
    }
    .top-bar { top: 40px; }
    .bottom-bar { bottom: 40px; }

    .frosted-pill {
      display: inline-flex; align-items: center; gap: 10px;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.12);
      padding: 6px 16px;
      border-radius: 100px;
      backdrop-filter: blur(20px);
      color: rgba(255, 255, 255, 0.85);
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      letter-spacing: 1.5px;
    }

    .synapse-dot {
      width: 7px; height: 7px; border-radius: 50%;
      background: var(--cyan);
      box-shadow: 0 0 12px var(--cyan);
      animation: synapsePulse 1.2s infinite;
    }
    @keyframes synapsePulse { 50% { opacity: 0.2; transform: scale(0.7); } }

    /* Monolithic Center Stage */
    .center-stage {
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

    .hero-badge {
      display: inline-block;
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      letter-spacing: 6px;
      color: var(--cyan);
      background: rgba(0, 240, 255, 0.06);
      border: 1px solid rgba(0, 240, 255, 0.25);
      padding: 6px 20px;
      border-radius: 100px;
      margin-bottom: 20px;
      backdrop-filter: blur(15px);
      text-transform: uppercase;
      box-shadow: 0 0 30px rgba(0, 240, 255, 0.15);
    }

    .hero-title {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 78px;
      font-weight: 700;
      letter-spacing: 12px;
      text-transform: uppercase;
      background: linear-gradient(135deg, #FFFFFF 0%, #E2E8F0 50%, var(--gb) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-shadow: 0 0 60px rgba(66, 133, 244, 0.4);
      margin-bottom: 12px;
      line-height: 1.1;
    }

    .hero-sub {
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      letter-spacing: 7px;
      color: var(--gy);
      text-transform: uppercase;
      text-shadow: 0 0 20px rgba(251, 188, 5, 0.6);
    }

    /* 4 Floating Spatial Cluster Capsules */
    .clusters-container {
      position: absolute;
      inset: 100px 60px;
      pointer-events: none;
      display: grid;
      grid-template-columns: 1fr 1fr;
      grid-template-rows: 1fr 1fr;
      z-index: 18;
    }

    .cluster-card {
      position: absolute;
      width: 330px;
      background: rgba(255, 255, 255, 0.025);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 16px;
      padding: 20px 24px;
      backdrop-filter: blur(24px);
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
      opacity: 0;
      transform: translateY(24px);
      transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .cluster-card.active {
      opacity: 1;
      transform: translateY(0);
    }

    .cluster-tl { top: 0; left: 0; }
    .cluster-tr { top: 0; right: 0; text-align: right; }
    .cluster-bl { bottom: 0; left: 0; }
    .cluster-br { bottom: 0; right: 0; text-align: right; }

    .cluster-title {
      font-family: 'Space Grotesk', sans-serif;
      font-size: 13px; font-weight: 700; letter-spacing: 2px;
      margin-bottom: 6px;
    }
    .cluster-desc {
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px; color: rgba(255, 255, 255, 0.5);
      line-height: 1.5;
    }

    .wave-line {
      width: 100%; height: 18px; margin-top: 10px;
    }

    /* Clean Floating Launch Button */
    .skip-btn {
      position: absolute;
      bottom: 50px; right: 60px;
      z-index: 40;
      background: rgba(255, 255, 255, 0.06);
      border: 1px solid rgba(0, 240, 255, 0.5);
      color: var(--cyan);
      font-family: 'Space Grotesk', sans-serif;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 3px;
      padding: 14px 32px;
      border-radius: 100px;
      cursor: pointer;
      backdrop-filter: blur(20px);
      box-shadow: 0 0 35px rgba(0, 240, 255, 0.25);
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      pointer-events: auto;
    }
    .skip-btn:hover {
      background: var(--cyan);
      color: #04060E;
      box-shadow: 0 0 55px rgba(0, 240, 255, 0.85);
      transform: scale(1.05);
    }
  </style>
</head>
<body>
  <div class="ambient-glow"></div>
  <canvas id="canvas"></canvas>

  <div class="top-bar">
    <div class="frosted-pill"><span class="synapse-dot"></span>NEURAL LATTICE // SYNCHRONIZED</div>
    <div>SPATIAL DEPTH: 1,200 NODES</div>
    <div>LATENCY: 0.42 ms</div>
  </div>

  <div class="bottom-bar">
    <div>ARCHITECTURE: QUANTUM SYNAPTIC CORE</div>
    <div>PRECISION: FLOAT32 FULL-SPECTRUM</div>
    <div class="frosted-pill">SYSTEM STATUS: OPTIMAL</div>
  </div>

  <div class="center-stage">
    <div id="hero-badge" class="hero-badge">NEURAL KERNEL INITIALIZATION</div>
    <div id="hero-title" class="hero-title"></div>
    <div id="hero-sub" class="hero-sub"></div>
  </div>

  <!-- 4 Spatial Capsule Modules -->
  <div class="clusters-container">
    <div id="card-1" class="cluster-card cluster-tl">
      <div class="cluster-title" style="color: var(--gb);">[01] GEMINI 2.5 SPATIAL AUDIO</div>
      <div class="cluster-desc">48 kHz Ultra-Res Bi-Directional Stream<br>Latency: ZERO-BUFFER REALTIME</div>
      <svg class="wave-line" viewBox="0 0 280 18">
        <path d="M0,9 Q35,2 70,9 T140,9 T210,9 T280,9" fill="none" stroke="var(--gb)" stroke-width="1.8" />
      </svg>
    </div>

    <div id="card-2" class="cluster-card cluster-tr">
      <div class="cluster-title" style="color: var(--gr);">[02] 5-LAYER SPATIAL TRACKER</div>
      <div class="cluster-desc">GNSS / IMU / BLE Triangulation<br>Matrix: 100% SENSOR REDUNDANT</div>
      <svg class="wave-line" viewBox="0 0 280 18">
        <path d="M0,9 Q35,16 70,9 T140,9 T210,9 T280,9" fill="none" stroke="var(--gr)" stroke-width="1.8" />
      </svg>
    </div>

    <div id="card-3" class="cluster-card cluster-bl">
      <div class="cluster-title" style="color: var(--gg);">[03] ESRI 3D DIGITAL TWIN</div>
      <div class="cluster-desc">Global Satellite Blueprint Mesh<br>Engine: HIGH-POLY 4K TERRAIN</div>
      <svg class="wave-line" viewBox="0 0 280 18">
        <path d="M0,9 Q35,3 70,9 T140,9 T210,9 T280,9" fill="none" stroke="var(--gg)" stroke-width="1.8" />
      </svg>
    </div>

    <div id="card-4" class="cluster-card cluster-br">
      <div class="cluster-title" style="color: var(--gy);">[04] COGNITIVE REASONING</div>
      <div class="cluster-desc">8,192 Token Multi-Hop Thinking<br>Status: DEEP RECURSION READY</div>
      <svg class="wave-line" viewBox="0 0 280 18">
        <path d="M0,9 Q35,15 70,9 T140,9 T210,9 T280,9" fill="none" stroke="var(--gy)" stroke-width="1.8" />
      </svg>
    </div>
  </div>

  <button class="skip-btn" onclick="skip()">LAUNCH INTERFACE &#9654;&#9654;</button>

  <script>
    /* =========================================================================
       1. PRISTINE FM ACOUSTIC SHIMMER & BINAURAL AUDIO SYNTHESIZER
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

    // Pristine FM Bell/Pad Shimmer Chord (Interstellar / Apple Keynote Style)
    function playHarmonicShimmer() {
      try {
        const ctx = getAudioCtx();
        if (!ctx) return;
        const now = ctx.currentTime;

        const freqs = [130.81, 196.00, 261.63, 392.00, 523.25]; // C3 Major Harmonic Chord
        freqs.forEach((f, i) => {
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          const pan = ctx.createStereoPanner ? ctx.createStereoPanner() : null;

          osc.type = 'sine';
          osc.frequency.setValueAtTime(f, now);
          osc.frequency.exponentialRampToValueAtTime(f * 1.008, now + 4.0);

          gain.gain.setValueAtTime(0.001, now);
          gain.gain.linearRampToValueAtTime(0.18 / (i + 1), now + 0.8);
          gain.gain.exponentialRampToValueAtTime(0.0001, now + 4.5);

          if (pan) {
            pan.pan.value = (i % 2 === 0 ? -0.4 : 0.4);
            osc.connect(gain); gain.connect(pan); pan.connect(ctx.destination);
          } else {
            osc.connect(gain); gain.connect(ctx.destination);
          }

          osc.start(now); osc.stop(now + 4.6);
        });
      } catch(e) {}
    }

    // Deep Spatial Sub Resonance Drop
    function playDeepSubPulse() {
      try {
        const ctx = getAudioCtx();
        if (!ctx) return;
        const now = ctx.currentTime;

        const sub = ctx.createOscillator();
        const filter = ctx.createBiquadFilter();
        const gain = ctx.createGain();

        sub.type = 'sine';
        sub.frequency.setValueAtTime(65, now);
        sub.frequency.exponentialRampToValueAtTime(28, now + 3.2);

        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(800, now);
        filter.frequency.exponentialRampToValueAtTime(80, now + 3.0);

        gain.gain.setValueAtTime(0.01, now);
        gain.gain.linearRampToValueAtTime(0.85, now + 0.15);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 3.4);

        sub.connect(filter); filter.connect(gain); gain.connect(ctx.destination);
        sub.start(now); sub.stop(now + 3.5);
      } catch(e) {}
    }

    // Glass Neural Ping
    function playGlassPing(f = 1760) {
      try {
        const ctx = getAudioCtx();
        if (!ctx) return;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'sine';
        osc.frequency.setValueAtTime(f, now);
        osc.frequency.exponentialRampToValueAtTime(f * 0.5, now + 0.15);

        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);

        osc.connect(gain); gain.connect(ctx.destination);
        osc.start(now); osc.stop(now + 0.15);
      } catch(e) {}
    }

    // Hyperdrive Neural Warp
    function playWarpSweep() {
      try {
        const ctx = getAudioCtx();
        if (!ctx) return;
        const now = ctx.currentTime;
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'triangle';
        osc.frequency.setValueAtTime(80, now);
        osc.frequency.exponentialRampToValueAtTime(1800, now + 2.0);

        gain.gain.setValueAtTime(0.01, now);
        gain.gain.linearRampToValueAtTime(0.4, now + 1.0);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 2.1);

        osc.connect(gain); gain.connect(ctx.destination);
        osc.start(now); osc.stop(now + 2.1);
      } catch(e) {}
    }

    function speakVoice(text) {
      if (!('speechSynthesis' in window)) return;
      try {
        window.speechSynthesis.cancel();
        playGlassPing(2200);
        const utt = new SpeechSynthesisUtterance(text);
        utt.rate = 1.0;
        utt.pitch = 0.96;

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
       2. PRISMATIC KINETIC TYPOGRAPHY DECRYPTION
       ========================================================================= */
    const SYMBOLS = 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789//';

    function decryptHeroText(elementId, finalText, duration = 1200) {
      const el = document.getElementById(elementId);
      if (!el) return;
      const startTime = performance.now();
      const length = finalText.length;

      function update(now) {
        const progress = Math.min(1, (now - startTime) / duration);
        const charsRevealed = Math.floor(progress * length);
        let output = '';

        for (let i = 0; i < length; i++) {
          if (i < charsRevealed) {
            output += finalText[i];
          } else if (finalText[i] === ' ') {
            output += ' ';
          } else {
            output += SYMBOLS[Math.floor(Math.random() * SYMBOLS.length)];
          }
        }
        el.innerText = output;

        if (progress < 1) {
          requestAnimationFrame(update);
        } else {
          el.innerText = finalText;
        }
      }
      requestAnimationFrame(update);
    }

    /* =========================================================================
       3. 3D SYNAPTIC PARTICLE MATRIX & QUANTUM MESH (4K HIGH-DPI)
       ========================================================================= */
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    let W, H, dpr = 1;

    function resize() {
      dpr = Math.max(2, window.devicePixelRatio || 1);
      W = window.innerWidth;
      H = window.innerHeight;
      canvas.width = W * dpr;
      canvas.height = H * dpr;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);
    }
    window.addEventListener('resize', resize);
    resize();

    // 3D Particles with Synaptic Connectivity
    const NUM_PARTICLES = 360;
    const particles = [];
    const GOOGLE_COLORS = ['#4285F4', '#EA4335', '#FBBC05', '#34A853', '#00F0FF'];

    for (let i = 0; i < NUM_PARTICLES; i++) {
      particles.push({
        x: (Math.random() - 0.5) * 2400,
        y: (Math.random() - 0.5) * 1600,
        z: Math.random() * 1200 + 100,
        vx: (Math.random() - 0.5) * 0.8,
        vy: (Math.random() - 0.5) * 0.8,
        vz: (Math.random() - 0.5) * 0.8,
        color: GOOGLE_COLORS[Math.floor(Math.random() * GOOGLE_COLORS.length)],
        baseRadius: Math.random() * 2.5 + 1.2
      });
    }

    /* =========================================================================
       4. DIRECTOR CHOREOGRAPHY (4 DISTINCT PHASES)
       ========================================================================= */
    let startTime = null;
    let p1 = false, p2 = false, p3 = false, p4 = false;

    function render(now) {
      if (!startTime) startTime = now;
      const elapsed = (now - startTime) / 1000;

      if (elapsed >= 30.0) {
        skip();
        return;
      }

      ctx.save();
      ctx.fillStyle = '#04060E';
      ctx.fillRect(0, 0, W, H);

      const cx = W / 2, cy = H / 2;
      const fov = 500;
      const speedMultiplier = elapsed > 23.0 ? 32 : (elapsed > 15.0 ? 2.5 : 1.2);

      // Project and render 3D Synaptic Lattice
      const projected = [];
      particles.forEach(p => {
        p.x += p.vx * speedMultiplier;
        p.y += p.vy * speedMultiplier;
        p.z -= (elapsed > 23.0 ? 45 : 0.8);

        if (p.z <= 10) p.z = 1200;
        if (p.z > 1200) p.z = 10;

        const k = fov / p.z;
        const px = p.x * k + cx;
        const py = p.y * k + cy;
        const alpha = Math.min(1, (1200 - p.z) / 700);

        if (px >= 0 && px <= W && py >= 0 && py <= H) {
          projected.push({ x: px, y: py, alpha, color: p.color, r: p.baseRadius * k });
        }
      });

      // Draw Synaptic Connective Lines between nearby nodes
      ctx.lineWidth = 0.8;
      for (let i = 0; i < projected.length; i++) {
        for (let j = i + 1; j < projected.length; j++) {
          const dx = projected[i].x - projected[j].x;
          const dy = projected[i].y - projected[j].y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 95) {
            const lineAlpha = (1 - dist / 95) * 0.22 * projected[i].alpha;
            ctx.strokeStyle = projected[i].color;
            ctx.globalAlpha = lineAlpha;
            ctx.beginPath();
            ctx.moveTo(projected[i].x, projected[i].y);
            ctx.lineTo(projected[j].x, projected[j].y);
            ctx.stroke();
          }
        }
      }

      // Draw Nodes
      projected.forEach(p => {
        ctx.globalAlpha = p.alpha;
        ctx.fillStyle = p.color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      });
      ctx.globalAlpha = 1.0;

      // ── PHASE 1: SYNAPTIC INCEPTION (0s – 7s) ──
      if (elapsed < 7.0 && !p1) {
        playHarmonicShimmer();
        playDeepSubPulse();
        decryptHeroText('hero-badge', 'SYNAPTIC NEURAL CORE // v7.0', 1000);
        decryptHeroText('hero-title', 'N E X U S   A I', 1400);
        decryptHeroText('hero-sub', 'AUTONOMOUS MULTIMODAL INTELLIGENCE', 1600);
        speakVoice("Synaptic neural lattice connected. NEXUS Multimodal Intelligence active.");
        p1 = true;
      }

      // ── PHASE 2: CREATOR MONOLITH - KAMRAN JALIL (7s – 15s) ──
      if (elapsed >= 7.0 && elapsed < 15.0 && !p2) {
        playHarmonicShimmer();
        playDeepSubPulse();
        decryptHeroText('hero-badge', 'CHIEF ARCHITECT CLEARANCE // LEVEL-0', 1000);
        decryptHeroText('hero-title', 'KAMRAN JALIL', 1400);
        decryptHeroText('hero-sub', 'PRINCIPAL AI SYSTEMS ARCHITECT & FOUNDER', 1600);
        speakVoice("Architect signature authenticated: Kamran Jalil. Master neural control established.");
        p2 = true;
      }

      // ── PHASE 3: SPATIAL COGNITIVE MATRIX (15s – 23s) ──
      if (elapsed >= 15.0 && elapsed < 23.0 && !p3) {
        playHarmonicShimmer();
        playWarpSweep();
        decryptHeroText('hero-badge', 'SPATIAL INTELLIGENCE CLUSTER', 1000);
        decryptHeroText('hero-title', 'ALL LAYERS SYNCED', 1200);
        decryptHeroText('hero-sub', 'SPATIAL TELEMETRY & RECURSIVE REASONING ENGAGED', 1500);
        speakVoice("Deploying 5-layer spatial telemetry, ESRI digital twin, and recursive reasoning.");

        // Animate frosted capsules
        document.querySelectorAll('.cluster-card').forEach((card, i) => {
          setTimeout(() => card.classList.add('active'), i * 220);
        });
        p3 = true;
      }

      // ── PHASE 4: QUANTUM SINGULARITY LAUNCH (23s – 30s) ──
      if (elapsed >= 23.0 && !p4) {
        playWarpSweep();
        playDeepSubPulse();
        decryptHeroText('hero-badge', 'SUPERPOSITION ACHIEVED', 800);
        decryptHeroText('hero-title', 'LAUNCHING NEXUS', 1000);
        decryptHeroText('hero-sub', 'ALL SYSTEMS NOMINAL. WELCOME, KAMRAN.', 1200);
        speakVoice("System synchronization complete. Welcome, Kamran.");
        p4 = true;
      }

      ctx.restore();
      requestAnimationFrame(render);
    }

    requestAnimationFrame(render);
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
    splash.finished.connect(lambda: (print("NEXUS Option 3 Splash completed!"), app.quit()))
    sys.exit(app.exec())