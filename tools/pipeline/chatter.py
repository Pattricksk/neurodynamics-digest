#!/usr/bin/env python3
"""'Buzz this week': how much online chatter each candidate paper is getting, from free no-key sources.
  * Bluesky public AppView (api.bsky.app app.bsky.feed.searchPosts, no auth): posts linking the paper's DOI / publisher URL,
    plus posts quoting the title. Bot accounts (preprint feeds) are excluded.
  * Hacker News (Algolia API): stories linking the DOI/URL or quoting the title.
  * --discover: Bluesky posts linking biorxiv/medrxiv/nature/etc. since the window start (sort=top), aggregated by link,
    to surface papers being talked about that the database search did not shortlist.
Not used (see README): Altmetric (key required since Nov 2025), Crossref Event Data (API sunset Apr 2026),
Reddit (blocks the box; OAuth needed), X (use the agent's own X tool instead).

Usage: python3 chatter.py --date 2026-10-25 [--top 40] [--discover] [--start 2026-10-19]
Reads out/<date>/candidates.json; writes out/<date>/chatter.json and chatter.md."""
import argparse, json, os, re, sys, time, datetime as dt
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import get, HERE, FetchError

BSKY = "https://api.bsky.app/xrpc/app.bsky.feed.searchPosts"
HN = "https://hn.algolia.com/api/v1/search"
BOT_RE = re.compile(r"bot\b|bot\.|biorxiv|medrxiv|arxiv|preprint|rridrobot|papers?feed|journal-?feed|newpapers|scholar-?alert|\.feed\b|pubmed", re.I)
PAUSE = 0.25

def log(*a):
    print(time.strftime("%H:%M:%S"), *a, file=sys.stderr, flush=True)

def bsky(params, errors):
    time.sleep(PAUSE)
    try:
        return get(BSKY, params={**params, "limit": 100}, timeout=25, retries=3).get("posts", [])
    except Exception as e:
        errors.append(f"bsky {params.get('q')!r} {params.get('url', '')}: {e}")
        return []

def url_variants(c):
    doi, url = (c.get("doi") or "").lower(), c.get("url") or ""
    v = []
    if doi:
        v += [f"https://doi.org/{doi}"]
        if doi.startswith(("10.1101/", "10.64898/")):
            server = "medrxiv" if "medrxiv" in (c.get("venue") or "").lower() or "medrxiv" in c.get("source", "") else "biorxiv"
            base = f"https://www.{server}.org/content/{doi}"
            v += [base + "v1", base + "v1.full", base + "v2", base]
        m = re.match(r"10\.1038/(.+)", doi)
        if m:
            v.append(f"https://www.nature.com/articles/{m.group(1)}")
        m = re.match(r"10\.1126/(.+)", doi)
        if m:
            v.append(f"https://www.science.org/doi/{doi}")
        m = re.match(r"10\.1016/(.+)", doi)
        if m and ("cell" in (c.get("venue") or "").lower() or "neuron" in (c.get("venue") or "").lower()):
            v.append(f"https://www.cell.com/action/showPdf?pii=")  # placeholder never matches; Cell URLs use PII, skipped
            v.pop()
        m = re.match(r"10\.48550/arxiv\.(.+)", doi)
        if m:
            v += [f"https://arxiv.org/abs/{m.group(1)}", f"https://arxiv.org/pdf/{m.group(1)}"]
    if url and url not in v and "europepmc" not in url:
        v.append(url)
    return v

def title_query(t):
    words = re.findall(r"[A-Za-z0-9][A-Za-z0-9\-']*", t or "")
    if len(words) < 5:
        return None
    return '"' + " ".join(words[:9]) + '"'

def post_rec(p):
    a = p.get("author", {})
    ext = ((p.get("embed") or {}).get("external") or {}).get("uri") or (((p.get("embed") or {}).get("media") or {}).get("external") or {}).get("uri")
    rk = p.get("uri", "").split("/")[-1]
    return {"uri": p.get("uri"), "url": f"https://bsky.app/profile/{a.get('handle')}/post/{rk}", "handle": a.get("handle"),
            "name": a.get("displayName"), "text": (p.get("record") or {}).get("text", "")[:300], "created": (p.get("record") or {}).get("createdAt"),
            "likes": p.get("likeCount", 0), "reposts": p.get("repostCount", 0), "quotes": p.get("quoteCount", 0), "replies": p.get("replyCount", 0),
            "link": ext}

def is_bot(p):
    return bool(BOT_RE.search(p.get("handle") or "") or BOT_RE.search(p.get("name") or ""))

def hn(c, errors):
    out = {}
    qs = [c.get("doi")] if c.get("doi") else []
    tq = title_query(c.get("title"))
    if tq:
        qs.append(tq.strip('"'))
    for q in qs:
        time.sleep(PAUSE)
        try:
            r = get(HN, params={"query": q, "tags": "story", "restrictSearchableAttributes": "url,title" if q == c.get("doi") else "title"}, timeout=20, retries=2)
        except Exception as e:
            errors.append(f"hn {q!r}: {e}"); continue
        for h in r.get("hits", []):
            out[h["objectID"]] = {"url": f"https://news.ycombinator.com/item?id={h['objectID']}", "title": h.get("title"),
                                  "points": h.get("points") or 0, "comments": h.get("num_comments") or 0, "created": h.get("created_at")}
    return list(out.values())

def buzz_score(posts, hn_hits):
    human = [p for p in posts if not p["bot"]]
    eng = sum(p["likes"] + 2 * p["reposts"] + 2 * p["quotes"] + p["replies"] for p in human)
    authors = len({p["handle"] for p in human})
    return round(3 * authors + eng ** 0.5 * 2 + sum(h["points"] ** 0.5 + h["comments"] ** 0.5 for h in hn_hits), 2), authors, eng

def check(c, since, errors):
    posts = {}
    for u in url_variants(c):
        for p in bsky({"q": "*", "url": u, "sort": "top"}, errors):
            posts[p["uri"]] = post_rec(p)
    tq = title_query(c.get("title"))
    if tq:
        for p in bsky({"q": tq, "sort": "top"}, errors):
            posts.setdefault(p["uri"], post_rec(p))
    for p in posts.values():
        p["bot"] = is_bot(p)
    hits = hn(c, errors)
    score, authors, eng = buzz_score(list(posts.values()), hits)
    plist = sorted(posts.values(), key=lambda p: -(p["likes"] + 2 * p["reposts"]))
    recent = [p for p in posts.values() if (p.get("created") or "")[:10] >= since]
    w_score, w_authors, _ = buzz_score(recent, [])
    return {"title": c["title"], "doi": c.get("doi"), "url": c.get("url"), "venue": c.get("venue"), "candidate_score": c.get("score"),
            "kind": c.get("_kind"), "buzz": score, "bsky_human_posters": authors, "bsky_engagement": eng,
            "buzz_in_window": w_score, "bsky_human_posters_in_window": w_authors, "bsky_posts_total": len(plist), "bsky_bot_posts": sum(p["bot"] for p in plist), "bsky_posts": plist[:8], "hn": hits}

DISCOVER_DOMAINS = ["biorxiv.org", "medrxiv.org", "nature.com", "science.org", "cell.com", "pnas.org", "elifesciences.org", "arxiv.org"]
NEURO_RE = re.compile(r"neuro|brain|cortex|cortical|eeg|fmri|psychedel|psilocyb|neuron|cogniti|conscious|addict|synap|hippocamp|mental|psychiat", re.I)

def discover(since, errors, queries=("neuroscience", "brain", "psychedelic", "EEG", "neurons")):
    agg = defaultdict(lambda: {"posts": {}, "link": None})
    calls = 0
    for dom in DISCOVER_DOMAINS:
        for q in queries:
            calls += 1
            for p in bsky({"q": q, "domain": dom, "since": f"{since}T00:00:00Z", "sort": "top"}, errors):
                r = post_rec(p)
                if not r["link"] or is_bot(r):
                    continue
                key = re.sub(r"(v\d+)?(\.full(-text)?|\.abstract|\.pdf)?([?#].*)?$", "", r["link"].rstrip("/")).lower()
                key = key.replace("http://", "https://").replace("//nature.com", "//www.nature.com")
                agg[key]["posts"][r["uri"]] = r
                agg[key]["link"] = r["link"]
    rows = []
    for key, v in agg.items():
        ps = list(v["posts"].values())
        for p in ps:
            p["bot"] = False
        score, authors, eng = buzz_score(ps, [])
        text = " ".join(p["text"] for p in ps)
        rows.append({"link": key, "buzz": score, "posters": authors, "engagement": eng, "neuro_text": bool(NEURO_RE.search(text) or NEURO_RE.search(key)),
                     "sample_post": max(ps, key=lambda p: p["likes"])["url"], "sample_text": max(ps, key=lambda p: p["likes"])["text"][:200]})
    rows.sort(key=lambda r: -r["buzz"])
    return rows, calls

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="out/<date>/ folder (window end)")
    ap.add_argument("--top", type=int, default=40, help="how many top candidates to check (plus all reviews)")
    ap.add_argument("--start", help="window start for --discover (default: date-6)")
    ap.add_argument("--discover", action="store_true")
    a = ap.parse_args()
    od = os.path.join(HERE, "out", a.date)
    d = json.load(open(os.path.join(od, "candidates.json"), encoding="utf-8"))
    since = a.start or str(dt.date.fromisoformat(a.date) - dt.timedelta(days=6))
    items = [dict(c, _kind="primary") for c in d["candidates"][:a.top]] + [dict(c, _kind="review") for c in d["reviews"]]
    if d.get("biorxiv_top"):   # also check the most-read preprints that match the brief
        for ym, rows in d["biorxiv_top"]["top"].items():
            for r in rows[:25]:
                if r["brief_keyword_score"] and not any((r["doi"] == (i.get("doi") or "")) for i in items):
                    items.append({"title": r["title"], "doi": r["doi"], "url": r["url"], "venue": "bioRxiv", "source": "biorxiv", "_kind": f"biorxiv-top {ym}"})
    t0, errors, res = time.time(), [], []
    for i, c in enumerate(items, 1):
        res.append(check(c, since, errors))
        if i % 10 == 0:
            log(f"{i}/{len(items)} checked")
    res.sort(key=lambda r: -r["buzz"])
    out = {"date": a.date, "since": since, "generated": dt.datetime.now().isoformat(timespec="seconds"), "checked": len(res),
           "with_any_human_bsky_post": sum(r["bsky_human_posters"] > 0 for r in res), "with_hn": sum(bool(r["hn"]) for r in res),
           "errors": errors[:50], "n_errors": len(errors), "ranking": res}
    if a.discover:
        rows, calls = discover(since, errors)
        out["discover"] = {"calls": calls, "rows": rows[:60]}
    out["runtime_seconds"] = round(time.time() - t0, 1)
    json.dump(out, open(os.path.join(od, "chatter.json"), "w"), indent=1, ensure_ascii=False)
    L = [f"# Buzz this week ({since} to {a.date})", "",
         f"Checked {len(res)} papers on Bluesky (DOI/publisher-URL links + title quotes, bots excluded) and Hacker News. "
         f"{out['with_any_human_bsky_post']} had at least one human Bluesky post; {out['with_hn']} had HN stories. Errors: {len(errors)}.",
         "Counts are lifetime (preprint-era posts included); 'since' = posters inside the window. Buzz = 3×distinct human posters + 2×√(likes + 2·reposts + 2·quotes + replies) + HN √points + √comments. Counts are as of the run.", ""]
    for i, r in enumerate([r for r in res if r["buzz"] > 0][:20], 1):
        top = next((p for p in r["bsky_posts"] if not p["bot"]), None)
        L.append(f"{i}. **{r['title']}** — buzz {r['buzz']} · {r['bsky_human_posters']} posters ({r['bsky_human_posters_in_window']} since {since}), {r['bsky_engagement']} engagement"
                 + (f" · HN {sum(h['points'] for h in r['hn'])} pts" if r["hn"] else "") + f" · [{r['kind']}] · {r['url']}")
        if top:
            L.append(f"   top post: @{top['handle']} ({top['likes']}♥ {top['reposts']}↻) {top['url']}")
    if a.discover:
        L += ["", "## Discovered via Bluesky link search (not necessarily in the candidate list)", ""]
        for r in [r for r in out["discover"]["rows"] if r["neuro_text"]][:20]:
            L.append(f"- {r['link']} — buzz {r['buzz']} · {r['posters']} posters · e.g. {r['sample_post']} — “{r['sample_text'][:120]}”")
    open(os.path.join(od, "chatter.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
    log(f"done in {out['runtime_seconds']}s; {out['with_any_human_bsky_post']}/{len(res)} with Bluesky chatter")

if __name__ == "__main__":
    main()
