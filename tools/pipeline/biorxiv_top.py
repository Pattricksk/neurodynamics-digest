"""biorxiv-top (RobertoDF/biorxiv-top) ranking, recomputed exactly as the site's notebook.py does:
score = (full-text + PDF reads in the period) / (median reads/day of tracked preprints posted within +-3 days, x days online);
needs >= 15 days online in the period and >= 10 peers. Fallback chain per brief: raw URL -> GitHub API contents -> git clone."""
import json, os, statistics, subprocess, tempfile, base64, datetime as dt
from common import get, FetchError

RAW = "https://raw.githubusercontent.com/RobertoDF/biorxiv-top/data/usage.json"
API = "https://api.github.com/repos/RobertoDF/biorxiv-top/contents/usage.json?ref=data"
MIN_DAYS, PEER_DAYS = 15, 3

def load(log):
    errs = []
    try:
        return get(RAW, timeout=90, retries=3), "raw.githubusercontent", errs
    except Exception as e:
        errs.append(f"raw: {e}")
    try:
        meta = get(API, timeout=60, retries=2)
        if meta.get("content"):
            return json.loads(base64.b64decode(meta["content"])), "github-api", errs
        if meta.get("download_url"):
            return get(meta["download_url"], timeout=90), "github-api-download", errs
    except Exception as e:
        errs.append(f"github api: {e}")
    try:
        d = tempfile.mkdtemp()
        subprocess.run(["git", "clone", "--depth", "1", "--branch", "data", "https://github.com/RobertoDF/biorxiv-top.git", d],
                       check=True, capture_output=True, timeout=180)
        for p in ("usage.json", "data/usage.json"):
            if os.path.exists(os.path.join(d, p)):
                return json.load(open(os.path.join(d, p))), "git-clone", errs
    except Exception as e:
        errs.append(f"git clone: {e}")
    raise FetchError("; ".join(errs))

def month_end(ym):
    first = dt.date.fromisoformat(ym + "-01")
    return (first.replace(day=28) + dt.timedelta(days=4)).replace(day=1) - dt.timedelta(days=1)

def rank(raw, months=None):
    papers = [p for p in raw["papers"] if p.get("usage")]
    today = dt.date.fromisoformat(raw["end"])
    month_list, d = [], dt.date.fromisoformat(raw["start"]).replace(day=1)
    while d <= today:
        month_list.append(d.strftime("%Y-%m")); d = month_end(d.strftime("%Y-%m")) + dt.timedelta(days=1)
    def days_online(p, first, last):
        return max(0, (min(last, today) - max(dt.date.fromisoformat(p["date"]), first)).days + 1)
    bounds = lambda ym: (dt.date.fromisoformat(ym + "-01"), month_end(ym))
    rates = {}
    for p in papers:
        for ym in month_list:
            n = days_online(p, *bounds(ym))
            if n and ym in p["usage"]:
                rates.setdefault((ym, p["date"]), []).append(sum(p["usage"][ym]) / n)
    typical = {}
    for ym in month_list:
        for dd in {d for (m, d) in rates if m == ym}:
            d0 = dt.date.fromisoformat(dd)
            peers = [r for k in range(-PEER_DAYS, PEER_DAYS + 1) for r in rates.get((ym, str(d0 + dt.timedelta(days=k))), [])]
            if len(peers) >= 10 and statistics.median(peers) > 0:
                typical[(ym, dd)] = statistics.median(peers)
    def period(ms):
        rows = []
        for p in papers:
            full = pdf = days = exp = 0
            for ym in ms:
                n = days_online(p, *bounds(ym))
                if not n or ym not in p["usage"] or (ym, p["date"]) not in typical:
                    continue
                full += p["usage"][ym][0]; pdf += p["usage"][ym][1]; days += n; exp += typical[(ym, p["date"])] * n
            if days >= MIN_DAYS and exp:
                rows.append({"doi": p["doi"].lower(), "title": p["title"], "first_author": p.get("first_author"), "date": p["date"],
                             "reads": full + pdf, "days": days, "score": round((full + pdf) / exp, 2)})
        rows.sort(key=lambda r: -r["score"])
        for i, r in enumerate(rows, 1):
            r["rank"] = i
        return rows
    months = months or month_list[-2:]
    return {ym: period([ym]) for ym in months}, {"updated": raw.get("updated"), "start": raw["start"], "end": raw["end"],
                                                  "category": raw.get("category"), "n_papers": len(raw["papers"])}
