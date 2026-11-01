# Neurodynamics Digest — database pipeline ("version B")

No LLM search. Pulls candidates from free scholarly APIs, dedupes, excludes already-covered items, scores cheaply.

## Run
    cd /workspace/newsletter/pipeline
    python3 fetch_candidates.py --start 2026-10-19 --end 2026-10-25     # ~25-80 s
    python3 chatter.py --date 2026-10-25 --top 30 [--discover]          # ~2-4 min

Outputs in `out/<end>/`:
- candidates.json: top ~60 primary papers, top ~15 reviews, psychedelic trials, biorxiv-top monthly rankings
- candidates.md: human-readable version (Reviews block = "Best reviews of the week")
- reviews.json, stats.json (per-source hits, timings, errors, drop counts)
- pool.jsonl: every scored item with its score_parts. dropped.tsv: what got dropped and why
- chatter.json / chatter.md: "Buzz this week"

## Sources
PubMed, Europe PMC, OpenAlex, bioRxiv/medRxiv API (v1 only), arXiv q-bio.NC, ClinicalTrials.gov v2, and biorxiv-top (usage.json from the GitHub data branch, recomputed like notebook.py).
Each source runs in its own try/except, so one failure is logged in stats.json and the run carries on.

## Tuning: everything lives in queries.json
- groups: query, keywords (regex on title/abstract), weight, require_imaging / requires_psychedelic / also_requires_re
- current_analyses: bonus for Patrick's current-analysis groups
- venues: top_venue_bonus (tier1 1.5, tier2 0.75). This is NOT impact-factor weighting; set it to 0 to disable it.
- scoring: penalties (engineering/ML, repository deposits, stale pubdate, off-topic), group_decay, thresholds
- keyword_negations: e.g. "DMT" meaning disease-modifying therapy

Exclusions: archive items.jsonl, shortlist.jsonl, sent-log DOIs.
Privacy: never copy details of Patrick's unpublished analyses into public archive notes (brief line 19). The group names here are generic topics.

## Chatter sources (checked 30 Oct 2026)
- Bluesky public AppView (api.bsky.app searchPosts, no auth): works. URL search is exact and version-sensitive, so several URL variants are tried, plus a quoted-title search. public.api.bsky.app returns 403.
- Hacker News Algolia: works, but neuroscience papers almost never appear.
- X: use the agent's own X tool (about 1000 calls/day). There is no scraper here.
- Altmetric: API key needed since Nov 2025 (free only for approved scientometric research; Imperial may have a licence). The bookmarklet is free for manual checks.
- Crossref Event Data: sunset in Apr 2026.
- Reddit: blocked from the box; needs OAuth.
- Semantic Scholar: citations only, no altmetrics, rate-limited.
- OpenAlex: no key, so it shares $0.10/day of free budget (one run costs about $0.015). A free key needs Patrick's email.
