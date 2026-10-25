#!/usr/bin/env python3
"""
KidsPlay AI Studio • Antigravity to GitHub Automatic Synchronization Engine
=============================================================================
Safely monitors, stages, commits, and pushes all codebase modifications made
by Antigravity or the user directly to the GitHub remote repository.

Features:
- Privacy Shield: Strictly prevents accidental staging of .env, tokens, logs, or PIDs.
- Semantic Auto-Commit: Automatically generates informative commit messages based on diffs.
- Autonomous Remote Push: Pushes to origin main with error diagnosis and branch tracking.
- CLI & API Integration: Can be invoked via CLI, systemd, or FastAPI endpoint.
"""

import argparse
import datetime
import logging
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [GitHubSync] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("GitHubSync")

# Critical files that must NEVER be committed to GitHub under any circumstances
BLOCKED_PATTERNS = [
    r"^\.env(\.(local|dev|prod|test|secrets|stage))?$",
    r".*\.pem$",
    r".*\.key$",
    r".*\.pid$",
    r".*\.log$",
    r"^data/kidsplay_server\.log.*$",
    r"^data/kidsplay_tunnel\.log.*$",
    r"^data/kidsplay_systemd\.log.*$",
    r"^data/kidsplay_server\.pid$",
    r"^data/kidsplay_public_url\.txt$",
    r"^data/job_queue\.json$",
    r"^data/state_checkpoint\.json$",
    r"^bin/cloudflared$",
    r"^static/kidsplay_mobile_qr\.png$",
    r"^server\.pid$",
    r"^server\.log$",
    r".*\.pyc$",
    r".*/__pycache__/.*",
    r"^\.venv/.*",
    r"^venv/.*",
]


def _run_git_cmd(args: List[str], check: bool = True) -> Tuple[int, str, str]:
    """Runs a git command in the project root directory."""
    try:
        proc = subprocess.run(
            ["git"] + args,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=check,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.CalledProcessError as e:
        return e.returncode, e.stdout.strip(), e.stderr.strip()
    except FileNotFoundError:
        return 127, "", "git binary not found on system PATH"


def is_git_initialized() -> bool:
    """Checks if git repository is initialized in project root."""
    return (PROJECT_ROOT / ".git").is_dir()


def init_repository(branch: str = "main") -> bool:
    """Initializes git repository if not already present."""
    if is_git_initialized():
        return True

    logger.info("Initializing new Git repository in project root...")
    code, out, err = _run_git_cmd(["init", "-b", branch])
    if code != 0:
        logger.error(f"Failed to initialize git repository: {err}")
        return False

    # Set local user identity
    _run_git_cmd(["config", "user.name", "Alpesh"])
    _run_git_cmd(["config", "user.email", "thakoralpesh3@users.noreply.github.com"])
    logger.info(f"✅ Git repository initialized on branch '{branch}'.")
    return True


def get_git_status() -> Dict[str, Any]:
    """Retrieves list of modified, added, deleted, and untracked files."""
    code, out, err = _run_git_cmd(["status", "--porcelain"])
    status = {"modified": [], "added": [], "deleted": [], "untracked": [], "clean": True}
    if code != 0 or not out:
        return status

    for line in out.splitlines():
        if len(line) < 3:
            continue
        code_xy = line[:2]
        file_path = line[3:].strip()
        if " -> " in file_path:
            file_path = file_path.split(" -> ")[1].strip()

        # Check safety blocklist
        is_blocked = False
        for pattern in BLOCKED_PATTERNS:
            if re.match(pattern, file_path):
                is_blocked = True
                break
        if is_blocked:
            continue

        if "M" in code_xy:
            status["modified"].append(file_path)
        elif "A" in code_xy:
            status["added"].append(file_path)
        elif "D" in code_xy:
            status["deleted"].append(file_path)
        elif code_xy == "??":
            status["untracked"].append(file_path)

    total_changes = len(status["modified"]) + len(status["added"]) + len(status["deleted"]) + len(status["untracked"])
    status["clean"] = (total_changes == 0)
    status["total_changes"] = total_changes
    return status


def generate_commit_message(status: Dict[str, Any], custom_msg: Optional[str] = None) -> str:
    """Generates a concise, informative semantic commit message."""
    if custom_msg and custom_msg.strip():
        return custom_msg.strip()

    total_changes = status.get("total_changes", 0)
    if total_changes == 0:
        return "chore: synchronization update from Antigravity"

    components = set()
    all_files = status["modified"] + status["added"] + status["untracked"] + status["deleted"]
    for f in all_files:
        top_part = f.split("/")[0]
        components.add(top_part)

    comp_str = ", ".join(sorted(list(components))[:3])
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"feat({comp_str}): sync changes from Antigravity ({now_str})"


def get_remote_info() -> Dict[str, str]:
    """Inspects configured git remotes."""
    code, out, err = _run_git_cmd(["remote", "-v"], check=False)
    remotes = {}
    if code == 0 and out:
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 2:
                remotes[parts[0]] = parts[1]
    return remotes


def sync_to_github(
    message: Optional[str] = None,
    remote: str = "origin",
    branch: str = "main",
    push: bool = True,
) -> Dict[str, Any]:
    """
    Executes complete synchronization:
    1. Checks repository initialization
    2. Validates safety & stages changed files
    3. Commits with descriptive message
    4. Pushes to remote repository on GitHub
    """
    if not is_git_initialized():
        init_repository(branch=branch)

    # 1. Inspect status
    status = get_git_status()
    total_changes = status.get("total_changes", 0)

    if total_changes == 0:
        logger.info("✨ Working tree clean. Checking remote sync status...")
        if push:
            code, out, err = _run_git_cmd(["push", remote, branch], check=False)
            if code == 0:
                logger.info("✅ All commits are up to date on GitHub.")
                return {"status": "UP_TO_DATE", "pushed": True, "message": "All commits are up to date on GitHub."}
            else:
                logger.warning(f"Push response: {err or out}")
        return {"status": "CLEAN", "pushed": False, "message": "No new local changes to commit."}

    logger.info(f"📝 Found {total_changes} change(s): {len(status['modified'])} mod, {len(status['added']) + len(status['untracked'])} new, {len(status['deleted'])} del.")

    # 2. Stage changes
    code, out, err = _run_git_cmd(["add", "-A"])
    if code != 0:
        logger.error(f"Failed to stage files: {err}")
        return {"status": "ERROR", "error": err}

    # Safety Shield: Unstage any blocked files if accidentally staged
    code, staged_out, _ = _run_git_cmd(["diff", "--name-only", "--cached"])
    for f in staged_out.splitlines():
        for pat in BLOCKED_PATTERNS:
            if re.match(pat, f):
                logger.warning(f"🛡️ Safety Shield: Unstaging blocked file: {f}")
                _run_git_cmd(["reset", "HEAD", f])

    # 3. Commit
    commit_msg = generate_commit_message(status, message)
    code, commit_out, commit_err = _run_git_cmd(["commit", "-m", commit_msg])
    if code != 0:
        if "nothing to commit" in commit_err or "nothing to commit" in commit_out:
            logger.info("✨ Nothing to commit (files matched safety shields).")
            return {"status": "CLEAN", "pushed": False}
        logger.error(f"Failed to commit: {commit_err}")
        return {"status": "ERROR", "error": commit_err}

    logger.info(f"✅ Committed: {commit_msg}")

    # 4. Push to remote
    if push:
        remotes = get_remote_info()
        if remote not in remotes:
            logger.warning(f"Remote '{remote}' not configured. Commit saved locally.")
            return {"status": "COMMITTED_LOCAL", "commit": commit_msg, "pushed": False}

        logger.info(f"🚀 Pushing to GitHub ({remote}/{branch})...")
        code, push_out, push_err = _run_git_cmd(["push", "-u", remote, branch], check=False)
        if code == 0:
            logger.info("🎉 Successfully synced and pushed changes to GitHub!")
            return {"status": "SYNCED", "commit": commit_msg, "pushed": True}
        else:
            logger.error(f"Push failed: {push_err or push_out}")
            return {"status": "PUSH_FAILED", "commit": commit_msg, "pushed": False, "error": push_err or push_out}

def watch_and_sync(interval_seconds: int = 30, branch: str = "main", remote: str = "origin"):
    """
    Continuous background watcher loop that automatically detects any modifications
    made by Antigravity or the user, and immediately commits and pushes them to GitHub.
    """
    import time
    logger.info(f"👀 Autonomous GitHub Sync Watcher active (polling every {interval_seconds}s)...")
    while True:
        try:
            status = get_git_status()
            if not status.get("clean", True):
                total = status.get("total_changes", 0)
                logger.info(f"🔄 Auto-Sync: Detected {total} changed file(s). Automatically syncing to GitHub...")
                res = sync_to_github(remote=remote, branch=branch, push=True)
                if res.get("pushed"):
                    logger.info(f"🎉 Auto-Sync: Successfully pushed changes to GitHub! ({res.get('commit')})")
        except Exception as e:
            logger.debug(f"Auto-Sync watcher check error: {e}")
        time.sleep(interval_seconds)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity to GitHub Sync Engine")
    parser.add_argument("-m", "--message", help="Custom commit message", default=None)
    parser.add_argument("--no-push", action="store_true", help="Commit locally without pushing")
    parser.add_argument("--status", action="store_true", help="Print current git status")
    parser.add_argument("--watch", "--daemon", dest="watch", action="store_true", help="Run continuous background auto-sync watcher")
    parser.add_argument("--interval", type=int, default=30, help="Watcher interval in seconds (default: 30)")
    args = parser.parse_args()

    if args.status:
        st = get_git_status()
        print(f"Git Status: {st}")
    elif args.watch:
        watch_and_sync(interval_seconds=args.interval)
    else:
        res = sync_to_github(message=args.message, push=not args.no_push)
        print(f"Result: {res}")
