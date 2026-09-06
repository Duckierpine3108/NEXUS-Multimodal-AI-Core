# ==============================================================================
#                  NEXUS — MULTIMODAL OS CORE INTERFACE
#          Ultra-Fidelity Frosted Matte Glassmorphism & 3D Arc Engine
# ==============================================================================

from __future__ import annotations

import json
import math
import os
# ── Unlock Chromium Audio Autoplay (No user click required) ───────────────────
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--autoplay-policy=no-user-gesture-required --no-sandbox --enable-gpu-rasterization --ignore-gpu-blocklist"
import platform
import random
import subprocess
import sys
import threading
import time
from pathlib import Path

import psutil

if platform.system() == "Windows":
    _WIN_HIDE: dict = {"creationflags": subprocess.CREATE_NO_WINDOW}
else:
    _WIN_HIDE: dict = {}

from PyQt6.QtCore import (
    QEasingCurve, QMimeData, QObject, QPointF, QRectF, QSize, Qt,
    QTimer, QUrl, pyqtSignal,
)
from PyQt6.QtGui import (
    QBrush, QColor, QConicalGradient, QDragEnterEvent, QDropEvent, QFont,
    QFontDatabase, QKeySequence, QLinearGradient, QPainter, QPainterPath,
    QPen, QPixmap, QRadialGradient, QShortcut,
)
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QFrame, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QScrollArea, QSizePolicy, QSplitter,
    QStackedWidget, QTextEdit, QVBoxLayout, QWidget, QProgressBar,
)

def _base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

BASE_DIR   = _base_dir()
CONFIG_DIR = BASE_DIR / "config"
API_FILE   = CONFIG_DIR / "api_keys.json"

def _read_full_config() -> dict:
    try:
        return json.loads(API_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

_DEFAULT_W, _DEFAULT_H = 1080, 740
_MIN_W,     _MIN_H     = 920,  640
_LEFT_W  = 160
_RIGHT_W = 360
_OS = platform.system()

# ── Dynamic Theme & Visual FX Engine ──────────────────────────────────────────
class Theme:
    DARK = True
    FX_MODE = "NONE"  # "NONE" | "MATRIX" | "GOOGLE_GLOW"

    # Google Signature Palette
    G_BLUE   = "#4285F4"
    G_RED    = "#EA4335"
    G_YELLOW = "#FBBC05"
    G_GREEN  = "#34A853"

    # Dark Mode Palette
    D_BG         = "#07090e"
    D_PANEL      = "rgba(13, 17, 26, 0.88)"
    D_PANEL_ALT  = "rgba(20, 26, 38, 0.75)"
    D_BORDER     = "rgba(255, 255, 255, 0.09)"
    D_BORDER_H   = "rgba(66, 133, 244, 0.45)"
    D_TEXT       = "#F1F5F9"
    D_TEXT_MUTED = "#94A3B8"
    D_TEXT_DIM   = "#64748B"
    D_BAR_BG     = "rgba(255, 255, 255, 0.07)"

    # Light Mode Palette (Ultra-Crisp & 100% Readable)
    L_BG         = "#F8FAFC"
    L_PANEL      = "rgba(255, 255, 255, 0.95)"
    L_PANEL_ALT  = "rgba(241, 245, 249, 0.90)"
    L_BORDER     = "rgba(15, 23, 42, 0.12)"
    L_BORDER_H   = "rgba(66, 133, 244, 0.65)"
    L_TEXT       = "#0F172A"       # Deep Slate Black (Never washed out)
    L_TEXT_MUTED = "#334155"       # High contrast secondary text
    L_TEXT_DIM   = "#64748B"
    L_BAR_BG     = "rgba(0, 0, 0, 0.08)"

    # Active dynamic slots
    BG        = D_BG
    PANEL     = D_PANEL
    PANEL_ALT = D_PANEL_ALT
    BORDER    = D_BORDER
    BORDER_H  = D_BORDER_H
    TEXT      = D_TEXT
    TEXT_MUTED= D_TEXT_MUTED
    TEXT_DIM  = D_TEXT_DIM
    BAR_BG    = D_BAR_BG

    PRI       = G_BLUE
    ACC       = G_YELLOW
    GREEN     = G_GREEN
    RED       = G_RED

    @classmethod
    def set_mode(cls, dark: bool):
        cls.DARK = dark
        if dark:
            cls.BG, cls.PANEL, cls.PANEL_ALT = cls.D_BG, cls.D_PANEL, cls.D_PANEL_ALT
            cls.BORDER, cls.BORDER_H, cls.TEXT = cls.D_BORDER, cls.D_BORDER_H, cls.D_TEXT
            cls.TEXT_MUTED, cls.TEXT_DIM, cls.BAR_BG = cls.D_TEXT_MUTED, cls.D_TEXT_DIM, cls.D_BAR_BG
        else:
            cls.BG, cls.PANEL, cls.PANEL_ALT = cls.L_BG, cls.L_PANEL, cls.L_PANEL_ALT
            cls.BORDER, cls.BORDER_H, cls.TEXT = cls.L_BORDER, cls.L_BORDER_H, cls.L_TEXT
            cls.TEXT_MUTED, cls.TEXT_DIM, cls.BAR_BG = cls.L_TEXT_MUTED, cls.L_TEXT_DIM, cls.L_BAR_BG

def qcol(h: str, a: int = 255) -> QColor:
    # Ensure alpha is always safely clamped between 0 and 255
    a = max(0, min(255, int(a)))
    if h.startswith("rgba"):
        parts = h.replace("rgba(", "").replace(")", "").split(",")
        r, g, b = int(parts[0]), int(parts[1]), int(parts[2])
        alpha = int(float(parts[3]) * 255) if len(parts) > 3 else a
        return QColor(r, g, b, max(0, min(255, alpha)))
    c = QColor(h)
    c.setAlpha(a)
    return c

# ── Hardware Metrics Monitor (Fail-safe & Isolated) ───────────────────────────
_nvml_lib: object = None
_nvml_ok:  object = None

def _nvml_gpu_windows() -> float:
    global _nvml_lib, _nvml_ok
    if _nvml_ok is False:
        return -1.0
    try:
        import ctypes
        class _Util(ctypes.Structure):
            _fields_ = [("gpu", ctypes.c_uint), ("memory", ctypes.c_uint)]

        if _nvml_lib is None:
            for dll in ("nvml.dll", r"C:\Windows\System32\nvml.dll"):
                try:
                    lib = ctypes.WinDLL(dll)
                    init_fn = getattr(lib, "nvmlInit_v2", getattr(lib, "nvmlInit", None))
                    if init_fn and init_fn() == 0:
                        _nvml_lib = lib
                        break
                except Exception:
                    continue

        if _nvml_lib is None:
            _nvml_ok = False
            return -1.0

        dev = ctypes.c_void_p()
        get_dev = getattr(_nvml_lib, "nvmlDeviceGetHandleByIndex_v2", getattr(_nvml_lib, "nvmlDeviceGetHandleByIndex", None))
        if get_dev and get_dev(0, ctypes.byref(dev)) == 0:
            util = _Util()
            if _nvml_lib.nvmlDeviceGetUtilizationRates(dev, ctypes.byref(util)) == 0:
                _nvml_ok = True
                return float(util.gpu)
    except Exception:
        pass
    _nvml_ok = False
    return -1.0

class _SysMetrics:
    def __init__(self):
        self.cpu = 0.0
        self.mem = 0.0
        self.net = 0.0
        self.gpu = -1.0
        self.tmp = -1.0
        self._lock = threading.Lock()
        self._last_net = None
        try:
            self._last_net = psutil.net_io_counters()
        except Exception:
            pass
        self._last_net_t = time.time()
        self._running = True

        # Warm-up CPU baseline counter
        try:
            psutil.cpu_percent(interval=None)
        except Exception:
            pass

        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while self._running:
            self._update()
            time.sleep(1.5)

    def _update(self):
        # 1. CPU (Isolated)
        try:
            cpu = float(psutil.cpu_percent(interval=None))
        except Exception:
            cpu = 0.0

        # 2. RAM (Isolated)
        try:
            mem = float(psutil.virtual_memory().percent)
        except Exception:
            mem = 0.0

        # 3. NET (Isolated)
        net = 0.0
        try:
            nc = psutil.net_io_counters()
            now = time.time()
            dt = now - self._last_net_t
            if self._last_net and dt > 0:
                sent = nc.bytes_sent - self._last_net.bytes_sent
                recv = nc.bytes_recv - self._last_net.bytes_recv
                net = (sent + recv) / (1024 * 1024 * dt)
            self._last_net = nc
            self._last_net_t = now
        except Exception:
            pass

        # 4. GPU (Isolated - failure will never block CPU or RAM)
        gpu = -1.0
        try:
            if _OS == "Windows":
                gpu = _nvml_gpu_windows()
        except Exception:
            gpu = -1.0

        # Commit readings safely to thread lock
        with self._lock:
            self.cpu = cpu
            self.mem = mem
            self.net = net
            self.gpu = gpu
            
            
    def snapshot(self) -> dict:
        with self._lock:
            return {
                "cpu": self.cpu,
                "mem": self.mem,
                "net": self.net,
                "gpu": self.gpu
            }
            
# ── Create the Global Instance (ADD THIS LINE) ────────────────────────────────
_metrics = _SysMetrics()

# ── Dynamic Multi-FX Central Reactor Core ─────────────────────────────────────
class CoreOrbCanvas(QWidget):
    def __init__(self, face_path: str, assistant_name: str = "NEXUS", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)
        self.setMinimumSize(360, 360)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.muted    = False
        self.speaking = False
        self.state    = "INITIALISING"
        self._assistant_name = assistant_name

        self._tick = 0
        self._rot1 = 0.0
        self._rot2 = 180.0
        self._scale = 1.0
        self._tgt_scale = 1.0
        self._glow_angle = 0.0
        self._particles: list[list[float]] = []

        # Matrix Rain Columns: [x, y, speed, length, char_list]
        self._matrix_cols: list[dict] = []
        self._init_matrix()

        self._face_px: QPixmap | None = None
        self._load_face(face_path)

        self._tmr = QTimer(self)
        self._tmr.timeout.connect(self._step)
        self._tmr.start(16)

    def _init_matrix(self):
        self._matrix_cols = []
        for x in range(0, 1920, 20):
            self._matrix_cols.append({
                "x": float(x),
                "y": random.uniform(-600, 0),
                "speed": random.uniform(3.5, 9.0),
                "len": random.randint(8, 22),
                "chars": [random.choice(["0", "1", "x", "f", "7", "A", "9"]) for _ in range(25)]
            })

    def _load_face(self, path: str):
        try:
            from PIL import Image, ImageDraw
            import io
            img = Image.open(path).convert("RGBA")
            sz = min(img.size)
            img = img.resize((sz, sz), Image.LANCZOS)
            mask = Image.new("L", (sz, sz), 0)
            ImageDraw.Draw(mask).ellipse((2, 2, sz - 2, sz - 2), fill=255)
            img.putalpha(mask)
            buf = io.BytesIO(); img.save(buf, format="PNG")
            px = QPixmap(); px.loadFromData(buf.getvalue())
            self._face_px = px
        except Exception:
            self._face_px = None

    def _step(self):
        self._tick += 1
        speed = 2.6 if self.speaking else (0.85 if not self.muted else 0.2)
        self._rot1 = (self._rot1 + speed) % 360
        self._rot2 = (self._rot2 - speed * 1.25) % 360
        self._glow_angle = (self._glow_angle + 2.2) % 360

        # Matrix step
        if Theme.FX_MODE == "MATRIX":
            H = self.height()
            for col in self._matrix_cols:
                col["y"] += col["speed"]
                if col["y"] > H + 200:
                    col["y"] = random.uniform(-200, -20)
                    col["speed"] = random.uniform(3.5, 8.5)

        if self.speaking:
            self._tgt_scale = 1.04 + 0.06 * math.sin(self._tick * 0.16)
            if random.random() < 0.35:
                ang = random.uniform(0, 2 * math.pi)
                r0 = random.uniform(85, 125)
                self._particles.append([
                    math.cos(ang) * r0, math.sin(ang) * r0,
                    math.cos(ang) * random.uniform(0.6, 2.0),
                    math.sin(ang) * random.uniform(0.6, 2.0),
                    1.0, random.choice([Theme.G_BLUE, Theme.G_RED, Theme.G_YELLOW, Theme.G_GREEN])
                ])
        else:
            self._tgt_scale = 1.0 + 0.012 * math.sin(self._tick * 0.05)

        self._scale += (self._tgt_scale - self._scale) * 0.18
        self._particles = [
            [p[0]+p[2], p[1]+p[3], p[2]*0.97, p[3]*0.97, p[4]-0.024, p[5]]
            for p in self._particles if (p[4] - 0.024) > 0
        ]
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), qcol(Theme.BG))

        W, H = self.width(), self.height()
        cx, cy = W / 2, H / 2
        fw = min(W, H)
        core_r = fw * 0.22 * self._scale

        # ── 1. MATRIX HACKER RAIN FX ──────────────────────────────────────────
        if Theme.FX_MODE == "MATRIX":
            p.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
            for col in self._matrix_cols:
                x = col["x"]
                if x > W + 20: continue
                for i in range(col["len"]):
                    y = col["y"] - (i * 15)
                    if 0 <= y <= H:
                        alpha = int(255 * (1.0 - i / col["len"]))
                        p.setPen(QPen(qcol("#FFFFFF" if i == 0 else "#00FF66", alpha)))
                        char = col["chars"][i % len(col["chars"])]
                        p.drawText(QPointF(x, y), char)

        # ── 2. GOOGLE GLOW AURORA AURA ────────────────────────────────────────
        elif Theme.FX_MODE == "GOOGLE_GLOW":
            glow_r = fw * 0.48
            conical = QConicalGradient(cx, cy, self._glow_angle)
            conical.setColorAt(0.00, qcol(Theme.G_BLUE, 65))
            conical.setColorAt(0.25, qcol(Theme.G_RED, 65))
            conical.setColorAt(0.50, qcol(Theme.G_YELLOW, 65))
            conical.setColorAt(0.75, qcol(Theme.G_GREEN, 65))
            conical.setColorAt(1.00, qcol(Theme.G_BLUE, 65))
            p.setBrush(QBrush(conical)); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(cx - glow_r, cy - glow_r, glow_r * 2, glow_r * 2))

        # ── 3. STANDARD ADAPTIVE BACKGROUND LIGHTING ──────────────────────────
        else:
            radial = QRadialGradient(cx, cy, fw * 0.48)
            if self.muted:
                radial.setColorAt(0.0, qcol("#2a0a0a", 80))
            elif self.speaking:
                radial.setColorAt(0.0, qcol(Theme.G_BLUE, 80))
                radial.setColorAt(0.5, qcol(Theme.G_GREEN, 30))
            elif Theme.DARK:
                radial.setColorAt(0.0, qcol("#141f36", 70))
            else:
                radial.setColorAt(0.0, qcol("#E2E8F0", 90))
            radial.setColorAt(1.0, qcol(Theme.BG, 0))
            p.setBrush(QBrush(radial)); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QRectF(cx - fw * 0.48, cy - fw * 0.48, fw * 0.96, fw * 0.96))

        # ── 4. CONCENTRIC 3D METALLIC DISCS (Dark & Light Mode Adaptive) ───────
        r_stages = [core_r * 1.85, core_r * 1.50, core_r * 1.18]
        if Theme.DARK:
            disc_colors = [
                (QColor("#0d121c"), QColor("#182232"), QColor("#222e44")),
                (QColor("#111724"), QColor("#1f2a3e"), QColor("#2b3952")),
                (QColor("#141c2c"), QColor("#243148"), QColor("#354664")),
            ]
        else:
            # Pearl Titanium / Silver for Light Mode
            disc_colors = [
                (QColor("#CBD5E1"), QColor("#FFFFFF"), QColor("#94A3B8")),
                (QColor("#E2E8F0"), QColor("#FFFFFF"), QColor("#CBD5E1")),
                (QColor("#F1F5F9"), QColor("#FFFFFF"), QColor("#E2E8F0")),
            ]

        for r_step, (c_bg, c_top, c_rim) in zip(r_stages, disc_colors):
            rect_step = QRectF(cx - r_step, cy - r_step, r_step * 2, r_step * 2)
            grad_disc = QLinearGradient(rect_step.topLeft(), rect_step.bottomRight())
            grad_disc.setColorAt(0.0, c_top); grad_disc.setColorAt(1.0, c_bg)
            p.setBrush(QBrush(grad_disc)); p.setPen(QPen(c_rim, 1.2))
            p.drawEllipse(rect_step)

        # ── 5. GOOGLE STUDIO ROTATING GLOWING ARCS ────────────────────────────
        colors = [Theme.G_GREEN, Theme.G_BLUE, Theme.G_RED, Theme.G_YELLOW] if not self.muted else [Theme.RED]*4

        # Outer Orbit Arcs
        arc1_r = core_r * 1.68
        rect_arc1 = QRectF(cx - arc1_r, cy - arc1_r, arc1_r * 2, arc1_r * 2)
        for i, c in enumerate(colors):
            start_ang = int((self._rot1 + i * 90) * 16)
            span_ang  = int(64 * 16)
            p.setPen(QPen(qcol(c, 45 if not self.muted else 20), 8.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawArc(rect_arc1, start_ang, span_ang)
            p.setPen(QPen(qcol(c, 240 if not self.muted else 140), 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawArc(rect_arc1, start_ang, span_ang)

        # Inner Orbit Arcs
        arc2_r = core_r * 1.34
        rect_arc2 = QRectF(cx - arc2_r, cy - arc2_r, arc2_r * 2, arc2_r * 2)
        for i, c in enumerate(colors):
            start_ang = int((self._rot2 + i * 90) * 16)
            span_ang  = int(52 * 16)
            p.setPen(QPen(qcol(c, 40 if not self.muted else 15), 6.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawArc(rect_arc2, start_ang, span_ang)
            p.setPen(QPen(qcol(c, 220 if not self.muted else 120), 2.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawArc(rect_arc2, start_ang, span_ang)

        # ── 6. PARTICLES ──────────────────────────────────────────────────────
        for pt in self._particles:
            p.setBrush(QBrush(qcol(pt[5], int(pt[4] * 255))))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx + pt[0], cy + pt[1]), 2.2, 2.2)

        # ── 7. CENTER SPHERE / DOME (High-Contrast in Light & Dark) ───────────
        if self._face_px:
            fsz = int(core_r * 1.7)
            scaled = self._face_px.scaled(fsz, fsz, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            p.drawPixmap(int(cx - fsz / 2), int(cy - fsz / 2), scaled)
        else:
            dome_r = core_r * 0.88
            rect_dome = QRectF(cx - dome_r, cy - dome_r, dome_r * 2, dome_r * 2)
            grad_dome = QLinearGradient(rect_dome.topLeft(), rect_dome.bottomRight())
            if self.muted:
                grad_dome.setColorAt(0.0, QColor("#381616")); grad_dome.setColorAt(1.0, QColor("#160808"))
            elif Theme.DARK:
                grad_dome.setColorAt(0.0, QColor("#3b485d")); grad_dome.setColorAt(0.5, QColor("#1c2534")); grad_dome.setColorAt(1.0, QColor("#0d121c"))
            else:
                grad_dome.setColorAt(0.0, QColor("#FFFFFF")); grad_dome.setColorAt(0.5, QColor("#F1F5F9")); grad_dome.setColorAt(1.0, QColor("#CBD5E1"))
            
            p.setBrush(QBrush(grad_dome))
            p.setPen(QPen(qcol(Theme.BORDER_H if not self.muted else Theme.RED, 190), 1.5))
            p.drawEllipse(rect_dome)

            p.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            p.setPen(QPen(qcol("#FFFFFF" if Theme.DARK else "#0F172A")))
            p.drawText(rect_dome, Qt.AlignmentFlag.AlignCenter, self._assistant_name)

        # ── 8. BOTTOM STATUS PILL ─────────────────────────────────────────────
        sy = cy + fw * 0.44
        state_str = "MUTED" if self.muted else (self.state if not self.speaking else "SPEAKING")
        st_col = Theme.RED if self.muted else (Theme.G_GREEN if self.state == "LISTENING" else (Theme.G_YELLOW if self.state in ("THINKING", "PROCESSING") else Theme.G_BLUE))

        chip_rect = QRectF(cx - 72, sy, 144, 26)
        p.setBrush(QBrush(qcol("#101622" if Theme.DARK else "#FFFFFF", 240)))
        p.setPen(QPen(qcol(st_col, 150), 1.4))
        p.drawRoundedRect(chip_rect, 13, 13)

        p.setBrush(QBrush(qcol(st_col)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(QPointF(cx - 48, sy + 13), 3.5, 3.5)

        p.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        p.setPen(QPen(qcol("#F1F5F9" if Theme.DARK else "#0F172A")))
        p.drawText(QRectF(cx - 38, sy, 95, 26), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, state_str)

# ── Semi-Circular Radial Speedometer Gauge ───────────────────────────────────
class MetricGauge(QWidget):
    def __init__(self, label: str, icon: str, color: str = Theme.G_BLUE, parent=None):
        super().__init__(parent)
        self._label = label
        self._icon  = icon
        self._color = color
        self._value = 0.0
        self._text  = "--"
        self.setFixedHeight(92)

    def set_value(self, pct: float, text: str):
        self._value = max(0.0, min(100.0, pct))
        self._text  = text
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()
        cx, cy = W / 2, H * 0.68
        r = 34.0

        arc_rect = QRectF(cx - r, cy - r, r * 2, r * 2)
        p.setBrush(Qt.BrushStyle.NoBrush)
        p.setPen(QPen(qcol(Theme.BAR_BG), 4.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        p.drawArc(arc_rect, 0 * 16, 180 * 16)

        span = int((self._value / 100.0) * 180)
        if span > 0:
            fill_col = Theme.G_RED if self._value > 88 else (Theme.G_YELLOW if self._value > 70 else self._color)
            p.setPen(QPen(qcol(fill_col, 50), 8.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawArc(arc_rect, 180 * 16, -span * 16)
            p.setPen(QPen(qcol(fill_col, 240), 4.0, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            p.drawArc(arc_rect, 180 * 16, -span * 16)

        p.setFont(QFont("Segoe UI Emoji", 10))
        p.setPen(QPen(qcol(self._color)))
        p.drawText(QRectF(cx - 16, cy - 28, 32, 16), Qt.AlignmentFlag.AlignCenter, self._icon)

        p.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        p.setPen(QPen(qcol(Theme.TEXT_MUTED)))
        p.drawText(QRectF(cx - 25, cy - 12, 50, 14), Qt.AlignmentFlag.AlignCenter, self._label)

        p.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        p.setPen(QPen(qcol(Theme.TEXT)))
        p.drawText(QRectF(cx - 35, cy + 8, 70, 16), Qt.AlignmentFlag.AlignCenter, self._text)


# ── High-Contrast Dynamic Activity Console ────────────────────────────────────
class LogWidget(QTextEdit):
    _sig = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setFont(QFont("Segoe UI", 8))
        self._refresh_style()
        self._sig.connect(self._append_line)

    def _refresh_style(self):
        border_style = f"border: 1px solid {Theme.BORDER_H};" if Theme.FX_MODE != "GOOGLE_GLOW" else f"border: 1.5px solid {Theme.G_BLUE};"
        self.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.PANEL};
                color: {Theme.TEXT};
                {border_style}
                border-radius: 10px;
                padding: 10px;
                line-height: 1.45;
            }}
            QScrollBar:vertical {{
                background: transparent; width: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.BORDER_H}; border-radius: 2px; min-height: 20px;
            }}
        """)

    def append_log(self, text: str):
        self._sig.emit(text)

    def _append_line(self, text: str):
        tl = text.lower()
        if "err" in tl or "alert" in tl or "fail" in tl:
            color = Theme.G_RED; badge = "[ALERT]"
        elif tl.startswith("you:"):
            color = Theme.G_BLUE; badge = "[USER]"
        elif "jarvis" in tl or "nexus" in tl:
            color = Theme.G_GREEN; badge = "[NEXUS]"
        elif "file" in tl:
            color = Theme.G_YELLOW; badge = "[FILE]"
        else:
            color = Theme.G_BLUE if not Theme.DARK else Theme.TEXT_MUTED; badge = "[SYS]"

        html = f"""<div style="margin-bottom:4px; font-family:'Segoe UI'; font-size:11px;">
            <span style="color:{color}; font-weight:bold;">● {badge}</span>
            <span style="color:{Theme.TEXT}; font-weight:500;"> {text}</span>
        </div>"""
        self.append(html)
        self.ensureCursorVisible()

# ── Elevated Glassmorphic File Drop Zone ───────────────────────────────────────
_EXT_TO_CAT = {
    **dict.fromkeys(["jpg","jpeg","png","gif","webp","bmp","svg"], "image"),
    **dict.fromkeys(["mp4","avi","mov","mkv","webm"],              "video"),
    **dict.fromkeys(["mp3","wav","ogg","m4a","flac"],              "audio"),
    **dict.fromkeys(["pdf"],                                       "pdf"),
    **dict.fromkeys(["doc","docx","txt","md"],                     "word"),
    **dict.fromkeys(["xls","xlsx","csv"],                          "excel"),
    **dict.fromkeys(["py","js","ts","html","css","java","cpp","go"],"code"),
}

def _fmt_size(size: int) -> str:
    if size < 1024: return f"{size} B"
    elif size < 1024**2: return f"{size/1024:.1f} KB"
    elif size < 1024**3: return f"{size/1024**2:.1f} MB"
    return f"{size/1024**3:.1f} GB"

class FileDropZone(QWidget):
    file_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(94)
        self._current_file: str | None = None
        self._hovering = False
        self._drag_over = False

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.mimeData().hasUrls():
            e.acceptProposedAction(); self._drag_over = True; self.update()

    def dragLeaveEvent(self, e):
        self._drag_over = False; self.update()

    def dropEvent(self, e: QDropEvent):
        self._drag_over = False
        urls = e.mimeData().urls()
        if urls:
            path = urls[0].toLocalFile()
            if Path(path).is_file(): self._set_file(path)
        self.update()

    def mousePressEvent(self, e):
        if self._current_file and e.pos().x() > self.width() - 32:
            self.clear_file()
        elif e.button() == Qt.MouseButton.LeftButton:
            self._browse()

    def enterEvent(self, e): self._hovering = True; self.update()
    def leaveEvent(self, e): self._hovering = False; self.update()
    def current_file(self) -> str | None: return self._current_file
    def clear_file(self): self._current_file = None; self.update()

    def _browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Upload File to Assistant", str(Path.home()), "All Files (*.*)")
        if path: self._set_file(path)

    def _set_file(self, path: str):
        self._current_file = path
        self.update()
        self.file_selected.emit(path)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        W, H = self.width(), self.height()
        rect = QRectF(2, 2, W - 4, H - 4)

        # Background Frosted Card
        bg_col = Theme.PANEL_ALT if not self._drag_over else Theme.BORDER_H
        p.setBrush(QBrush(qcol(bg_col)))
        p.setPen(QPen(qcol(Theme.G_BLUE if self._hovering else Theme.BORDER), 1.2, Qt.PenStyle.DashLine if not self._current_file else Qt.PenStyle.SolidLine))
        p.drawRoundedRect(rect, 8, 8)

        if self._current_file:
            path = Path(self._current_file)
            p.setFont(QFont("Segoe UI Emoji", 16))
            p.drawText(QRectF(14, 0, 30, H), Qt.AlignmentFlag.AlignVCenter, "📄")

            p.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
            p.setPen(QPen(qcol(Theme.TEXT)))
            name = path.name if len(path.name) <= 24 else path.name[:21] + "..."
            p.drawText(QRectF(50, 22, W - 90, 20), Qt.AlignmentFlag.AlignLeft, name)

            p.setFont(QFont("Segoe UI", 7))
            p.setPen(QPen(qcol(Theme.TEXT_MUTED)))
            p.drawText(QRectF(50, 44, W - 90, 16), Qt.AlignmentFlag.AlignLeft, _fmt_size(path.stat().st_size))

            p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            p.setPen(QPen(qcol(Theme.G_RED)))
            p.drawText(QRectF(W - 30, 0, 20, H), Qt.AlignmentFlag.AlignCenter, "✕")
        else:
            # Upload Badge Icon
            icon_rect = QRectF(W / 2 - 16, 12, 32, 24)
            p.setBrush(QBrush(qcol(Theme.PANEL)))
            p.setPen(QPen(qcol(Theme.BORDER), 1))
            p.drawRoundedRect(icon_rect, 4, 4)

            p.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            p.setPen(QPen(qcol(Theme.G_BLUE)))
            p.drawText(icon_rect, Qt.AlignmentFlag.AlignCenter, "⬆")

            p.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            p.setPen(QPen(qcol(Theme.TEXT if self._hovering else Theme.TEXT_MUTED)))
            p.drawText(QRectF(0, 42, W, 18), Qt.AlignmentFlag.AlignCenter, "Drop file here to browse")

            p.setFont(QFont("Segoe UI", 7))
            p.setPen(QPen(qcol(Theme.TEXT_DIM)))
            p.drawText(QRectF(0, 60, W, 16), Qt.AlignmentFlag.AlignCenter, "Supports code, images, audio, video & documents")

# ── Overlays: Camera Snapshot, Clipboard Panel, Setup, Remote ─────────────────
class _CameraPreview(QWidget):
    _W, _H = 250, 190

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(self._W)
        self.setStyleSheet(f"_CameraPreview {{ background: {Theme.PANEL}; border: 1px solid {Theme.BORDER_H}; border-radius: 10px; }}")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(8, 6, 8, 8); lay.setSpacing(4)
        hdr = QHBoxLayout()
        t = QLabel("CAMERA CAPTURE"); t.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold)); t.setStyleSheet(f"color: {Theme.G_BLUE};")
        hdr.addWidget(t); hdr.addStretch()
        cb = QPushButton("✕"); cb.setFixedSize(16, 16); cb.setStyleSheet(f"color: {Theme.TEXT_MUTED}; background: transparent; border: none;"); cb.clicked.connect(self.hide)
        hdr.addWidget(cb); lay.addLayout(hdr)

        self._img_lbl = QLabel(); self._img_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter); lay.addWidget(self._img_lbl)
        self._tmr = QTimer(self); self._tmr.setSingleShot(True); self._tmr.timeout.connect(self.hide); self.hide()

    def show_frame(self, img_bytes: bytes) -> None:
        px = QPixmap(); px.loadFromData(img_bytes)
        if not px.isNull():
            scaled = px.scaled(self._W - 16, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self._img_lbl.setPixmap(scaled); self.adjustSize()
        self.show(); self.raise_(); self._tmr.start(6000)

class ClipboardPanel(QWidget):
    action_requested = pyqtSignal(str)
    _W, _H = 340, 110

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(self._W)
        self._clip_text = ""
        self.setStyleSheet(f"ClipboardPanel {{ background: {Theme.PANEL}; border: 1px solid {Theme.BORDER_H}; border-radius: 8px; }}")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8); lay.setSpacing(6)
        hdr = QHBoxLayout()
        t = QLabel("📋  CLIPBOARD DETECTED"); t.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold)); t.setStyleSheet(f"color: {Theme.G_YELLOW};")
        hdr.addWidget(t); hdr.addStretch()
        cb = QPushButton("✕"); cb.setFixedSize(16, 16); cb.setStyleSheet(f"color: {Theme.TEXT_MUTED}; background: transparent; border: none;"); cb.clicked.connect(self.hide)
        hdr.addWidget(cb); lay.addLayout(hdr)

        self._preview = QLabel(); self._preview.setFont(QFont("Segoe UI", 8)); self._preview.setStyleSheet(f"color: {Theme.TEXT}; background: {Theme.PANEL_ALT}; border-radius: 4px; padding: 4px;")
        lay.addWidget(self._preview)

        btn_row = QHBoxLayout(); btn_row.setSpacing(4)
        for label, cmd in [("Translate", "Translate this text to English: {text}"), ("Summarize", "Summarize this: {text}"), ("Fix Grammar", "Fix grammar and spelling: {text}")]:
            b = QPushButton(label); b.setFixedHeight(22); b.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold)); b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.G_BLUE}; border-radius: 3px; border: 1px solid {Theme.BORDER};")
            b.clicked.connect(lambda _, c=cmd: self._trigger(c))
            btn_row.addWidget(b)
        lay.addLayout(btn_row)

        self._tmr = QTimer(self); self._tmr.setSingleShot(True); self._tmr.timeout.connect(self.hide); self.hide()

    def _trigger(self, cmd_fmt: str):
        if self._clip_text: self.action_requested.emit(cmd_fmt.format(text=self._clip_text[:800]))
        self.hide()

    def show_clipboard(self, text: str):
        self._clip_text = text
        prev = text[:48].replace("\n", " ") + ("…" if len(text) > 48 else "")
        self._preview.setText(f'"{prev}"'); self.show(); self.raise_(); self._tmr.start(8000)

class SetupOverlay(QWidget):
    done = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"SetupOverlay {{ background: {Theme.PANEL}; border: 1px solid {Theme.BORDER_H}; border-radius: 12px; }}")
        detected = {"darwin": "mac", "windows": "windows"}.get(_OS.lower(), "linux")
        self._sel_os = detected

        lay = QVBoxLayout(self)
        lay.setContentsMargins(26, 20, 26, 20); lay.setSpacing(8)
        t = QLabel("System Initialization"); t.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold)); t.setStyleSheet(f"color: {Theme.TEXT};"); lay.addWidget(t)
        st = QLabel("Enter Gemini API key to activate voice, vision, and core tools."); st.setFont(QFont("Segoe UI", 8)); st.setStyleSheet(f"color: {Theme.TEXT_MUTED};"); lay.addWidget(st)

        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("Enter Gemini API Key (AIza...)")
        self._key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._key_input.setFixedHeight(34)
        self._key_input.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.TEXT}; border: 1px solid {Theme.BORDER}; border-radius: 6px; padding: 4px 10px;")
        lay.addWidget(self._key_input)

        lay.addSpacing(2)
        os_lbl = QLabel(f"Target Environment (Auto-detected: {detected.upper()})")
        os_lbl.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold)); os_lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED};"); lay.addWidget(os_lbl)

        os_row = QHBoxLayout(); os_row.setSpacing(6)
        self._os_btns: dict[str, QPushButton] = {}
        for k, label in [("windows", "🪟 Windows"), ("mac", "🍎 macOS"), ("linux", "🐧 Linux")]:
            b = QPushButton(label); b.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold)); b.setFixedHeight(28); b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _, key=k: self._select_os(key))
            os_row.addWidget(b); self._os_btns[k] = b
        lay.addLayout(os_row)
        self._select_os(detected)

        lay.addSpacing(4)
        btn = QPushButton("Confirm & Launch Core")
        btn.setFixedHeight(36); btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold)); btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"background: {Theme.G_BLUE}; color: white; border: none; border-radius: 6px;")
        btn.clicked.connect(self._submit)
        lay.addWidget(btn)

    def _select_os(self, key: str):
        self._sel_os = key
        for k, btn in self._os_btns.items():
            if k == key:
                btn.setStyleSheet(f"background: {Theme.G_BLUE}; color: white; border: none; border-radius: 4px;")
            else:
                btn.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.TEXT_MUTED}; border: 1px solid {Theme.BORDER}; border-radius: 4px;")

    def _submit(self):
        k = self._key_input.text().strip()
        if k: self.done.emit(k, self._sel_os)

class RemoteKeyOverlay(QWidget):
    closed = pyqtSignal()
    _OW, _OH = 380, 470

    def __init__(self, url: str, key: str, auto_login_url: str = "", manual_url: str = "", expiry_secs: int = 600, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"RemoteKeyOverlay {{ background: {Theme.PANEL}; border: 1px solid {Theme.BORDER_H}; border-radius: 14px; }}")
        self._expiry = time.time() + expiry_secs
        self._on_new_key = None
        self._manual_url = manual_url or url
        self._auto_login_url = auto_login_url

        lay = QVBoxLayout(self)
        lay.setContentsMargins(20, 16, 20, 16); lay.setSpacing(6)
        t = QLabel("📱  Mobile Remote Access")
        t.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {Theme.TEXT};")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(t)

        self._qr_lbl = QLabel()
        self._qr_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._qr_lbl.setFixedSize(160, 160)
        self._qr_lbl.setStyleSheet("background: white; border-radius: 8px; padding: 4px;")
        self._load_qr(auto_login_url or url)
        qr_box = QHBoxLayout(); qr_box.addStretch(); qr_box.addWidget(self._qr_lbl); qr_box.addStretch(); lay.addLayout(qr_box)

        self._key_lbl = QLabel(key)
        self._key_lbl.setFont(QFont("Consolas", 20, QFont.Weight.Bold))
        self._key_lbl.setStyleSheet(f"color: {Theme.G_YELLOW}; background: {Theme.PANEL_ALT}; border: 1px solid {Theme.BORDER}; border-radius: 6px; padding: 6px; letter-spacing: 6px;")
        self._key_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._key_lbl)

        self._timer_lbl = QLabel()
        self._timer_lbl.setFont(QFont("Segoe UI", 8))
        self._timer_lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED};")
        self._timer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(self._timer_lbl)

        btn_row = QHBoxLayout()
        new_btn = QPushButton("New Key")
        new_btn.setFixedHeight(30)
        new_btn.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.G_BLUE}; border: 1px solid {Theme.BORDER}; border-radius: 4px;")
        new_btn.clicked.connect(self._refresh_key)
        btn_row.addWidget(new_btn)

        cb = QPushButton("Dismiss")
        cb.setFixedHeight(30)
        cb.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.TEXT_MUTED}; border: 1px solid {Theme.BORDER}; border-radius: 4px;")
        cb.clicked.connect(self._do_close)
        btn_row.addWidget(cb)
        lay.addLayout(btn_row)

        self._ctimer = QTimer(self)
        self._ctimer.timeout.connect(self._tick)
        self._ctimer.start(1000)
        self._tick()

    def set_new_key_callback(self, fn) -> None:
        self._on_new_key = fn

    def _tick(self):
        rem = max(0, int(self._expiry - time.time()))
        m, s = divmod(rem, 60)
        self._timer_lbl.setText(f"Passkey expires in {m:02d}:{s:02d}")
        if rem == 0:
            self._do_close()

    def _refresh_key(self):
        if self._on_new_key:
            res = self._on_new_key()
            if res:
                url, key = res[0], res[1]
                auto = res[2] if len(res) >= 3 else ""
                self._key_lbl.setText(key)
                self._load_qr(auto or url)
                self._expiry = time.time() + 600
                self._tick()

    def _load_qr(self, url: str):
        try:
            import qrcode, io
            qr = qrcode.QRCode(box_size=4, border=1); qr.add_data(url); qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white"); buf = io.BytesIO(); img.save(buf, format="PNG")
            px = QPixmap(); px.loadFromData(buf.getvalue()); self._qr_lbl.setPixmap(px.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        except Exception: self._qr_lbl.setText(url[:20])

    def mark_connected(self):
        self._ctimer.stop()
        self._key_lbl.setText("CONNECTED")
        self._key_lbl.setStyleSheet(f"color: {Theme.G_GREEN}; background: {Theme.PANEL_ALT}; border-radius: 6px; letter-spacing: 2px;")
        self._timer_lbl.setText("Device active and paired")

    def _do_close(self):
        self._ctimer.stop()
        self.hide()
        self.closed.emit()

class CustomizeOverlay(QWidget):
    saved = pyqtSignal(str, str, str, str)  # name, user_name, voice_name, ui_color
    _OW, _OH = 380, 310

    def __init__(self, assistant_name="NEXUS", user_name="", current_voice="Fenrir", parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"CustomizeOverlay {{ background: {Theme.PANEL}; border: 1px solid {Theme.BORDER_H}; border-radius: 12px; }}")

        lay = QVBoxLayout(self)
        lay.setContentsMargins(22, 16, 22, 16)
        lay.setSpacing(6)

        t = QLabel("⚙  Assistant Customization")
        t.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        t.setStyleSheet(f"color: {Theme.TEXT};")
        lay.addWidget(t)

        self._name_in = QLineEdit(assistant_name)
        self._name_in.setPlaceholderText("Assistant Name (e.g. NEXUS)")
        self._name_in.setFixedHeight(30)
        self._name_in.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.TEXT}; border: 1px solid {Theme.BORDER}; border-radius: 4px; padding: 4px 8px;")
        lay.addWidget(self._name_in)

        self._user_in = QLineEdit(user_name)
        self._user_in.setPlaceholderText("Your Name (e.g. Tony)")
        self._user_in.setFixedHeight(30)
        self._user_in.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.TEXT}; border: 1px solid {Theme.BORDER}; border-radius: 4px; padding: 4px 8px;")
        lay.addWidget(self._user_in)

        # ── Voice Model Selector ──────────────────────────────────────────────
        v_lbl = QLabel("AI Voice Model:")
        v_lbl.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        v_lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED};")
        lay.addWidget(v_lbl)

        from PyQt6.QtWidgets import QComboBox
        self._voice_combo = QComboBox()
        self._voice_combo.setFixedHeight(30)
        self._voice_combo.setFont(QFont("Segoe UI", 8))
        self._voice_combo.setStyleSheet(f"""
            QComboBox {{
                background: {Theme.PANEL_ALT}; color: {Theme.TEXT};
                border: 1px solid {Theme.BORDER}; border-radius: 4px; padding: 4px 8px;
            }}
            QComboBox QAbstractItemView {{
                background: {Theme.PANEL}; color: {Theme.TEXT};
                selection-background-color: {Theme.G_BLUE}; border-radius: 4px;
            }}
        """)
        self._voices = [
            ("Fenrir",  "Fenrir — Deep Baritone (Lowest Pitch)"),
            ("Charon",  "Charon — Calm & Authoritative"),
            ("Orpheus", "Orpheus — Confident & Deep"),
            ("Puck",    "Puck — Energetic & Friendly"),
            ("Aoede",   "Aoede — Soft & Melodic (Female)"),
            ("Kore",    "Kore — Composed & Natural (Female)"),
            ("Zephyr",  "Zephyr — Warm & Gentle"),
            ("Leda",    "Leda — Bright & Youthful (Female)"),
        ]
        cur_idx = 0
        for idx, (v_id, v_label) in enumerate(self._voices):
            self._voice_combo.addItem(v_label, v_id)
            if v_id.lower() == (current_voice or "fenrir").lower():
                cur_idx = idx

        self._voice_combo.setCurrentIndex(cur_idx)
        lay.addWidget(self._voice_combo)

        lay.addSpacing(4)
        btn = QPushButton("Save & Apply")
        btn.setFixedHeight(32)
        btn.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet(f"background: {Theme.G_BLUE}; color: white; border: none; border-radius: 4px;")
        btn.clicked.connect(self._save)
        lay.addWidget(btn)

    def _save(self):
        sel_voice = self._voice_combo.currentData() or "Fenrir"
        self.saved.emit(
            self._name_in.text().strip() or "NEXUS",
            self._user_in.text().strip(),
            sel_voice,
            Theme.G_BLUE
        )
        self.hide()

class PluginManagerOverlay(QWidget):
    _OW = 360

    def __init__(self, plugins: list[dict], parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet(f"PluginManagerOverlay {{ background: {Theme.PANEL}; border: 1px solid {Theme.BORDER_H}; border-radius: 12px; }}")
        self.setFixedWidth(self._OW)

        lay = QVBoxLayout(self); lay.setContentsMargins(18, 14, 18, 14); lay.setSpacing(6)
        t = QLabel("🧩  Plugin Modules"); t.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold)); t.setStyleSheet(f"color: {Theme.TEXT};"); lay.addWidget(t)

        for p in plugins:
            row = QHBoxLayout()
            lbl = QLabel(p["name"]); lbl.setFont(QFont("Segoe UI", 8)); lbl.setStyleSheet(f"color: {Theme.TEXT if p['valid'] else Theme.TEXT_MUTED};"); row.addWidget(lbl, stretch=1)
            btn = QPushButton("ON" if p.get("enabled", True) else "OFF"); btn.setFixedSize(50, 22); btn.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
            btn.setStyleSheet(f"background: {'#1b4d2e' if p.get('enabled', True) else Theme.PANEL_ALT}; color: {'#34A853' if p.get('enabled', True) else Theme.TEXT_MUTED}; border-radius: 3px;")
            btn.clicked.connect(lambda _, n=p["name"], b=btn: self._toggle(n, b))
            row.addWidget(btn); lay.addLayout(row)

        cb = QPushButton("Close"); cb.setFixedHeight(28); cb.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.TEXT_MUTED}; border: 1px solid {Theme.BORDER}; border-radius: 4px;"); cb.clicked.connect(self.hide); lay.addWidget(cb)
        self.adjustSize()

    def _toggle(self, name: str, btn: QPushButton):
        try:
            from memory.config_manager import get_plugin_enabled, save_plugin_enabled
            new_val = not get_plugin_enabled(name); save_plugin_enabled(name, new_val)
            btn.setText("ON" if new_val else "OFF")
            btn.setStyleSheet(f"background: {'#1b4d2e' if new_val else Theme.PANEL_ALT}; color: {'#34A853' if new_val else Theme.TEXT_MUTED}; border-radius: 3px;")
        except Exception: pass
        
# ── Real High-Res Satellite, 3D Streets & Super-Zoom (Level 22) ───────────────
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    _WEBVIEW_AVAILABLE = True
except ImportError:
    _WEBVIEW_AVAILABLE = False

class SpatialMapCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(360, 360)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._devices = {}
        self._selected_id = None
        self._map_initialized = False

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if _WEBVIEW_AVAILABLE:
            self._web = QWebEngineView()
            self._web.setStyleSheet("background: transparent;")
            layout.addWidget(self._web)
        else:
            self._fallback_lbl = QLabel()
            self._fallback_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._fallback_lbl.setStyleSheet(f"background: {Theme.BG}; color: {Theme.TEXT}; padding: 20px;")
            layout.addWidget(self._fallback_lbl)

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._sync_telemetry)
        self._timer.start(2000)

        self._load_map_html()

    def set_fleet(self, devices: dict, selected_id: str = None):
        self._devices = devices or {}
        if self._devices:
            self._selected_id = selected_id or list(self._devices.keys())[0]
        self._sync_telemetry()

    def _load_map_html(self):
        from actions.device_tracker import _load_devices
        self._devices = _load_devices()

        sel_dev = self._devices.get(self._selected_id or "Mobile-Phone", {})
        if not sel_dev and self._devices:
            sel_dev = list(self._devices.values())[0]

        lat = sel_dev.get("lat", 31.51698)
        lon = sel_dev.get("lon", 74.36111)
        name = sel_dev.get("name", "Android Smartphone")
        addr = sel_dev.get("address", "Lahore, Pakistan")
        bat = sel_dev.get("battery", 100)
        speed = sel_dev.get("speed_kmh", 0.0)

        map_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                body {{ margin:0; padding:0; background:#07090e; font-family:'Segoe UI',sans-serif; overflow:hidden; }}
                #map {{ width:100vw; height:100vh; background:#07090e; }}
                .telemetry-card {{
                    position:absolute; top:14px; left:14px; z-index:1000;
                    background:rgba(15,23,42,0.94); border:1px solid rgba(66,133,244,0.6);
                    border-radius:10px; padding:12px 16px; color:#F1F5F9; font-size:12px;
                    box-shadow:0 6px 24px rgba(0,0,0,0.7); backdrop-filter:blur(10px);
                    max-width: 320px;
                }}
                .layer-btn-wrap {{
                    position:absolute; top:14px; right:14px; z-index:1000;
                    display:flex; gap:6px;
                }}
                .layer-btn {{
                    background:rgba(15,23,42,0.92); color:#F1F5F9; border:1px solid rgba(255,255,255,0.15);
                    border-radius:6px; padding:6px 12px; font-size:11px; font-weight:bold; cursor:pointer;
                    transition:all 0.2s;
                }}
                .layer-btn:hover {{ background:rgba(66,133,244,0.3); border-color:#4285F4; }}
                .layer-btn.active {{ background:#4285F4; color:#ffffff; border-color:#4285F4; }}
                .pin-pulse {{
                    width:20px; height:20px; background:#00E676; border:3px solid #ffffff;
                    border-radius:50%; box-shadow:0 0 18px #00E676; animation:pulse 1.8s infinite;
                }}
                @keyframes pulse {{ 0% {{ box-shadow:0 0 0 0 rgba(0,230,118,0.7); }} 70% {{ box-shadow:0 0 0 24px rgba(0,230,118,0); }} 100% {{ box-shadow:0 0 0 0 rgba(0,230,118,0); }} }}
            </style>
        </head>
        <body>
            <div class="telemetry-card" id="card">
                <div style="font-weight:bold; color:#4285F4; font-size:13px; margin-bottom:4px;" id="t_name">📍 {name}</div>
                <div style="color:#E2E8F0; font-size:11px; margin-bottom:3px; line-height:1.4;" id="t_addr"><b>Location:</b> {addr}</div>
                <div style="color:#94A3B8; font-size:11px;" id="t_gps"><b>GPS:</b> {lat:.5f}° N, {lon:.5f}° E • <b id="t_speed">{speed} km/h</b></div>
                <div style="color:#00E676; font-size:11px; font-weight:bold; margin-top:4px;" id="t_bat">● ONLINE • Battery: {bat}%</div>
            </div>

            <div class="layer-btn-wrap">
                <button class="layer-btn active" id="btn_sat" onclick="switchLayer('sat')">🛰️ Satellite</button>
                <button class="layer-btn" id="btn_dark" onclick="switchLayer('dark')">🌑 Dark Streets</button>
            </div>

            <div id="map"></div>

            <script>
                // 1. Super-Zoom Satellite Layer (Oversampled to Zoom Level 22)
                const satLayer = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
                    maxNativeZoom: 19,
                    maxZoom: 22,
                    attribution: 'ESRI Satellite'
                }});

                // 2. OpenStreetMap Streets Layer (Oversampled to Level 22)
                const darkLayer = L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                    maxNativeZoom: 19,
                    maxZoom: 22,
                    attribution: 'OSM Streets'
                }});

                // Enable Full Interactive Mouse Wheel & Button Zoom Controls
                const map = L.map('map', {{
                    zoomControl: true,
                    scrollWheelZoom: true,
                    doubleClickZoom: true,
                    layers: [satLayer],
                    maxZoom: 22
                }}).setView([{lat}, {lon}], 18);

                // Pulse Pin Marker
                const icon = L.divIcon({{ className: 'pin-pulse', iconSize: [20, 20], iconAnchor: [10, 10] }});
                const marker = L.marker([{lat}, {lon}], {{ icon: icon }}).addTo(map);

                function switchLayer(type) {{
                    if (type === 'sat') {{
                        map.removeLayer(darkLayer);
                        map.addLayer(satLayer);
                        document.getElementById('btn_sat').className = 'layer-btn active';
                        document.getElementById('btn_dark').className = 'layer-btn';
                    }} else {{
                        map.removeLayer(satLayer);
                        map.addLayer(darkLayer);
                        document.getElementById('btn_dark').className = 'layer-btn active';
                        document.getElementById('btn_sat').className = 'layer-btn';
                    }}
                }}

                window.updatePhoneLive = function(newLat, newLon, newName, newAddr, newBat, newSpeed) {{
                    const newPos = [newLat, newLon];
                    marker.setLatLng(newPos);

                    document.getElementById('t_name').textContent = "📍 " + newName;
                    document.getElementById('t_addr').innerHTML = "<b>Location:</b> " + newAddr;
                    document.getElementById('t_gps').innerHTML = "<b>GPS:</b> " + newLat.toFixed(5) + "° N, " + newLon.toFixed(5) + "° E • <b>" + newSpeed + " km/h</b>";
                    document.getElementById('t_bat').innerHTML = "● ONLINE • Battery: " + newBat + "%";
                }};
            </script>
        </body>
        </html>
        """
        if _WEBVIEW_AVAILABLE:
            self._web.setHtml(map_html)
            self._map_initialized = True

    def _sync_telemetry(self):
        from actions.device_tracker import _load_devices
        self._devices = _load_devices()

        if not self._devices or not _WEBVIEW_AVAILABLE or not self._map_initialized:
            return

        sel_dev = self._devices.get(self._selected_id or "Mobile-Phone", {})
        if not sel_dev:
            sel_dev = list(self._devices.values())[0]

        lat = float(sel_dev.get("lat", 31.51698))
        lon = float(sel_dev.get("lon", 74.36111))
        name = str(sel_dev.get("name", "Android Smartphone")).replace("'", "")
        addr = str(sel_dev.get("address", "Lahore, Pakistan")).replace("'", "")
        bat = int(sel_dev.get("battery", 100))
        speed = float(sel_dev.get("speed_kmh", 0.0))

        js = f"if (window.updatePhoneLive) {{ window.updatePhoneLive({lat}, {lon}, '{name}', '{addr}', {bat}, {speed}); }}"
        self._web.page().runJavaScript(js)
        
# ── Dynamic Smart Non-Repeating Splash Screen Selector ────────────────────────
def get_random_splash_class():
    import sys
    # Lock BASE_DIR into sys.path so imports never fail regardless of launch path
    if str(BASE_DIR) not in sys.path:
        sys.path.insert(0, str(BASE_DIR))

    splash_map = {}

    # Option 1: Cyberdeck Singularity
    try:
        import nexus_splash
        splash_map[1] = ("Option 1 [Cyberdeck Singularity]", nexus_splash.NexusSplashScreen)
    except Exception as e:
        print(f"[SplashLoader] ⚠️ Option 1 unavailable: {e}")

    # Option 2: Enterprise Defense Command
    try:
        import nexus_splash_option2
        splash_map[2] = ("Option 2 [Enterprise Defense Command]", nexus_splash_option2.NexusSplashScreen)
    except Exception as e:
        print(f"[SplashLoader] ⚠️ Option 2 unavailable: {e}")

    # Option 3: Synaptic Particle Matrix
    try:
        import nexus_splash_option3
        splash_map[3] = ("Option 3 [Synaptic Particle Matrix]", nexus_splash_option3.NexusSplashScreen)
    except Exception as e:
        print(f"[SplashLoader] ⚠️ Option 3 unavailable: {e}")

    available_ids = list(splash_map.keys())
    if not available_ids:
        print("[SplashLoader] ❌ No splash modules available.")
        return None

    # ── Read last played splash from cache to guarantee no consecutive repeats ──
    state_file = CONFIG_DIR / "last_splash.json"
    last_id = 0
    try:
        if state_file.exists():
            last_id = json.loads(state_file.read_text(encoding="utf-8")).get("last_id", 0)
    except Exception:
        pass

    # Pick from options that were NOT played on the previous startup
    pool = [i for i in available_ids if i != last_id]
    chosen_id = random.choice(pool) if pool else available_ids[0]

    # Save state for the next run
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        state_file.write_text(json.dumps({"last_id": chosen_id}), encoding="utf-8")
    except Exception:
        pass

    name, chosen_class = splash_map[chosen_id]
    print(f"[NEXUS Core] 🎬 Loading Startup Cinematic ({chosen_id}/3): {name}")
    return chosen_class
    
# ── 3D Avatar Host Widget (Watchdog Bridge) ───────────────────────────────────
from PyQt6.QtWebEngineCore import QWebEnginePage, QWebEngineSettings

class AvatarWebPage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.featurePermissionRequested.connect(self._grant_permission)

    def _grant_permission(self, url, feature):
        if feature in (
            QWebEnginePage.Feature.MediaVideoCapture,
            QWebEnginePage.Feature.MediaAudioCapture,
        ):
            self.setFeaturePermission(
                url, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser
            )

class Avatar3DView(QWidget):
    def __init__(self, assistant_name: str = "NEXUS", parent=None):
        super().__init__(parent)
        self.setMinimumSize(360, 360)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.muted = False
        self.speaking = False
        self._tracking_enabled = False
        self._current_view = "bust"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._web = QWebEngineView()
        self._page = AvatarWebPage(self._web)
        self._web.setPage(self._page)
        self._web.setStyleSheet("background: #020617; border-radius: 12px;")
        
        settings = self._web.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.Accelerated2dCanvasEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, True)

        html_path = BASE_DIR / "index.html"
        self._web.setUrl(QUrl.fromLocalFile(str(html_path.resolve())))
        layout.addWidget(self._web)

    def run_js(self, js: str):
        if self._web and self._web.page():
            self._web.page().runJavaScript(js)

    def pulse_speech(self):
        """Sends an active audio heartbeat pulse to the 3D watchdog"""
        self.run_js("if(window.NexusCore && window.NexusCore.pulseSpeech) window.NexusCore.pulseSpeech();")

    def set_speaking(self, is_speaking: bool):
        self.speaking = is_speaking
        self.run_js(f"if(window.NexusCore && window.NexusCore.setLiveSpeaking) window.NexusCore.setLiveSpeaking({str(is_speaking).lower()});")

    def toggle_tracking(self) -> bool:
        self._tracking_enabled = not self._tracking_enabled
        self.run_js(f"window.NexusCore.toggleTracking({str(self._tracking_enabled).lower()});")
        return self._tracking_enabled

    def toggle_view(self) -> str:
        self._current_view = "full" if self._current_view == "bust" else "bust"
        self.run_js(f"window.NexusCore.setCameraMode('{self._current_view}');")
        return self._current_view

    def pause_camera(self):
        self.run_js("window.NexusCore.pauseCamera();")

    def resume_camera(self):
        self.run_js("window.NexusCore.resumeCamera();")

# ── Main Application Window ───────────────────────────────────────────────────
class MainWindow(QMainWindow):
    _log_sig        = pyqtSignal(str)
    _state_sig      = pyqtSignal(str)
    _content_sig    = pyqtSignal(str, str)
    _reconfig_sig   = pyqtSignal()
    _camera_sig     = pyqtSignal(bytes)
    _cam_stream_sig = pyqtSignal(bool)
    _cam_frame_sig  = pyqtSignal(bytes)
    _clipboard_sig  = pyqtSignal(str)

    def __init__(self, face_path: str):
        super().__init__()
        self._face_path = face_path
        _cfg = _read_full_config()
        self._assistant_name = (_cfg.get("assistant_name") or "NEXUS").strip()

        self.setWindowTitle(f"{self._assistant_name} — Multimodal OS Core")
        self.setMinimumSize(_MIN_W, _MIN_H); self.resize(_DEFAULT_W, _DEFAULT_H)

        screen = QApplication.primaryScreen().availableGeometry()
        self.move((screen.width() - _DEFAULT_W) // 2, (screen.height() - _DEFAULT_H) // 2)

        self.on_text_command = self.on_remote_clicked = self.on_interrupt = self.get_plugins = None
        self._muted = False
        self._cam_stop = threading.Event()
        self._remote_overlay = self._customize_overlay = self._overlay = None

        self._central = QWidget()
        self.setCentralWidget(self._central)
        self._apply_global_style()

        root = QVBoxLayout(self._central); root.setContentsMargins(0, 0, 0, 0); root.setSpacing(0)
        root.addWidget(self._build_header())

        body = QHBoxLayout(); body.setContentsMargins(12, 10, 12, 10); body.setSpacing(12)
        self._left_panel_w = self._build_left_panel()
        body.addWidget(self._left_panel_w, stretch=0)

        # ── CENTER COLUMN: 3D Avatar + Controls + Spatial Map ───────────────
        self.hud = Avatar3DView(self._assistant_name)
        self.spatial_map = SpatialMapCanvas()
        self._content_panel = self._build_content_panel()

        # Build Avatar Quick Control Bar (AI Tracking, Eye Tracking, View Toggle)
        self._avatar_ctl_bar = self._build_avatar_controls()

        # Center Container (Avatar on top, Quick Action Buttons below)
        self._avatar_container = QWidget()
        _av_lay = QVBoxLayout(self._avatar_container)
        _av_lay.setContentsMargins(0, 0, 0, 0)
        _av_lay.setSpacing(6)
        _av_lay.addWidget(self.hud, stretch=1)
        _av_lay.addWidget(self._avatar_ctl_bar, stretch=0)

        # Camera Stack
        self._cam_container = QWidget()
        self._cam_container.setStyleSheet("background: #000000; border-radius: 12px;")
        _cv = QVBoxLayout(self._cam_container)
        _cv.setContentsMargins(0, 0, 0, 0)
        self._cam_live_lbl = QLabel()
        self._cam_live_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        _cv.addWidget(self._cam_live_lbl)

        self._hud_stack = QStackedWidget()
        self._hud_stack.addWidget(self._avatar_container)  # Index 0: 3D Avatar
        self._hud_stack.addWidget(self._cam_container)     # Index 1: Camera Feed
        self._hud_stack.addWidget(self.spatial_map)        # Index 2: 3D Spatial Map

        # Vertical splitter for center area
        self._center_split = QSplitter(Qt.Orientation.Vertical)
        self._center_split.addWidget(self._hud_stack)
        self._center_split.addWidget(self._content_panel)
        self._center_split.setStretchFactor(0, 4)
        self._center_split.setStretchFactor(1, 1)
        self._center_split.setCollapsible(0, False)
        body.addWidget(self._center_split, stretch=5)

        # Right Panel (creates self._log)
        self._right_panel_w = self._build_right_panel()
        body.addWidget(self._right_panel_w, stretch=0)

        root.addLayout(body, stretch=1)
        root.addWidget(self._build_footer())

        # Overlays & Signals
        self._cam_preview = _CameraPreview(self._central)
        self._clipboard_panel = ClipboardPanel(self._central)
        self._clipboard_panel.action_requested.connect(self._on_clipboard_action)
        QApplication.clipboard().dataChanged.connect(self._on_clipboard_changed)

        self._log_sig.connect(self._log.append_log)
        self._state_sig.connect(self._apply_state)
        self._content_sig.connect(self._show_content)
        self._reconfig_sig.connect(self._show_setup)
        self._camera_sig.connect(self._show_camera_frame)
        self._cam_stream_sig.connect(self._on_cam_stream)
        self._cam_frame_sig.connect(self._on_cam_frame)
        self._clipboard_sig.connect(self._clipboard_panel.show_clipboard)

        self._clock_tmr = QTimer(self); self._clock_tmr.timeout.connect(self._tick_clock); self._clock_tmr.start(1000); self._tick_clock()
        self._metric_tmr = QTimer(self)
        self._metric_tmr.timeout.connect(self._update_metrics)
        self._metric_tmr.start(1500)
        self._update_metrics()

        QShortcut(QKeySequence("F4"), self).activated.connect(self._toggle_mute)
        QShortcut(QKeySequence("F11"), self).activated.connect(self._toggle_fullscreen)
        QShortcut(QKeySequence("Escape"), self).activated.connect(self._do_interrupt)

        self._ready = self._check_config()
        if not self._ready: self._show_setup()

    def _apply_global_style(self):
        self._central.setStyleSheet(f"""
            QWidget {{
                background-color: {Theme.BG};
                color: {Theme.TEXT};
                font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            }}
        """)
        
    def show_spatial_map(self, devices: dict = None, selected_id: str = None):
        if devices:
            self.spatial_map.set_fleet(devices, selected_id)
        self._hud_stack.setCurrentIndex(2)
        self._log.append_log(f"SYS: Spatial Blueprint Map active. Tracking {len(devices or {})} fleet assets.")

    def show_reactor_core(self):
        self._hud_stack.setCurrentIndex(0)
        
    def _build_avatar_controls(self) -> QWidget:
        """The 3 control buttons: AI Tracking, Eye Tracking, and View Mode"""
        bar = QWidget()
        bar.setFixedHeight(36)
        bar.setStyleSheet(f"background: {Theme.PANEL}; border: 1px solid {Theme.BORDER}; border-radius: 8px;")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(8, 0, 8, 0)
        lay.setSpacing(8)

        # Button 1: AI Tracking Toggle
        self._btn_ai_track = QPushButton("🤖 AI Tracking: ON")
        self._btn_ai_track.setFixedHeight(26)
        self._btn_ai_track.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self._btn_ai_track.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_ai_track.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.G_GREEN}; border: 1px solid {Theme.BORDER}; border-radius: 4px;")
        self._btn_ai_track.clicked.connect(self._on_toggle_ai_tracking)
        lay.addWidget(self._btn_ai_track)

        # Button 2: Eye Tracking Toggle
        self._btn_eye_track = QPushButton("👁️ Eye Tracking: OFF")
        self._btn_eye_track.setFixedHeight(26)
        self._btn_eye_track.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self._btn_eye_track.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_eye_track.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.TEXT_MUTED}; border: 1px solid {Theme.BORDER}; border-radius: 4px;")
        self._btn_eye_track.clicked.connect(self._on_toggle_eye_tracking)
        lay.addWidget(self._btn_eye_track)

        # Button 3: View Toggle (Full Body vs Chest-to-Face)
        self._btn_view_mode = QPushButton("👤 Bust / Face View")
        self._btn_view_mode.setFixedHeight(26)
        self._btn_view_mode.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self._btn_view_mode.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_view_mode.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.G_BLUE}; border: 1px solid {Theme.BORDER}; border-radius: 4px;")
        self._btn_view_mode.clicked.connect(self._on_toggle_view_mode)
        lay.addWidget(self._btn_view_mode)

        return bar

    def _on_toggle_ai_tracking(self):
        is_on = "ON" in self._btn_ai_track.text()
        new_state = "OFF" if is_on else "ON"
        self._btn_ai_track.setText(f"🤖 AI Tracking: {new_state}")
        self._btn_ai_track.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.G_GREEN if new_state == 'ON' else Theme.TEXT_MUTED}; border: 1px solid {Theme.BORDER}; border-radius: 4px;")
        self._log.append_log(f"SYS: Neural Tracking set to {new_state}.")

    def _on_toggle_eye_tracking(self):
        active = self.hud.toggle_tracking()
        self._btn_eye_track.setText(f"👁️ Eye Tracking: {'ON' if active else 'OFF'}")
        self._btn_eye_track.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.G_GREEN if active else Theme.TEXT_MUTED}; border: 1px solid {Theme.BORDER}; border-radius: 4px;")
        self._log.append_log(f"SYS: Hardware Eye Tracking {'engaged' if active else 'disengaged'}.")

    def _on_toggle_view_mode(self):
        mode = self.hud.toggle_view()
        label = "👤 Bust / Face View" if mode == "bust" else "🧍 Full Body View"
        self._btn_view_mode.setText(label)
        self._log.append_log(f"SYS: Camera perspective switched to {mode.upper()}.")
    
    def _on_thinking_changed(self, index: int):
        levels = ["low", "medium", "high"]
        selected = levels[index]
        data = _read_full_config()
        data["thinking_level"] = selected
        try:
            API_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")
            self._log.append_log(f"SYS: Thinking mode set to {selected.upper()}.")
        except Exception as e:
            self._log.append_log(f"ERR: Could not save thinking mode — {e}")

    def _build_header(self) -> QWidget:
        w = QWidget(); w.setFixedHeight(50); w.setStyleSheet(f"background: {Theme.PANEL}; border-bottom: 1px solid {Theme.BORDER};")
        lay = QHBoxLayout(w); lay.setContentsMargins(16, 0, 16, 0)

        brand = QLabel("●  NEXUS CORE"); brand.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold)); brand.setStyleSheet(f"color: {Theme.G_BLUE};")
        lay.addWidget(brand); lay.addStretch()

        # ── Thinking Mode Dropdown (Google AI Studio Style) ───────────────────
        from PyQt6.QtWidgets import QComboBox
        self._think_combo = QComboBox()
        self._think_combo.setFixedHeight(28)
        self._think_combo.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self._think_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self._think_combo.addItems(["🧠 Low", "🧠 Medium", "🧠 High"])
        
        # Load saved level
        saved_level = _read_full_config().get("thinking_level", "medium").lower()
        idx = {"low": 0, "medium": 1, "high": 2}.get(saved_level, 1)
        self._think_combo.setCurrentIndex(idx)
        self._think_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: {Theme.PANEL_ALT};
                color: {Theme.TEXT};
                border: 1px solid {Theme.BORDER};
                border-radius: 6px;
                padding: 2px 10px;
            }}
            QComboBox:hover {{ border: 1px solid {Theme.G_BLUE}; }}
            QComboBox::drop-down {{ border: none; width: 18px; }}
            QComboBox QAbstractItemView {{
                background-color: {Theme.PANEL};
                color: {Theme.TEXT};
                selection-background-color: {Theme.G_BLUE};
                selection-color: #FFFFFF;
                border: 1px solid {Theme.BORDER_H};
                border-radius: 6px;
                padding: 4px;
            }}
        """)
        self._think_combo.currentIndexChanged.connect(self._on_thinking_changed)
        lay.addWidget(self._think_combo)
        lay.addSpacing(6)

        # Effects & Mode Toggles
        self._glow_btn = QPushButton("🌈 Google Glow"); self._glow_btn.setFixedHeight(28); self._glow_btn.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        self._glow_btn.setCursor(Qt.CursorShape.PointingHandCursor); self._glow_btn.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.G_BLUE}; border: 1px solid {Theme.BORDER}; border-radius: 6px; padding: 0 8px;")
        self._glow_btn.clicked.connect(self._toggle_google_glow); lay.addWidget(self._glow_btn)

        self._matrix_btn = QPushButton("💻 Matrix Rain"); self._matrix_btn.setFixedHeight(28); self._matrix_btn.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        self._matrix_btn.setCursor(Qt.CursorShape.PointingHandCursor); self._matrix_btn.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.G_GREEN}; border: 1px solid {Theme.BORDER}; border-radius: 6px; padding: 0 8px;")
        self._matrix_btn.clicked.connect(self._toggle_matrix); lay.addWidget(self._matrix_btn)

        self._theme_btn = QPushButton("🌓" if Theme.DARK else "☀️"); self._theme_btn.setFixedSize(30, 30); self._theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_btn.setStyleSheet(f"background: {Theme.PANEL_ALT}; border: 1px solid {Theme.BORDER}; border-radius: 6px;")
        self._theme_btn.clicked.connect(self._toggle_theme); lay.addWidget(self._theme_btn)

        cust_btn = QPushButton("⚙"); cust_btn.setFixedSize(30, 30); cust_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cust_btn.setStyleSheet(f"background: {Theme.PANEL_ALT}; border: 1px solid {Theme.BORDER}; border-radius: 6px;"); cust_btn.clicked.connect(self._open_customize); lay.addWidget(cust_btn)

        lay.addSpacing(8)
        self._clock_lbl = QLabel("00:00:00"); self._clock_lbl.setFont(QFont("Consolas", 11, QFont.Weight.Bold)); self._clock_lbl.setStyleSheet(f"color: {Theme.TEXT};")
        lay.addWidget(self._clock_lbl)
        return w

    def _build_left_panel(self) -> QWidget:
        w = QWidget(); w.setFixedWidth(_LEFT_W); w.setStyleSheet(f"background: {Theme.PANEL}; border: 1px solid {Theme.BORDER}; border-radius: 12px;")
        lay = QVBoxLayout(w); lay.setContentsMargins(8, 10, 8, 10); lay.setSpacing(4)

        lbl = QLabel("SYSTEM METRICS"); lbl.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold)); lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED};"); lay.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        # Semi-Circular Radial Gauges matching design
        self._gauge_cpu = MetricGauge("CPU", "⚡", Theme.G_GREEN)
        self._gauge_mem = MetricGauge("RAM", "💾", Theme.G_RED)
        self._gauge_net = MetricGauge("NET", "🌐", Theme.G_YELLOW)
        self._gauge_gpu = MetricGauge("GPU", "🎮", Theme.G_BLUE)

        for g in [self._gauge_cpu, self._gauge_mem, self._gauge_net, self._gauge_gpu]:
            lay.addWidget(g)

        lay.addStretch()
        rem_btn = QPushButton("📱 Remote Connect"); rem_btn.setFixedHeight(28); rem_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold)); rem_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        map_btn = QPushButton("📍 3D Spatial Map")
        map_btn.setFixedHeight(28)
        map_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        map_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        map_btn.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.G_GREEN}; border: 1px solid {Theme.BORDER}; border-radius: 6px;")
        map_btn.clicked.connect(lambda: self.show_spatial_map())
        lay.addWidget(map_btn)
        rem_btn.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.G_BLUE}; border: 1px solid {Theme.BORDER}; border-radius: 6px;"); rem_btn.clicked.connect(self._open_remote); lay.addWidget(rem_btn)

        plug_btn = QPushButton("🧩 Plugins"); plug_btn.setFixedHeight(28); plug_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold)); plug_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        plug_btn.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.TEXT}; border: 1px solid {Theme.BORDER}; border-radius: 6px;"); plug_btn.clicked.connect(self._open_plugin_manager); lay.addWidget(plug_btn)
        sc_btn = QPushButton("⊞ Desktop Shortcut")
        sc_btn.setFixedHeight(28)
        sc_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        sc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        sc_btn.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.TEXT_MUTED}; border: 1px solid {Theme.BORDER}; border-radius: 6px;")
        sc_btn.clicked.connect(self._create_desktop_shortcut)
        lay.addWidget(sc_btn)
        return w

    def _build_right_panel(self) -> QWidget:
        w = QWidget(); w.setFixedWidth(_RIGHT_W); w.setStyleSheet(f"background: {Theme.PANEL}; border: 1px solid {Theme.BORDER}; border-radius: 12px;")
        lay = QVBoxLayout(w); lay.setContentsMargins(10, 10, 10, 10); lay.setSpacing(6)

        lbl = QLabel("ACTIVITY CONSOLE"); lbl.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold)); lbl.setStyleSheet(f"color: {Theme.TEXT_MUTED};"); lay.addWidget(lbl)
        self._log = LogWidget(); lay.addWidget(self._log, stretch=1)

        self._drop_zone = FileDropZone(); self._drop_zone.file_selected.connect(self._on_file_selected); lay.addWidget(self._drop_zone)

        in_row = QHBoxLayout()
        self._input = QLineEdit(); self._input.setPlaceholderText("Ask or command anything..."); self._input.setFont(QFont("Segoe UI", 9)); self._input.setFixedHeight(32)
        self._input.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.TEXT}; border: 1px solid {Theme.BORDER}; border-radius: 6px; padding: 4px 8px;"); self._input.returnPressed.connect(self._send)
        in_row.addWidget(self._input)

        send_btn = QPushButton("↑"); send_btn.setFixedSize(32, 32); send_btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold)); send_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        send_btn.setStyleSheet(f"background: {Theme.G_BLUE}; color: white; border: none; border-radius: 6px;"); send_btn.clicked.connect(self._send); in_row.addWidget(send_btn)
        lay.addLayout(in_row)

        ctl_row = QHBoxLayout()
        self._mute_btn = QPushButton("🎙 Mic Active"); self._mute_btn.setFixedHeight(28); self._mute_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold)); self._mute_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._mute_btn.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.G_GREEN}; border: 1px solid {Theme.BORDER}; border-radius: 6px;"); self._mute_btn.clicked.connect(self._toggle_mute); ctl_row.addWidget(self._mute_btn)

        self._intr_btn = QPushButton("⏹ Stop [ESC]"); self._intr_btn.setFixedHeight(28); self._intr_btn.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold)); self._intr_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._intr_btn.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.G_RED}; border: 1px solid {Theme.BORDER}; border-radius: 6px;"); self._intr_btn.clicked.connect(self._do_interrupt); ctl_row.addWidget(self._intr_btn)
        lay.addLayout(ctl_row)
        return w

    def _build_content_panel(self) -> QWidget:
        w = QWidget(); w.setStyleSheet(f"background: {Theme.PANEL}; border: 1px solid {Theme.BORDER}; border-radius: 10px;"); w.hide()
        lay = QVBoxLayout(w); lay.setContentsMargins(10, 8, 10, 8); lay.setSpacing(4)
        hdr = QHBoxLayout()
        self._content_title = QLabel("BRIEFING"); self._content_title.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold)); self._content_title.setStyleSheet(f"color: {Theme.G_BLUE};")
        hdr.addWidget(self._content_title); hdr.addStretch()
        cb = QPushButton("✕"); cb.setFixedSize(16, 16); cb.setStyleSheet(f"color: {Theme.TEXT_MUTED}; background: transparent; border: none;"); cb.clicked.connect(w.hide); hdr.addWidget(cb); lay.addLayout(hdr)

        self._content_txt = QTextEdit(); self._content_txt.setReadOnly(True); self._content_txt.setFont(QFont("Segoe UI", 8))
        self._content_txt.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.TEXT}; border: none; border-radius: 6px; padding: 6px;"); lay.addWidget(self._content_txt)
        return w

    def _build_footer(self) -> QWidget:
        w = QWidget(); w.setFixedHeight(22); w.setStyleSheet(f"background: {Theme.PANEL}; border-top: 1px solid {Theme.BORDER};")
        lay = QHBoxLayout(w); lay.setContentsMargins(14, 0, 14, 0)
        l1 = QLabel("[F4] Mute   ·   [F11] Fullscreen   ·   [ESC] Interrupt"); l1.setFont(QFont("Segoe UI", 7)); l1.setStyleSheet(f"color: {Theme.TEXT_MUTED};"); lay.addWidget(l1); lay.addStretch()
        l2 = QLabel("Powered by Gemini Multimodal Live Engine"); l2.setFont(QFont("Segoe UI", 7)); l2.setStyleSheet(f"color: {Theme.TEXT_DIM};"); lay.addWidget(l2)
        return w
        
    # ── Auto-Start & Desktop Shortcut Handlers ────────────────────────────────
    @staticmethod
    def _get_desktop_dir() -> Path:
        home = Path.home()
        if _OS == "Windows":
            try:
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
                    val, _ = winreg.QueryValueEx(key, "Desktop")
                p = Path(os.path.expandvars(val))
                if p.is_dir(): return p
            except Exception: pass
        elif _OS == "Linux":
            try:
                out = subprocess.run(["xdg-user-dir", "DESKTOP"], capture_output=True, text=True, timeout=3)
                p = Path(out.stdout.strip())
                if p.is_dir(): return p
            except Exception: pass
        return home / "Desktop"

    def _create_desktop_shortcut(self):
        script = Path(__file__).resolve().parent / "main.py"
        python = Path(sys.executable)
        desktop = self._get_desktop_dir()
        
        # Build and link custom NEXUS icon
        ico_path = CONFIG_DIR / "nexus.ico"
        if not ico_path.exists():
            build_nexus_icon(ico_path)

        try:
            if _OS == "Windows":
                pythonw = python.parent / "pythonw.exe"
                target = str(pythonw if pythonw.exists() else python)
                lnk = str(desktop / f"{self._assistant_name}.lnk")
                vbs = (
                    f'Set ws = CreateObject("WScript.Shell")\n'
                    f'Set sc = ws.CreateShortcut("{lnk}")\n'
                    f'sc.TargetPath = "{target}"\n'
                    f'sc.Arguments = Chr(34) & "{script}" & Chr(34)\n'
                    f'sc.WorkingDirectory = "{script.parent}"\n'
                    f'sc.IconLocation = "{ico_path}"\n'
                    f'sc.Save'
                )
                import tempfile
                fd, tmp = tempfile.mkstemp(suffix=".vbs")
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(vbs)
                subprocess.Popen(["wscript.exe", "/nologo", tmp], creationflags=subprocess.CREATE_NO_WINDOW).wait(timeout=5)
                os.unlink(tmp)
            elif _OS == "Linux":
                desk = desktop / f"{self._assistant_name}.desktop"
                desk.write_text(f"[Desktop Entry]\nName={self._assistant_name}\nExec={python} {script}\nPath={script.parent}\nType=Application\nTerminal=false\n")
                desk.chmod(0o755)
            self._log.append_log("SYS: Desktop shortcut with custom NEXUS icon created.")
        except Exception as e:
            self._log.append_log(f"ERR: Shortcut creation failed — {e}")

    def _check_autostart(self) -> bool:
        try:
            if _OS == "Windows":
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ) as key:
                    winreg.QueryValueEx(key, "NEXUS_AI")
                    return True
            elif _OS == "Darwin":
                return (Path.home() / "Library" / "LaunchAgents" / "com.nexus.assistant.plist").exists()
            else:
                return (Path.home() / ".config" / "autostart" / "nexus.desktop").exists()
        except Exception: return False

    def _toggle_autostart(self):
        on = self._check_autostart()
        try:
            script = str(Path(__file__).resolve().parent / "main.py")
            if _OS == "Windows":
                import winreg
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS) as reg:
                    if on:
                        winreg.DeleteValue(reg, "NEXUS_AI")
                    else:
                        pythonw = Path(sys.executable).parent / "pythonw.exe"
                        exe = str(pythonw if pythonw.exists() else sys.executable)
                        winreg.SetValueEx(reg, "NEXUS_AI", 0, winreg.REG_SZ, f'"{exe}" "{script}"')
            self._log.append_log(f"SYS: Auto-start {'disabled' if on else 'enabled'}.")
        except Exception as e:
            self._log.append_log(f"ERR: Auto-start toggle failed — {e}")

    # ── Callbacks & Runtime Handlers ──────────────────────────────────────────
    def _toggle_theme(self):
        Theme.set_mode(not Theme.DARK)
        self._theme_btn.setText("🌓" if Theme.DARK else "☀️")
        self._apply_global_style()
        self._log._refresh_style()
        self._refresh_box_borders()
        self.hud.update(); self.update()
        
    def _toggle_matrix(self):
        Theme.FX_MODE = "MATRIX" if Theme.FX_MODE != "MATRIX" else "NONE"
        self._refresh_box_borders()
        self.hud.update()
        
    def _toggle_google_glow(self):
        Theme.FX_MODE = "GOOGLE_GLOW" if Theme.FX_MODE != "GOOGLE_GLOW" else "NONE"
        self._refresh_box_borders()
        self.hud.update()
        
    def _refresh_box_borders(self):
        if Theme.FX_MODE == "GOOGLE_GLOW":
            # Google Studio Glowing Gradient Border Style
            glow_style = f"""
                border: 1.8px solid {Theme.G_BLUE};
                border-radius: 12px;
                background-color: {Theme.PANEL};
            """
            self._left_panel_w.setStyleSheet(f"QWidget {{ {glow_style} }}")
            self._right_panel_w.setStyleSheet(f"QWidget {{ {glow_style} }}")
        else:
            self._left_panel_w.setStyleSheet(f"background: {Theme.PANEL}; border: 1px solid {Theme.BORDER}; border-radius: 12px;")
            self._right_panel_w.setStyleSheet(f"background: {Theme.PANEL}; border: 1px solid {Theme.BORDER}; border-radius: 12px;")

    def _tick_clock(self):
        self._clock_lbl.setText(time.strftime("%H:%M:%S"))

    def _update_metrics(self):
        snap = _metrics.snapshot()
        self._gauge_cpu.set_value(snap["cpu"], f"{snap['cpu']:.0f}%")
        self._gauge_mem.set_value(snap["mem"], f"{snap['mem']:.0f}%")
        
        net = snap["net"]
        net_str = f"{net*1024:.0f} KB/s" if net < 1.0 else f"{net:.1f} MB/s"
        self._gauge_net.set_value(min(100, net * 10), net_str)

        if snap["gpu"] >= 0:
            self._gauge_gpu.set_value(snap["gpu"], f"{snap['gpu']:.0f}%")
        else:
            self._gauge_gpu.set_value(0, "N/A")

    def _send(self):
        txt = self._input.text().strip()
        if not txt: return
        self._input.clear(); self._log.append_log(f"You: {txt}")
        if self.on_text_command: threading.Thread(target=self.on_text_command, args=(txt,), daemon=True).start()

    def _toggle_mute(self):
        self._muted = not self._muted; self.hud.muted = self._muted
        if self._muted:
            self._mute_btn.setText("🔇 Muted"); self._mute_btn.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.G_RED}; border: 1px solid {Theme.BORDER}; border-radius: 6px;"); self._apply_state("MUTED")
        else:
            self._mute_btn.setText("🎙 Mic Active"); self._mute_btn.setStyleSheet(f"background: {Theme.PANEL_ALT}; color: {Theme.G_GREEN}; border: 1px solid {Theme.BORDER}; border-radius: 6px;"); self._apply_state("LISTENING")

    def _do_interrupt(self):
        if self.on_interrupt: self.on_interrupt()

    def _toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def _apply_state(self, state: str):
        is_spk = (state == "SPEAKING")
        self.hud.set_speaking(is_spk)

    def _show_content(self, title: str, text: str):
        self._content_title.setText(title.upper()); self._content_txt.setPlainText(text); self._content_panel.show()

    def _on_file_selected(self, path: str):
        p = Path(path); self._log.append_log(f"FILE: {p.name} ({_fmt_size(p.stat().st_size)}) loaded")
        if self.on_text_command:
            msg = f"[FILE_UPLOADED] path={path} | name={p.name} | size={_fmt_size(p.stat().st_size)}"
            threading.Thread(target=self.on_text_command, args=(msg,), daemon=True).start()

    def _open_remote(self):
        if not self.on_remote_clicked: return
        res = self.on_remote_clicked()
        if not res: return
        url, key = res[0], res[1]; auto = res[2] if len(res) >= 3 else ""
        cw = self._central
        ov = RemoteKeyOverlay(url, key, auto_login_url=auto, parent=cw)
        ov.setGeometry((cw.width() - RemoteKeyOverlay._OW) // 2, (cw.height() - RemoteKeyOverlay._OH) // 2, RemoteKeyOverlay._OW, RemoteKeyOverlay._OH)
        ov.show(); self._remote_overlay = ov

    def _open_customize(self):
        cfg = _read_full_config()
        cw = self._central
        ov = CustomizeOverlay(
            assistant_name=self._assistant_name,
            user_name=cfg.get("user_name", ""),
            current_voice=cfg.get("voice_name", "Fenrir"),
            parent=cw
        )
        ov.setGeometry((cw.width() - CustomizeOverlay._OW) // 2, (cw.height() - CustomizeOverlay._OH) // 2, CustomizeOverlay._OW, CustomizeOverlay._OH)
        ov.saved.connect(self._apply_identity)
        ov.show()
        self._customize_overlay = ov

    def _apply_identity(self, name: str, user_name: str, voice_name: str, color_hex: str):
        self._assistant_name = name
        self.hud._assistant_name = name
        self.setWindowTitle(f"{name} — Multimodal OS Core")
        data = _read_full_config()
        data["assistant_name"] = name
        data["user_name"] = user_name
        data["voice_name"] = voice_name
        try:
            API_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")
            self._log.append_log(f"SYS: Identity updated. Voice set to {voice_name.upper()}.")
        except Exception:
            pass

    def _open_plugin_manager(self):
        plugins = self.get_plugins() if self.get_plugins else []; cw = self._central
        ov = PluginManagerOverlay(plugins, parent=cw)
        ov.setGeometry((cw.width() - ov.width()) // 2, (cw.height() - ov.height()) // 2, ov.width(), ov.height()); ov.show()

    def _on_clipboard_changed(self):
        try:
            t = QApplication.clipboard().text().strip()
            if len(t) >= 10: self._clipboard_sig.emit(t)
        except Exception: pass

    def _on_clipboard_action(self, cmd: str):
        if self.on_text_command: threading.Thread(target=self.on_text_command, args=(cmd,), daemon=True).start()

    def _show_camera_frame(self, img_bytes: bytes):
        self._cam_preview.show_frame(img_bytes)
        cw = self._central; self._cam_preview.setGeometry(cw.width() - _RIGHT_W - _CameraPreview._W - 14, cw.height() - _CameraPreview._H - 30, _CameraPreview._W, _CameraPreview._H)

    def _on_cam_stream(self, start: bool): self._hud_stack.setCurrentIndex(1 if start else 0)

    def _on_cam_frame(self, data: bytes):
        px = QPixmap(); px.loadFromData(data)
        if not px.isNull():
            w, h = self._cam_live_lbl.width(), self._cam_live_lbl.height()
            if w > 1 and h > 1: self._cam_live_lbl.setPixmap(px.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio))

    def start_camera_stream(self):
        # 1. Release avatar webcam first to avoid camera conflict/crashes
        self.hud.pause_camera()
        time.sleep(0.3)
        self._cam_stop.clear()
        self._cam_stream_sig.emit(True)
        threading.Thread(target=self._cam_loop, daemon=True).start()

    def stop_camera_stream(self):
        self._cam_stop.set()
        # 2. Resume eye tracking camera after stream stops
        QTimer.singleShot(600, self.hud.resume_camera)

    def _cam_loop(self):
        try:
            import cv2
            cam_idx = 0
            try:
                cfg = json.loads((CONFIG_DIR / "api_keys.json").read_text())
                cam_idx = int(cfg.get("camera_index", 0))
            except Exception: pass

            backend = cv2.CAP_DSHOW if _OS == "Windows" else cv2.CAP_ANY
            cap = cv2.VideoCapture(cam_idx, backend)
            if not cap.isOpened():
                cap = cv2.VideoCapture(0)

            while not self._cam_stop.wait(0.033) and cap.isOpened():
                ret, frame = cap.read()
                if ret and frame is not None:
                    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 65])
                    self._cam_frame_sig.emit(buf.tobytes())
            cap.release()
        except Exception as e:
            print(f"[Camera Stream Error] {e}")
        finally:
            self._cam_stream_sig.emit(False)

    def _check_config(self) -> bool:
        if not API_FILE.exists(): return False
        try: return bool(json.loads(API_FILE.read_text(encoding="utf-8")).get("gemini_api_key"))
        except Exception: return False

    def _show_setup(self):
        ov = SetupOverlay(self._central); cw = self._central; ow, oh = 400, 220
        ov.setGeometry((cw.width() - ow) // 2, (cw.height() - oh) // 2, ow, oh); ov.done.connect(self._on_setup_done); ov.show(); self._overlay = ov

    def _on_setup_done(self, key: str, os_name: str):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        API_FILE.write_text(json.dumps({"gemini_api_key": key, "os_system": os_name}, indent=4), encoding="utf-8")
        self._ready = True
        if self._overlay: self._overlay.hide(); self._overlay = None
        self._apply_state("LISTENING")

    def resizeEvent(self, e):
        super().resizeEvent(e)
        cw = self._central
        if self._overlay and self._overlay.isVisible(): self._overlay.setGeometry((cw.width() - 400) // 2, (cw.height() - 220) // 2, 400, 220)
        if self._clipboard_panel and self._clipboard_panel.isVisible(): self._clipboard_panel.setGeometry((cw.width() - ClipboardPanel._W) // 2, cw.height() - ClipboardPanel._H - 10, ClipboardPanel._W, ClipboardPanel._H)

# ── Headless/GUI Wrapper Compatible with JarvisLive API ───────────────────────
class _RootShim:
    def __init__(self, app: QApplication): self._app = app
    def mainloop(self): self._app.exec()
    def protocol(self, *_): pass

class JarvisUI:
    def __init__(self, face_path: str, size=None):
        self._app = QApplication.instance() or QApplication(sys.argv)
        self._app.setStyle("Fusion")

        # ── Event to synchronize Splash Screen with background AI runner ──────
        self._splash_done_evt = threading.Event()

        icon_path = BASE_DIR / "config" / "nexus.ico"
        if not icon_path.exists():
            build_nexus_icon(icon_path)

        self._win = MainWindow(face_path)

        # ── Launch Fullscreen 4K Splash (Randomly Selected) ───────────────────
        SplashClass = get_random_splash_class()
        if SplashClass is not None:
            self._splash = SplashClass()
            self._splash.finished.connect(self._on_splash_done)
            self._splash.showFullScreen()
        else:
            self._splash = None
            self._splash_done_evt.set()
            self._win.showFullScreen()

        self.root = _RootShim(self._app)

    def _on_splash_done(self):
        """Called when splash finishes or when user clicks SKIP"""
        self._splash_done_evt.set()
        self._win.showFullScreen()
        self._win.raise_()
        self._win.activateWindow()
        
    def avatar_speak(self, text: str):
        """Directly passes text to the 3D avatar lip-sync engine"""
        QTimer.singleShot(0, lambda: self._win.hud.speak(text))
        
    def avatar_pulse(self):
        """Direct audio watchdog heartbeat"""
        QTimer.singleShot(0, self._win.hud.pulse_speech)

    def set_avatar_speaking(self, is_speaking: bool):
        QTimer.singleShot(0, lambda: self._win.hud.set_speaking(is_speaking))

    def pause_avatar_camera(self):
        QTimer.singleShot(0, self._win.hud.pause_camera)

    def resume_avatar_camera(self):
        QTimer.singleShot(0, self._win.hud.resume_camera)
        
    def avatar_set_audio_energy(self, level: float):
        QTimer.singleShot(0, lambda: self._win.hud.set_audio_energy(level))

    def avatar_push_phoneme(self, text_chunk: str):
        QTimer.singleShot(0, lambda: self._win.hud.push_phoneme(text_chunk))

    def wait_for_splash(self):
        """Holds Gemini AI voice until splash is completely finished or skipped"""
        while not self._splash_done_evt.is_set():
            time.sleep(0.05)
            
    @property
    def muted(self) -> bool: return self._win._muted
    @muted.setter
    def muted(self, v: bool):
        if v != self._win._muted: self._win._toggle_mute()

    @property
    def current_file(self) -> str | None: return self._win._drop_zone.current_file()
    @property
    def on_text_command(self): return self._win.on_text_command
    @on_text_command.setter
    def on_text_command(self, cb): self._win.on_text_command = cb
    @property
    def on_remote_clicked(self): return self._win.on_remote_clicked
    @on_remote_clicked.setter
    def on_remote_clicked(self, cb): self._win.on_remote_clicked = cb
    @property
    def on_interrupt(self): return self._win.on_interrupt
    @on_interrupt.setter
    def on_interrupt(self, cb): self._win.on_interrupt = cb
    @property
    def get_plugins(self): return self._win.get_plugins
    @get_plugins.setter
    def get_plugins(self, cb): self._win.get_plugins = cb

    def notify_phone_connected(self) -> None:
        if self._win._remote_overlay and self._win._remote_overlay.isVisible():
            self._win._remote_overlay.mark_connected()

    def set_state(self, state: str): self._win._state_sig.emit(state)
    def write_log(self, text: str): self._win._log_sig.emit(text)
    def wait_for_api_key(self):
        while not self._win._ready: time.sleep(0.1)
    def show_content(self, title: str, text: str): self._win._content_sig.emit(title[:48], text[:4000])
    def prompt_reconfig(self): self._win._ready = False; self._win._reconfig_sig.emit()
    def show_camera_frame(self, img_bytes: bytes): self._win._camera_sig.emit(img_bytes)
    def start_camera_stream(self) -> None: self._win.start_camera_stream()
    def stop_camera_stream(self) -> None: self._win.stop_camera_stream()
    @property
    def assistant_name(self) -> str: return self._win._assistant_name
    def start_speaking(self): self.set_state("SPEAKING")
    def stop_speaking(self):
        if not self.muted: self.set_state("LISTENING")
        
    def show_spatial_map(self, devices: dict = None, selected_id: str = None):
        QTimer.singleShot(0, lambda: self._win.show_spatial_map(devices, selected_id))

    def show_reactor_core(self):
        QTimer.singleShot(0, lambda: self._win.show_reactor_core())