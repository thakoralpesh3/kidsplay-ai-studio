"""
KidsPlay AI Studio • 24/7 Autonomous Mobile Cloud Mirror & Watchdog (Like Project Chhaya)
Author: Antigravity AI, reporting to Alpesh Sir

Features:
1. 24/7 Process Supervision: Keeps KidsPlay Studio running continuously on port 8899.
2. Auto-Restart on Crash: Automatically restarts server within 3 seconds if process exits.
3. Cloudflare Quick Tunnel: Generates a secure, 24/7 public HTTPS URL for mobile access anywhere.
4. Mobile QR Code Generation: Generates scannable QR codes for phone/tablet camera access.
5. Dual-Agent Cross-Navigation: Links Agent 1 (Chamunda RE Enterprise / Chhaya) and Agent 2 (KidsPlay Studio).
"""

import os
import sys
import time
import json
import socket
import signal
import re
import urllib.request
import subprocess
import logging
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import qrcode
except ImportError:
    qrcode = None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [KidsPlayWatchdog] %(message)s"
)
logger = logging.getLogger("KidsPlayWatchdog")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
BIN_DIR = BASE_DIR / "bin"
CLOUDFLARED_BIN = BIN_DIR / "cloudflared"
PID_FILE = DATA_DIR / "kidsplay_server.pid"
TUNNEL_URL_FILE = DATA_DIR / "kidsplay_public_url.txt"
TUNNEL_LOG = DATA_DIR / "kidsplay_tunnel.log"
SERVER_LOG = DATA_DIR / "kidsplay_server.log"
QR_CODE_PATH = STATIC_DIR / "kidsplay_mobile_qr.png"
DESKTOP_QR_PATH = Path("/home/alpesh/Desktop/KidsPlay_Mobile_Access_QR.png")
DESKTOP_HUB_PATH = Path("/home/alpesh/Desktop/Mobile_Access_Both_Agents.html")
CHHAYA_URL_FILE = Path("/home/alpesh/chamunda_re_enterprise/data/chhaya_public_url.txt")

PORT = 8899


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def generate_qr_code(url: str, output_path: Path):
    """Generate a mobile-friendly QR code image."""
    if not qrcode:
        logger.warning("qrcode library not found; skipping QR image generation.")
        return
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=3,
        )
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0c0d1c", back_color="#ffffff")
        img.save(str(output_path))
        logger.info("📱 Scannable Mobile QR Code saved to: %s", output_path)
    except Exception as e:
        logger.error("Failed to generate QR code: %s", e)


def generate_dual_agent_hub_html(kidsplay_url: str, chhaya_url: str):
    """Create a unified desktop and mobile HTML hub to switch between both agents."""
    html_content = f"""<!DOCTYPE html>
<html lang="gu">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📱 Alpesh Sir • Dual Agent Mobile Access Hub</title>
    <style>
        :root {{
            --bg: #0b0c16;
            --card-bg: rgba(22, 24, 48, 0.9);
            --neon-blue: #00f0ff;
            --neon-pink: #ff007a;
            --neon-gold: #ffe600;
            --text: #ffffff;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }}
        body {{
            background: radial-gradient(circle at top, #181b38 0%, var(--bg) 100%);
            color: var(--text);
            min-height: 100vh;
            padding: 24px 16px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .header {{
            text-align: center;
            margin-bottom: 24px;
        }}
        .header h1 {{
            font-size: 26px;
            background: linear-gradient(90deg, var(--neon-pink), var(--neon-blue), var(--neon-gold));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 8px;
        }}
        .header p {{
            font-size: 14px;
            color: #a0a5cc;
        }}
        .badge-live {{
            display: inline-block;
            background: rgba(0, 230, 118, 0.2);
            color: #00e676;
            border: 1px solid #00e676;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 700;
            margin-top: 8px;
        }}
        .agents-grid {{
            width: 100%;
            max-width: 600px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .agent-card {{
            background: var(--card-bg);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.12);
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
            transition: all 0.3s ease;
        }}
        .agent-card.chamunda {{
            border-color: rgba(255, 230, 0, 0.4);
        }}
        .agent-card.kidsplay {{
            border-color: rgba(255, 0, 122, 0.4);
        }}
        .agent-card:hover {{
            transform: translateY(-4px);
        }}
        .agent-icon {{
            font-size: 42px;
            margin-bottom: 10px;
        }}
        .agent-title {{
            font-size: 20px;
            font-weight: 800;
            margin-bottom: 6px;
        }}
        .agent-card.chamunda .agent-title {{ color: var(--neon-gold); }}
        .agent-card.kidsplay .agent-title {{ color: var(--neon-blue); }}
        .agent-desc {{
            font-size: 13px;
            color: #c0c5ea;
            line-height: 1.4;
            margin-bottom: 16px;
        }}
        .btn-launch {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            width: 100%;
            padding: 14px;
            border-radius: 14px;
            font-size: 15px;
            font-weight: 800;
            text-decoration: none;
            color: #0b0c16;
            transition: all 0.2s ease;
        }}
        .btn-chamunda {{
            background: linear-gradient(135deg, #ffe600, #ff9900);
            box-shadow: 0 4px 15px rgba(255, 230, 0, 0.4);
        }}
        .btn-kidsplay {{
            background: linear-gradient(135deg, var(--neon-pink), var(--neon-blue));
            color: #ffffff;
            box-shadow: 0 4px 15px rgba(255, 0, 122, 0.4);
        }}
        .btn-launch:hover {{
            transform: scale(1.02);
            filter: brightness(1.1);
        }}
        .qr-section {{
            margin-top: 16px;
            background: #ffffff;
            padding: 8px;
            border-radius: 12px;
            display: inline-block;
        }}
        .qr-section img {{
            width: 140px;
            height: 140px;
            display: block;
        }}
        .footer {{
            margin-top: 30px;
            text-align: center;
            font-size: 12px;
            color: #6d729c;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📱 Alpesh Sir • Dual Agent Mobile Hub</h1>
        <p>Project Chhaya (પ્રોજેક્ટ છાયા) & KidsPlay AI Studio 24/7 Mobile Gateway</p>
        <span class="badge-live">⚡ Cloudflare 24/7 Public Tunnels Active</span>
    </div>

    <div class="agents-grid">
        <!-- Agent 1: Chamunda Automobile Enterprise (Project Chhaya) -->
        <div class="agent-card chamunda">
            <div class="agent-icon">🏍️</div>
            <div class="agent-title">Agent 1: Chamunda Enterprise (Chhaya)</div>
            <p class="agent-desc">Royal Enfield Workshop OS, Sub-Agents, Voice Diagnostic Copilot, Job Card Mutator & 24/7 Cloud Shadow Mirror</p>
            <a href="{chhaya_url}" target="_blank" class="btn-launch btn-chamunda">
                🚀 Open Chamunda Mobile Agent
            </a>
            <p class="small text-muted" style="margin-top:8px;font-size:11px;color:#8f95c0;word-break:break-all;">{chhaya_url}</p>
        </div>

        <!-- Agent 2: KidsPlay AI Studio (Sparky) -->
        <div class="agent-card kidsplay">
            <div class="agent-icon">🎮</div>
            <div class="agent-title">Agent 2: KidsPlay AI Studio (Sparky)</div>
            <p class="agent-desc">Autonomous Kids Game Creator, Gujarati Voice Assistant, Guided Brainstorming, Self-Evolution & Surprise Idea Engine</p>
            <a href="{kidsplay_url}" target="_blank" class="btn-launch btn-kidsplay">
                🚀 Open KidsPlay Studio on Mobile
            </a>
            <p class="small text-muted" style="margin-top:8px;font-size:11px;color:#8f95c0;word-break:break-all;">{kidsplay_url}</p>
            
            <div class="qr-section">
                <img src="/static/kidsplay_mobile_qr.png" alt="Scan to open KidsPlay Studio" onerror="this.style.display='none'">
            </div>
            <span style="font-size:11px;color:#a0a5cc;margin-top:6px;">Scan with Phone Camera to Open Instantly!</span>
        </div>
    </div>

    <div class="footer">
        <p>24/7 Autonomous Self-Supervised by Chhaya & KidsPlay Watchdog</p>
        <p>© Alpesh Sir • Chamunda Automobiles & KidsPlay AI Studio</p>
    </div>
</body>
</html>
"""
    try:
        with open(DESKTOP_HUB_PATH, "w", encoding="utf-8") as f:
            f.write(html_content)
        # Also copy to static directory so it can be viewed at /mobile-hub
        with open(STATIC_DIR / "mobile_hub.html", "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info("✨ Dual Agent Mobile Hub saved to %s and %s", DESKTOP_HUB_PATH, STATIC_DIR / "mobile_hub.html")
    except Exception as e:
        logger.error("Failed to generate Dual Agent Hub HTML: %s", e)


class KidsPlayWatchdog:
    """
    Supervises KidsPlay AI Studio on port 8899 and maintains public Cloudflare Tunnel.
    """
    def __init__(self, port: int = PORT):
        self.port = port
        self.server_proc: Optional[subprocess.Popen] = None
        self.tunnel_proc: Optional[subprocess.Popen] = None
        self.running = True
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        STATIC_DIR.mkdir(parents=True, exist_ok=True)

    def start_server(self) -> bool:
        """Launch uvicorn server.main:app as a managed subprocess."""
        if is_port_in_use(self.port):
            if self.check_health():
                logger.info("Existing KidsPlay server on port %d is healthy.", self.port)
                return True
            else:
                logger.warning("Port %d is occupied but unresponsive. Reclaiming port...", self.port)
                os.system(f"pkill -9 -f 'server.main:app' >/dev/null 2>&1 || true")
                os.system(f"fuser -k -9 {self.port}/tcp >/dev/null 2>&1 || true")
                time.sleep(1.5)

        logger.info("Starting KidsPlay AI Studio on port %d...", self.port)
        log_out = open(SERVER_LOG, "a", encoding="utf-8")

        uvicorn_bin = "/home/alpesh/.local/bin/uvicorn"
        if not os.path.exists(uvicorn_bin):
            uvicorn_bin = "uvicorn"

        self.server_proc = subprocess.Popen(
            [uvicorn_bin, "server.main:app", "--host", "0.0.0.0", "--port", str(self.port)],
            cwd=str(BASE_DIR),
            stdout=log_out,
            stderr=log_out,
            start_new_session=True
        )

        with open(PID_FILE, "w") as f:
            f.write(str(self.server_proc.pid))

        for _ in range(25):
            time.sleep(0.5)
            if self.check_health():
                logger.info("✅ KidsPlay Studio healthy on http://127.0.0.1:%d (PID: %d)", self.port, self.server_proc.pid)
                return True

        logger.error("Failed to verify KidsPlay Studio health on port %d", self.port)
        return False

    def check_health(self) -> bool:
        """Check /api/health endpoint."""
        try:
            url = f"http://127.0.0.1:{self.port}/api/health"
            req = urllib.request.Request(url, headers={"User-Agent": "KidsPlayWatchdog/1.0"})
            with urllib.request.urlopen(req, timeout=8.0) as resp:
                data = json.loads(resp.read().decode())
                return data.get("status") == "ok"
        except Exception:
            return False

    def start_public_tunnel(self):
        """Start Cloudflare Quick Tunnel to expose port 8899 securely via HTTPS."""
        if not CLOUDFLARED_BIN.exists() or not os.access(CLOUDFLARED_BIN, os.X_OK):
            logger.warning("Cloudflared binary not found at %s", CLOUDFLARED_BIN)
            return

        if self.tunnel_proc and self.tunnel_proc.poll() is None:
            return  # Already running

        logger.info("🌐 Starting Cloudflare Quick Tunnel for KidsPlay Studio (Port %d)...", self.port)
        tunnel_log_file = open(TUNNEL_LOG, "a", encoding="utf-8")

        self.tunnel_proc = subprocess.Popen(
            [str(CLOUDFLARED_BIN), "tunnel", "--url", f"http://127.0.0.1:{self.port}"],
            cwd=str(BASE_DIR),
            stdout=tunnel_log_file,
            stderr=tunnel_log_file,
            start_new_session=True
        )

        # Parse generated trycloudflare.com URL
        time.sleep(3)
        kidsplay_url = None
        for _ in range(10):
            try:
                if TUNNEL_LOG.exists():
                    with open(TUNNEL_LOG, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()[-40:]
                        for line in lines:
                            if "trycloudflare.com" in line and "api.trycloudflare.com" not in line:
                                m = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
                                if m and "api.trycloudflare.com" not in m.group(0):
                                    kidsplay_url = m.group(0)
                                    with open(TUNNEL_URL_FILE, "w") as uf:
                                        uf.write(kidsplay_url)
                                    logger.info("🎉 KidsPlay 24/7 Mobile Public URL: %s", kidsplay_url)
                                    break
                if kidsplay_url:
                    break
            except Exception as e:
                logger.debug("Error parsing tunnel URL: %s", e)
            time.sleep(1)

        # Generate QR code and Dual Agent Hub
        if kidsplay_url:
            generate_qr_code(kidsplay_url, QR_CODE_PATH)
            generate_qr_code(kidsplay_url, DESKTOP_QR_PATH)

            chhaya_url = "https://flu-francisco-bug-okay.trycloudflare.com"
            if CHHAYA_URL_FILE.exists():
                try:
                    with open(CHHAYA_URL_FILE, "r") as f:
                        chhaya_url = f.read().strip() or chhaya_url
                except Exception:
                    pass

            generate_dual_agent_hub_html(kidsplay_url, chhaya_url)

    def run_supervision_loop(self):
        """Continuous supervision loop."""
        logger.info("🛡️ Starting KidsPlay 24/7 Watchdog (Port %d)...", self.port)
        self.start_server()
        self.start_public_tunnel()

        iteration = 0
        consecutive_failures = 0
        while self.running:
            time.sleep(12)
            iteration += 1

            # 1. Health check & Auto-Restart (requires 4 consecutive failures = 48s)
            if not self.check_health():
                consecutive_failures += 1
                logger.warning("⚠️ KidsPlay Studio server missed health check (%d/4)...", consecutive_failures)
                if consecutive_failures >= 4:
                    logger.warning("⚠️ KidsPlay Studio server UNHEALTHY! Auto-restarting...")
                    self.start_server()
                    consecutive_failures = 0
            else:
                consecutive_failures = 0

            # 2. Check Tunnel every 60s
            if iteration % 6 == 0:
                self.start_public_tunnel()

    def stop(self, signum=None, frame=None):
        """Gracefully terminate child processes."""
        self.running = False
        logger.info("🛑 Shutdown signal received. Stopping managed processes...")
        if self.server_proc:
            try:
                self.server_proc.terminate()
                self.server_proc.wait(timeout=2)
            except Exception:
                pass
        if self.tunnel_proc:
            try:
                self.tunnel_proc.terminate()
                self.tunnel_proc.wait(timeout=2)
            except Exception:
                pass
        os.system(f"fuser -k {self.port}/tcp >/dev/null 2>&1 || true")
        sys.exit(0)


if __name__ == "__main__":
    wd = KidsPlayWatchdog()
    signal.signal(signal.SIGTERM, wd.stop)
    signal.signal(signal.SIGINT, wd.stop)
    try:
        wd.run_supervision_loop()
    except (KeyboardInterrupt, SystemExit):
        wd.stop()
