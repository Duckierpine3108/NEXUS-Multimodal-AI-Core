# ==============================================================================
#            ACTIONS: REAL DEVICE TELEMETRY & 3D SPATIAL ENGINE
# ==============================================================================

import json
import time
import urllib.request
from pathlib import Path

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"
DEVICES_FILE = CONFIG_DIR / "devices_telemetry.json"
GEO_CACHE = {}

def _load_devices() -> dict:
    try:
        if DEVICES_FILE.exists():
            return json.loads(DEVICES_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def _save_devices(data: dict):
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        DEVICES_FILE.write_text(json.dumps(data, indent=4), encoding="utf-8")
    except Exception:
        pass

def _resolve_real_address(lat: float, lon: float) -> str:
    """
    Translates raw GPS coordinates (lat/lon) into real human street,
    neighborhood, city, and country names.
    """
    coord_key = f"{round(lat, 4)},{round(lon, 4)}"
    if coord_key in GEO_CACHE:
        return GEO_CACHE[coord_key]

    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        req = urllib.request.Request(url, headers={"User-Agent": "NexusAI-DeviceTracker/2.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            addr = data.get("address", {})
            road = addr.get("road") or addr.get("suburb") or addr.get("neighbourhood") or ""
            city = addr.get("city") or addr.get("town") or addr.get("county") or ""
            state = addr.get("state") or ""
            country = addr.get("country") or ""

            parts = [p for p in [road, city, state, country] if p]
            result = ", ".join(parts) if parts else data.get("display_name", "Unknown Street")
            GEO_CACHE[coord_key] = result
            return result
    except Exception:
        return f"Coordinates: {lat:.5f}° N, {lon:.5f}° E"

def register_or_update_real_device(device_id: str, name: str, lat: float, lon: float, 
                                   speed_kmh: float = 0.0, heading: float = 0.0, 
                                   battery: int = 100, status: str = "ONLINE") -> dict:
    devices = _load_devices()
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    real_addr = _resolve_real_address(lat, lon)

    devices[device_id] = {
        "name": name or f"Device-{device_id[:6]}",
        "device_id": device_id,
        "status": status,
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "speed_kmh": round(speed_kmh, 1),
        "heading_deg": round(heading, 1),
        "battery": int(battery),
        "last_seen": now_str,
        "address": real_addr,
        "layer": "Level 1 (Live GPS + 5G)" if status == "ONLINE" else "Level 3 (Offline Blackbox Cache)"
    }
    _save_devices(devices)
    return devices[device_id]

def mark_device_offline(device_id: str):
    devices = _load_devices()
    if device_id in devices:
        devices[device_id]["status"] = "OFFLINE"
        devices[device_id]["layer"] = "Level 3 (Offline Blackbox Hold)"
        _save_devices(devices)

def track_device(parameters: dict, player=None, speak=None) -> str:
    action = (parameters.get("action") or "locate").lower().strip()
    target = (parameters.get("device_id") or parameters.get("query") or "").upper().strip()
    devices = _load_devices()

    if not devices:
        msg = "No real devices are paired yet. Please click 'Remote Connect' on the UI and scan the QR code with your phone."
        if player and hasattr(player, "show_content"):
            player.show_content("DEVICE TRACKER", msg)
        return msg

    if action == "list" or not target:
        summary_lines = []
        for dev_id, d in devices.items():
            summary_lines.append(
                f"• [{d['status']}] {d['name']}: {d.get('address', 'Unknown')} | Speed: {d['speed_kmh']} km/h | Bat: {d['battery']}%"
            )
        output = f"Real Paired Fleet ({len(devices)} device(s)):\n" + "\n".join(summary_lines)
        if player and hasattr(player, "show_content"):
            player.show_content("REAL DEVICE FLEET", output)
        if player and hasattr(player, "show_spatial_map"):
            player.show_spatial_map(devices)
        return output

    matched_id = None
    for dev_id, d in devices.items():
        if target in dev_id.upper() or target.lower() in d["name"].lower():
            matched_id = dev_id
            break

    if not matched_id:
        avail = ", ".join([d['name'] for d in devices.values()])
        return f"Device '{target}' not found. Active devices: {avail}"

    dev = devices[matched_id]
    telemetry_report = (
        f"◈ REAL 3D SPATIAL TELEMETRY: {dev['name']} ({matched_id})\n"
        f"• Status: {dev['status']}\n"
        f"• Real Street Address: {dev.get('address', 'Resolving...')}\n"
        f"• Coordinates: {dev['lat']}° N, {dev['lon']}° E\n"
        f"• Velocity: {dev['speed_kmh']} km/h | Heading: {dev['heading_deg']}°\n"
        f"• Battery Level: {dev['battery']}%\n"
        f"• Last Synchronized: {dev['last_seen']}"
    )

    if player and hasattr(player, "show_content"):
        player.show_content(f"TRACKING — {dev['name']}", telemetry_report)

    if player and hasattr(player, "show_spatial_map"):
        player.show_spatial_map(devices, selected_id=matched_id)

    return (
        f"{dev['name']} is currently located at {dev.get('address', 'its coordinates')}. "
        f"Status is {dev['status']}, speed is {dev['speed_kmh']} km/h with {dev['battery']}% battery."
    )