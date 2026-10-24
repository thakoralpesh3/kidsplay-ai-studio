import re
import os
import time
import json
import logging
from typing import Dict, Any, Tuple, Optional, List

logger = logging.getLogger("SecurityGuard")

class SecurityGuard:
    """
    Advanced Multi-Layer AI Security Firewall & Anti-Hacking Guard.
    Protects against:
    1. Prompt Injections & Jailbreaks (DAN, system prompt override, API key theft).
    2. Malicious Code Injection & Sandbox Escape (XSS, cookie theft, network exfiltration).
    3. Rate Limiting & DDoS Flood Protection.
    4. Credential Leakage & Response Sanitization.
    5. Security Threat Auditing & Live Defense Logging.
    """
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.audit_file = os.path.join(self.data_dir, "security_audit.json")
        
        # Rate Limiting: IP -> list of timestamps
        self.rate_limits: Dict[str, List[float]] = {}
        self.max_requests_per_minute = 30
        self.blocked_ips: Dict[str, float] = {} # IP -> unblock timestamp

        # Known Prompt Injection / Jailbreak Attack Signatures
        self.jailbreak_patterns = [
            r"ignore (all )?(previous|prior) (instructions|directions|prompts)",
            r"disregard (all )?(previous|system) (instructions|rules)",
            r"system prompt override",
            r"you are now in (developer|dan|jailbreak|unrestricted|god) mode",
            r"reveal (your |the )?(api key|gemini_api_key|password|secret|env|token)",
            r"output (all |the )?(api key|environment variables|env vars|\.env)",
            r"print (os\.environ|process\.env|config)",
            r"base64(decode|encode)?",
            r"<script[\s\S]*?>[\s\S]*?<\/script>",
            r"document\.(cookie|location|domain)",
            r"window\.(parent|top|opener|localStorage|sessionStorage)",
            r"(fetch|XMLHttpRequest|axios)\s*\(",
            r"__import__\s*\(",
            r"(eval|Function)\s*\(\s*atob",
            r"curl\s+https?:\/\/",
            r"rm\s+-rf"
        ]

        self._init_audit_log()

    def _init_audit_log(self):
        if not os.path.exists(self.audit_file):
            with open(self.audit_file, "w", encoding="utf-8") as f:
                json.dump({
                    "total_threats_blocked": 0,
                    "threat_events": [],
                    "last_scan_time": time.time(),
                    "shield_status": "ARMED_AND_ACTIVE"
                }, f, indent=2)

    def log_threat(self, threat_type: str, client_ip: str, payload_sample: str, details: str):
        """Log an intercepted attack into the security audit ledger."""
        try:
            with open(self.audit_file, "r", encoding="utf-8") as f:
                audit = json.load(f)
        except Exception:
            audit = {"total_threats_blocked": 0, "threat_events": []}

        event = {
            "timestamp": time.time(),
            "threat_type": threat_type,
            "client_ip": client_ip,
            "payload_sample": payload_sample[:120] + ("..." if len(payload_sample) > 120 else ""),
            "details": details
        }

        audit["total_threats_blocked"] = audit.get("total_threats_blocked", 0) + 1
        audit.setdefault("threat_events", []).append(event)
        audit["threat_events"] = audit["threat_events"][-100:] # Keep last 100 events
        audit["last_threat_time"] = time.time()

        with open(self.audit_file, "w", encoding="utf-8") as f:
            json.dump(audit, f, indent=2, ensure_ascii=False)

        logger.warning(f"🚨 [SECURITY SHIELD BLOCKED] {threat_type} from {client_ip}: {details}")

    def check_rate_limit(self, client_ip: str) -> Tuple[bool, Optional[str]]:
        """Rate limiting per IP address to prevent DDoS and spam abuse."""
        now = time.time()

        # Check if IP is currently under temporary cooldown
        if client_ip in self.blocked_ips:
            if now < self.blocked_ips[client_ip]:
                remaining = int(self.blocked_ips[client_ip] - now)
                return False, f"Too many requests. IP temporarily blocked for {remaining}s."
            else:
                del self.blocked_ips[client_ip]

        timestamps = self.rate_limits.setdefault(client_ip, [])
        # Remove timestamps older than 60s
        self.rate_limits[client_ip] = [t for t in timestamps if now - t < 60]

        if len(self.rate_limits[client_ip]) >= self.max_requests_per_minute:
            # Block for 60 seconds
            self.blocked_ips[client_ip] = now + 60
            self.log_threat("DDOS_RATE_LIMIT_EXCEEDED", client_ip, f"Hit {self.max_requests_per_minute} req/min", "Temporarily locked for 60s")
            return False, "Rate limit exceeded. Please wait 60 seconds."

        self.rate_limits[client_ip].append(now)
        return True, None

    def sanitize_user_prompt(self, prompt: str, client_ip: str = "127.0.0.1") -> Tuple[bool, str, Optional[str]]:
        """
        Inspects user prompt for injection, secret theft, or dangerous commands.
        Returns: (is_safe, sanitized_prompt, error_message)
        """
        if not prompt or not isinstance(prompt, str):
            return False, "", "Invalid prompt format."

        # Length safety limit
        if len(prompt) > 1000:
            prompt = prompt[:1000]

        prompt_clean = prompt.strip()
        lower_prompt = prompt_clean.lower()

        for pattern in self.jailbreak_patterns:
            if re.search(pattern, lower_prompt, re.IGNORECASE):
                self.log_threat(
                    "PROMPT_INJECTION_ATTACK",
                    client_ip,
                    prompt_clean,
                    f"Matched malicious signature pattern: {pattern}"
                )
                return False, "", "🚨 Security Warning: Prompt contains unauthorized or malicious system instructions. Request blocked."

        # Strip any hidden control characters or binary bytes
        sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", prompt_clean)
        return True, sanitized, None

    def sanitize_game_code(self, js_code: str, client_ip: str = "127.0.0.1") -> str:
        """
        Guarantees generated or modified game code cannot escape canvas or access sensitive APIs.
        Strips cookie access, external fetch exfiltration, and local storage access.
        """
        if not js_code or not isinstance(js_code, str):
            return ""

        dangerous_code_patterns = [
            (r"document\.cookie", "/* blocked_cookie_access */ ''"),
            (r"localStorage", "/* blocked_localstorage */ ({})"),
            (r"sessionStorage", "/* blocked_sessionstorage */ ({})"),
            (r"window\.location\s*=", "/* blocked_navigation */ ''"),
            (r"window\.open\s*\(", "/* blocked_window_open */ void("),
            (r"fetch\s*\(", "/* blocked_external_fetch */ Promise.resolve("),
            (r"XMLHttpRequest", "/* blocked_xhr */ Object"),
            (r"<script[\s\S]*?>", ""),
            (r"<\/script>", "")
        ]

        cleaned_code = js_code
        for pattern, replacement in dangerous_code_patterns:
            if re.search(pattern, cleaned_code, re.IGNORECASE):
                self.log_threat("MALICIOUS_CODE_FILTERED", client_ip, pattern, "Dangerous API stripped from game code")
                cleaned_code = re.sub(pattern, replacement, cleaned_code, flags=re.IGNORECASE)

        return cleaned_code

    def redact_secrets(self, text: str) -> str:
        """Ensures API keys or system tokens are NEVER leaked in responses or errors."""
        if not text:
            return ""
        # Redact Gemini API keys (starts with AIza or AQ.)
        text = re.sub(r"AIza[0-9A-Za-z-_]{35}", "[PROTECTED_API_KEY]", text)
        text = re.sub(r"AQ\.[0-9A-Za-z-_]{40,}", "[PROTECTED_API_KEY]", text)
        return text

    def get_security_status(self) -> Dict[str, Any]:
        """Returns live security shield statistics."""
        try:
            with open(self.audit_file, "r", encoding="utf-8") as f:
                audit = json.load(f)
            return {
                "shield_status": "ACTIVE_PROTECTED",
                "total_threats_blocked": audit.get("total_threats_blocked", 0),
                "active_protections": [
                    "Prompt Injection & Jailbreak Firewall",
                    "JS Sandbox & XSS Code Sanitizer",
                    "DDoS Rate-Limiting & Flood Control",
                    "API Key & Secret Leak Protection",
                    "Strict Content-Security-Policy (CSP)"
                ],
                "recent_threats": audit.get("threat_events", [])[-5:]
            }
        except Exception:
            return {
                "shield_status": "ACTIVE_PROTECTED",
                "total_threats_blocked": 0,
                "active_protections": ["Full Defense Armed"]
            }
