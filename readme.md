# NEXUS // MARK I — Multimodal Autonomous Desktop AI Core

NEXUS is a native desktop artificial intelligence assistant built from the ground up in Python and WebGL. It integrates real-time bidirectional audio streaming, computer vision, operating system automation, an autonomous developer agent, and an interactive 3D humanoid avatar running locally at 60 FPS.

Unlike standard API wrappers, NEXUS operates as an autonomous OS companion capable of perceiving its physical surroundings, analyzing active screens, controlling system hardware, and executing multi-file software engineering tasks.

---

## Key Architecture & Core Systems

### 1. 3D Neural Avatar & Real-Time Lip Sync Engine
- **WebGL2 / Three.js Runtime:** Embeds a 3D humanoid avatar (generated via Avaturn) natively inside a desktop PyQt6 viewport.
- **Hardware-Driven Audio Watchdog:** Lip-sync articulation is driven directly by active speaker audio buffers rather than text-to-speech approximations. Features an automated 140ms watchdog decay that strictly closes the mouth when voice audio stops.
- **Armature & Bone Calibration:** Hardcoded Euler angular offsets lock upper arms (`64°, 13°, 11°`) and shoulders (`12°, 0°, 0°`) to prevent T-pose distortion.
- **1:1 MediaPipe Head & Eye Tracking:** Real-time facial landmark detection (MediaPipe FaceMesh) tracks user head position and gaze direction via webcam.
- **Procedural Blinking:** Natural sinusoidal eyelid blink cycle firing every ~4.5 seconds.

### 2. Low-Latency Voice Streaming (Gemini Multimodal Live)
- **Bidirectional WebSocket Pipeline:** Low-latency native audio streaming (16kHz PCM input, 24kHz PCM output) powered by Google's Gemini Multimodal Live API.
- **Acoustic Echo Cancellation Gate:** Automatically mutes microphone capture while the AI is outputting audio through speakers to prevent audio feedback loops.
- **Instant Speech Interruption:** Pressing ESC or speaking mid-sentence drains pending audio queues and immediately returns to listening state.
- **Configurable Thinking Levels:** Dynamic reasoning budget selector (Low, Medium, High) to allocate extended analytical processing tokens.

### 3. Multimodal Computer Vision & Safe Hardware Arbitration
- **Physical Object Recognition:** Captures high-resolution webcam frames on command to identify objects, documents, and physical hardware.
- **Windows DirectShow Conflict Arbiter:** Automatically pauses avatar webcam tracking before taking OpenCV camera captures, preventing Windows `0xC0000005` COM access violations and driver crashes.
- **Live Screen Analysis:** Captures and evaluates multi-monitor screen regions for code debugging, layout inspection, and error diagnosis.
- **Picture-in-Picture Preview:** Displays floating camera capture snapshots directly inside the UI.

### 4. Autonomous Developer Agent & Direct OS Automation
- **Autonomous Dev Agent:** Plans multi-file project architectures, writes code across files, resolves and installs pip dependencies, opens the project in VSCode, and runs execution tests.
- **Direct System Settings:** Controls Windows master volume scalar via Core Audio APIs / pycaw, adjusts display brightness, toggles Dark/Light mode, manages active windows, and executes system power states.
- **GUI Automation:** Mouse movement, coordinate-based clicks, keyboard typing simulation, and hotkey injection via PyAutoGUI.
- **Multimodal File Drop Zone:** Drag-and-drop file processing for PDFs, CSVs, images, code files, and documents with instant OCR and summarization.

### 5. 3D Spatial Telemetry & Mobile Remote Dashboard
- **3D Spatial Satellite Map:** Integrated Leaflet mapping engine with 22x zoom satellite and dark street layers for physical hardware and fleet GPS tracking.
- **Hardware Telemetry Gauges:** Real-time monitoring of CPU, RAM, Network I/O, and dedicated NVIDIA GPU utilization via NVML C-types integration.
- **Mobile Web Remote Access:** Built-in local FastAPI server with 10-minute expiring secure QR codes and passkeys allowing any smartphone on the local network to stream microphone audio directly into NEXUS.
- **Long-Term Memory Engine:** Extracts and stores user identity, preferences, active projects, and end-of-session summaries in local JSON memory.

---

## Repository Structure

```text
NEXUS-AI/
├── actions/
│   ├── browser_control.py      # Multi-browser web automation
│   ├── code_helper.py          # Single-file code generator & runner
│   ├── computer_control.py      # GUI, hotkeys, mouse & keyboard automation
│   ├── computer_settings.py     # OS volume, brightness, power controls
│   ├── deep_think.py           # Deep analytical reasoning runner
│   ├── desktop.py              # Desktop organization & wallpaper controls
│   ├── dev_agent.py            # Autonomous multi-file project builder
│   ├── device_tracker.py       # 5-layer spatial GPS asset tracker
│   ├── file_controller.py      # File system management & disk analytics
│   ├── file_processor.py       # Multimodal file drag-and-drop processor
│   ├── screen_processor.py     # Webcam object vision & screen capture
│   ├── web_search.py           # Live search, comparison & news engine
│   └── youtube_video.py        # YouTube video extraction & summarizer
├── config/
│   ├── api_keys.json           # API key & preference configuration
│   └── prompt.txt              # System prompt and assistant identity
├── memory/
│   ├── memory_manager.py       # Long-term memory & session summarizer
│   └── long_term.json          # Persistent user memory store
├── head.glb                    # 3D humanoid avatar rigged model
├── index.html                  # Three.js WebGL2 3D avatar viewport & tracking
├── ui.py                       # PyQt6 desktop GUI & telemetry engine
├── main.py                     # Core Gemini Live WebSocket async event loop
├── requirements.txt            # Python dependencies
└── README.md                   # System documentation

Prerequisites & Installation
1. Requirements
Operating System: Windows 10/11, macOS, or Linux
Python Version: Python 3.10 to 3.13
Hardware: Dedicated GPU recommended for simultaneous WebGL 3D rendering and real-time audio processing.

2. Clone Repository
git clone https://github.com/YOUR_USERNAME/NEXUS-Multimodal-AI-Core.git
cd NEXUS-Multimodal-AI-Core

3. Install Dependencies
pip install -r requirements.txt

4. Configure API Key
Create or edit config/api_keys.json:
{
    "gemini_api_key": "YOUR_GEMINI_API_KEY",
    "assistant_name": "NEXUS",
    "user_name": "Your Name",
    "thinking_level": "medium",
    "voice_name": "Fenrir"
}

Running NEXUS
Launch the core application:
python main.py

Quick Keyboard Shortcuts:
F4: Toggle Microphone Mute
F11: Toggle Full-Screen Mode
ESC: Instant Speech Interruption

Capabilities Overview & Tool Summary
Module	Core Functionality
3D Avatar Viewport	60 FPS WebGL2 avatar, real-time lip-sync watchdog, MediaPipe 1:1 eye tracking
Gemini Live Stream	Native bidirectional 16kHz/24kHz PCM audio over WebSockets
Dev Agent	Autonomous multi-file project creation, dependency installation, and testing
Computer Vision	Webcam physical object identification and desktop screen analysis
OS Automation	Windows Core Audio volume scalar, window focus, typing, and hotkeys
Spatial Blueprint	Level-22 satellite tracking map with live telemetry overlays
Hardware Gauges	Real-time CPU, RAM, Network I/O, and NVIDIA NVML GPU monitoring
Remote Dashboard	Local mobile web controller with QR code login and phone mic relay

Performance & Optimization Note
Running a live 3D WebGL viewport simultaneously with real-time video face mesh tracking and full-duplex PCM audio streaming requires hardware GPU acceleration. On systems with a dedicated GPU and standard RAM, the interface runs at a locked 60 FPS.
Opportunities & Contact
I am actively open to:
Full-Time Roles: AI Engineer, Multimodal Systems Developer, Full-Stack Python Engineer
Contract & Freelance: Custom AI agents, desktop automation tools, and vision pipelines
LinkedIn: [Insert your LinkedIn URL]
Email: [Insert your contact email]
