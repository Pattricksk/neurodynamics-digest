# Build your own weekly research newsletter and archive: the full process

> **Read this first.** This is a generic, shareable version of a process document from a working setup: a personal weekly research newsletter, written by an AI agent, published as a web page, emailed to one reader, and collected into a searchable archive website. Everything specific to the original reader (research topics, keywords, named researchers, section names, example papers, the brief itself) and every visual design choice (colours, theme, fonts, icons, layout) has been removed.
>
> Anything in `<ANGLE_BRACKETS>` is a placeholder for you to fill in. Sections marked **Decide:** are choices you need to make for your own newsletter. The mechanics (discovery, ranking, dedupe, verification, the Catch-up section, the archive, publishing, email, feedback, scheduling) are described in full, as they ran in production.
>
> It assumes an agent that has a persistent machine (a Linux box or similar) where it can run Python and git, plus web search and fetch, scheduled tasks, an email inbox (or a draft-and-approve flow), and a GitHub account. Swap in your own platform's equivalents where they differ.

---

## Contents
1. [What you are building](#1-what-you-are-building)
2. [Moving parts at a glance](#2-moving-parts-at-a-glance)
3. [File layout](#3-file-layout)
4. [The brief: your source of truth](#4-the-brief)
5. [Discovery: two methods, combined](#5-discovery-two-methods-combined)
6. [Choosing and testing your discovery methods](#6-choosing-and-testing-your-discovery-methods)
7. [Writing the issue](#7-writing-the-issue)
8. [The Catch-up section](#8-the-catch-up-section)
9. [Building the HTML](#9-building-the-html)
10. [Sending the email](#10-sending-the-email)
11. [Publishing on GitHub Pages](#11-publishing-on-github-pages)
12. [The archive: data, build, website](#12-the-archive)
13. [Graph view (optional)](#13-graph-view-optional)
14. [Shortlist and literature search (optional)](#14-shortlist-and-literature-search-optional)
15. [Cross-device sync without a server (optional)](#15-cross-device-sync-without-a-server-optional)
16. [The feedback loop](#16-the-feedback-loop)
17. [Logs: sent-log, catch-up log, provenance](#17-logs)
18. [Cost and usage](#18-cost-and-usage)
19. [Step-by-step setup](#19-step-by-step-setup)
20. [Weekly run checklist](#20-weekly-run-checklist)
21. [Appendix A: brief template](#appendix-a-brief-template)
22. [Appendix B: routine prompt template](#appendix-b-routine-prompt-template)
23. [Appendix C: query-group config template](#appendix-c-query-group-config-template)
24. [Appendix D: privacy and safety rules](#appendix-d-privacy-and-safety-rules)

---

## 1. What you are building

- **What:** a weekly, email-first newsletter for one reader (`<READER_NAME>`), covering new research in `<YOUR_FIELD>` from the past 7 days. Each item is tied to the reader's own work.
- **Audience:** `<READER_LEVEL>` (e.g. PhD-level researcher, clinician, engineer, interested non-specialist). This decides how much you explain.
- **Goal:** keep the reader on top of interesting developments, not only breakthroughs, in their core area and the wider field.
- **Schedule:** `<DAY>` at `<TIME>` `<TIMEZONE>`, covering `<WINDOW>` (e.g. Monday to Sunday). Start the scheduled run about 20–60 minutes early so discovery, writing and publishing finish on time.
- **Sender → recipient:** from your agent's inbox (`<SENDER_INBOX>`) to `<RECIPIENT_EMAIL>`. If your platform needs human approval before sending, the run prepares a draft and the reader presses Send (§10).
- **Outputs every week:**
  - a web page for the issue, the full designed version, on GitHub Pages
  - an email with a condensed body and a link to the web page
  - new rows in an archive database, which feeds a searchable archive website
  - log entries so nothing repeats
- **Optional extras:** a graph view of the archive, a shortlist and free literature search, cross-device sync of the reader's marks (stars, read, not interested), and a feedback inbox.

**Decide:**
- the newsletter's name, sign-off name and persona
- the tone (§7.4)
- the time window, the send time and the time zone

## 2. Moving parts at a glance

```
          ┌────── brief.md (source of truth) + preferences.md + sent-log.md + catchup-log.jsonl ──────┐
          │                                                                                          │
 Weekly   ▼                                                                                          │
 routine ─► Step B: database sweep (free scholarly APIs; scripted; no LLM in retrieval)              │
          Step A: targeted web pass (agent browsing; fills B's gaps)                                │
          Step C: Catch-up picks (5 older must-reads; never-repeat check)                           │
          ▼                                                                                          │
          merge + dedupe + rank + verify every item against its real source                         │
          ▼                                                                                          │
          content file ─► renderer ─► full HTML (web) + compact HTML (email) + plain text           │
          ▼                                                                                          │
          provenance.json (found_by A/B/AB)   archive/items.jsonl   catchup-log.jsonl               │
          ▼                                                                                          │
          site repo: issues/<nnn>.html + index.html + archive build ─► git push (GitHub Pages)      │
          ▼                                                                                          │
          email (draft for approval, or direct send): condensed body + link to the web issue        │
          ▼                                                                                          │
          chat note to the reader; sent-log updated once sent                                       │
          ▼                                                                                          │
 Reader ─► reads; stars / marks / "not interested" / requests on the archive site ──────────────────┘
          (marks sync to a separate branch; feedback arrives as chat messages or emails to the agent)
```

## 3. File layout

Pick one root folder on the agent's machine (`<ROOT>`, e.g. `/workspace/newsletter`) and keep this layout. Scripts should read the root from one constant or environment variable.

| Path | What it is |
|---|---|
| `<ROOT>/brief.md` | **The private brief, the source of truth** (§4, template in Appendix A). |
| `<ROOT>/preferences.md` | Append-only log of the reader's like/dislike signals (§16). |
| `<ROOT>/sent-log.md` | Every item ever sent, with link and date. Used to avoid repeats. |
| `<ROOT>/catchup-log.jsonl` | Every Catch-up paper ever shown or known to the reader (§8). |
| `<ROOT>/docs/routine-prompt.txt` | A saved copy of the scheduled routine prompt (Appendix B). |
| `<ROOT>/pipeline/` | The database sweep scripts and `queries.json`. Outputs go to `pipeline/out/<end-date>/`. |
| `<ROOT>/issue-<nnn>/build/` | Each week's build folder: `content.py` + renderer scripts. Copy from the newest previous issue. Outputs: `issue-<nnn>-full.html`, `issue-<nnn>-compact.html`, `issue-<nnn>.txt`. |
| `<ROOT>/runs/<date>/` | Per-week bookkeeping: `provenance.json`, the archive-row script and its output, and `email/` (subject, plain-text body, compact HTML). |
| `<ROOT>/archive/items.jsonl` | The archive database (append-only JSON lines). |
| `<ROOT>/archive/shortlist.jsonl` | Optional shortlist database, kept separate from the archive. |
| `<ROOT>/build/` | `build_archive_site.py`, `tag_map.json`, favicon generator. |
| `<ROOT>/site/` | Local clone of the public GitHub Pages repo. |

## 4. The brief

`brief.md` is the single source of truth for what goes in the newsletter. Every run reads the latest version. Every change the reader asks for, in chat or by email, is written into it with a dated change-log line (`- <YYYY-MM-DD> (chat|email): <what changed>`). Keep it private: it usually holds details of the reader's unpublished work.

What the brief should contain (fill in the template in Appendix A):

1. **Who and what for:** the reader's role, field and current projects. Write these concretely enough that the agent can write a specific "Why it matters for you" line for every item.
2. **Current analyses / active questions:** a short list of what the reader is working on right now. These get a ranking boost and drive the "Why it matters" text.
3. **Method/modality priority:** if the reader cares more about some methods than others (`<METHOD_PRIORITY>`), say so in order.
4. **Scope:** what's in, what's in only under conditions (e.g. "other applications only when they use method X"), and what's out (e.g. job ads, policy commentary).
5. **Core interests (highest priority),** numbered. State that named examples are examples only, so the agent goes beyond them.
6. **Secondary interests,** and anything low priority that should appear only for major work.
7. **Wider field and wildcards:** high-impact work outside the core, plus a list of researchers, labs or feeds whose output is worth watching (`<NAMED_RESEARCHERS>`).
8. **Ranking rules** (keep these, they worked well):
   - Relevance to the reader's work and study quality drive selection. Venue prestige is only a **small tie-breaker**, never a main factor.
   - Up-weight items similar to liked ones; down-weight items similar to "not interested" ones; **never re-feature a not-interested item**.
   - Don't over-narrow: keep the section structure, keep wildcards and some out-of-profile items every week, treat down-weighting as "fewer/shorter" rather than "never", require 2+ consistent signals before adding a derived rule, and let explicit instructions override derived rules.
   - **Repeats:** never repeat anything in the sent-log, the archive or the shortlist. A short ICYMI pointer to a notable slightly older item that wasn't covered is fine.
   - **Integrity:** never invent papers, authors, findings, numbers, deadlines or links. Verify every item against its real source (publisher/DOI page, PubMed/Europe PMC, preprint server). Say plainly when something couldn't be verified, and when a section has nothing new.
9. **Sections, format, tone, visual style** (§7, §9).
10. **Source-access notes:** which sites block plain fetches, which APIs work, and fallback routes. Add notes as the agent learns them.
11. **Archive rules:** the archive fields and tag vocabularies (§12).
12. **Delivery:** addresses, schedule, the approval flow.
13. **Change log.**

**Decide (how to choose your interests):** start from the reader's last 6–12 months of work. List 5–8 core interests as *questions or methods* rather than broad fields ("new ways to measure X", "models of Y applied to Z"). Put the 3–6 things they are actively analysing in "Current analyses". Then name 5–15 researchers whose work they always want to see. Expect to revise the brief after the first 2–3 issues.

## 5. Discovery: two methods, combined

The production setup ran an A/B test of two discovery methods for one week, then **combined both** into one merged issue for thoroughness. The order each week is: **B (database sweep) → A (web pass) → C (Catch-up picks) → merge/verify**.

### 5.1 Step B: database sweep (scripted, cheap, broad)

```bash
cd <ROOT>/pipeline
python3 fetch_candidates.py --start <WINDOW_START YYYY-MM-DD> --end <WINDOW_END YYYY-MM-DD>   # ~25–80 s
python3 chatter.py --date <WINDOW_END> --top 30 [--discover]                                # ~2–4 min
```

No LLM is used for retrieval, only free scholarly APIs. Run the sources in parallel (e.g. a thread pool), with each one in its own try/except, and record failures in `stats.json` so a broken source never kills the run. Send a contact email (`mailto`/`email` parameter or User-Agent) with requests where APIs offer a "polite pool"; read it from an environment variable rather than hard-coding it.

| Source | Endpoint and how to query |
|---|---|
| PubMed | NCBI E-utilities: `esearch` (term + `datetype=pdat` + `mindate`/`maxdate` for the window) then `efetch` (XML) for titles, abstracts, authors, journal, DOI, publication types. One search per query group. |
| Europe PMC | REST `search` API (`query=... AND FIRST_PDATE:[start TO end]`, `resultType=core`). Picks up some preprints and journals PubMed misses. |
| OpenAlex | `works` API with `filter=from_publication_date:...,to_publication_date:...` and a search string. Use it only for the query groups that need it: without a key it shares a small free daily budget (a full run cost about 15% of it in production). |
| bioRxiv / medRxiv | `api.biorxiv.org/details/<server>/<start>/<end>/<cursor>` lists everything posted in the window; filter by `<YOUR_PREPRINT_CATEGORIES>`. These "bulk" preprints must reach a minimum keyword score (2.0 in production) to stay in the pool. |
| arXiv | `export.arxiv.org/api/query` on `<YOUR_ARXIV_CATEGORIES>`, sorted by submission date, cut to the window. |
| ClinicalTrials.gov v2 | `/api/v2/studies` with a query term and a first-posted date range. Keep new registrations only if they match `<YOUR_TRIAL_FILTER>` (optional; only if trials matter in your field). |
| Most-read tracker (optional) | If your field has a public "most-read preprints" tracker with downloadable data, add it as a source with a fallback chain (§5.5). |

**Merge records:**
- Merge by DOI, else by normalised title (only if the title is over ~25 characters).
- Metadata preference: PubMed > Europe PMC > OpenAlex > preprint servers.

**Exclude before scoring:**
- anything already in `archive/items.jsonl`, `archive/shortlist.jsonl` or the sent-log (by DOI)
- errata, retractions and notices
- bulk preprints outside the window, or below the keyword threshold

**Score** (everything tunable in `queries.json`; template in Appendix C):
- **Query groups:** each has a search query (for the APIs), keyword regexes (for scoring) and a weight. In production weights ran from 10 (the reader's most specific current analyses) down to 1 (low-priority areas), with a weight-0 "wildcard / top venues" group used for retrieval only, and separate review-only groups. A group can require an extra condition (e.g. it must also mention a required method or entity).
- **Keyword score:** group weight × hit strength (title hit 1.0, abstract-only 0.6). Combine multiple matching groups with decaying weights [1, 0.5, 0.3, 0.2] so one paper can't stack unlimited points.
- **Method/modality bonus:** an extra bonus for the reader's preferred methods, in priority order (production used +4 / +2.5 / +1). Abstract-only matches need ≥2 mentions and are scaled by 0.6.
- **Named researchers** (author match): +5.
- **Current-analysis groups:** an extra +3 × hit for the groups that match the reader's active analyses.
- **Top venue:** tier 1 +1.5, tier 2 +0.75, a tie-break only (set to 0 to disable).
- **Most-read tracker rank** (if used): top 20 +3, top 100 +1.5.
- **Similarity to the archive:** TF-IDF cosine to past archive items × 8. This rewards the reader's established interests.
- **Preferences:** similarity to liked items × 10, to disliked items × −6 (read from `preferences.md`).
- **Penalties:** no abstract −1.5; low-value publication types (comments, editorials) −2; off-target engineering/ML regex −4; repository deposits −8; stale publication date (>60 days) −1.5; off-topic −3.
- **Acronym negations:** list acronyms that collide with other meanings in your field and exclude those senses (e.g. an abbreviation that is also a statistics term).

**Outputs** in `pipeline/out/<end-date>/`:

| File | Contents |
|---|---|
| `candidates.json` / `candidates.md` | top ~60 primary papers, top ~15 reviews, trials (if used), tracker rankings |
| `reviews.json` | the review candidates (they feed "Best reviews") |
| `pool.jsonl` | every scored item with its `score_parts`, no abstracts (for tuning) |
| `dropped.tsv` | what was dropped and why |
| `stats.json` | per-source hits, timings, errors, drop counts, preference-signal counts |
| `chatter.json` / `chatter.md` | social buzz data |

Typical production funnel for one week: ~1,400–1,950 raw hits → ~1,300–1,700 after merge → ~950–1,400 scored → 60 candidates + 15 reviews, in under a minute.

**Chatter** (`chatter.py`, optional "Buzz this week" signal):
- Bluesky: the public no-login API. `searchPosts` worked on `api.bsky.app` (the `public.api.bsky.app` search endpoint returned 403); author feeds work on `public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed`. Search several URL variants of each paper (DOI link, publisher link, preprint link) plus a quoted-title search, and exclude bot accounts.
- Hacker News: the Algolia search API.
- buzz = 3 × distinct authors + 2 × √(engagement) + HN terms. Keep a separate **in-window** buzz score as the weekly signal.
- `--discover`: also look for papers being shared that the sweep didn't find.
- Not usable for free (at the time of writing): Altmetric (key required), Crossref Event Data (retired), Reddit (OAuth needed), X (use your agent's own X tool if it has one).

The agent then reads `candidates.md` and `chatter.md`, shortlists relevant items and discards obvious noise. **The pipeline is a candidate generator, not an editor:** every claim is still checked against the abstract or full text.

### 5.2 Step A: targeted web pass (agent browsing; fills B's gaps)

The agent researches the same window by web search and browsing:
- journals, especially high-profile ones that index slowly in the databases
- preprint servers
- the named researchers' pages and feeds
- policy, regulatory and trial news (if relevant to your field)
- conference and funding sources, summer schools/training
- notable slightly older ICYMI papers
- the most-read tracker, if you use one

The aim is to find **what the database sweep missed**, not to re-read what it already found.

### 5.3 Step C: Catch-up picks

A separate look back over roughly 10 years for the 5 Catch-up papers (§8). These are not part of the A/B provenance counts.

### 5.4 Merge, dedupe, verify, provenance
- Take the union of A and B, deduped by DOI, else by title.
- Rank by relevance and study quality per the brief.
- **Verify every item against its real source.** Nothing goes in from a snippet, an email or memory alone.
- Don't label items by method in the issue; the method is recorded only internally.
- Save `runs/<date>/provenance.json` (schema in §17) with `found_by` = `"A"`, `"B"` or `"AB"` for every weekly item. Write the same value to each item's archive row. This lets you check later whether both methods are still worth their cost.

### 5.5 Source-access lessons (generic)
- **JS-only sites:** look for the data file behind the page (a JSON file in a GitHub repo, an API endpoint) before you reach for a headless browser. A robust fallback chain is: raw file URL → GitHub API contents endpoint (`?ref=<branch>`) → shallow `git clone --branch <branch>` → headless Chrome on the live page. Retry with backoff. If every route fails, say so in the issue and the chat note; never skip a mandatory source silently.
- **Publisher sites that bot-check plain fetches:** use headless Chrome.
- **Preprint PDFs rate-limited (429):** use the full-text HTML instead.
- **Funding portals that are JS-only:** load their per-call JSON data files.
- **Events:** organisers' newsletters/RSS feeds are often the most reliable source for dates.
- Record each lesson in the brief's source-access notes.

## 6. Choosing and testing your discovery methods

In production, a one-week A/B test sent two versions of the same issue:
- **B (database pipeline)** found about twice as many on-topic in-window items, much more cheaply.
- **A (web search)** caught older high-profile papers that B's date filter dropped, and slow-indexing journals.
- The first combined week: about 85% of weekly items came from B only, about 13% from A only, and a few from both. A's unique finds were press-resurfaced older papers, just-published journal papers and news items.

Recommendation: **start with B** (cheap and broad), add A as a gap-filling pass, and track `found_by` for a few weeks. If A rarely adds anything you'd miss, cut it back to a short check of the top journals and the named researchers. If B is noisy, tune `queries.json` using `pool.jsonl` and `dropped.tsv`. A possible improvement is to give B a wider look-back, or an ICYMI pass for big-venue items.

## 7. Writing the issue

### 7.1 Item format (worked well; adapt freely)
- **Header:** issue number, date and coverage window; a short themed intro tying the week together ("Hi `<READER_NAME>`, this covers …"); a key explaining the tags.
- **Tags on each item:** publication status (PREPRINT vs PEER REVIEWED), plus study type and topic tags (`<YOUR_TAG_VOCABULARY>`).
- **Main items:**
  - punchy headline
  - byline: first … last author (affiliation), venue, date
  - **what they did**, with concrete numbers (n, design, effect sizes, CIs)
  - **what they found**
  - **honest caveats** (sample size, conflicts, animal-only, preprint status, …)
  - **"Why it matters for you"**: specific to the reader's work, never generic
  - a ref row: venue, date, DOI, registration ID
- **Short items:** one paragraph for secondary picks. Mark slightly older items "ICYMI".
- **Sign-off:** a closing note inviting replies, signed with your persona's name; a disclaimer (summaries come from abstracts/full text where available; preprints aren't peer reviewed; check sources before citing).

### 7.2 Rules that apply every issue
- "Why it matters for you" on **every** paper item, in every section.
- Optional fixed sections that worked well:
  - a **dedicated section for the reader's core method**, right after the headline
  - a **weekly explainer**: one concept the reader is learning, ideally tied to a paper in the issue
  - **"Buzz this week"**, from the chatter data, only when there is real buzz
- **"Best reviews of the week" is second-to-last:** 2–5 reviews, perspectives or meta-analyses published that week. Each gets its scope, key takeaways, caveats (narrative vs systematic, the authors' own stake) and "Why it matters for you". If there are none, say so in one line.
- **"Catch-up" is always last** (§8).
- Sections are fluid: drop empty ones, and say plainly when one is quiet. A genuinely quiet week still gets a shorter edition.

### 7.3 Choose your sections
**Decide:** pick 8–15 sections. A structure that worked:

| Slot | Section | Notes |
|---|---|---|
| 1 | Headline act | the week's single most important item |
| 2 | `<CORE_METHOD_SECTION>` | everything using the reader's main method |
| 3 | `<READERS_OWN_COMMUNITY>` | the reader's own lab, centre or collaborators (optional) |
| 4–8 | `<TOPIC_SECTION_1>` … `<TOPIC_SECTION_N>` | one per core interest cluster |
| … | Weekly explainer | one concept |
| … | Critiques and nulls | failed replications, null results, critiques |
| … | Wildcards | high-impact items outside the core; the most-read pick |
| … | Datasets and tools | new open data and software |
| … | Policy / regulation | if relevant |
| … | Conferences | verified dates, locations, deadlines |
| … | Training / summer schools | |
| … | Funding radar | tuned to the reader's career stage and country |
| … | Buzz this week | optional |
| second-to-last | Best reviews of the week | |
| last | Catch-up | |

Guidance: group by what the reader *does with* the paper (methods they could reuse, findings in their area, critiques), not just by topic. Keep section names stable so the archive tabs stay meaningful.

### 7.4 Tone
**Decide** your voice (e.g. friendly and fun, written for `<READER_LEVEL>`). Whatever you choose, keep it **neutral and accurate**: no overclaiming, no oversimplifying, and explain hard concepts without dumbing down findings. Avoid gimmick voices: if the reader rejects a voice, ban it in the brief.

## 8. The Catch-up section

A fixed final section, so the reader doesn't miss the field's critical older papers.

**Selection rules**
- **Exactly 5 papers** per issue, from roughly the **last 10 years** (landmark papers first; recent years fine).
- **Occasionally (at most about one a week)** a truly foundational older paper is allowed.
- Aim for must-reads: high-impact, well-cited, or foundational methods and findings.
- **Rotate across the reader's interest areas** (`<CATCHUP_ROTATION_LIST>`, usually the core interests plus the current analyses) so coverage spreads out. Record each pick's area in the log.
- **Never repeat a paper.** Before choosing, check `catchup-log.jsonl`, `archive/items.jsonl` and `sent-log.md` by DOI and by title. Skip anything shown in any section of any issue, or logged as already known.
- Verify every paper against its real source.

**Each item** is a normal main item (tags: publication status, year, article type, interest area; title; authors · venue · year; DOI) with:
- a short summary of what it found or introduced, and "Why it mattered" (its importance to the field)
- caveats, and "Why it matters for you"
- **Since then:** one verified line on what happened next (replications, failed replications, key critiques, the standard toolbox implementation), with a link.
- **Reading level:** exactly one of "Skim the abstract", "Read the methods", "Worth a full read".
- **Code/data:** a link to public code or data the reader could reuse. Omit the row entirely if none exists.

**Monthly mechanics**
- **Themed week**, about once a month: all 5 papers tell one connected story on a single theme, ordered so each builds on the last, with a one-line theme intro.
- **Gap check**, on the first issue of each month: in the chat note, ask the reader for 2–3 papers they consider essential. Log them as `known: true` and use them to adjust the rotation.
- **Known papers:** if the reader says they already know a pick, log it with `known: true` and lean toward less obvious picks.
- **Archive shelf:** Catch-up items go into the archive with section "Catch-up" and get their own tab/filter.

**After the issue:** append one line per paper to `catchup-log.jsonl` (§17).

## 9. Building the HTML

### 9.1 Design: pick your own
**Decide:** your theme (light or dark), colour palette, fonts, masthead, whether sections get icons or colours, and any decorative elements. A few lessons that are about *function*, not taste:
- Give each section a recognisable, consistent header so the reader learns the layout.
- If you use symbols as section icons, use text symbols (forcing text presentation with U+FE0E where needed), not images or colour emoji, so they survive image blocking.
- Make the PREPRINT tag visually distinct from PEER REVIEWED.
- Ensure link colours are readable on your background.
- Add a contents list at the top that links to section anchors (`id` and `<a name>`), with a "back to contents" link per section. Anchors work in browsers, Apple Mail and Gmail web; some desktop and mobile clients ignore them.
- Add a "View in browser" link to the web copy.
- Write your design rules into the brief so every run reproduces them.

### 9.2 Email-safe constraints (keep these whatever your design)
- Table-based layout with **inline styles only**.
- Set backgrounds with both the `bgcolor` attribute and inline `background-color`, so desktop clients that strip CSS keep your theme.
- No external fonts, scripts or remote images; the email must survive image blocking.
- Max width around 680 px, readable on mobile.
- Three outputs per issue:
  - **full HTML:** the web version, published as `issues/<nnn>.html`
  - **compact HTML:** for inline email; **target <60 KB, hard limit 80 KB** (some clients clip larger messages)
  - **plain text:** the fallback, and the source of the condensed email body

### 9.3 Build scripts (one way to do it)
- `content.py` (per issue) holds all the text as data:
  - fields: `NUM, SUBJECT, TITLE, SUBTITLE, VIEW_URL, PREHEADER, OUT_COMPACT, OUT_FULL, OUT_TXT, INTRO, KEY, SECTIONS, SIGNOFF_TITLE, SIGNOFF, DISCLAIMER, IMPRINT`
  - `SECTIONS` is a list of `dict(title, sub, items)`. Item kinds:
    - `main`: `tags` [(TEXT, style)], `head`, `byline`, `body` [paras], `caveats`, `why`, `ref` [(label, url)], optional `extra` [(LABEL, text)] for additional meta rows (used for Catch-up's Since then / Reading level / Code/data)
    - `short`: `label`, `text`
    - `explainer`: `paras`
  - inline links as `[[text|url]]`; allow `<b>`/`<i>`
- `render.py`: writes full HTML, compact HTML (via `compact.py`) and plain text. It writes to the absolute `OUT_*` paths, so **change them before testing a template**, or you will overwrite a real issue.
- A style module: section → header style mapping, sign-off name, feedback addresses (keep real addresses out of any public copy).
- `check_issue.py` pre-send checks: compact size ≤80 KB, Best reviews present, Catch-up present and last, banned-voice words absent, plus any design rules you want enforced (e.g. no light backgrounds in a dark theme, no unwanted scripts or characters).
- Each week, copy the **newest** build folder to `issue-<nnn>/build/`, write a new `content.py`, render, check.

## 10. Sending the email

- **One email per issue** from `<SENDER_INBOX>` to `<RECIPIENT_EMAIL>`. Subject: `<NEWSLETTER_NAME> #<n>: <2–3 highlights>`.
- **Approval flow:** many agent platforms require explicit approval before sending email on someone's behalf. In that case the scheduled run *prepares a draft* (recipient, subject, body) and the reader presses Send. Don't assume the run can send silently. The send then happens whenever the reader approves; in production that was 2–4 hours after the scheduled time.
- **Draft bodies are often plain text or very basic HTML,** so the designed version lives on the web page. A condensed body that worked:
  1. `<NEWSLETTER_NAME> #<nnn>. <date>, covering <window>.`
  2. `Full issue with caveats and why-it-matters notes: <web link>`
  3. the intro and the week's theme paragraph
  4. each section as a numbered heading, one bullet per item: headline (authors · venue · date) `<link>`
  5. Best reviews, then the Catch-up papers
  6. a feedback line, the next-issue time, the sign-off and the disclaimer
- If your send path accepts full HTML, send the compact HTML instead (keep the plain text as the alternative part).
- **Publish before sending**, so the web link works. If publishing fails, still send, drop the link, and say so.
- **Chat note after the run:** say the issue is live and the draft is ready (or what blocked it), give the link, and add a 2–3 line summary including how many items each method found (A-only / B-only / both). Add the usage flag only if triggered (§18), and the gap-check question on the first issue of the month (§8).
- **After the send:** mark the issue SENT in the sent-log with the date and time.
- Never send to additional addresses unless the reader asks.

## 11. Publishing on GitHub Pages

- **Repo:** a public GitHub repo `<GITHUB_USER>/<REPO_NAME>`. Enable GitHub Pages from **`main`, root**. Clone it to `<ROOT>/site`.
- **Site:** `https://<GITHUB_USER>.github.io/<REPO_NAME>/`. To keep it unlisted, add `<meta name="robots" content="noindex">` to the pages and a `robots.txt` with `Disallow: /`. Remember that a public repo is still readable by anyone.
- **Structure:**
  ```
  index.html                 # issue list, newest first, inserted after a marker comment like <!-- ISSUES (newest first) -->
  issues/<nnn>.html          # full HTML of each issue
  archive/index.html         # archive search UI (plain HTML/JS)
  archive/items.json         # built from archive/items.jsonl
  archive/item/<id>.html     # per-item detail pages (citation meta tags)
  archive/shortlist.html / shortlist.json / search.html / graph.html / sync.js   # optional (§13–15)
  archive/vendor/            # vendored JS libraries (no CDN)
  favicon files, robots.txt
  docs/, tools/              # optional: your process notes and sanitised code copies
  ```
- **For each issue:** add `issues/<nnn>.html` (insert favicon links before `</head>`), add an `<li>` to `index.html`, rerun the archive build, then commit `issues/`, `index.html` and `archive/` (including `archive/item/`) and push.
- **Git rules:**
  - Always `git pull --rebase` before committing; if the push is rejected, pull with rebase again and retry.
  - **Never force-push.**
  - If you use the sync branch (§15), **automation must never touch it**.
- **Auth:** use a credential with push rights kept outside the repo (e.g. the `gh` CLI login on the agent's machine). Never commit tokens.

## 12. The archive

### 12.1 Rows: `archive/items.jsonl`
Append-only, one JSON object per item. Dedupe by DOI, else title (and skip existing issue+title pairs). Never rewrite rows; the one exception is adding the reader's notes to an existing row's `notes` field. If you ever have to fix a field in bulk, back up the file first and record the fix in the brief.

| Field | Meaning |
|---|---|
| `issue`, `issue_date` | e.g. "003", "2026-01-18" ("" for items the reader promoted directly) |
| `section` | the issue's section title, exactly as written (tabs key on it) |
| `title`, `authors`, `venue`, `pub_date`, `doi`, `url` | bibliographic data |
| `item_type` | paper / preprint / review / dataset / tool / conference / funding / policy / news / training |
| `<PRIMARY_METHOD_FIELD>` | e.g. `modality` or `method`: the main method family from your controlled vocabulary |
| `<ENTITY_TAGS>`, `populations`, `methods`, `topics` | lists of tags. `<ENTITY_TAGS>` is your field's key entity (e.g. compounds, organisms, materials, datasets, models) |
| `summary` | 1–2 sentences |
| `caveats` | short |
| `verified` | true/false |
| `stage` | **optional**, one controlled field for study stage (e.g. `<STAGE_VALUES>`), empty for non-study items. Never mix publication status into it |
| `pub_status` | publication status, its own field: "Peer reviewed" / "Preprint" / "Reviewed preprint" / "Registered" / empty for non-papers |
| `found_by` | "A" / "B" / "AB" (weekly items) |
| `catchup`, `interest_area`, `since_then`, `reading_level`, `code_data` | Catch-up rows only (these have no `found_by`) |
| optional `source`, `notes`, `relevance` (1–3) | provenance of reader-sent items, reader notes, a manual relevance override |

Lesson learned: keep each concept in its own field. Production once stored publication status in the stage field and had to migrate it.

Write the rows with a small per-issue script that imports that week's `content.py`, strips links/HTML to plain text, merges a per-item metadata table (type, tags, found_by, etc.), saves the rows to `runs/<date>/records.json`, and appends the new ones.

### 12.2 Build: `build/build_archive_site.py` (safe to rerun)
- Reads `items.jsonl`, drops test rows and duplicates, and writes `site/archive/items.json`. Builds the shortlist (if any) separately.
- Adds `issue_url` (`../issues/<nnn>.html#sNN`, using section anchors parsed from the published issue), `id`, a derived `relevance` (from section priority + core-topic hits; a stored value wins).
- Adds `similar` (top 6 by plain-Python TF-IDF cosine over title, summary, notes and up-weighted tags) and `similar_w` (the scores).
- Normalises tags into chip fields via `tag_map.json` (synonym merges, display labels, controlled method families, a stage derivation, a `pub_status` derivation from `item_type` and venue: preprint server = Preprint, trial registry = Registered, other papers/reviews = Peer reviewed; a stored value wins).
  - **Merge tag synonyms only when certain** (same entity under another name or code). If unsure, don't merge; unknown names pass through as their own label.
- Writes `site/archive/item/<id>.html` detail pages with Highwire `citation_*` meta tags (so reference managers like Zotero can import them), and hidden COinS spans on cards.

### 12.3 Archive website (`archive/index.html`, plain HTML/JS, no build step)
- **Browsing:**
  - tabs by section (a `SECTIONS` list of `[title, label, …]` in the page; a tab appears once that section has items; include Best reviews and Catch-up)
  - always-visible chip rows for your key facets (e.g. entity, method, population, stage, publication status), OR within a row and AND across rows
  - a small publication-status badge on each card
  - collapsible filters (method, population, month, venue, issue, relevance)
  - keyword search (all words must match), clickable tag chips, "More like this"
- **Marks:** star, To read / Read, and views for each. "Not interested" quarantines an item, with undo.
- **Preferences:**
  - "More like this" clicks count as positive signals.
  - A **"Send my preferences"** button opens a `mailto:` to the agent's inbox with subject "Digest preferences update", grouped STARRED / MORE LIKE THIS / NOT INTERESTED / READ, one line per item. Past ~1,800 characters it falls back to copy-to-clipboard.
  - An "Export preferences (JSON)" button.
- **Storage:** all state lives in one localStorage key, e.g. `<PREFIX>-archive`.
- Header art/animation: your choice.

## 13. Graph view (optional)
`archive/graph.html` is an Obsidian-style force graph built on vendored d3-force (no CDN), fully client-side.
- **Nodes:** archive papers. Non-research items are hidden by default.
- **Links:** papers sharing a tag group (entity, method family, …). Optional extra link types: topic tags, authors, text similarity (`similar_w`). Link weight = the number of shared attributes; draw only each paper's strongest N links (default 4, range 1–12), above a "min shared" threshold.
- **Modes:** paper–paper links; tags as their own nodes with papers linked to them; or both.
- **Colour:** by one facet of your choice. Split multi-valued nodes like a pie.
- **Filters:** the same chips as the archive; keyword highlight; filter by the reader's marks; an optional dashed shortlist layer (never written into archive data); quarantined items hidden by default.
- **Interaction:** hover shows the title; click opens a side panel with details, marks and linked papers; zoom, fit and re-layout controls; labels auto/all/off.
- **Settings:** in their own localStorage key, not synced.

## 14. Shortlist and literature search (optional)
- **Archive** = items that appeared in an issue, plus items the reader explicitly promoted. **Shortlist** = candidates the reader flagged but hasn't promoted. Keep them fully separate: shortlist items never appear in archive results, tabs, filters or "More like this".
- `archive/shortlist.jsonl` has the archive fields plus `added_date`, `seed`, `notes` and `status`. It builds to `shortlist.json`, shown on `shortlist.html` with its own search, marks, detail pages and "Add to archive" / "Remove" buttons (each opens a pre-filled request email to the agent).
- Items the reader sends in chat go to the shortlist unless they say "archive".
- **Literature search** (`search.html`, free, client-side, costs the agent nothing):
  - opened from "Search for more like this" on any card (`search.html?seed=<doi or id>`), with the query prefilled from the seed's tags and title, and editable
  - filters kept in the URL: year range, type, open access, venue, min citations, include/exclude words, sort, count
  - **"Similar to this paper"** uses Semantic Scholar recommendations, falling back to keyword search
  - **"Keyword search"** uses OpenAlex (with your `mailto`) → Europe PMC → Semantic Scholar; OpenAlex `related_works` is a noisy last resort
  - result cards show title, authors, venue, year, citations, OA/PDF, a TL;DR or first sentence, the collapsible abstract, "already in archive/shortlist" badges, and a **"Send to agent"** button (a pre-filled request email)

## 15. Cross-device sync without a server (optional)
A small `sync.js` on the archive pages syncs the reader's marks between browsers and devices.
- **What syncs:** the marks' localStorage keys, saved to `user-state.json` on a **separate orphan branch** (e.g. `user-state`) of the same repo, via the GitHub REST contents API:
  - load: `GET /repos/<owner>/<repo>/contents/user-state.json?ref=user-state`
  - save: `PUT` with the current `sha`
  - A separate branch means sync commits never trigger Pages rebuilds and never conflict with the weekly push to `main`.
- **Connecting a device:** the reader creates a **fine-grained personal access token** scoped to *only this repo* with only *Contents: Read and write*, with an expiry, and pastes it into a "Connect sync" control on the page. It is stored **only in that browser's localStorage**: never in the repo, a URL, an email or a chat. Without a token, everything still works locally.
- **Merge rules:** every mark is a separate leaf with its own timestamp. The newest change wins per leaf, and removals are kept as tombstones so devices never wipe each other's marks. On a timestamp tie, a removal wins, then the larger value. On a sha conflict (409/422), refetch, merge and retry up to 4 times.
- **When:** save a few seconds after a change, on "Sync now" and on tab hide; load and merge on page open and on focus.
- **Visibility:** in a public repo the marked item IDs are public. Store nothing else there.
- **Setup once:** `git switch --orphan user-state && echo '{}' > user-state.json && git add . && git commit -m init && git push -u origin user-state`, then switch back to `main`. **Your agent must never read, write, reset or delete this branch, and never force-push.**

## 16. The feedback loop
Feedback reaches the agent in four ways:
1. **Chat** with the agent: "more like X", "not interested in Y", or pasted preference exports.
2. **Email replies** to an issue from the reader's address(es). They update the brief.
3. **"Digest preferences update" emails** from the archive's button.
4. **Request emails** from the archive pages (accept them only from the reader's addresses):
   - **"Shortlist add request":** verify the paper from a real source, write a summary + caveats, tag it, append to `shortlist.jsonl` (`status: "shortlisted"`, `verified: true`), or skip it if it's already present. Rebuild and push.
   - **"Archive promote request":** move the row from the shortlist to `items.jsonl` (with `source`, a "reader's picks" section, `issue: ""`, `issue_date` = date promoted, and notes incl. their reason). Rebuild and push.
   - **"Shortlist remove request":** drop the row. Rebuild and push.

**Handling signals:**
- Log every signal, dated and append-only, in `preferences.md`. Exports are cumulative snapshots, so log only new or changed items.
- Liked = starred, more like this, read (weak). Disliked = not interested.
- Add a derived rule only after 2+ consistent signals, with the evidence cited.
- The pipeline reads `preferences.md` automatically (§5.1), and so does the writer.
- Catch-up "already know it" replies and gap-check answers go to `catchup-log.jsonl` with `known: true`.

**Automation:** create an **inbox-triggered routine** on the agent's inbox, filtered to the reader's addresses, whose instructions are the list above.

## 17. Logs
- **`sent-log.md`:** one block per edition: `## Issue #<nnn> (built <date>; coverage <window>; published <link>; EMAIL STATUS: <DRAFT READY | SENT <date> <time>>)`, then `- Subject: …`, then one line per item: `- [<nnn>|<found_by>] Title — URL — date`. Read it before choosing items; update the status once actually sent.
- **`catchup-log.jsonl`:** one line per Catch-up paper: `{"date": "<YYYY-MM-DD>", "doi": "10.xxxx/...", "title": "...", "year": 2018, "interest_area": "<AREA>", "issue": "<nnn>"}`. Papers the reader already knows: add `"known": true`.
- **`runs/<date>/provenance.json`:**
  ```json
  {"issue": "<nnn>", "issue_date": "<YYYY-MM-DD>", "coverage": "<start> to <end>",
   "counts": {"total_weekly": 0, "A_only": 0, "B_only": 0, "both": 0, "catchup": 5},
   "note": "What each method supplied; notable single-method finds; items surfaced but excluded and why; chatter summary.",
   "items": [{"section": "...", "title": "...", "doi": "...", "url": "...", "found_by": "B"}]}
  ```
  `items` holds weekly items only; Catch-up papers are counted but have no `found_by`.
- **Special editions** (optional): occasional on-request editions in a different style, e.g. a deep catch-up on one interest area.

## 18. Cost and usage
- **Database sweep:** nearly free in API terms (free APIs; OpenAlex keyless budget is small, so a free key helps). Its agent cost is mostly reading 40–60 candidates and writing.
- **Web pass:** costs more per useful item (many searches and fetches, and dead ends).
- **Catch-up:** adds a search, verification and a "Since then" lookup for 5 papers a week.
- **Writing and building** is usually the largest share.
- **Archive site, search, graph and sync:** cost the agent nothing (client-side; GitHub Pages is free).
- **Usage flag:** record the usage share of the first full run as a baseline (production: about 4% of a 30-day allowance for one weekly run). After each run, check usage, and **flag it in the chat note only if a run uses roughly double the baseline or more**; otherwise say nothing.
- If you need to cut cost: shrink the web pass first, then trim sections, then reduce Catch-up to 3 papers.

## 19. Step-by-step setup

What you need: an agent with a persistent Linux machine (Python 3.10+, git, headless Chrome for JS-only sites), web search/fetch, scheduled tasks, an email inbox it can send or draft from, an inbox-triggered task for feedback, and a GitHub account.

1. **Brief.** Fill in Appendix A with the reader → `<ROOT>/brief.md`. Create `preferences.md` (sections: Liked, Not interested, Derived rules), an empty `sent-log.md` and an empty `catchup-log.jsonl`.
2. **Layout.** Create `<ROOT>/{pipeline,build,archive,docs,runs}` and an `issue-template/build/` folder.
3. **Pipeline.** Write or adapt `fetch_candidates.py` (sources in §5.1), `chatter.py` and `queries.json` (Appendix C). Set the contact email via an environment variable.
4. **Issue build.** Write `content_template.py`, `render.py`, `compact.py`, a style module and `check_issue.py` (§9.3) with your own design.
5. **Site repo.** Create a public repo, enable Pages (main, root), add `index.html` (with the issue-list marker), `robots.txt`, `noindex` tags, the archive pages, and favicons. Clone it to `<ROOT>/site`.
6. **Archive.** Start with empty `items.jsonl` (and `shortlist.jsonl`); write `build_archive_site.py` and `tag_map.json` (§12.2); run it once.
7. **Sync (optional).** Create the orphan branch (§15), and have the reader connect each device with a fine-grained token in the browser only.
8. **Test.** Run the pipeline for last week and check that `stats.json` shows no failures. Fill a test `content.py` (with test output paths), render, and run `check_issue.py`.
9. **Schedule.** Create the weekly routine with the prompt in Appendix B, starting 20–60 min before the send time.
10. **Feedback routine.** Create the inbox-triggered routine (§16).
11. **First run.** Watch it end to end: sweep → web pass → Catch-up → merge/verify → build → provenance → archive + catchup-log → publish → email draft → chat note → sent-log after send. Then record the usage baseline.
12. **Iterate.** After 2–3 issues, revisit the brief, the query weights and the section list with the reader.

## 20. Weekly run checklist
- [ ] Read the latest `brief.md`, `preferences.md`, `sent-log.md` and `catchup-log.jsonl`.
- [ ] Run the database sweep and chatter for the window; check `stats.json` for failures.
- [ ] Do the web pass, including any mandatory sources.
- [ ] Pick 5 Catch-up papers: rotation (or monthly theme), never-repeat check against all three logs, verify each, add Since then / reading level / code-data.
- [ ] Merge, dedupe (DOI, else title), rank, and **verify every item**.
- [ ] Write `content.py` from the newest build: Best reviews second-to-last, Catch-up last, "Why it matters for you" on every paper, your voice.
- [ ] Render full + compact + text; run `check_issue.py` (compact <80 KB).
- [ ] Save `provenance.json` with `found_by`.
- [ ] Append archive rows (found_by on weekly items; Catch-up fields on Catch-up rows; stage and pub_status separate) and 5 `catchup-log.jsonl` lines.
- [ ] In `site/`: `git pull --rebase`, add the issue page, update `index.html`, rebuild the archive, commit, push `main`. No force-push; never touch the sync branch.
- [ ] Prepare the email (draft for approval, or send): condensed body + web link.
- [ ] Write the sent-log block; mark it SENT after the actual send.
- [ ] Check usage; flag only if ~2× baseline.
- [ ] Chat note: status, link, per-method counts; gap check on the first issue of the month.

---

## Appendix A: brief template

```markdown
# <NEWSLETTER_NAME>: brief (source of truth; last updated <DATE>)

## Reader
- <READER_NAME>, <ROLE> in <FIELD>, at career stage <STAGE> in <COUNTRY>.
- Works on: <ONE_PARAGRAPH_DESCRIPTION>. (Private: never put unpublished details in public files.)

## Current analyses (boost these; use them in "Why it matters for you")
- <ANALYSIS_1>
- <ANALYSIS_2>
- <ANALYSIS_3>

## Method priority
<METHOD_1> first, <METHOD_2> second, others after.

## Scope
- In: <IN_SCOPE>
- Only when: <CONDITIONAL_SCOPE>
- Out: <OUT_OF_SCOPE>

## Core interests (highest priority; examples are examples only, go beyond them)
1. <CORE_INTEREST_1>
2. <CORE_INTEREST_2>
3. <CORE_INTEREST_3>

## Secondary interests
- <SECONDARY_1>
- <LOW_PRIORITY_ONLY_IF_MAJOR>

## Wider field and wildcards
- High-impact work in <WIDER_FIELD>, even if off-topic.
- Researchers/feeds to watch: <NAMED_RESEARCHERS>
- Mandatory sources: <MANDATORY_SOURCES>

## Ranking rules
- Relevance to the reader's work and study quality first; venue is only a small tie-breaker.
- Up-weight liked, down-weight not-interested; never re-feature a not-interested item.
- Don't over-narrow (keep sections and wildcards; 2+ signals before a derived rule; explicit instructions win).
- Never repeat anything in sent-log, archive or shortlist (ICYMI pointers allowed).
- Never invent anything; verify every item against its real source.

## Sections (in order)
<SECTION_LIST> ... Best reviews of the week (second-to-last); Catch-up (last).

## Catch-up
- 5 papers, roughly the last 10 years, ≤1 foundational older paper a week, rotating over: <CATCHUP_ROTATION_LIST>.
- Never repeat (check catchup-log.jsonl, archive/items.jsonl, sent-log.md). Since then / reading level / code-data on each.
- Themed week about monthly; gap check on the first issue of each month; known papers logged with known: true.

## Format and tone
- Item format: headline, byline, what they did (numbers), what they found, caveats, why it matters for you, refs.
- Voice: <TONE>. Never: <BANNED_VOICES>.

## Visual style
- <YOUR_DESIGN_RULES> (theme, palette, fonts, section header style, icons yes/no)

## Delivery
- <DAY> <TIME> <TIMEZONE>, window <WINDOW>, from <SENDER_INBOX> to <RECIPIENT_EMAIL>, via <SEND_OR_DRAFT_FLOW>.
- Web copy: https://<GITHUB_USER>.github.io/<REPO_NAME>/issues/<nnn>.html

## Archive rules
- Fields as in the process doc; tag vocabularies: <ENTITY_TAG_VOCAB>, <METHOD_VOCAB>, <STAGE_VALUES>.

## Source-access notes
- <SITE>: <WHAT_WORKS>

## Usage
- Baseline: <BASELINE_PERCENT> of <PERIOD>. Flag only if a run uses ~2× or more.

## Change log
- <YYYY-MM-DD> (chat): <change>
```

## Appendix B: routine prompt template

````text
Write and send <READER_NAME>'s weekly research newsletter so it lands by <TIME> <TIMEZONE> on <DAY>. Use the most thorough approach: discovery uses BOTH methods (A: web search, B: database pipeline), merged into ONE issue.

1. Read <ROOT>/brief.md (the source of truth for interests, priorities, sections incl. "Best reviews of the week" second-to-last and the FINAL "Catch-up" section, the "Why it matters for you" rule, tone, format, visual style, source-access notes, archive rules). It changes over time, so always follow the latest version. Also read <ROOT>/sent-log.md and <ROOT>/catchup-log.jsonl so nothing repeats. Copy the newest issue build folder as the template.

2. DATABASE SWEEP (B): cd <ROOT>/pipeline && python3 fetch_candidates.py --start <WINDOW_START> --end <WINDOW_END>, then python3 chatter.py --date <WINDOW_END> --top 30. Read out/<WINDOW_END>/candidates.md and chatter.md (use in-window counts as the buzz signal). Shortlist relevant items; ignore obvious noise.

3. WEB PASS (A): research the same window: journals (especially slow-indexing high-profile ones), preprint servers, researchers named in the brief, policy/trial news, conference and funding sources, training, notable slightly older ICYMI papers, plus any mandatory sources in the brief (use their fallback chains). Aim to find what the sweep missed.

3b. CATCH-UP: pick exactly 5 key papers from roughly the last 10 years per the brief (rotation or monthly theme; at most one foundational older paper); check catchup-log.jsonl, archive/items.jsonl and sent-log.md by DOI and title so nothing repeats; verify each; add Since then, reading level and code/data.

4. MERGE into one issue: union, deduped by DOI else title, ranked by relevance and study quality (venue only a small tie-break). Verify every item against its real source; never invent anything. Write to the brief's format and voice, "Why it matters for you" on every paper, Best reviews second-to-last, Catch-up last. Build full HTML, a compact email HTML under 80 KB, and plain text. Don't label items by method.

5. PROVENANCE: save <ROOT>/runs/<date>/provenance.json with found_by "A", "B" or "AB" per weekly item, counts, and a note on notable single-method finds.

6. ARCHIVE: append one JSON object per item to <ROOT>/archive/items.jsonl (dedupe by DOI else title; append only) with the brief's fields and found_by (Catch-up rows: catchup true + extras). Append one line per Catch-up paper to <ROOT>/catchup-log.jsonl.

7. PUBLISH before sending: in <ROOT>/site, git pull --rebase; add issues/<nnn>.html; update index.html; rerun the archive build; commit and push to main (pull --rebase and retry if rejected). Never force-push; never touch the sync branch. If publishing fails, still send without the link and say so.

8. EMAIL: one email from <SENDER_INBOX> to <RECIPIENT_EMAIL>, subject "<NEWSLETTER_NAME> #<n>: <highlights>". If sending needs approval, prepare the draft (condensed plain-text body linking the web issue).

9. LOG: write the issue block to <ROOT>/sent-log.md; mark it SENT once actually sent.

Then post a short chat note: live/blocked, the link, a 2–3 line summary with per-method counts. Check usage and mention it only if this run used roughly double the baseline or more. On the first issue of the month, ask the reader for 2–3 essential papers for Catch-up. If the week is quiet, still send a shorter edition.
````

## Appendix C: query-group config template

```json
{
  "_note": "One entry per interest cluster. 'query' is sent to the APIs; 'keywords' are regexes used for scoring; 'weight' sets priority.",
  "groups": {
    "<current_analysis_1>": {"query": "<API search string>", "keywords": ["<regex>", "<regex>"], "weight": 10, "current_analysis": true},
    "<core_interest_1>":    {"query": "<API search string>", "keywords": ["<regex>"], "weight": 8, "requires": "<optional regex that must also match>"},
    "<secondary_1>":        {"query": "<API search string>", "keywords": ["<regex>"], "weight": 4},
    "<low_priority>":       {"query": "<API search string>", "keywords": ["<regex>"], "weight": 1},
    "wildcard_top_venues":  {"query": "<top-venue filter>", "keywords": [], "weight": 0, "openalex": true},
    "reviews_core":         {"query": "<core terms> AND review[pt]", "keywords": ["<regex>"], "weight": 6, "reviews_only": true}
  },
  "method_bonus": {"<METHOD_1>": 4, "<METHOD_2>": 2.5, "<OTHER>": 1},
  "named_researchers": ["<Surname Initials>", "..."],
  "named_researcher_bonus": 5,
  "current_analysis_bonus": 3,
  "venue_tiers": {"tier1": ["<venue>"], "tier2": ["<venue>"], "bonus": [1.5, 0.75]},
  "preprint_categories": {"biorxiv": ["<category>"], "medrxiv": ["<category>"], "arxiv": ["<category>"]},
  "min_keyword_score_bulk": 2.0,
  "similarity_weights": {"archive": 8, "liked": 10, "disliked": -6},
  "penalties": {"no_abstract": -1.5, "low_value_type": -2, "off_target_regex": -4, "repository_deposit": -8, "stale_days_60": -1.5, "off_topic": -3},
  "acronym_negations": {"<ACRONYM>": ["<other meaning to ignore>"]}
}
```

## Appendix D: privacy and safety rules
- Keep the brief, real addresses and the reader's unpublished project details **private**. Any public copy uses placeholders.
- **Never put tokens or passwords in the repo, URLs, emails or chat.** Sync tokens live only in the reader's browser.
- Never force-push; automation never touches the sync branch.
- Never invent sources, numbers or links; verify everything.
- Only send to addresses the reader has approved; respect the platform's approval flow.
- A public GitHub Pages site is readable by anyone, even with `noindex`.
