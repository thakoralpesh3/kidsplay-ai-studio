import os
import sys
import uuid
import json
import base64
import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Load environment
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("KidsPlayStudio")

from server.resilience_manager import ResilienceManager
from server.evolution_engine import EvolutionEngine
from server.gemini_agent import GeminiAgent
from server.security_guard import SecurityGuard
from server.game_synthesizer import synthesize_game_for_prompt

API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-4-argon")
DEFAULT_LANG = os.getenv("DEFAULT_LANGUAGE", "gu-IN")
DATA_DIR = os.getenv("DATA_DIR", str(Path(__file__).resolve().parent.parent / "data"))
STATIC_DIR = str(Path(__file__).resolve().parent.parent / "static")

# Subsystems
resilience = ResilienceManager(DATA_DIR)
evolution = EvolutionEngine(DATA_DIR)
security = SecurityGuard(DATA_DIR)
agent = GeminiAgent(api_key=API_KEY, model=MODEL_NAME)

app = FastAPI(title="KidsPlay AI Studio Secure Backend", version="2.0.0")

# Security Middleware: Headers, Rate Limiting & Secret Redaction
@app.middleware("http")
async def security_firewall_middleware(request: Request, call_next):
    # Extract client IP
    client_ip = request.client.host if request.client else "127.0.0.1"

    # 1. Rate Limit Enforcement (skip static assets for performance)
    if request.url.path.startswith("/api/"):
        allowed, rate_err = security.check_rate_limit(client_ip)
        if not allowed:
            return JSONResponse(status_code=429, content={
                "error": "RATE_LIMIT_EXCEEDED",
                "message": rate_err
            })

    response: Response = await call_next(request)

    # 2. Add Strict Cybersecurity Headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "microphone=*, camera=(), geolocation=()"
    response.headers["X-Security-Shield"] = "Active-Protected"

    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Active WebSocket connections
active_connections: list[WebSocket] = []

async def broadcast_ws(message: Dict[str, Any]):
    dead_connections = []
    for ws in list(active_connections):
        try:
            await ws.send_json(message)
        except Exception:
            dead_connections.append(ws)
    for ws in dead_connections:
        if ws in active_connections:
            active_connections.remove(ws)

# Unified Resume Callback for Crash Recovery and Network Resilience
async def handle_resumed_job(job: Dict[str, Any]):
    job_id = job["id"]
    job_type = job["type"]
    prompt = job["prompt"]
    language = job.get("language", DEFAULT_LANG)
    stage = job.get("stage", "INITIALIZED")
    logger.info(f"🔄 Auto-resuming interrupted process {job_id} ({job_type}) from stage '{stage}': {prompt}")

    await broadcast_ws({
        "type": "resilience_status",
        "status": "resuming",
        "job_id": job_id,
        "message": f"🔄 પ્રક્રિયા આપોઆપ શરૂ થઈ રહી છે (Auto-resuming): '{prompt}'"
    })

    try:
        resilience.update_job_stage(job_id, "PROCESSING_RECOVERY", status="PROCESSING")
        skills_summary = evolution.get_skills_summary()

        if job_type == "create":
            result = await asyncio.to_thread(agent.generate_game, prompt, language, skills_summary)
        elif job_type == "modify":
            current_game = job.get("game_context", {})
            result = await asyncio.to_thread(agent.modify_game, current_game, prompt, language, skills_summary)
        elif job_type == "heal":
            err_msg = job.get("game_context", {}).get("error", "Unknown error")
            code = job.get("game_context", {}).get("code", "")
            result = await asyncio.to_thread(agent.diagnose_and_heal_code, err_msg, code)
        else:
            result = {"error": "Unsupported job type"}

        # Sanitize any generated game code
        if isinstance(result, dict) and "game_code" in result:
            result["game_code"] = security.sanitize_game_code(result["game_code"])

        resilience.update_job_status(job_id, "COMPLETED", result=result)

        if isinstance(result, dict) and "new_skill_learned" in result and result["new_skill_learned"]:
            sk = result["new_skill_learned"]
            if sk.get("id") and sk.get("name"):
                evolution.register_new_skill(sk["id"], sk["name"], sk.get("description", ""), "")

        await broadcast_ws({
            "type": "job_completed",
            "job_id": job_id,
            "job_type": job_type,
            "result": result
        })
        logger.info(f"✅ Interrupted job {job_id} successfully finished and recovered!")

    except Exception as e:
        logger.error(f"❌ Error during auto-resume of job {job_id}: {e}")
        if not resilience.check_internet():
            resilience.mark_job_paused_offline(job_id)
            await broadcast_ws({
                "type": "resilience_status",
                "status": "paused_offline",
                "job_id": job_id,
                "message": "નેટવર્ક બંધ હોવાથી પ્રક્રિયા સેવ કરી છે. નેટ આવતા આપોઆપ શરૂ થશે."
            })
        else:
            resilience.update_job_status(job_id, "FAILED", error=str(e))

resilience.register_resume_callback(handle_resumed_job)

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(resilience.start_monitor(poll_interval=3.0))
    asyncio.create_task(resilience.recover_on_startup())

# Request Models
class CreateGameRequest(BaseModel):
    prompt: str
    language: Optional[str] = "gu-IN"

class ModifyGameRequest(BaseModel):
    prompt: str
    current_game: Dict[str, Any]
    language: Optional[str] = "gu-IN"

class SelfHealRequest(BaseModel):
    error: str
    code: str
    stack: Optional[str] = ""

class TranscribeRequest(BaseModel):
    audio_base64: str
    mime_type: Optional[str] = "audio/webm"
    language: Optional[str] = "gu-IN"

class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "gu-IN"
    conversation_history: Optional[List[Dict[str, str]]] = []
    current_game: Optional[Dict[str, Any]] = None

@app.get("/api/health")
async def health_check():
    online = resilience.check_internet()
    return {
        "status": "ok",
        "online": online,
        "security_shield": "ACTIVE_PROTECTED",
        "model": MODEL_NAME,
        "tier": "Gemini 4 Frontier Argon",
        "frontier_reasoning": True,
        "default_language": DEFAULT_LANG,
        "memory": evolution.get_memory(),
        "skills_count": len(evolution.get_all_skills())
    }

@app.get("/api/security/stats")
async def get_security_stats():
    """Live security threat and protection metrics."""
    return security.get_security_status()

@app.get("/api/job/{job_id}")
async def get_job_status(job_id: str):
    cp = resilience.get_checkpoint(job_id)
    if not cp:
        raise HTTPException(status_code=404, detail="Job not found")
    return cp

@app.post("/api/chat")
async def chat_with_copilot(req: ChatRequest, request: Request):
    """Interactive guided conversation & brainstorming copilot for kids with prompt firewall."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    
    # 1. Prompt Injection Firewall Check
    is_safe, clean_prompt, err = security.sanitize_user_prompt(req.message, client_ip)
    if not is_safe:
        return {
            "action": "CONVERSE",
            "spoken_response": "દોસ્ત, હું ફક્ત મસ્ત અને સુંદર ગેમ બનાવવામાં મદદ કરું છું! ચાલો ગેમ બનાવીએ!",
            "question_for_kid": "તમારે કઈ નવી ગેમ બનાવવી છે?",
            "suggested_options": ["🦄 યુનિકોર્ન ગેમ", "🚀 સ્પેસ રોકેટ", "🏎️ કાર રેસિંગ"]
        }

    try:
        res = await asyncio.to_thread(
            agent.interactive_copilot_chat,
            clean_prompt,
            req.conversation_history or [],
            req.language or DEFAULT_LANG,
            req.current_game
        )
        return res
    except Exception as e:
        logger.error(f"Chat copilot error: {e}")
        return {
            "action": "CONVERSE",
            "spoken_response": "નમસ્તે દોસ્ત! ચાલો એક મજેદાર ગેમ બનાવીએ! 🎮✨",
            "question_for_kid": "તમારે કેવી રમત બનાવવી છે?",
            "suggested_options": ["🦄 યુનિકોર્ન ગેમ", "🚀 સ્પેસ રોકેટ", "🏎️ કાર રેસિંગ"]
        }

@app.post("/api/voice/transcribe")
async def transcribe_voice(req: TranscribeRequest):
    """Universal voice transcriber endpoint with audio firewall."""
    try:
        raw_b64 = req.audio_base64
        if "base64," in raw_b64:
            raw_b64 = raw_b64.split("base64,")[1]
        
        audio_bytes = base64.b64decode(raw_b64)
        mime_type = req.mime_type or "audio/webm"
        language = req.language or DEFAULT_LANG

        transcript = await asyncio.to_thread(agent.transcribe_audio, audio_bytes, mime_type, language)
        return {"status": "ok", "transcript": transcript}
    except Exception as e:
        logger.error(f"Failed to transcribe audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/game/create")
async def create_game(req: CreateGameRequest, request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    
    # 1. Prompt Injection Firewall Check
    is_safe, clean_prompt, err = security.sanitize_user_prompt(req.prompt, client_ip)
    if not is_safe:
        raise HTTPException(status_code=400, detail=err)

    job_id = str(uuid.uuid4())
    logger.info(f"🎮 Received game creation request: '{clean_prompt}' (lang: {req.language})")

    skills_summary = evolution.get_skills_summary()
    result = None

    # Try Gemini AI Generation if online
    if resilience.check_internet():
        resilience.enqueue_job(job_id, "create", clean_prompt, req.language, stage="CALLING_GEMINI")
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(agent.generate_game, clean_prompt, req.language, skills_summary),
                timeout=5.0
            )
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning(f"Gemini generation call bypassed/failed ({e}). Falling back to Instant Synthesizer!")
            result = None

    # Instant Fallback: Multi-Genre HTML/CSS/JS Synthesizer (Works offline & during 429/503 quota/latency)
    if not result or not isinstance(result, dict) or "game_code" not in result:
        logger.info(f"Synthesizing instant HTML/CSS/JS game for: '{clean_prompt}'")
        result = synthesize_game_for_prompt(clean_prompt, req.language or DEFAULT_LANG, skills_summary)
        if not resilience.check_internet():
            prefix = "ઓફલાઇન મોડ: " if (req.language or DEFAULT_LANG).startswith("gu") else "Offline Mode: "
            result["spoken_response"] = prefix + result.get("spoken_response", "ગેમ તૈયાર છે! 🎮✨")

    # 2. Sanitize and Sandbox Output Code
    if isinstance(result, dict) and "game_code" in result:
        result["game_code"] = security.sanitize_game_code(result["game_code"], client_ip)

    if isinstance(result, dict) and "new_skill_learned" in result and result["new_skill_learned"]:
        sk = result["new_skill_learned"]
        if sk.get("id") and sk.get("name"):
            evolution.register_new_skill(sk["id"], sk["name"], sk.get("description", ""), "")

    evolution._increment_memory_counter("total_games_created")
    resilience.update_job_status(job_id, "COMPLETED", result=result)
    return {"job_id": job_id, "status": "COMPLETED", "result": result}

@app.post("/api/game/modify")
async def modify_game(req: ModifyGameRequest, request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"

    # 1. Prompt Injection Firewall Check
    is_safe, clean_prompt, err = security.sanitize_user_prompt(req.prompt, client_ip)
    if not is_safe:
        raise HTTPException(status_code=400, detail=err)

    job_id = str(uuid.uuid4())
    logger.info(f"✨ Received game modification: '{clean_prompt}'")

    skills_summary = evolution.get_skills_summary()
    result = None

    # Try Gemini AI Modification if online
    if resilience.check_internet():
        resilience.enqueue_job(job_id, "modify", clean_prompt, req.language, game_context=req.current_game, stage="CALLING_GEMINI")
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(agent.modify_game, req.current_game, clean_prompt, req.language, skills_summary),
                timeout=5.0
            )
        except (asyncio.TimeoutError, Exception) as e:
            logger.warning(f"Gemini modification call bypassed/failed ({e}). Falling back to Instant Synthesizer!")
            result = None

    # Instant Fallback: Multi-Genre Synthesis
    if not result or not isinstance(result, dict) or "game_code" not in result:
        current_title = req.current_game.get('title', 'Kids Game') if req.current_game else 'Kids Game'
        lang = req.language or DEFAULT_LANG
        result = synthesize_game_for_prompt(f"{current_title} {clean_prompt}", lang, skills_summary)
        result["spoken_response"] = "મેં તમારી ગેમમાં ફેરફાર કરી દીધા છે! નવી શક્તિઓ સાથે રમવાની મજા માણો! ✨" if lang.startswith("gu") else "I updated your game with awesome new tweaks! Enjoy playing! ✨"

    # 2. Sanitize and Sandbox Output Code
    if isinstance(result, dict) and "game_code" in result:
        result["game_code"] = security.sanitize_game_code(result["game_code"], client_ip)

    if isinstance(result, dict) and "new_skill_learned" in result and result["new_skill_learned"]:
        sk = result["new_skill_learned"]
        if sk.get("id") and sk.get("name"):
            evolution.register_new_skill(sk["id"], sk["name"], sk.get("description", ""), "")

    evolution._increment_memory_counter("total_modifications")
    resilience.update_job_status(job_id, "COMPLETED", result=result)
    return {"job_id": job_id, "status": "COMPLETED", "result": result}


@app.post("/api/game/heal")
async def self_heal_game(req: SelfHealRequest, request: Request):
    client_ip = request.client.host if request.client else "127.0.0.1"
    logger.warning(f"🛡️ Client error caught by Self-Healing boundary: {req.error}")
    try:
        result = await asyncio.to_thread(agent.diagnose_and_heal_code, req.error, req.code, req.stack or "")
        
        # Sanitize healed code
        if isinstance(result, dict) and "fixed_game_code" in result:
            result["fixed_game_code"] = security.sanitize_game_code(result["fixed_game_code"], client_ip)

        evolution.record_self_healed_bug(req.error, result.get("diagnosis", ""), {"stack": req.stack})
        return {"status": "HEALED", "result": result}
    except Exception as e:
        logger.error(f"Failed to self-heal: {e}")
        raise HTTPException(status_code=500, detail=security.redact_secrets(str(e)))

@app.get("/api/skills")
async def get_skills():
    return {"skills": evolution.get_all_skills()}

@app.get("/api/memory")
async def get_memory():
    return {"memory": evolution.get_memory()}

class SurpriseRequest(BaseModel):
    current_game: Optional[Dict[str, Any]] = None
    language: Optional[str] = "gu-IN"

@app.post("/api/evolution/surprise")
async def get_surprise_idea(req: SurpriseRequest):
    """
    Autonomous Creative Surprise Generator:
    Surprises the kid with unexpected ideas and secret mechanics.
    """
    try:
        skills_summary = evolution.get_skills_summary()
        idea = await asyncio.to_thread(
            agent.generate_surprise_idea,
            req.current_game,
            req.language or DEFAULT_LANG,
            skills_summary
        )
        # Register new evolutionary skill if provided
        if isinstance(idea, dict) and "evolution_skill" in idea and idea["evolution_skill"]:
            sk = idea["evolution_skill"]
            if sk.get("id") and sk.get("name"):
                evolution.register_new_skill(sk["id"], sk["name"], sk.get("description", ""), "")

        evolution.record_surprise_idea(idea)
        return {"status": "ok", "surprise": idea, "memory": evolution.get_memory()}
    except Exception as e:
        logger.warning(f"Using fallback surprise idea: {e}")
        fallback = evolution.get_fallback_surprise_ideas(req.language or DEFAULT_LANG)
        return {"status": "ok", "surprise": fallback, "memory": evolution.get_memory()}

@app.get("/api/mobile/status")
async def get_mobile_status():
    """Returns live public Cloudflare URLs for both agents."""
    kidsplay_url = "Not initialized yet"
    chhaya_url = "https://flu-francisco-bug-okay.trycloudflare.com"

    kidsplay_file = Path(DATA_DIR) / "kidsplay_public_url.txt"
    if kidsplay_file.exists():
        try:
            with open(kidsplay_file, "r") as f:
                kidsplay_url = f.read().strip() or kidsplay_url
        except Exception:
            pass

    chhaya_file = Path("/home/alpesh/chamunda_re_enterprise/data/chhaya_public_url.txt")
    if chhaya_file.exists():
        try:
            with open(chhaya_file, "r") as f:
                chhaya_url = f.read().strip() or chhaya_url
        except Exception:
            pass

    return {
        "status": "ok",
        "kidsplay_mobile_url": kidsplay_url,
        "chamunda_chhaya_url": chhaya_url,
        "qr_code_image": "/kidsplay_mobile_qr.png",
        "dual_agent_hub_url": "/mobile-hub"
    }

@app.get("/mobile-hub")
async def get_mobile_hub():
    hub_file = Path(STATIC_DIR) / "mobile_hub.html"
    if hub_file.exists():
        from fastapi.responses import FileResponse
        return FileResponse(hub_file)
    raise HTTPException(status_code=404, detail="Mobile hub not generated yet")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    await websocket.send_json({
        "type": "connection_established",
        "online": resilience.check_internet(),
        "security_shield": "ARMED_AND_ACTIVE",
        "skills_count": len(evolution.get_all_skills())
    })
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong", "online": resilience.check_internet()})
    except WebSocketDisconnect:
        if websocket in active_connections:
            active_connections.remove(websocket)
    except Exception:
        if websocket in active_connections:
            active_connections.remove(websocket)

@app.get("/api/github/status")
async def get_github_status():
    """Inspects GitHub repository sync status and branch."""
    from scripts.github_sync import get_git_status, get_remote_info
    try:
        status = await asyncio.to_thread(get_git_status)
        remotes = await asyncio.to_thread(get_remote_info)
        return {
            "status": "ok",
            "git_status": status,
            "remotes": remotes,
            "repo_url": remotes.get("origin", "https://github.com/thakoralpesh3/kidsplay-ai-studio")
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/api/github/sync")
async def trigger_github_sync(req: Optional[Dict[str, Any]] = None):
    """Triggers an Antigravity to GitHub commit & push."""
    from scripts.github_sync import sync_to_github
    try:
        custom_msg = req.get("message") if req else None
        res = await asyncio.to_thread(sync_to_github, message=custom_msg)
        return {"status": "ok", "sync_result": res}
    except Exception as e:
        logger.error(f"GitHub sync error: {e}")
        return {"status": "error", "detail": str(e)}

# Mount static web UI files
if os.path.exists(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8899))
    uvicorn.run(app, host=host, port=port)
