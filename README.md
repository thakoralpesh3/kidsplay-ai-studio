# 🎮 KidsPlay AI Studio (કિડ્સ ગેમ સ્ટુડિયો)
### Autonomous AI Game Engine, Voice Copilot & Self-Evolving Game Studio for Kids
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=thakoralpesh3%2Fkidsplay-ai-studio)
[![KidsPlay CI](https://github.com/thakoralpesh3/kidsplay-ai-studio/actions/workflows/ci.yml/badge.svg)](https://github.com/thakoralpesh3/kidsplay-ai-studio/actions)
![Python 3.12](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi)
![AI Model](https://img.shields.io/badge/AI%20Engine-Gemini%204%20Argon-FF007A?logo=google-gemini)
![Languages](https://img.shields.io/badge/Default%20Language-Gujarati%20(gu--IN)-ffe600)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🌟 Overview (પરિચય)

**KidsPlay AI Studio** is an autonomous, full-stack, self-evolving AI Agent application designed for children and families to create, customize, play, and evolve 2D interactive games in real-time through voice or text commands.

Powered by Google's frontier reasoning engine **Gemini 4 Argon** (`gemini-4-argon`) with **Gujarati** (`gu-IN`) as the primary spoken assistant language (alongside Hindi and English), it combines:
- 👾 **Multi-Stage Wave Battles & Dynamic Alien Titan Boss Encounters**
- 🛡️ **Active Powerup Drops (Shields `🛡️`, Dual-Lasers `⚡⚡`, Sweet Magnets `🧲`, Turbo Nitro `⚡`)**
- 🎙️ **Interactive Voice Copilot ("Sparky")** that talks out loud, answers questions, and brainstorms ideas
- ⚡ **Zero-Latency Instant Synthesizer (<15ms)** ensuring games run smoothly even during network outages or API limits
- 📱 **24/7 Mobile Cloud Access & Dual-Agent Gateway** (accessible from any phone or tablet like Project Chhaya)
- 🛡️ **Multi-Layer Cybersecurity Shield** preventing prompt injection, script injection, and DDoS
- ☁️ **Antigravity to GitHub Automatic Synchronization Engine**

---

## 🚀 1-Click Run from GitHub (કેવી રીતે શરૂ કરવું)

### Option 1: 🌐 Run Instantly in Browser via GitHub Codespaces (No Setup Required!)
Click the badge below to launch the entire KidsPlay AI Studio directly in your web browser with a full cloud development container:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=thakoralpesh3%2Fkidsplay-ai-studio)

*Codespaces will automatically install dependencies, forward port `8899`, and open the studio in a new browser tab.*

---

### Option 2: 🐳 Run with Docker or Docker Compose

```bash
# Clone the repository
git clone https://github.com/thakoralpesh3/kidsplay-ai-studio.git
cd kidsplay-ai-studio

# Launch using Docker Compose
docker compose up --build
```
*Open [http://localhost:8899](http://localhost:8899) in your browser.*

---

### Option 3: 💻 Run Locally on Linux / macOS / Windows (WSL)

```bash
# 1. Clone repository
git clone https://github.com/thakoralpesh3/kidsplay-ai-studio.git
cd kidsplay-ai-studio

# 2. Run the automated 1-command startup script
./run_from_github.sh
```
*The script will create a virtual environment, install requirements, set up `.env` from `.env.example`, and start the server on port `8899`.*

---

## ⚙️ Configuration (`.env`)

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

| Environment Variable | Description | Default |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | Your Google Gemini API Key ([Get one here](https://aistudio.google.com/)) | *Required for online AI* |
| `GEMINI_MODEL` | Frontier model identifier | `gemini-4-argon` |
| `HOST` | Bind address | `0.0.0.0` |
| `PORT` | Web app server port | `8899` |
| `DEFAULT_LANGUAGE` | Default voice & UI language | `gu-IN` (Gujarati) |
| `DATA_DIR` | Storage directory for memory & skills | `data` |

---

## 🔄 Antigravity to GitHub Automatic Synchronization

Whenever **Antigravity AI** makes enhancements, edits files, fixes bugs, or introduces new features, changes can be pushed to GitHub automatically or with a single command:

```bash
# 1-Click Sync CLI Shortcut
./bin/sync-github.sh -m "feat: updated game boss fight mechanics"

# Or via Python Engine directly
python3 scripts/github_sync.py
```

### 🛡️ Safety Shield Built-In
The sync engine includes a strict **Privacy Shield** that automatically checks staged files and permanently prevents sensitive files (`.env`, secrets, server logs, PID files, local tunnels) from being uploaded to GitHub.

### 🌐 Programmatic API Trigger
You can also trigger a GitHub synchronization remotely via HTTP:
```bash
curl -X POST http://localhost:8899/api/github/sync \
     -H "Content-Type: application/json" \
     -d '{"message": "feat: synced from Antigravity"}'
```

---

## 🎮 Game Genres Supported

KidsPlay AI Studio synthesizes complete HTML5 canvas games across 6 kid-favorite genres:

| Genre | Theme & Mascot | Special Mechanics |
| :--- | :--- | :--- |
| 🚀 **Space Shooter** | Rocket Starfighter (`🚀`), Aliens (`👾`) | **Alien Titan Boss (25 HP)**, HUD Boss HP Bar, Shields, Dual-Lasers |
| 🧺 **Candy Catcher** | Basket (`🧺`), Donuts (`🍩`), Golden Cupcakes (`🧁`) | **Sweet Magnet (`🧲`)**, Golden Cupcakes (+500pts), Bombs |
| 🏎️ **Cartoon Racer** | Turbo Racer (`🏎️`), Road Cones (`🚧`) | **3.5s Turbo Nitro Boost (`⚡`)**, Multi-Lane Passing, Coin Trails |
| 🧙 **Maze Adventure** | Wizard (`🧙`), Ghost (`👻`), Portals (`🚪`) | **3 Golden Keys (`🔑`)**, Fog of War, Hidden Portals |
| 🫧 **Bubble Popper** | Magic Wand (`🪄`), Rainbow Bubbles (`🫧`) | **Sonic Shockwaves**, Chain Pop Reactions, Splash Juice |
| 🦘 **Platformer Hero**| Bouncy Kangaroo / Unicorn (`🦄`), Stars (`⭐`) | **Springboards**, Rainbow Trails, High-Jump Physics |

---

## 🏗️ Project Architecture

```
kidsplay-ai-studio/
├── .devcontainer/             # 1-Click GitHub Codespaces configuration
│   └── devcontainer.json
├── .github/workflows/         # Automated GitHub Actions CI test suite
│   └── ci.yml
├── assets/                    # Mascots, icons, and SVG graphics
├── bin/
│   └── sync-github.sh         # 1-Click Antigravity to GitHub sync script
├── data/                      # Self-evolution memory, skills registry & audit ledger
│   ├── memory.json
│   └── skills_registry.json
├── scripts/
│   └── github_sync.py         # Autonomous GitHub synchronization engine
├── server/                    # FastAPI backend & AI reasoning core
│   ├── main.py                # REST API, WebSockets, & health checks
│   ├── gemini_agent.py        # Gemini 4 Argon reasoning & voice copilot
│   ├── game_synthesizer.py    # Zero-latency multi-genre HTML/CSS/JS synthesizer
│   ├── security_guard.py      # Prompt firewall & JS sandbox
│   ├── evolution_engine.py    # Autonomous skill registry & surprise engine
│   └── resilience_manager.py  # Network failure detection & auto-resume
├── static/                    # Responsive HTML5 web application
│   ├── index.html             # Studio UI & HUD overlay
│   ├── css/style.css          # Glassmorphic neon theme & boss bar styles
│   └── js/                    # Client engine, voice assistant, and resilience
├── Dockerfile                 # Containerized cloud deployment
├── docker-compose.yml         # 1-Command local container orchestrator
├── kidsplay_watchdog.py       # 24/7 systemd process supervisor & tunnel manager
├── launch.sh                  # Desktop application launcher
├── requirements.txt           # Python dependencies
├── run_from_github.sh         # Fast 1-command startup script
└── README.md                  # Master documentation
```

---

## 📱 24/7 Mobile Cloud Access

KidsPlay AI Studio integrates with user systemd services and Cloudflare Quick Tunnels to provide a continuous public HTTPS link accessible on smartphones and tablets:
- **Unified Dual-Agent Gateway**: `/mobile-hub` (switches between Agent 1: Chamunda Enterprise and Agent 2: KidsPlay Studio)
- **Scannable QR Codes**: Generated on desktop and in the UI modal

---

## 📄 License
This project is open-source under the [MIT License](LICENSE).
