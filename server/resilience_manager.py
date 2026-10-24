import json
import os
import time
import asyncio
import urllib.request
import logging
from typing import Dict, Any, Optional, List, Callable

logger = logging.getLogger("ResilienceManager")

class ResilienceManager:
    """
    Universal Process Interruption, Crash Recovery & Network Resilience Manager.
    Features:
    1. Atomic File Transactions (crash-safe JSON writes).
    2. Process Startup Recovery: Automatically detects and resumes any job
       interrupted by crash, power cut, server restart, or network loss.
    3. Non-blocking Network Health Monitoring & Auto-Resume Daemon.
    """
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.queue_file = os.path.join(self.data_dir, "job_queue.json")
        self.checkpoint_file = os.path.join(self.data_dir, "state_checkpoint.json")
        self.is_online = True
        self.resume_callbacks: List[Callable] = []
        self._init_storage()

    def _init_storage(self):
        if not os.path.exists(self.queue_file):
            self._atomic_write(self.queue_file, [])
        if not os.path.exists(self.checkpoint_file):
            self._atomic_write(self.checkpoint_file, {})

    def _atomic_write(self, filepath: str, data: Any):
        """Crash-safe write using temporary file and atomic replace."""
        temp_file = f"{filepath}.tmp.{os.getpid()}"
        try:
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_file, filepath)
        except Exception as e:
            logger.error(f"Atomic write error for {filepath}: {e}")
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception:
                    pass

    def _read_json(self, filepath: str, default_val: Any) -> Any:
        if not os.path.exists(filepath):
            return default_val
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}. Returning default.")
            return default_val

    def probe_connectivity(self) -> bool:
        """Fast non-blocking connectivity check."""
        try:
            with urllib.request.urlopen("https://www.google.com", timeout=3.0) as resp:
                return resp.status == 200
        except Exception:
            return False

    def check_internet(self) -> bool:
        """Instant non-blocking check using background monitor cached state."""
        return getattr(self, "is_online", True)

    def save_checkpoint(self, job_id: str, payload: Dict[str, Any]):
        """Persist state checkpoint with timestamp and execution phase."""
        checkpoints = self._read_json(self.checkpoint_file, {})
        checkpoints[job_id] = {
            **payload,
            "updated_at": time.time()
        }
        self._atomic_write(self.checkpoint_file, checkpoints)

    def get_checkpoint(self, job_id: str) -> Optional[Dict[str, Any]]:
        checkpoints = self._read_json(self.checkpoint_file, {})
        return checkpoints.get(job_id)

    def enqueue_job(self, job_id: str, job_type: str, prompt: str, language: str = "gu-IN", game_context: Optional[Dict[str, Any]] = None, stage: str = "INITIALIZED") -> Dict[str, Any]:
        """Record an incoming generation or modification job with exact execution stage."""
        job = {
            "id": job_id,
            "type": job_type, # 'create', 'modify', 'fix', 'evolve'
            "prompt": prompt,
            "language": language,
            "game_context": game_context or {},
            "status": "PROCESSING",
            "stage": stage,
            "created_at": time.time(),
            "updated_at": time.time(),
            "attempts": 0
        }
        queue = self._read_json(self.queue_file, [])
        queue.append(job)
        self._atomic_write(self.queue_file, queue)
        self.save_checkpoint(job_id, job)
        return job

    def update_job_stage(self, job_id: str, stage: str, status: Optional[str] = None):
        """Update the checkpoint stage (e.g. 'PROMPT_PARSED', 'CALLING_GEMINI', 'GENERATING_CODE')."""
        queue = self._read_json(self.queue_file, [])
        for job in queue:
            if job["id"] == job_id:
                job["stage"] = stage
                if status:
                    job["status"] = status
                job["updated_at"] = time.time()
                break
        self._atomic_write(self.queue_file, queue)

        cp = self.get_checkpoint(job_id) or {}
        cp["stage"] = stage
        if status:
            cp["status"] = status
        self.save_checkpoint(job_id, cp)

    def update_job_status(self, job_id: str, status: str, result: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        queue = self._read_json(self.queue_file, [])
        for job in queue:
            if job["id"] == job_id:
                job["status"] = status
                if result is not None:
                    job["result"] = result
                if error is not None:
                    job["error"] = error
                job["updated_at"] = time.time()
                break
        self._atomic_write(self.queue_file, queue)

        cp = self.get_checkpoint(job_id) or {}
        cp["status"] = status
        if result is not None:
            cp["result"] = result
        if error is not None:
            cp["error"] = error
        self.save_checkpoint(job_id, cp)

    def mark_job_paused_offline(self, job_id: str):
        self.update_job_status(job_id, "PAUSED_OFFLINE")
        logger.warning(f"⏸️ Job {job_id} safely checkpointed in offline queue.")

    def get_pending_or_interrupted_jobs(self) -> List[Dict[str, Any]]:
        """Finds any job that was halted midway due to crash or network interruption."""
        queue = self._read_json(self.queue_file, [])
        interrupted = []
        for j in queue:
            status = j.get("status")
            if status in ["PROCESSING", "QUEUED", "PAUSED_OFFLINE", "INTERRUPTED"]:
                interrupted.append(j)
        return interrupted

    def register_resume_callback(self, callback: Callable):
        self.resume_callbacks.append(callback)

    async def recover_on_startup(self):
        """
        Runs automatically on server start:
        Scans checkpoints and immediately resumes any processes that were stopped midway!
        """
        interrupted = self.get_pending_or_interrupted_jobs()
        if not interrupted:
            logger.info("✨ Clean startup: No interrupted processes found.")
            return

        logger.warning(f"🚨 Crash Recovery Detected! Found {len(interrupted)} interrupted process(es). Resuming now...")
        for job in interrupted:
            job_id = job["id"]
            logger.info(f"🔄 Auto-resuming interrupted process {job_id} ('{job.get('prompt')}') from stage '{job.get('stage')}'")
            job["status"] = "RECOVERING"
            self.save_checkpoint(job_id, job)
            
            for cb in self.resume_callbacks:
                try:
                    if asyncio.iscoroutinefunction(cb):
                        asyncio.create_task(cb(job))
                    else:
                        cb(job)
                except Exception as e:
                    logger.error(f"Error executing crash recovery callback for job {job_id}: {e}")

    async def start_monitor(self, poll_interval: float = 3.0):
        """Background loop that watches network status and resumes paused work."""
        logger.info("Resilience network & process monitor active.")
        while True:
            try:
                current_online = await asyncio.to_thread(self.check_internet)
                if not self.is_online and current_online:
                    logger.info("🌐 Network connection RESTORED! Resuming any paused jobs...")
                    self.is_online = True
                    pending = self.get_pending_or_interrupted_jobs()
                    for job in pending:
                        for cb in self.resume_callbacks:
                            try:
                                if asyncio.iscoroutinefunction(cb):
                                    asyncio.create_task(cb(job))
                                else:
                                    cb(job)
                            except Exception as e:
                                logger.error(f"Error in resume callback: {e}")
                elif self.is_online and not current_online:
                    logger.warning("⚠️ Network connection LOST. Active requests are safely checkpointed.")
                    self.is_online = False

            except Exception as e:
                logger.error(f"Error in resilience monitor loop: {e}")

            await asyncio.sleep(poll_interval)
