"""
security.py  -  Cybersecurity Layer for EduPredict
===================================================
Features:
  1. Rate Limiting       - blocks brute-force/flood attacks
  2. Input Sanitization  - strips XSS payloads, validates ranges
  3. Audit Logging       - timestamped event log
  4. HMAC Token Auth     - stateless session tokens (SHA-256)
  5. Injection Guard     - detects SQL/script injection patterns
"""
import os, re, time, hmac, hashlib, logging
from datetime import datetime
from collections import defaultdict
from functools import wraps
from flask import request, jsonify

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, 'outputs', 'audit.log')
SECRET_KEY = os.environ.get('EDUPREDICT_SECRET', 'edupredict-secret-key-2024')

logging.basicConfig(
    filename=LOG_PATH, level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

SECURITY_LOG = []


def audit(event_type: str, detail: str, severity: str = 'INFO', ip: str = 'unknown'):
    ts  = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    msg = f"[{severity}] [{event_type}] IP={ip} | {detail}"
    logging.info(msg)
    entry = {"ts": ts, "type": event_type, "detail": detail,
             "severity": severity, "ip": ip}
    SECURITY_LOG.append(entry)
    if len(SECURITY_LOG) > 200:
        SECURITY_LOG.pop(0)


# Rate Limiter
_RATE_STORE: dict = defaultdict(list)
RATE_LIMIT  = 60
RATE_WINDOW = 60


def is_rate_limited(ip: str) -> bool:
    now  = time.time()
    hits = [t for t in _RATE_STORE[ip] if now - t < RATE_WINDOW]
    _RATE_STORE[ip] = hits
    if len(hits) >= RATE_LIMIT:
        audit('RATE_LIMIT', f'Blocked after {len(hits)} requests', 'WARNING', ip)
        return True
    hits.append(now)
    return False


def rate_limit(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = request.remote_addr or '0.0.0.0'
        if is_rate_limited(ip):
            return jsonify({"error": "Too many requests. Slow down."}), 429
        return f(*args, **kwargs)
    return decorated


# Input Sanitizer
_XSS_PATTERNS = [
    r'<script', r'javascript\s*:', r'on\w+\s*=',
    r'<iframe', r'eval\(', r'document\.cookie',
]
_SQLI_PATTERNS = [
    r"('\s*(or|and)\s*'?\d)", r'(--|#|/\*)',
    r'\b(select|insert|update|delete|drop|union|exec)\b',
]


def _check_pattern(value: str, patterns: list) -> bool:
    v = str(value).lower()
    return any(re.search(p, v, re.IGNORECASE) for p in patterns)


def sanitize_string(value: str, field: str = 'field') -> tuple:
    if _check_pattern(value, _XSS_PATTERNS):
        ip = request.remote_addr if request else 'unknown'
        audit('XSS_ATTEMPT', f'XSS payload in field={field}', 'CRITICAL', ip)
        return '', False
    if _check_pattern(value, _SQLI_PATTERNS):
        ip = request.remote_addr if request else 'unknown'
        audit('SQLI_ATTEMPT', f'Injection in field={field}', 'CRITICAL', ip)
        return '', False
    clean = re.sub(r'[<>&"\']', '', str(value)).strip()
    return clean, True


def validate_predict_input(data: dict) -> tuple:
    errors = []
    clean  = {}

    numeric_rules = {
        'Hours_Studied':   (5,  40),
        'Attendance':      (0, 100),
        'Previous_Scores': (40, 100),
        'Test_Score':      (10, 30),
        'Project_Marks':   (10, 40),
        'Backlogs':        (0,  5),
    }
    for field, (lo, hi) in numeric_rules.items():
        try:
            val = float(data.get(field, lo))
            if not (lo <= val <= hi):
                errors.append(f"{field} must be between {lo} and {hi}.")
                val = max(lo, min(val, hi))
            clean[field] = val
        except (TypeError, ValueError):
            errors.append(f"{field} must be a number.")
            clean[field] = lo

    cat_rules = {
        'Submission_Timeliness': ['On time', 'Late', 'No Submission'],
        'Participation':         ['High', 'Medium', 'Low'],
        'Extra_C':               ['Highly Active', 'Active', 'Inactive'],
    }
    for field, allowed in cat_rules.items():
        raw, ok = sanitize_string(str(data.get(field, '')), field)
        if raw not in allowed:
            errors.append(f"{field} must be one of {allowed}.")
            raw = allowed[1]
        clean[field] = raw

    return clean, errors


# HMAC Token Auth
def _sign(payload: str) -> str:
    return hmac.new(SECRET_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()


def generate_token(user: str, role: str = 'teacher') -> str:
    import base64
    ts      = int(time.time())
    payload = f"{user}:{role}:{ts}"
    sig     = _sign(payload)
    raw     = f"{payload}:{sig}"
    return base64.urlsafe_b64encode(raw.encode()).decode()


def verify_token(token: str) -> tuple:
    try:
        import base64
        raw     = base64.urlsafe_b64decode(token.encode()).decode()
        parts   = raw.rsplit(':', 1)
        payload, sig = parts[0], parts[1]
        if not hmac.compare_digest(sig, _sign(payload)):
            return None, None, False
        user, role, ts = payload.split(':', 2)
        if time.time() - int(ts) > 3600 * 8:
            return None, None, False
        return user, role, True
    except Exception:
        return None, None, False


def get_security_stats() -> dict:
    counts = {"INFO": 0, "WARNING": 0, "CRITICAL": 0}
    types  = {}
    for e in SECURITY_LOG:
        counts[e['severity']] = counts.get(e['severity'], 0) + 1
        types[e['type']]      = types.get(e['type'], 0) + 1
    return {
        "total_events": len(SECURITY_LOG),
        "by_severity":  counts,
        "by_type":      types,
        "recent":       SECURITY_LOG[-10:][::-1],
    }
