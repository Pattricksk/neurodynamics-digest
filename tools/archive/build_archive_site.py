#!/usr/bin/env python3
"""Convert archive/items.jsonl -> site/archive/items.json (the archive) and
archive/shortlist.jsonl -> site/archive/shortlist.json (Patrick's shortlist, kept SEPARATE:
shortlist items never enter items.json, tabs, filters, More-like-this or search badges).
Safe to rerun: outputs are fully regenerated each time. TEST-000 rows are excluded.
Optional fields: source ('newsletter' | 'sent-by-patrick'), notes (str); shortlist rows add
added_date, seed, notes, status. sent-by-patrick rows go under section "Patrick's picks"."""
import json, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "archive/items.jsonl"
SL_SRC = ROOT / "archive/shortlist.jsonl"
SL_OUT = ROOT / "site/archive/shortlist.json"
PICKS = "Patrick's picks"
OUT = ROOT / "site/archive/items.json"
ISSUES = ROOT / "site/issues"

def anchors(issue):
    """Map section title -> anchor id by reading the published issue page."""
    p = ISSUES / f"{issue}.html"
    if not p.exists(): return {}
    h = p.read_text(encoding="utf-8"); m = {}
    for a in re.finditer(r'id="(s\d\d)"', h):
        t = re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", h[a.end():a.end()+1500]))
        t = re.search(r"\d\d\s*&nbsp;\s*(.+?)\s+SEC\.", t)
        if t: m[t.group(1).strip()] = a.group(1)
    return m

# Relevance to Patrick's PhD (3 high, 2 medium, 1 low). A stored 'relevance' value wins.
HIGH = {"The headline act", "EEG", "Your own corner", "Psychedelic neuroimaging", "Complexity and dynamics", "Weekly explainer", PICKS}
MED = {"Addiction", "Brain–body coupling", "Preclinical", "Critiques and nulls", "Datasets and tools"}
PSY = re.compile(r"psilocybin|lsd|dmt|mebufotenin|ketamine|mdma|psychedelic|ayahuasca|mescaline|5-meo|ibogaine", re.I)
def relevance(r):
    if r.get("relevance") in (1, 2, 3): return r["relevance"]
    sec = r.get("section"); score = 3 if sec in HIGH else 2 if sec in MED else 1
    blob = " ".join([r.get("modality") or ""] + (r.get("methods") or []) + (r.get("topics") or []))
    if score < 3 and ("EEG" in blob or "entropy" in blob.lower() or "complexity" in blob.lower()): score += 1
    if score < 3 and PSY.search(" ".join(r.get("drugs") or []) + " " + r.get("title", "")): score += 1
    return score

def load(path):
    if not path.exists(): return []
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
rows, seen, cache = [], set(), {}
for r in load(SRC):
    if str(r.get("issue", "")).upper().startswith("TEST"): continue
    key = (r.get("issue"), r.get("title"))
    if key in seen: continue
    seen.add(key)
    r.setdefault("source", "newsletter"); r.setdefault("notes", "")
    if r["source"] == "sent-by-patrick": r["section"] = PICKS
    iss = r.get("issue")
    if r["source"] == "newsletter" and iss:
        ab = r.get("ab_version")  # A/B-tested issues publish as {iss}a.html / {iss}b.html
        page = iss + ("a" if ab == "A" else "b") if ab else iss
        if page not in cache: cache[page] = anchors(page)
        a = cache[page].get(r.get("section"), "")
        r["issue_url"] = f"../issues/{page}.html" + (f"#{a}" if a else "")
    r["relevance"] = relevance(r)
    r["id"] = f"{iss or 'chat'}-{len(rows):04d}"
    rows.append(r)
# ---- Shortlist (separate file, separate output; never merged into rows) ----
sl_rows, sl_seen = [], set()
for r in load(SL_SRC):
    k = (r.get("doi") or r.get("title") or "").lower()
    if k in sl_seen: continue
    sl_seen.add(k)
    r.setdefault("notes", ""); r.setdefault("status", "shortlisted"); r["source"] = "shortlist"; r["section"] = "Shortlist"
    r["relevance"] = r.get("relevance") if r.get("relevance") in (1, 2, 3) else relevance(r)
    r["id"] = f"sl-{len(sl_rows):04d}"
    sl_rows.append(r)
# ---- Normalised chip fields (rules in build/tag_map.json) ----
TM = json.loads((ROOT / "build/tag_map.json").read_text(encoding="utf-8"))
DRUG = {n.lower(): lab for lab, names in TM["drug_groups"].items() for n in names}
NONHAL = {n.lower() for n in TM["non_hal"]}
def rx(lst): return [re.compile(x) for x in lst]
MODRX = {k: rx(v) for k, v in TM["modality_map"].items()}
METRX = {k: rx(v) for k, v in TM.get("method_map", {}).items() if not k.startswith("_")}
DISRX = {k: rx(v) for k, v in TM["disorder_map"].items() if not k.startswith("_")}
ST = TM["stage"]; PRE, CLIN = rx(ST["preclinical_patterns"]), rx(ST["clinical_patterns"])
def hit(pats, t): return any(p.search(t) for p in pats)
def uniq(x): return list(dict.fromkeys(x))
def drug_label(d):
    k = d.strip().lower()
    if k in NONHAL: return TM["non_hal_label"]
    if k in DRUG: return DRUG[k]
    return d[:1].upper() + d[1:]
for r in rows + sl_rows:
    r["drug_groups"] = uniq(drug_label(d) for d in r.get("drugs") or [])
    r["drug_labels"] = [drug_label(d) for d in r.get("drugs") or []]
    r["drug_display"] = []
    for d in r.get("drugs") or []:
        lab = drug_label(d); core = re.sub(r"\s*\(.*?\)", "", d).strip() or d
        r["drug_display"].append(lab if core.lower() in lab.lower() else f"{lab} ({core})")
    mt = " | ".join([r.get("modality") or ""] + (r.get("methods") or []) + (r.get("topics") or [])).lower()
    r["modality_groups"] = [m for m in TM["modality_order"] if hit(MODRX[m], mt)]
    pt = " | ".join((r.get("populations") or []) + (r.get("topics") or [])).lower()
    r["disorders"] = [k for k, v in DISRX.items() if hit(v, pt)]
    # Coarse method families (graph view edges); rules in tag_map.json "method_map".
    mtx = " | ".join((r.get("methods") or []) + (r.get("topics") or [])).lower()
    r["method_groups"] = [k for k, v in METRX.items() if hit(v, mtx)]
    pops = " | ".join(r.get("populations") or []).lower()
    st = ""
    if r.get("item_type") in ST["study_types"]:
        if r.get("modality") == "preclinical" or hit(PRE, pops): st = "Pre-clinical"
        elif hit(CLIN, pops) or any(m in ST["human_modalities"] for m in r["modality_groups"]): st = "Clinical"
    if not r.get("stage"): r["stage"] = st  # a stage stored in items.jsonl wins
    for pre, ov in TM["overrides"].items():
        if not pre.startswith("_") and (r.get("title") or "").startswith(pre): r.update(ov)

# NOTE: this script only writes site/archive/items.json, shortlist.json and item/*.html.
# It must NEVER read, write or delete site/data/user-state.json (Patrick's synced marks; user-owned).
# "More like this": TF-IDF cosine similarity in plain Python (tags weighted up).
import math, collections
STOP = set("a an the and or of in on for to with by from at as is are was were be this that these those its it into vs via than not no".split())
def toks(t): return [w for w in re.findall(r"[a-z0-9][a-z0-9\-]+", (t or "").lower()) if w not in STOP and len(w) > 2]
def doc(r):
    c = collections.Counter()
    for f, w in (("title", 2), ("summary", 1), ("notes", 1)):
        for t in toks(r.get(f)): c[t] += w
    for f in ("topics", "methods", "drugs", "populations"):
        for v in r.get(f) or []:
            c["tag:" + v.lower()] += 3
            for t in toks(v): c[t] += 1
    m = r.get("modality")
    if m and m != "none": c["mod:" + m.lower()] += 2
    return c
docs = [doc(r) for r in rows]
df = collections.Counter(t for d in docs for t in d)
N = len(docs)
vecs = []
for d in docs:
    v = {t: (1 + math.log(n)) * math.log((1 + N) / (1 + df[t])) for t, n in d.items()}
    norm = math.sqrt(sum(x * x for x in v.values())) or 1
    vecs.append({t: x / norm for t, x in v.items()})
for i, r in enumerate(rows):
    sims = []
    for j, v in enumerate(vecs):
        if i == j: continue
        s_ = sum(x * v.get(t, 0) for t, x in vecs[i].items())
        if s_ > 0.05: sims.append((s_, rows[j]["id"]))
    top = sorted(sims, reverse=True)[:6]
    r["similar"] = [k for _, k in top]
    r["similar_w"] = [round(x, 3) for x, _ in top]  # cosine scores, parallel to similar (graph view)

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"wrote {len(rows)} items -> {OUT}")

# ---- Zotero support: per-item pages with Highwire Press meta tags (archive/item/<id>.html) ----
import html as H
ZOT_ALWAYS = {"paper", "preprint"}
ZOT_IF_DOI = {"dataset", "tool", "news"}
def clean_venue(v): return re.sub(r"\s*\((preprint|journal|paper)\)\s*$", "", v or "", flags=re.I).strip()
ITEMDIR = OUT.parent / "item"; ITEMDIR.mkdir(exist_ok=True)
for old in ITEMDIR.glob("*.html"): old.unlink()
FAV = ('<link rel="icon" href="../../favicon.svg" type="image/svg+xml"><link rel="icon" href="../../favicon-32.png" sizes="32x32" type="image/png">'
       '<link rel="icon" href="../../favicon-16.png" sizes="16x16" type="image/png"><link rel="apple-touch-icon" href="../../apple-touch-icon.png">')
CSS = ("body{margin:0;background:#11161b;color:#e6e9ec;font-family:Arial,Helvetica,sans-serif;line-height:1.5}main{max-width:760px;margin:0 auto;padding:28px 18px 60px}"
       "a{color:#a9c7e0}.m{font-family:Consolas,Menlo,monospace;color:#9aa7b2;font-size:12px}h1{font-size:24px;line-height:1.25;margin:10px 0 6px}"
       ".au{color:#9aa7b2;font-size:14px}.cav{color:#9aa7b2;font-size:14px;border-left:2px solid #5f7180;padding-left:10px}.cav b{color:#e0453b;font-family:Consolas,monospace;font-size:11px}"
       ".tags span{display:inline-block;border:1px solid #2a333c;background:#171e24;color:#9aa7b2;font-size:12px;padding:2px 7px;margin:0 4px 4px 0}"
       ".note{background:#1f2a1f;border-left:2px solid #a6dc8f;padding:6px 10px;font-size:14px}.z{background:#171e24;border:1px solid #2a333c;border-left:4px solid #e0453b;padding:8px 12px;font-size:13px;margin:18px 0}")
for r in rows + sl_rows:
    r["zotero"] = r.get("item_type") in ZOT_ALWAYS or (r.get("item_type") in ZOT_IF_DOI and bool(r.get("doi")))
    r["venue_clean"] = clean_venue(r.get("venue"))
    r["detail_url"] = f"item/{r['id']}.html"
    e = lambda x: H.escape(str(x or ""), quote=True)
    meta = [f'<meta name="citation_title" content="{e(r.get("title"))}">']
    meta += [f'<meta name="citation_author" content="{e(a)}">' for a in r.get("authors") or []]
    if r["venue_clean"]: meta.append(f'<meta name="citation_journal_title" content="{e(r["venue_clean"])}">')
    if r.get("pub_date"): meta.append(f'<meta name="citation_publication_date" content="{e(r["pub_date"].replace("-", "/"))}">')
    if r.get("doi"): meta.append(f'<meta name="citation_doi" content="{e(r["doi"])}">')
    if r.get("url"): meta.append(f'<meta name="citation_abstract_html_url" content="{e(r["url"])}">')
    if not r["zotero"]: meta = []  # non-paper items: no citation metadata
    tags = [*r.get("drug_display", []), *r.get("modality_groups", []), *r.get("disorders", []), *([r["stage"]] if r.get("stage") else []),
            *(r.get("methods") or []), *(r.get("populations") or []), *["#" + t for t in r.get("topics") or []]]
    au = ", ".join(r.get("authors") or [])
    links = []
    if r.get("url"): links.append(f'<a href="{e(r["url"])}" target="_blank" rel="noopener">Open the {"paper" if r["zotero"] else "page"} →</a>')
    if r.get("issue_url"): links.append(f'<a href="../{e(r["issue_url"])}">In issue #{e(r.get("issue"))} →</a>')
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex, nofollow">
<title>{e(r.get("title"))} · Neurodynamics Digest Archive</title>
{chr(10).join(meta)}
{FAV}<style>{CSS}</style></head><body><main>
<p class="m"><a href="../{'shortlist.html' if r['source'] == 'shortlist' else ''}">← Back to the {'shortlist' if r['source'] == 'shortlist' else 'archive'}</a> · {e(r.get("section"))} · {e(r.get("item_type"))}</p>
<h1>{e(r.get("title"))}</h1>
{f'<div class="au">{e(au)}</div>' if au else ''}<div class="m">{e(r.get("venue"))}{(" · " + e(r.get("pub_date"))) if r.get("pub_date") else ""}{(" · doi:" + e(r.get("doi"))) if r.get("doi") else ""}</div>
<div class="tags" style="margin:12px 0">{"".join(f"<span>{e(t)}</span>" for t in tags)}</div>
{f'<p>{e(r.get("summary"))}</p>' if r.get("summary") else ''}{f'<div class="cav"><b>CAVEATS</b> {e(r.get("caveats"))}</div>' if r.get("caveats") else ''}
{f'<p class="note"><b>My notes:</b> {e(r.get("notes"))}</p>' if r.get("notes") else ''}
{'<div class="z">Zotero: click the Zotero button in your browser toolbar to save this item. For the PDF too, open the paper and save from there.</div>' if r["zotero"] else ''}
<p>{" · ".join(links)}</p>
</main></body></html>
"""
    (ITEMDIR / f"{r['id']}.html").write_text(page, encoding="utf-8")
OUT.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
SL_OUT.write_text(json.dumps(sl_rows, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"wrote {len(rows) + len(sl_rows)} item pages -> {ITEMDIR}; {len(sl_rows)} shortlist items -> {SL_OUT}")
