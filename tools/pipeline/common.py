"""Shared helpers for the Neurodynamics Digest pipeline (HTTP with retries, normalisation, I/O)."""
import json, os, re, time, random, unicodedata, datetime as dt
import requests

HERE = os.path.dirname(os.path.abspath(__file__))
NEWS = os.path.dirname(HERE)
MAILTO = os.environ.get("NDD_MAILTO", "sender-inbox@example.invalid")  # set to the sender inbox (used as polite-pool contact for APIs)
UA = f"ndd-pipeline/0.2 (Neurodynamics Digest; mailto:{MAILTO})"

_session = None
def session():
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({"User-Agent": UA})
    return _session

class FetchError(Exception):
    pass

def http(method, url, *, params=None, data=None, timeout=30, retries=4, backoff=1.5, expect="json", headers=None, log=None):
    """GET/POST with retries + exponential backoff on timeouts, 429 and 5xx. Raises FetchError after the last try."""
    last = None
    for attempt in range(retries + 1):
        try:
            r = session().request(method, url, params=params, data=data, timeout=timeout, headers=headers)
            if r.status_code == 429 or r.status_code >= 500:
                ra = r.headers.get("Retry-After")
                wait = float(ra) if ra and ra.isdigit() else backoff * (2 ** attempt) + random.random()
                last = f"HTTP {r.status_code}"
                if attempt < retries:
                    time.sleep(min(wait, 60)); continue
                raise FetchError(last)
            if r.status_code >= 400:
                raise FetchError(f"HTTP {r.status_code}: {r.text[:200]}")
            if expect == "json":
                return r.json()
            return r.text
        except (requests.Timeout, requests.ConnectionError, ValueError) as e:
            last = f"{type(e).__name__}: {str(e)[:150]}"
            if attempt < retries:
                time.sleep(backoff * (2 ** attempt) + random.random()); continue
            raise FetchError(last)
    raise FetchError(last or "unknown error")

def get(url, **kw):
    return http("GET", url, **kw)

def post(url, **kw):
    return http("POST", url, **kw)

def norm_doi(d):
    if not d:
        return ""
    d = d.strip().lower()
    d = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", d)
    d = re.sub(r"^doi:\s*", "", d)
    return d.rstrip(".")

def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s or "") if not unicodedata.combining(c))

def norm_title(t):
    t = strip_accents(re.sub(r"<[^>]+>", " ", t or "")).lower()
    return re.sub(r"[^a-z0-9]+", "", t)[:150]

def clean(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", s).strip()

def load_jsonl(path):
    out = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return out

def daterange_ok(d, start, end):
    try:
        x = dt.date.fromisoformat(d[:10])
    except Exception:
        return True  # unknown date: keep (API already filtered by window)
    return start <= x <= end
