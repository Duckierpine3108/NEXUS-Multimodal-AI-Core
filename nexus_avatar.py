"""
=============================================================================
NEXUS AI - 3D GLB AVATAR INTERFACE (PROD ENGINE v3.0)
=============================================================================
1. Zero Dots: Clean, realistic eyes rendered directly from your 3D model.
2. Pure Face & Neck Framing: Shoulders, arms, and body completely cut away.
3. Dynamic Mesh Mouth Articulation: Real-time talking & jaw flapping.
4. Real-Time Webcam Head & Gaze Tracking.
=============================================================================
"""

import os
import sys
import socket
import urllib.request
import threading
import http.server
import socketserver
import numpy as np
import cv2
import sounddevice as sd
import webview


# =============================================================================
# 0. ROBUST FACE CASCADE HANDLER
# =============================================================================
def get_safe_cascade():
    cascade_file = "haarcascade_frontalface_default.xml"
    if os.path.exists(cascade_file):
        c = cv2.CascadeClassifier(cascade_file)
        if not c.empty():
            return c
    
    url = "https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_frontalface_default.xml"
    try:
        urllib.request.urlretrieve(url, cascade_file)
        c = cv2.CascadeClassifier(cascade_file)
        if not c.empty():
            return c
    except Exception:
        pass
    return None


# =============================================================================
# 1. CORE STATE & CONTROLLER
# =============================================================================
class NexusCore:
    def __init__(self):
        self.running = True
        self.is_speaking = False
        self.target_yaw = 0.0
        self.target_pitch = 0.0
        self.audio_level = 0.0

nexus = NexusCore()


# =============================================================================
# 2. AUDIO LISTENER (Real-Time Lip-Sync)
# =============================================================================
def audio_callback(indata, frames, time_info, status):
    if nexus.is_speaking:
        volume = float(np.linalg.norm(indata) * 20.0)
        nexus.audio_level = float(np.clip(volume, 0.0, 1.0))
    else:
        nexus.audio_level = 0.0

def start_audio_pipeline():
    try:
        stream = sd.InputStream(callback=audio_callback, channels=1, samplerate=16000)
        with stream:
            while nexus.running:
                sd.sleep(25)
    except Exception as e:
        print(f"[Audio Notice]: {e}")


# =============================================================================
# 3. WEBCAM HEAD TRACKING
# =============================================================================
def tracking_pipeline():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return

    cascade = get_safe_cascade()

    while nexus.running:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape

        if cascade is not None and not cascade.empty():
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = cascade.detectMultiScale(gray, 1.2, 5, minSize=(60, 60))
            if len(faces) > 0:
                x, y, fw, fh = faces[0]
                cx = (x + fw / 2.0) / w - 0.5
                cy = (y + fh / 2.0) / h - 0.5
                nexus.target_yaw = float(cx * 38.0)
                nexus.target_pitch = float(cy * 24.0)
            else:
                nexus.target_yaw = 0.0
                nexus.target_pitch = 0.0

    cap.release()


# =============================================================================
# 4. PYTHON-TO-JAVASCRIPT API BRIDGE
# =============================================================================
class API:
    def get_state(self):
        return {
            "yaw": nexus.target_yaw,
            "pitch": nexus.target_pitch,
            "is_speaking": nexus.is_speaking,
            "audio_level": nexus.audio_level
        }

    def toggle_speech(self):
        nexus.is_speaking = not nexus.is_speaking
        return nexus.is_speaking


# =============================================================================
# 5. LOCAL SERVER & HTML VIEWER ENGINE
# =============================================================================
def generate_index_html():
    html_code = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>NEXUS AI</title>
    <style>
        body { margin: 0; padding: 0; overflow: hidden; background-color: #040711; }
        #canvas-container { width: 100vw; height: 100vh; }
        #hud {
            position: absolute; top: 25px; left: 25px;
            color: #00f0ff; font-family: 'Courier New', monospace;
            font-size: 13px; text-shadow: 0 0 10px #00f0ff;
            pointer-events: none; z-index: 10;
        }
        .status-dot {
            display: inline-block; width: 9px; height: 9px;
            border-radius: 50%; margin-right: 6px;
            background-color: #00ff66; box-shadow: 0 0 10px #00ff66;
        }
        #loading {
            position: absolute; top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            color: #00f0ff; font-family: monospace; font-size: 18px;
            text-shadow: 0 0 10px #00f0ff;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="loading">[INITIALIZING NEXUS CORE...]</div>
    <div id="hud">
        <div>[SYSTEM] NEXUS AI CORE v3.0</div>
        <div>[STATUS] <span class="status-dot" id="status-dot"></span><span id="state-text" style="color:#00ff66;">IDLE / NEUTRAL</span></div>
        <div>[CONTROL] Press SPACE to Toggle Speech Mode</div>
    </div>
    <div id="canvas-container"></div>

    <script>
        let scene, camera, renderer, model, controls;
        let rimLight;
        let currentYaw = 0, currentPitch = 0, mouthOpen = 0;
        let headTargetPos = new THREE.Vector3();
        let morphMeshes = [];
        let mouthDeformers = [];

        function init() {
            const container = document.getElementById('canvas-container');
            scene = new THREE.Scene();

            // Tight cinematic portrait framing (19 deg FOV)
            camera = new THREE.PerspectiveCamera(19, window.innerWidth / window.innerHeight, 0.05, 100);
            
            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(window.devicePixelRatio);
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.2;
            renderer.localClippingEnabled = true;
            container.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;

            // --- STUDIO LIGHTING ---
            const ambient = new THREE.AmbientLight(0xffffff, 1.15);
            scene.add(ambient);

            const keyLight = new THREE.DirectionalLight(0xffffff, 1.6);
            keyLight.position.set(2, 4, 3);
            scene.add(keyLight);

            rimLight = new THREE.DirectionalLight(0x00f0ff, 0.9);
            rimLight.position.set(-3, 1, 2);
            scene.add(rimLight);

            const fillLight = new THREE.DirectionalLight(0xffffff, 0.5);
            fillLight.position.set(0, -2, 3);
            scene.add(fillLight);

            // --- LOAD 3D MODEL ---
            const loader = new THREE.GLTFLoader();
            loader.load('/model.glb', function(gltf) {
                document.getElementById('loading').style.display = 'none';
                model = gltf.scene;
                scene.add(model);

                const box = new THREE.Box3().setFromObject(model);
                const size = box.getSize(new THREE.Vector3());
                const center = box.getCenter(new THREE.Vector3());

                // Center model at origin
                model.position.x = -center.x;
                model.position.z = -center.z;
                model.position.y = -box.min.y;

                // Exact Head Height
                const headY = size.y * 0.915;
                headTargetPos.set(0, headY, 0);

                // --- STRICT NECK CLIPPING (Erases shoulders, chest & T-pose arms completely) ---
                const neckCutoffY = headY - (size.y * 0.072);
                const clipPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), -neckCutoffY);

                model.traverse((child) => {
                    if (child.isMesh) {
                        if (Array.isArray(child.material)) {
                            child.material.forEach(m => { m.clippingPlanes = [clipPlane]; m.clipShadows = true; });
                        } else if (child.material) {
                            child.material.clippingPlanes = [clipPlane];
                            child.material.clipShadows = true;
                        }

                        // Check for built-in blendshapes / morph targets
                        if (child.morphTargetInfluences && child.morphTargetInfluences.length > 0) {
                            morphMeshes.push(child);
                        }

                        // --- SETUP REAL-TIME MESH JAW & LIP DEFORMATION ---
                        if (child.geometry && child.geometry.attributes && child.geometry.attributes.position) {
                            const pos = child.geometry.attributes.position;
                            const origPos = new Float32Array(pos.array);
                            const mouthIndices = [];

                            // Find vertices in the mouth / jaw region
                            const mouthMinY = headY - size.y * 0.065;
                            const mouthMaxY = headY - size.y * 0.022;
                            const mouthWidth = size.x * 0.16;

                            for (let i = 0; i < pos.count; i++) {
                                const vy = origPos[i * 3 + 1];
                                const vx = origPos[i * 3];
                                const vz = origPos[i * 3 + 2];

                                if (vy >= mouthMinY && vy <= mouthMaxY && Math.abs(vx) <= mouthWidth && vz > 0) {
                                    const factor = 1.0 - (Math.abs(vx) / mouthWidth);
                                    mouthIndices.push({
                                        idx: i * 3,
                                        weight: Math.pow(factor, 1.4)
                                    });
                                }
                            }

                            if (mouthIndices.length > 0) {
                                mouthDeformers.push({
                                    mesh: child,
                                    origPos: origPos,
                                    mouthIndices: mouthIndices,
                                    dropScale: size.y * 0.015
                                });
                            }
                        }
                    }
                });

                // Zoom camera straight into the face (No shoulders visible)
                camera.position.set(0, headY, size.y * 0.28);
                camera.lookAt(headTargetPos);
                controls.target.copy(headTargetPos);

                animate();
            }, undefined, function(error) {
                document.getElementById('loading').innerText = '[ERROR LOADING MODEL.GLB]';
                console.error(error);
            });

            window.addEventListener('resize', onResize);
            window.addEventListener('keydown', (e) => {
                if (e.code === 'Space') {
                    window.pywebview.api.toggle_speech();
                }
            });
        }

        function onResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        async function syncWithPython() {
            if (window.pywebview && window.pywebview.api) {
                const state = await window.pywebview.api.get_state();

                // Smooth Gaze & Head Tracking
                currentYaw += (state.yaw - currentYaw) * 0.08;
                currentPitch += (state.pitch - currentPitch) * 0.08;

                if (model) {
                    model.rotation.y = THREE.MathUtils.degToRad(currentYaw);
                    model.rotation.x = THREE.MathUtils.degToRad(currentPitch);
                }

                // --- REAL-TIME SPEECH & JAW ARTICULATION ---
                let speechFactor = 0;
                if (state.is_speaking) {
                    const time = performance.now() * 0.018;
                    // Natural human speech cadence wave + microphone volume modulation
                    const syllableWave = Math.max(0, Math.sin(time) * 0.6 + Math.sin(time * 2.4) * 0.4);
                    speechFactor = Math.max(state.audio_level * 1.2, syllableWave * 0.75);
                }

                mouthOpen += (speechFactor - mouthOpen) * 0.35;

                // 1. Deform geometry vertices for jaw/mouth movement
                for (let def of mouthDeformers) {
                    const pos = def.mesh.geometry.attributes.position;
                    const drop = mouthOpen * def.dropScale;

                    for (let item of def.mouthIndices) {
                        const idx = item.idx;
                        pos.array[idx + 1] = def.origPos[idx + 1] - (drop * item.weight); // Move Down
                        pos.array[idx + 2] = def.origPos[idx + 2] - (drop * 0.25 * item.weight); // Recede slightly
                    }
                    pos.needsUpdate = true;
                }

                // 2. Blendshape fallback if present
                for (let mesh of morphMeshes) {
                    mesh.morphTargetInfluences[0] = mouthOpen;
                }

                // --- STATE HUD & AMBIENT GLOW ---
                const stateText = document.getElementById('state-text');
                const dot = document.getElementById('status-dot');

                if (state.is_speaking) {
                    stateText.innerText = "SPEAKING / ACTIVE";
                    stateText.style.color = "#ff1133";
                    dot.style.backgroundColor = "#ff1133";
                    dot.style.boxShadow = "0 0 10px #ff1133";
                    if (rimLight) rimLight.color.setHex(0xff2244);
                } else {
                    stateText.innerText = "IDLE / NEUTRAL";
                    stateText.style.color = "#00ff66";
                    dot.style.backgroundColor = "#00ff66";
                    dot.style.boxShadow = "0 0 10px #00ff66";
                    if (rimLight) rimLight.color.setHex(0x00f0ff);
                }
            }
        }

        function animate() {
            requestAnimationFrame(animate);
            controls.update();
            syncWithPython();
            renderer.render(scene, camera);
        }

        window.onload = init;
    </script>
</body>
</html>"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_code)


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass


def start_local_server(port):
    handler = QuietHandler
    with socketserver.TCPServer(("127.0.0.1", port), handler) as httpd:
        httpd.serve_forever()


# =============================================================================
# 6. MAIN LAUNCHER
# =============================================================================
def main():
    if not os.path.exists("model.glb"):
        print("[ERROR] 'model.glb' not found! Place model.glb in F:\\NEXUS AI\\")
        return

    generate_index_html()
    port = get_free_port()

    # Start Background Threads
    threading.Thread(target=start_local_server, args=(port,), daemon=True).start()
    threading.Thread(target=tracking_pipeline, daemon=True).start()
    threading.Thread(target=start_audio_pipeline, daemon=True).start()

    print("\n=======================================================")
    print("   NEXUS AI - 3D AVATAR ONLINE (PROD ENGINE v3.0)")
    print("=======================================================")
    print(" [SPACE] : Toggle Speaking Mode (Active Jaw/Mouth Articulation)")
    print("  Webcam : Tracks your head/eye movement live")
    print("  Mouse  : Left-click drag to rotate / Scroll to zoom")
    print("=======================================================\n")

    api = API()
    webview.create_window(
        'NEXUS AI - Autonomous 3D Avatar Core',
        url=f'http://127.0.0.1:{port}/index.html',
        js_api=api,
        width=1280,
        height=800,
        background_color='#040711'
    )
    
    webview.start()
    nexus.running = False
    sys.exit()

if __name__ == "__main__":
    main()