# Neurodynamics Digest: the full process

This document explains, end to end, how the **Neurodynamics Digest** is made, published, archived and improved. It aims to be complete enough that another agent (another Grok Bot account, or an agent on a different platform) could rebuild and run the whole system from this file and the code in [`tools/`](../tools/).

*Snapshot: 1 November 2026, written after Issue 002, the last A/B issue. The first combined-method issue is due Sunday 8 November 2026.*

> **Privacy conventions in this public file.** The repo is public, so email addresses appear only as placeholders: `<RECIPIENT_EMAIL>` (the recipient's main address), `<RECIPIENT_ALT_EMAIL>` (his second address, also accepted for feedback) and `<SENDER_INBOX>` (the agent's own sending inbox). The subscriber's unpublished research projects are described only in generic terms. No tokens or passwords appear anywhere. Where a detail is not known, it is marked **Unknown**.

---

## Contents
1. [What it is: purpose, audience, schedule](#1-what-it-is)
2. [Moving parts at a glance](#2-moving-parts-at-a-glance)
3. [File layout on the agent box](#3-file-layout-on-the-agent-box)
4. [The brief: interests, scope and ranking rules](#4-the-brief)
5. [Discovery: the chosen combined method](#5-discovery-the-combined-method)
6. [Why combined? The A/B history](#6-why-combined-the-ab-history)
7. [Writing the issue: format, section order, tone](#7-writing-the-issue)
8. [Visual rules and the HTML build](#8-visual-rules-and-the-html-build)
9. [Sending: draft-card approval and its limits](#9-sending)
10. [Publishing to GitHub Pages](#10-publishing-to-github-pages)
11. [The archive: items.jsonl, archive build, website](#11-the-archive)
12. [Graph view](#12-graph-view)
13. [Shortlist vs archive, and the literature search](#13-shortlist-vs-archive)
14. [Cross-device sync (sync.js, user-state branch, PAT)](#14-cross-device-sync)
15. [The feedback loop](#15-the-feedback-loop)
16. [sent-log, provenance and special editions](#16-sent-log-provenance-special-editions)
17. [Other tools (Undermind, Edison) and cost notes](#17-other-tools-and-cost)
18. [Step-by-step rebuild from scratch](#18-rebuild-from-scratch)
19. [Weekly run checklist](#19-weekly-run-checklist)
20. [Known gaps and unknowns](#20-known-gaps-and-unknowns)
21. [Appendix A: the current routine prompt (verbatim)](#appendix-a-the-current-routine-prompt-verbatim)
22. [Appendix B: what is in tools/](#appendix-b-what-is-in-tools)

---

## 1. What it is

- **What:** a weekly, email-first science newsletter for one reader, Patrick Kleine. He is a PhD researcher in psychedelic neuroimaging at Imperial College London (Centre for Psychedelic Research; Pedro Mediano's information-theory group). His work centres on EEG, with some fMRI, and includes addiction (gambling especially).
- **Audience:** a PhD-level scientist. The issue should be friendly and fun to read, and scientifically exact.
- **Goal:** keep him on top of interesting developments in his area (not only breakthroughs) and in neuroscience more broadly. Each paper is tied to his own analyses.
- **Schedule:** every **Sunday at 19:00 Europe/London**. It covers the past 7 days, **Monday to Sunday**. The scheduled routine may start up to **59 minutes early**, so the run has to finish (pipeline, writing, publishing, send prep) inside that margin. Issue 002 needed draft-card approval and went out late, at about 22:54 UK time.
- **Sender → recipient:** from the agent's own inbox (`<SENDER_INBOX>`, a Grok Bot mail address) to `<RECIPIENT_EMAIL>`.
- **Sign-off persona:** the issue is signed "— Mochi" (the bot's name to Patrick), never "Grok Bot".
- **Name and look:** "Neurodynamics Digest". It uses a dark-mode "declassified technical manual" aesthetic.
- **History:**
  - 27 Oct 2026: a TEST edition, never sent, written in a deliberately over-the-top "bro" voice that must never be reused.
  - 27 Oct 2026: Issue 001.
  - 1 Nov 2026: Issue 002, sent as two versions (A = web search, B = database pipeline) for an A/B test.
  - From 8 Nov 2026: one combined issue per week.

## 2. Moving parts at a glance

```
            ┌───────────── brief.md (source of truth) + preferences.md + sent-log.md ─────────────┐
            │                                                                                      │
 Sunday     ▼                                                                                      │
 routine ─► B: database sweep (pipeline/fetch_candidates.py + chatter.py)                          │
            A: targeted web pass (agent browsing; mandatory biorxiv-top)                           │
            ▼                                                                                      │
            merge + dedupe + verify every item against its real source                            │
            ▼                                                                                      │
            write content.py ─► render.py ─► full HTML (web) + compact HTML (<80 KB) + plain text │
            ▼                                                                                      │
            provenance.json (found_by A/B/AB)   archive/items.jsonl (+found_by)   sent-log.md      │
            ▼                                                                                      │
            site/ repo: issues/<nnn>.html + index.html + build_archive_site.py ─► git push main    │
            ▼                                                                                      │
            email via draft card (condensed body + link to the web issue)                          │
            ▼                                                                                      │
 Patrick ─► reads; stars / marks / "not interested" / "send to Mochi" on the archive site ─────────┘
            (marks sync to the user-state branch; feedback arrives as emails to <SENDER_INBOX>)
```

## 3. File layout on the agent box

All scripts assume this layout and hard-code `/workspace/newsletter`. If you rebuild elsewhere, keep the layout or edit the `ROOT`/path constants.

| Path | What it is |
|---|---|
| `/workspace/newsletter/brief.md` | **The private brief, the source of truth.** A sanitised copy is in [`tools/brief/brief.sanitised.md`](../tools/brief/brief.sanitised.md). |
| `/workspace/newsletter/preferences.md` | Append-only log of like/dislike signals (template: [`tools/brief/preferences.template.md`](../tools/brief/preferences.template.md)). |
| `/workspace/newsletter/sent-log.md` | Every item ever sent, with link and date, used to avoid repeats. |
| `/workspace/newsletter/docs/routine-prompt.txt` | The exact scheduled-routine prompt (reproduced in Appendix A). |
| `/workspace/newsletter/pipeline/` | Method B, the database pipeline (copy in [`tools/pipeline/`](../tools/pipeline/)). Outputs go to `pipeline/out/<Sunday>/`. |
| `/workspace/newsletter/issue-001/build/` | The issue templates the routine reuses (`content.py`, `render.py`, `compact.py`, `section_icons.py`, `house_style.py`, `archive_items.py`). Copies are in [`tools/issue-build/`](../tools/issue-build/). |
| `/workspace/newsletter/issue-002b/build/` | Latest real content example (Issue 002 B). |
| `/workspace/newsletter/ab/<date>/` | Per-week method bookkeeping: `comparison.md` (A/B weeks), `provenance.json` (combined weeks), `A_items.json`, `B_items.json`, `build_records.py`, `email/`. |
| `/workspace/newsletter/archive/items.jsonl` | The archive database (append-only JSON lines; 128 rows at 1 Nov 2026). |
| `/workspace/newsletter/archive/shortlist.jsonl` | Shortlist database (separate from the archive). |
| `/workspace/newsletter/build/` | `build_archive_site.py`, `tag_map.json`, `favicon.py` (copies in [`tools/archive/`](../tools/archive/)). |
| `/workspace/newsletter/site/` | Local clone of this repo (GitHub Pages source). |
| `/workspace/newsletter/style-reference-reality-switch.png` | Visual reference: the cover of Andrew Gallimore's *Reality Switch Technologies*. Take the aesthetic only; never reproduce the artwork. |
| `/workspace/newsletter/example-collaborator-newsletter.pdf` | Format model ("Alpha Girl", a collaborator's newsletter). Not public. |

## 4. The brief

`brief.md` is the source of truth and changes over time. Every run must read the latest version. Every change requested in chat or by email is written into it, with a dated change-log line. The sanitised copy in `tools/brief/` is the full brief minus addresses and project specifics. In summary:

### 4.1 Who and what for
- PhD in psychedelic neuroimaging. It uses EEG (plus a little fMRI) to explain acute and pre/post mechanisms of psychedelics in healthy and clinical groups. Addiction is a strand (gambling specifically, addiction broadly).
- **Method priority everywhere: EEG first, fMRI second, others after.**
- **Current analysis interests** (used to make "Why it matters for you" concrete, and boosted in ranking):
  - travelling waves in EEG
  - DCM and whole-brain modelling of ERPs and resting dynamics
  - aperiodic and oscillatory features, including non-sinusoidal waveform shape (e.g. bycycle)
  - MMN and DCM in addiction
  - a brain–body coupling pipeline (EEG/EGG/ECG/respiration), relevant to a psilocybin study in gambling disorder
  - EEG cue reactivity in addiction
  - spatial autocorrelation in psychedelic fMRI

  *The private brief holds more specific project details. They are deliberately left out of this public repo.*

### 4.2 Scope
- **Drugs:** all psychedelics and consciousness-altering drugs, plus non-drug altered states (breathwork, meditation, etc.).
- **Other disorders** (depression, PTSD, …) only when it is a psychedelic study that fits his other interests, or when imaging/EEG predicts treatment outcome, especially for psychedelic or brain-stimulation treatment.
- **Sleep and consciousness:** genuinely ground-breaking papers only (EEG sleep work welcome).
- **ML / EEG foundation models:** flag only very big developments.
- **Not wanted:** postdoc job listings.

### 4.3 Core interests (highest priority)
1. Neuroimaging explaining psychedelic mechanisms (acute and post-acute; healthy and clinical).
2. Novel EEG/fMRI analysis approaches. The named methods are examples only; go well beyond them.
3. Information theory and brain dynamics in mental health and drug imaging (Mediano-group style). Explain these accessibly, because he is still learning information theory.
4. EEG task studies that answer psychedelic-mechanism questions (plasticity, sensory processing, E/I balance).
5. Computational modelling of EEG/fMRI in psychedelics, other drugs, addiction and mental health. Pitch it to a learner and tie it to his research.
6. **Addiction, narrowed:** ONLY (a) addiction neuroimaging and (b) psychedelic studies in addiction. Exclude epidemiology, policy, general pharmacotherapy, behavioural/psychosocial interventions, and non-imaging non-psychedelic preclinical work.
7. Fundamental understanding of EEG/MEG signals: generators, laminar/circuit sources, forward/biophysical models, intracranial–scalp links, and what oscillations, aperiodic activity and waveform shape reflect.

### 4.4 Secondary interests
- Pharmaco-EEG/fMRI of anaesthetics, stimulants, cannabis, hypnotics and sedatives.
- The same imaging approaches in mental health more broadly.
- Brain–body coupling (respiration, cardiac, gastric; EEG **and** fMRI).
- Neuroplasticity measurement, plus big papers on non-hallucinogenic psychoplastogens.
- Preclinical psychedelic mechanisms, and work linking wet lab to human studies.
- High-impact metabolic psychiatry.
- Brain stimulation (TI/TMS): low priority. Include it only for major work or key stimulation studies in addiction with interesting analysis.

### 4.5 Wider field and wildcards
- High-impact "new ways of looking at the brain" work. Inspiration list of researchers (named in the pipeline too): James Pang, Robert Leech, Eli Müller, Katja Heuer, Justine Y. Hansen, Daniel Margulies, Bradley Voytek, Andrea Luppi, Alex Kwan, Roberto De Filippo, Natalie Schaworonkow, Luiz Pessoa. Their Bluesky feeds are useful sources.
- Wildcards: very high-impact papers from top journals/groups, ideally neuro, even if off-topic. The bioRxiv most-read tracker (https://robertodf.github.io/biorxiv-top/) is a mandatory source.

### 4.6 Ranking rules
- **Relevance to his analyses and study quality drive selection.** Journal/venue prestige is only a **small tie-breaking bump**, never a main factor.
- **Preferences:**
  - up-weight items similar to liked ones (starred, "more like this", read as a weak positive)
  - down-weight items similar to "not interested" ones
  - **never re-feature a not-interested item**
- **Don't over-narrow:**
  - keep the section structure
  - keep Wildcards and some out-of-profile items every week
  - down-weighting means "fewer/shorter", not "never"
  - derived rules need 2+ consistent signals
  - explicit chat instructions override derived rules
- **Repeats:** never repeat what is in `sent-log.md`, the archive or the shortlist. The exception is a short ICYMI pointer for a notable slightly older item that wasn't covered.
- **Integrity:** never invent papers, authors, findings, numbers, deadlines or links. Verify every item against its real source (publisher/DOI page, PubMed/Europe PMC, preprint server). Say plainly when something couldn't be verified, and when a section has nothing new.

### 4.7 Source access notes (from the brief)
- **bioRxiv top tracker (MANDATORY every issue):**
  - The page is JS-only, so read `usage.json` from the GitHub repo `RobertoDF/biorxiv-top`, **data** branch.
  - Fallback chain, retrying with backoff before giving up:
    1. raw.githubusercontent.com
    2. the GitHub API contents endpoint (`?ref=data`)
    3. a shallow `git clone --branch data`
    4. headless Chrome on the live site
  - Rank it the way the site does: reads ÷ (median reads/day of preprints posted within ±3 days × days online), with at least 15 days online.
  - If every route fails, say so in the issue and the chat note; never skip it silently.
- **Bluesky:** public no-login API.
  - Author feeds: `public.api.bsky.app/xrpc/app.bsky.feed.getAuthorFeed`.
  - The chatter script uses `api.bsky.app` searchPosts, because `public.api.bsky.app` search returns 403.
- **Springer, Cell/ScienceDirect, NHMRC:** plain fetches get bot-checked or time out, so use headless Chrome.
- **bioRxiv:** if PDFs return 429, use the full-text HTML. api.biorxiv.org, Europe PMC and Crossref APIs work.
- **EU Funding & Tenders (MSCA):** the portal is JS-only, so load the per-call JSON data files.
- **Breaking Convention:** use its Substack feed for dates.

## 5. Discovery: the combined method

Since 1 Nov 2026 the chosen method is **both A and B, merged into one issue** ("the most thorough approach", Patrick's choice). The order is:

### 5.1 Step B: database sweep (runs first; cheap and broad)
```bash
cd /workspace/newsletter/pipeline
python3 fetch_candidates.py --start <Monday YYYY-MM-DD> --end <Sunday YYYY-MM-DD>   # ~25–80 s
python3 chatter.py --date <Sunday> --top 30 [--discover]                            # ~2–4 min
```
No LLM is involved in retrieval; it uses only free scholarly APIs. The sources run in parallel (ThreadPoolExecutor). Each one sits in its own try/except, and failures are recorded in `stats.json`.

| Source | Endpoint / notes |
|---|---|
| PubMed | NCBI E-utilities (esearch + efetch), by publication date window |
| Europe PMC | REST search API |
| OpenAlex | works API, only for query groups flagged `openalex: true`. Without a key it shares a ~$0.10/day free budget; one run costs ~$0.015 |
| bioRxiv / medRxiv | `api.biorxiv.org/details` (v1) for the window, filtered by category. bioRxiv: neuroscience, pharmacology_and_toxicology. medRxiv: psychiatry_and_clinical_psychology, neurology, addiction_medicine, radiology_and_imaging. These "bulk" preprints must reach `min_keyword_score` 2.0 |
| arXiv | q-bio.NC via export.arxiv.org |
| ClinicalTrials.gov v2 | new registrations, kept only if a psychedelic is named; flagged for addiction/imaging |
| biorxiv-top | `biorxiv_top.py`: usage.json via the fallback chain above |

**Merge:**
- Records merge by DOI, else by normalised title (if over 25 characters).
- Metadata preference: pubmed > europepmc > openalex > rxiv/arxiv.

**Excluded before scoring:**
- anything already in `archive/items.jsonl`, `archive/shortlist.jsonl` or among the sent-log DOIs
- errata, retractions and notices
- bulk preprints outside the window
- bulk preprints below the keyword threshold

**Scoring.** All of it is tunable in `queries.json`.
- **Query groups**, each with a query, keyword regexes and a weight:
  - psychedelic_imaging 10, gambling 10
  - eeg_generators 9, travelling_waves 9, dcm_wholebrain 9, aperiodic_waveform 9
  - psychedelic_any 8, psychedelic_addiction 8, brain_body 8, mmn 8, cue_reactivity 8
  - eeg_methods 7, info_theory_dynamics 7, comp_modelling 7, addiction_imaging 7, spatial_autocorr 7, treatment_prediction 7
  - own_centre 6 (affiliation query), altered_states_nondrug 6
  - pharmaco_imaging_other 5, plasticity_nonhal 5
  - preclinical_psychedelic 4
  - metabolic_psych 3, sleep_consciousness 3
  - mental_health_imaging 1.5, stimulation 1
  - wildcard_top_journals 0 (retrieval only)
  - reviews_core / reviews_top_journals (reviews only)
  - Groups can require imaging, a psychedelic, or an extra regex.
- **Keyword score:** group weight × hit strength (title 1.0, abstract only 0.6). Multiple groups are combined with decay [1, 0.5, 0.3, 0.2].
- **Modality bonus:** EEG/MEG +4, fMRI +2.5, other imaging +1. An abstract-only match needs ≥2 mentions and is multiplied by 0.6.
- **Named researchers:** +5.
- **Current-analysis groups:** extra +3 × hit (travelling_waves, dcm_wholebrain, aperiodic_waveform, mmn, gambling, cue_reactivity, brain_body, spatial_autocorr, eeg_generators).
- **Top venue:** tier 1 +1.5, tier 2 +0.75 (tie-break only; set to 0 to disable).
- **biorxiv-top rank:** top 20 +3, top 100 +1.5.
- **Similarity to the archive:** TF-IDF cosine × 8.
- **Preferences:** similarity to liked items × 10, to disliked items × −6 (from `preferences.md`).
- **Penalties:**
  - no abstract −1.5
  - low-value publication type −2
  - engineering/ML regex −4 (unless psychedelic)
  - repository deposits −8
  - stale pubdate (>60 days) −1.5
  - off-topic −3
- **Keyword negations:** "DMT" = disease-modifying therapy and "LSD" = least significant difference don't count.

**Outputs** in `pipeline/out/<Sunday>/`:

| File | Contents |
|---|---|
| `candidates.json` / `candidates.md` | top 60 primary papers, top 15 reviews, psychedelic trials, biorxiv-top rankings |
| `reviews.json` | the review candidates |
| `pool.jsonl` | every scored item with `score_parts` (no abstracts) |
| `dropped.tsv` | what was dropped and why |
| `stats.json` | per-source hits, timings, errors, drop counts |
| `chatter.json` / `chatter.md` | the buzz data |

Example (1 Nov 2026): raw 1947 hits → 1696 after merge/dedupe → scored pool 1408 → 60 candidates + 15 reviews + 3 trials, in 37.6 s.

**Chatter** (`chatter.py`, for "Buzz this week"):
- Bluesky searchPosts uses several URL variants of each paper plus a quoted-title search, and excludes bot accounts. Hacker News uses Algolia.
- buzz = 3×(distinct authors) + 2×√(engagement) + HN terms. A separate **in-window** buzz score is the one used as the weekly signal.
- `--discover` also searches for papers being shared that the pipeline didn't find.
- Not used:
  - Altmetric (API key needed since Nov 2025)
  - Crossref Event Data (sunset Apr 2026)
  - Reddit (blocked; needs OAuth)
  - X (use the agent's own X tool if needed)

The agent then reads `candidates.md` and `chatter.md`, shortlists the relevant items and discards obvious noise (e.g. non-neuro "MEG" acronym hits). **The pipeline is not fully automatic:** every claim is still checked against the abstract or full text.

### 5.2 Step A: targeted web pass (runs second; fills B's gaps)
The agent researches the same Monday–Sunday window by browsing. It covers:
- journals, especially high-profile ones that index slowly in databases
- preprint servers
- researchers named in the brief
- policy and trial news, and ClinicalTrials.gov
- conference and funding sources, and summer schools
- notable slightly older **catch-up (ICYMI)** papers

The bioRxiv-top tracker is **mandatory** (via the fallback chain). The aim is to find **what the database sweep missed**, not to re-read what it already found.

### 5.3 Merge, dedupe, verify
- Take the union of A and B, deduped by DOI, else by title.
- Rank by relevance and study quality per the brief; the venue is only a small tie-break.
- **Verify every item against its real source.** Nothing goes in from a snippet, an email or memory alone.
- **Don't label items by method in the issue itself.** The method is recorded only internally.

### 5.4 Provenance
Save `/workspace/newsletter/ab/<date>/provenance.json`. It lists each included item with `found_by` = `"A"`, `"B"` or `"AB"`, plus a short note of the counts and of notable items that only one method found. It is used later to judge whether both methods are still pulling their weight.

The routine fixes only those contents, not a schema. A suggested shape (*not yet produced; the first one is due 8 Nov 2026*):
```json
{"date": "2026-11-08", "window": ["2026-11-02", "2026-11-08"],
 "counts": {"A": 0, "B": 0, "AB": 0, "total": 0},
 "items": [{"section": "EEG", "title": "...", "doi": "10.xxxx/...", "url": "https://doi.org/...", "found_by": "AB"}],
 "notes": "Notable single-method finds: ..."}
```
The same `found_by` value is written to each item's archive row.

## 6. Why combined? The A/B history

Issue 002 (window 26 Oct–1 Nov 2026) was sent as two separate emails and web pages. **A** was built from web search only; **B** was built from the database pipeline only, plus light web search for conference details. The full write-up is in `ab/2026-11-01/comparison.md` (not in this repo). Results, excluding one paper Patrick had requested in advance:

| | A (web) | B (pipeline) |
|---|---|---|
| Linked items | **12** | **23** |
| Overlap (in both) | 6 | 6 |
| Rendered | 8 main + 8 short | 11 main + 16 short |

- **B was stronger in-window.** It found on-brief work A missed entirely:
  - a corticothalamic neural-field model fitted to patients' EEG
  - MEG excitability dimensions
  - travelling waves in OCD
  - connectome-dependent aperiodic slopes
  - DCM for individual classification
  - psilocybin reward learning in rats
  - three in-window reviews
- **A caught older, high-profile catch-ups** that B's date filter dropped. The key example is the **McCulloch et al. LSD simultaneous PET-MRI paper in *Nature Neuroscience*** (5-HT2A occupancy, blood flow, connectivity). Others were an iEEG travelling-waves preprint, an EEG–ECG–EGG brain–heart–gut paper, an AUD psilocybin meta-analysis, PhaseICA and a TI-in-mouse-cortex preprint.
- **Effort:** A needed many searches and page fetches, with dead ends such as Cloudflare blocks and unverifiable trade-press claims, so it had a higher cost per useful item. B was one cheap pipeline run plus reading ~40 abstracts and hand-filtering noise.
- **Decision (1 Nov 2026, Patrick):** "for now, i want the most thorough approach. i like what both A and B pull, so combining them both to capture the most complete picture would be great!" The routine was rewritten for combined issues from 8 Nov, and `found_by` is tracked so the decision can be revisited.
- A possible future tweak, not yet implemented: give the pipeline a wider look-back or an ICYMI pass for big-venue items.

## 7. Writing the issue

### 7.1 Format model (from a collaborator's newsletter)
- **Header:**
  - issue number, date and coverage window
  - a short themed intro tying the week together, opening "Hi Patrick, this covers …"
  - a key line explaining the tags
- **Tags on each item:** PREPRINT (red badge) vs PEER REVIEWED, plus study type and topic (e.g. PHASE 2B RCT, METHODS, PRECLINICAL, EEG).
- **Main items:**
  - punchy headline
  - byline: first … last author (affiliation), journal, date
  - **what they did**, with concrete numbers (n, design, effect sizes, CIs, p)
  - **what they found**
  - **honest caveats** (sample size, conflicts, unblinding, animal-only, preprint status)
  - **"Why it matters for you"**
  - a ref row (journal, date, DOI, trial ID)
- **Short items:** one paragraph for secondary picks. "ICYMI" marks slightly older items.
- **Sign-off:**
  - a friendly closing panel inviting replies, signed "— Mochi"
  - a disclaimer footer (summaries from abstracts/full text where available; preprints not peer reviewed; check sources before citing)
  - an imprint line in the technical-manual style

### 7.2 Rules that apply every issue
- **"Why it matters for you" on EVERY paper item in every section.** Tie it concretely to his PhD (psychedelic EEG, information theory/brain dynamics, Mediano-group methods, addiction and mental-health interests). Never make it generic.
- **EEG gets its own dedicated section every issue, right after the headline act.** It collects EEG papers of every kind. Don't duplicate items: if the headline is an EEG paper, cross-reference it in one line.
- **Weekly explainer:** one information-theory or computational-modelling concept (e.g. Phi-ID, Lempel-Ziv complexity, bifurcations, whole-brain models), ideally tied to a paper in the issue.
- **"Buzz this week":** a short note from the chatter data (in-window counts) if worthwhile.
- **"Best reviews of the week" is ALWAYS the final content section**, just before the sign-off:
  - usually 2–5 reviews, perspectives or meta-analyses
  - each with its scope, key takeaways, caveats (narrative vs systematic, the authors' own stake) and "Why it matters for you"
  - if there are none, say so in one line
- Sections are fluid. Include or drop them depending on the week, and say plainly when one is quiet. A genuinely quiet week still gets a shorter edition.
- Length: a long, comprehensive Sunday read is welcome.

### 7.3 Section order (as used in Issue 002)
1. The headline act ★
2. EEG ∿
3. Your own corner ⌂ (Centre for Psychedelic Research, Mediano group, collaborators; used in 001)
4. Psychedelic neuroimaging ◆
5. Complexity and methods ∑
6. Weekly explainer Φ
7. Addiction ⟳
8. Brain–body coupling ♥
9. Preclinical ⚗
10. Critiques and nulls ∅ (used in 001)
11. Wildcards ✦ (includes a bioRxiv most-read pick)
12. Datasets and tools ⚙
13. Policy pulse ⚖ (FDA/EU regulation, big trial readouts, new psychedelic trial registrations)
14. Conferences on the horizon ◎ (verified dates, locations, abstract/early-bird deadlines)
15. Summer schools and training ✎
16. Funding radar £ (UK-based 2nd-year PhD with ~2 years left: travel grants, small grants and awards now; postdoc and early-career fellowships to prepare for; UK/EU first, notable US/AU)
17. Buzz this week
18. **Best reviews of the week ≡** (always last)

Brain stimulation appears only when warranted.

### 7.4 Tone
- Friendly, fun and interesting, written for PhD-level scientists.
- **Neutral and accurate**: no overclaiming, no taking liberties, no oversimplifying.
- Explain information theory and computational modelling accessibly without dumbing down the findings.
- **Normal voice only, never the "bro" voice.** That voice was used once, for the unsent TEST edition, and is banned.

## 8. Visual rules and the HTML build

### 8.1 Look
- A "declassified technical manual / lab spec sheet" in **DARK MODE**, inspired by the *Reality Switch Technologies* cover (aesthetic only).
- **Colours:**
  - page around #11161b
  - panels around #1c252e–#26323d
  - thin grey rules around #5f7180
  - body text around #e6e9ec
  - metadata around #9aa7b2
  - no large white areas
- **Type:** bold Helvetica/Arial-style headlines; monospace for codes, tags and metadata.
- **No Japanese or other non-English subtitle text.** The `TITLE_JP` field name is historical and now holds an English subtitle.
- **No barcodes.**
- **Accents and links:**
  - signal red #e0453b for the masthead, stamps and PREPRINT badges
  - light-grey bars as bullets
  - links in a light tone, never dark blue
- **Furniture:**
  - spec-code issue numbers like `<PKND_ISSUE_001>`
  - corner/registration marks from simple HTML blocks
  - a text-glyph "brainwave strip" (∿ lines in section colours) in the masthead
  - a "View in browser" link top right, pointing to the GitHub Pages copy
  - a reworded technical imprint line in the footer
- **Section headers:**
  - a full-width lighter-slate bar with a coloured left edge/underline
  - a square icon tile
  - the section number and title in large bold type, with a one-line subtitle
  - icons are monochrome text symbols (U+FE0E to force text presentation), never images or colourful emoji
- **Icons and accent colours** (defined in `section_icons.py`):

  | Section | Icon | Colour |
  |---|---|---|
  | Headline act | ★ | amber #f0a35e |
  | EEG | ∿ | teal #5fc9bf |
  | Your own corner | ⌂ | gold #e8c15a |
  | Psychedelic neuroimaging | ◆ | violet #c3a6f0 |
  | Complexity/methods | ∑ | sky #7fc0ee |
  | Weekly explainer | Φ | lime #b9d86a |
  | Addiction | ⟳ | rose #f095ad |
  | Brain–body coupling | ♥ | coral #f39a85 |
  | Preclinical | ⚗ | mint #7ddcae |
  | Critiques and nulls | ∅ | sand #d0b090 |
  | Wildcards | ✦ | orchid #e3a5e0 |
  | Datasets and tools | ⚙ | periwinkle #9fb4f2 |
  | Policy | ⚖ | ice #a8d8e8 |
  | Conferences | ◎ | straw #e6d27a |
  | Summer schools | ✎ | sage #a6dc8f |
  | Funding | £ | honey #e7b97a |
  | Best reviews | ≡ | silver #b8c4d6 |
  | Fallback | ◆ | violet |

- **Contents list:** every section links to its anchor (`s01`, `s02` … using both `id` and `<a name>`), and each section ends with "↑ contents". Anchors work in browsers, Apple Mail and Gmail web; Outlook and mobile apps may ignore them.

### 8.2 Email-safe build constraints
- Table-based layout with **inline styles only**.
- Dark backgrounds set with both the `bgcolor` attribute and inline `background-color`, so Outlook and mobile keep the dark theme. The recipient's institution uses Outlook.
- No external fonts, scripts or remote images; it must survive image blocking.
- Max width around 680 px, and readable on mobile.
- Three outputs per issue:
  - **full HTML:** the web version, published as `issues/<nnn>.html`
  - **compact HTML:** for inline email, **target <60 KB, hard limit 80 KB**
  - **plain-text fallback**

### 8.3 The build scripts ([`tools/issue-build/`](../tools/issue-build/))
- `content.py` (per issue) holds all the text. Start from [`content_template.py`](../tools/issue-build/content_template.py).
  - **Fields:** `NUM, SUBJECT, ISSUE_CODE, TITLE, TITLE_JP (English subtitle), TAGLINE, COVER, VIEW_URL, TOPRIGHT, STAMP, SPECLINE, PREHEADER, OUT_COMPACT, OUT_FULL, OUT_TXT, INTRO, KEY, SECTIONS, SIGNOFF_TITLE, SIGNOFF, DISCLAIMER, IMPRINT`.
  - **`SECTIONS`** is a list of `dict(title, sub, items)`. Item kinds:
    - `main`: `tags` [(TEXT, 0/1/2)], `head`, `byline`, `body` [paras], `caveats`, `why`, `ref` [(label, url)]
    - `short`: `label`, `text`
    - `explainer`: `paras`
  - **Inline links** use `[[text|url]]`; `<b>` and `<i>` are allowed.
- `render.py` is run **from the build folder** (it imports `content` from `.`).
  - Without flags it writes the compact version (via `compact.py`) and the plain text.
  - `--full` writes the full web version as well.
- `section_icons.py` holds the icon, accent colour, header background and brainwave strip for each section title.
- `house_style.py` holds the sign-off name ("Mochi") and the two feedback addresses shown in the sign-off. They are placeholders in the public copy; fill them in locally and never commit them.
- `check_issue.py` (added in `tools/`) runs pre-send checks: compact size ≤80 KB, no CJK characters, no barcode-like markup, no light backgrounds, no bro-voice markers, and the Best-reviews section present. The private build used similar checks in `verify.py`.
- Original location: `/workspace/newsletter/issue-001/build/`. The routine copies these into a new `issue-<nnn>/build/` each week. In Issue 002 the A and B versions shared blocks through `ab/2026-11-01/shared002.py`.

## 9. Sending

- **One email per week** from `<SENDER_INBOX>` to `<RECIPIENT_EMAIL>`. The subject reads like `Neurodynamics Digest #<n>: <highlights>`.
- **Draft-card approval flow:**
  - On Grok Bot, an email sent on the user's behalf may need explicit approval. The agent prepares a **draft card** in the chat (recipient, subject, body), and Patrick taps send.
  - The scheduled run therefore *prepares* the card. It does not assume it can send silently. Issue 002 went out this way at about 22:54 UK time on 1 Nov 2026, after the 19:00 target, because the cards waited for approval.
- **Card limits:**
  - Draft cards accept **only basic HTML**. Inline styles, tables, background colours and the dark-mode design do not survive.
  - So the email body is a **condensed version**: short intro, the top items as short text entries with links, and a prominent **"Read the full issue in your browser"** link to `https://pattricksk.github.io/neurodynamics-digest/issues/<nnn>.html`.
  - The full design lives on the web page. The compact HTML (<80 KB) and the plain text are still built: they are the fallback if a send path accepts full HTML, and the plain text feeds the condensed body.
- **If publishing fails:** still send, drop the browser link, and say so in the chat note.
- **Chat note after sending:** say it went out (or what blocked it), give the browser link, and add a 2–3 line summary that includes **how many items each method contributed** (A-only / B-only / both).
- Issue 001 (27 Oct 2026) went out with the full HTML as an attachment, plus a resend to the alternate address. From Issue 002 the draft-card route was used.
- In the A/B week, the email files were kept in `ab/2026-11-01/email/` (`subject-*.txt`, `*-compact.html`, `*.txt`).

## 10. Publishing to GitHub Pages

- **Repo:** `Pattricksk/neurodynamics-digest`, public. GitHub Pages serves from **`main`, root**. Local clone: `/workspace/newsletter/site`.
- **Site:** https://pattricksk.github.io/neurodynamics-digest/. It is unlisted, with `noindex` meta tags on the index and archive pages plus `robots.txt`.
- **Structure:**
  ```
  index.html                 # issue list (newest first, after the "<!-- ISSUES (newest first) -->" marker) + "Search the archive" button
  issues/<nnn>.html          # full HTML of each issue (001, 002a, 002b, then 003, ...)
  archive/index.html         # archive search UI (EEG canvas header hand-written here)
  archive/items.json         # built from archive/items.jsonl
  archive/shortlist.html / shortlist.json
  archive/search.html        # free client-side literature search
  archive/graph.html         # graph view
  archive/item/<id>.html     # per-item detail pages (Zotero citation meta)
  archive/sync.js            # cross-device marks sync
  archive/vendor/            # vendored d3-force (ISC)
  favicon.svg, favicon-32.png, favicon-16.png, apple-touch-icon.png   # tryptamine skeletal formula (build/favicon.py)
  robots.txt
  docs/PROCESS.md            # this file
  tools/                     # sanitised copies of the code
  ```
- **For each new issue:**
  - Add `issues/<nnn>.html`, inserting the favicon links before `</head>`: `<link rel="icon" href="../favicon.svg" type="image/svg+xml"><link rel="icon" href="../favicon-32.png" sizes="32x32" type="image/png"><link rel="icon" href="../favicon-16.png" sizes="16x16" type="image/png"><link rel="apple-touch-icon" href="../apple-touch-icon.png">`
  - Add an `<li>` to `index.html`.
  - Rerun the archive build.
  - Commit `issues/`, `index.html` and `archive/` (including `archive/item/`), then push.
- **Git rules:**
  - Always `git pull --rebase` before committing. If the push is rejected, pull with rebase again and retry.
  - **Never force-push.**
  - **Never touch the `user-state` branch or `user-state.json`**: no reading, writing, resetting or deleting it, and never create one on `main`.
  - Publish **before** sending, so the "View in browser" link works.
- **Auth:** on the original box, the `gh` CLI is logged in as the repo owner. On a rebuild, use any credential with push rights to `main`, kept outside the repo.

## 11. The archive

### 11.1 Rows: `archive/items.jsonl`
Append-only, one JSON object per item. Dedupe by DOI, else title (and skip existing issue+title pairs); never rewrite. The one exception: Patrick's notes on an existing item go in that row's `notes` field.

| Field | Meaning |
|---|---|
| `issue`, `issue_date` | e.g. "002", "2026-11-01" ("" for chat-promoted items) |
| `section` | the newsletter section title (Best reviews → "Best reviews") |
| `title`, `authors`, `venue`, `pub_date`, `doi`, `url` | bibliographic data |
| `item_type` | paper / preprint / review / dataset / tool / conference / funding / policy / news / training |
| `modality` | EEG / fMRI / MEG / intracranial / PET / behavioural / preclinical / none. Name every imaging modality in `methods` too (e.g. "diffusion MRI", "SV2A PET", "OPM-MEG") |
| `drugs`, `populations`, `methods`, `topics` | lists of tags |
| `summary` | 1–2 sentences |
| `caveats` | short |
| `verified` | true/false |
| `stage` | "Clinical" / "Pre-clinical" / empty (non-study items). Animal EEG = EEG + Pre-clinical |
| optional `source` | "newsletter" (default) or "sent-by-patrick" |
| optional `notes` | Patrick's notes |
| optional `relevance` | 1–3, overrides the derived value |
| `ab_version` | "A"/"B", Issue 002 only. Decides whether the issue link goes to 002a or 002b |
| `found_by` | **"A" / "B" / "AB"**, from combined issues onward |

The routine's step 6 does this append. In practice it is a small per-issue script; Issue 002 used `ab/2026-11-01/build_records.py`. The older `issue-001/build/archive_items.py` depended on a temporary Crossref cache, so treat it as an example only.

### 11.2 Build: `build/build_archive_site.py`
Run it with `python3 /workspace/newsletter/build/build_archive_site.py`. It is safe to rerun. It:
- reads `archive/items.jsonl`, dropping `TEST` rows and duplicate issue+title rows, and writes `site/archive/items.json`
- reads `archive/shortlist.jsonl` and writes `site/archive/shortlist.json` (kept separate)
- adds `issue_url` (`../issues/<page>.html#sNN`, using section anchors parsed from the published issue; A/B rows point to `<nnn>a`/`<nnn>b`)
- adds `relevance` (PhD relevance 3/2/1 from section priority, +1 for EEG/complexity or psychedelic content; a stored value wins)
- adds `id`
- adds `similar` (top 6 by plain-Python TF-IDF cosine over title, summary, notes and up-weighted tags) and `similar_w` (the cosine scores)
- adds normalised chip fields from `build/tag_map.json`:
  - `drug_groups` / `drug_labels` / `drug_display`
  - `modality_groups` (exactly EEG, MEG (+ OPM), fMRI, DTI, PET)
  - `disorders`
  - `stage`
  - `method_groups` (from `method_map` regexes)
- writes `site/archive/item/<id>.html` detail pages (Highwire `citation_*` meta for Zotero), and adds `zotero`, `venue_clean` and `detail_url`. Cards carry hidden COinS spans. **No "Add to Zotero" button or toast anywhere**, per Patrick.

`tag_map.json` keys: `drug_groups`, `non_hal_label`, `non_hal`, `modality_order`, `modality_map`, `disorder_map`, `stage`, `overrides`, `method_map`. Drug-merge rules:
- Merge only when certain (same compound, formulation/brand/code, or direct active metabolite), e.g. psilocybin + psilocin + COMP360 → Psilocybin; mebufotenin/BPL-003/GH001 → 5-MeO-DMT.
- DMT and 5-MeO-DMT stay separate, as do ketamine and esketamine.
- Non-hallucinogenic analogues go under "Non-hal", but only when the source says so.
- Unknown names pass through as their own label.

### 11.3 Archive website (`site/archive/index.html`)
Plain HTML/JS with no build step. It loads `items.json` and offers:
- **Browsing:**
  - tabs by section (with icon and colour)
  - always-visible chip rows for Drug, Modality, Disorder/population and Clinical/Pre-clinical (OR within a row, AND across rows)
  - collapsible filters (method, population, month, venue, issue, PhD relevance)
  - keyword search (all words must match)
  - clickable tag chips
  - "More like this"
- **Marks:**
  - star, To read/Read, and Starred/To read/Read views
  - **"Not interested"** quarantines the item, with Undo/restore
- **Preferences:**
  - "More like this" clicks count as positive signals
  - **"Send my preferences to Mochi"** (shows an unsent-signal count) opens a `mailto:` to the sender inbox, subject "Digest preferences update", grouped STARRED / MORE LIKE THIS / NOT INTERESTED / READ, one line per item. A copy-to-clipboard fallback kicks in past ~1800 characters.
  - "Export preferences (JSON)"
- **Storage:** all state lives in localStorage key `ndd-archive`.
- **Not included:** author filter, BibTeX export.
- **Header:** a canvas EEG animation (Fz/Cz/Pz, 1/f noise plus occasional ~10 Hz alpha bursts).

## 12. Graph view

`site/archive/graph.html` is linked from the archive, shortlist and search headers as "◌ Graph view". It is an Obsidian-style force graph, pure client-side, using vendored d3-force with no CDN.
- **Nodes:** archive papers, as dots. Non-research items (funding, conferences …) are hidden by default.
- **Links:**
  - On by default: links between papers sharing a **drug group, modality group or method family**.
  - Optional: topic tags, authors and text similarity (`similar_w`).
  - Link weight = the number of shared attributes. Only each paper's strongest N links are drawn ("Links / paper", default 4, range 1–12), above a "Min shared" threshold (1–4).
- **Colour by modality:** EEG, MEG (+ OPM), fMRI, DTI, PET, other/none. Multi-modal dots are split like a pie.
- **Modes (tag-node toggle):**
  - **Papers:** paper–paper links
  - **Tags:** drug, modality and method values as their own diamond nodes, with papers linked to their tags
  - **Both**
- **Filters:** the same chip filters as the archive, plus keyword search that highlights matches and dims the rest.
- **My marks filter:** filter by Patrick's own marks (starred, read). Stars also show as a gold ring.
- **Shortlist layer:** an optional toggle draws shortlist papers as dashed hollow dots. They are never written into archive data.
- **Quarantine:** hidden by default, with a toggle to show.
- **Interaction:** hover shows the title. Click opens a side panel with details, tags, marks, links (detail page, issue section, source) and the linked papers. There are zoom buttons, fit and re-layout, and labels Auto/All/Off.
- **Settings:** saved in localStorage `ndd-graph`, which is **not synced**.
- **Data:** `method_groups` and `similar_w` come from the archive build; graph.html itself has no build step.

## 13. Shortlist vs archive

- **Archive** = items that appeared in a newsletter, plus papers explicitly promoted.
- **Shortlist** = candidate papers Patrick flagged (from search or sent in chat) that have **not** been promoted. It is fully separate: shortlist items never appear in the archive's results, tabs, filters, "More like this", or the "in archive" badges on search.html. The archive header shows only a "Shortlist (n)" link.
- **Files:**
  - Shortlist data: `archive/shortlist.jsonl`, with the same fields as items.jsonl plus `added_date`, `seed`, `notes` and `status`. It builds to `site/archive/shortlist.json`.
  - Page: `shortlist.html`, which has:
    - its own search
    - star / not-interested marks (localStorage `ndd-shortlist`)
    - detail pages `item/sl-NNNN.html`
    - "Search for more like this"
    - **"Add to archive"** and "Remove from shortlist"
- **Papers Patrick sends in chat go to the shortlist**, unless he explicitly says to put them straight in the archive.
- **Literature search** (`site/archive/search.html`, free and client-side, costs the agent nothing):
  - **Opening it:** from "⌕ Search for more like this" on any eligible card (`search.html?seed=<doi or id>`) or from the header link.
  - **Query:** prefilled from the seed's tags and title words, and editable.
  - **Filters**, all kept in the URL:
    - year range, type, open access
    - venue contains, min citations
    - include/exclude words
    - sort (relevance/newest/most cited), count
  - **Modes:**
    - "Similar to this paper": Semantic Scholar recommendations, falling back to keyword search
    - "Keyword search": OpenAlex (with the sender inbox as `mailto`) → Europe PMC → Semantic Scholar graph search
    - OpenAlex related_works as a last resort
  - **Result cards:**
    - title, authors, venue, year, citations, OA/PDF
    - TL;DR or the first abstract sentence, plus the collapsible abstract
    - "already in archive / on shortlist" badges
    - **"✉ Send to Mochi"**, whose sent state is remembered in `ndd-search-sent`
    - "More like this"

## 14. Cross-device sync

`site/archive/sync.js` runs on the index, shortlist, search and graph pages. It syncs Patrick's marks between browsers/devices **without any server**.

- **What syncs:** the localStorage keys `ndd-archive`, `ndd-shortlist` and `ndd-search-sent`. They go to `user-state.json` on a **separate orphan branch `user-state`** of this repo, via the GitHub REST contents API:
  - load: `GET /repos/<owner>/<repo>/contents/user-state.json?ref=user-state`
  - save: `PUT` with the current `sha`, commit message "sync: user state"
  - A separate branch means sync commits never trigger Pages rebuilds and never conflict with the weekly push to `main`.
- **Connecting a device (generic setup):**
  1. On GitHub, create a **fine-grained personal access token** with *Only select repositories* → this repo, and the single permission *Contents: Read and write*. Choose an expiry.
  2. Open any archive page and click the ⇅ pill (bottom right) → "Connect sync", then paste the token.
  3. The token is stored **only in that browser's localStorage** (`ndd-sync-token`). It never goes in the repo, a URL, an email or a chat. Sync bookkeeping lives in `ndd-sync-meta`. An optional `ndd-sync-api` overrides the API base.
  4. Repeat per device. Without a token everything still works, locally only.
- **Merge rules:**
  - Each mark is a separate leaf with its own timestamp. The newest change wins per leaf, and removals are kept as tombstones, so devices never wipe each other's marks.
  - On a timestamp tie, a removal wins, then the larger value (deterministic everywhere).
  - On a 409/422 sha conflict, the client refetches, merges and retries up to 4 times.
- **When it saves and loads:**
  - saves: 4 s after a change, on "Sync now", and on tab hide
  - loads and merges: on every page open and when the tab regains focus
- **Public visibility:** the repo is public, so the marked item ids in `user-state.json` are publicly visible. Nothing else is stored there.
- **Automation must never touch `user-state`** (see §10).
- **Rebuilding in a different repo:** change `REPO` (and if needed `BRANCH`/`PATH`) at the top of sync.js. Create the orphan branch once by hand, e.g. `git switch --orphan user-state && echo '{}' > user-state.json && git add . && git commit -m init && git push -u origin user-state`, then switch back to main.

## 15. The feedback loop

Feedback reaches the agent in four ways:
1. **Grok Bot chat:** plain comments like "more like X" or "not interested in Y", or pasted preference lists/JSON exports.
2. **Email replies to an issue** from the recipient address (or the alternate address). The sign-off invites them, and they update the brief.
3. **"Digest preferences update" emails** to the sender inbox, from the archive's "Send my preferences to Mochi" button.
4. **Request emails** to the sender inbox from the archive pages (from the recipient address or the alternate address only):
   - **"Shortlist add request"** (from search.html; body: Title, Authors, Year, Venue, DOI/URL, Seed paper, Found via, "My notes:").
     - Verify from a real source.
     - Write a 1–2 sentence summary plus caveats, and tag it (drugs/modality/methods/populations/topics, stage, relevance 1–3).
     - Append to `shortlist.jsonl` with `added_date`, `seed`, `notes`, `status: "shortlisted"` and `verified: true`.
     - Skip it (and say so) if it is already in the archive or shortlist.
     - Rebuild and push.
   - **"Archive promote request"** (from shortlist.html; body: Title, DOI/URL, Shortlist id, "Why it earns a place:").
     - Move the row from the shortlist to items.jsonl with `source: "sent-by-patrick"`, section "Patrick's picks", `issue: ""`, `issue_date` = the date promoted, and `notes` = "<notes> | Why: <why>".
     - Match by DOI, else title.
     - Rebuild and push.
   - **"Shortlist remove request"**: drop the row, rebuild and push.

**Handling signals:**
- Every signal is logged, dated and append-only, in `preferences.md`. Updates are cumulative snapshots, so only log items that are new or changed.
- Liked = STARRED, MORE LIKE THIS, READ (weak). Disliked = NOT INTERESTED.
- Derived rules are added only after 2+ consistent signals, with the evidence cited.
- The pipeline reads `preferences.md` automatically (liked ×10, disliked ×−6 similarity), and the writer reads it too.
- As of 1 Nov 2026 **no signals had been logged yet**.

**How the emails trigger work:** a separate event-driven routine watches the sender inbox for these mails, accepted only from the recipient addresses, and carries out the steps above. **Unknown:** that routine's exact trigger configuration and prompt text are not recorded in the files this document was written from. If you rebuild, create an inbox-triggered routine filtered to the recipient addresses, whose prompt is the bullet list above.

## 16. sent-log, provenance, special editions

- **`sent-log.md`:** one header per edition, e.g. `## Issue 002 · 1 Nov 2026 · … · STATUS: SENT …`, then one line per item: `- [NNN] Title — URL — date`. The TEST edition used `[TEST]` and Issue 002 used `[AB]`/version markers. Read it before choosing items, and append to it after sending (routine step 9).
- **Provenance:** `ab/<date>/provenance.json`, see §5.4. A/B weeks used `comparison.md` instead.
- **Special editions:** Patrick would like occasional **on-request special editions** in a different style from the weekly digest, to catch up on big papers from past years he may have missed across his interests. None has been produced yet, and no format is fixed. Backfilling key older papers into the archive is deferred. A one-off "requested paper" item can also be added to a single issue; this was done for 1 Nov, and the instruction was then removed from the routine.

## 17. Other tools and cost

- **Undermind:** Patrick has a free-plan Undermind account (an AI paper-search tool). It has **no connector** to the agent, so it can only be used by Patrick, or through a browser session he signs into. A set of 12 Undermind queries was drafted. **Unknown/pending:** those queries are not stored in the files this document was written from, and no Undermind results have been processed into the digest yet.
- **Edison:** mentioned alongside Undermind as an outside literature-search option. **Unknown:** what was planned. No setup, results or decision are recorded in the files this document was written from.
- **Cost notes:**
  - Method B (the pipeline) is almost free in API terms: free APIs, and OpenAlex costs ~$0.015 per run against a ~$0.10/day keyless budget (a free key needs an email). Its agent cost is mainly reading ~40–60 candidates and writing.
  - Method A (web search) costs more per useful item: many searches and fetches, and dead ends.
  - The weekly routine was observed at roughly **4% of a 30-day usage window**, measured only at the routine level. **Unknown:** an exact per-method split. The combined method will cost more than either alone; check with the usage tools after a few combined runs.
  - The archive site, search, graph and sync cost the agent nothing (all client-side, GitHub Pages is free).

## 18. Rebuild from scratch

What you need:
- an agent with a persistent Linux box (Python 3.10+, git, headless Chrome for JS-only sites)
- web search/fetch
- a scheduled-routine feature
- an email inbox it can send from (or a draft/approval flow)
- an inbox-triggered routine for feedback
- a GitHub account

1. **Layout.** Create `/workspace/newsletter/{pipeline,build,archive,docs,ab}` and `issue-template/build`.
2. **Code.** Copy from this repo's `tools/`:
   - `tools/pipeline/*` → `pipeline/`
   - `tools/archive/*` → `build/`
   - `tools/issue-build/*` → `issue-template/build/` (on the original box, `issue-001/build/` plays this role)
3. **Brief.** Start from `tools/brief/brief.sanitised.md` → `brief.md`. Fill in the real addresses, and add the reader's private project details back privately. Create `preferences.md` from the template and an empty `sent-log.md`.
4. **Placeholders:**
   - Set `NDD_MAILTO` (or edit `pipeline/common.py`) to the sender inbox; it is used as the polite-pool contact for APIs.
   - Set the feedback addresses in `house_style.py`.
   - Never commit real addresses to a public repo.
5. **Site repo.** Create a public GitHub repo and enable Pages (main, root). Add `index.html` (with the `<!-- ISSUES (newest first) -->` marker), `robots.txt` (Disallow: /) and `noindex` meta tags. Add the `archive/` pages from this repo (`index.html`, `search.html`, `shortlist.html`, `graph.html`, `sync.js`, `vendor/`), with `REPO` edited in `sync.js`. Generate favicons with `build/favicon.py`. Clone the repo to `/workspace/newsletter/site`.
6. **Archive data.** Start with empty `archive/items.jsonl` and `archive/shortlist.jsonl`, then run `python3 build/build_archive_site.py` once.
7. **Sync (optional).** Create the orphan `user-state` branch (§14) and give each device a fine-grained PAT, pasted only into the browser.
8. **Test.** Run `python3 pipeline/fetch_candidates.py --start <Mon> --end <Sun>` and check that `stats.json` shows no failures. Then copy `content_template.py` to `content.py` in a test build folder, fill it in, run `python3 render.py --full`, then `python3 check_issue.py <files>`.
9. **Schedule.** Create a weekly routine for Sunday 19:00 Europe/London (start it ~1 h early) using the prompt in Appendix A. Swap in your paths, addresses and repo.
10. **Feedback routine.** Create an inbox-triggered routine on the sender inbox, accepting mail only from the recipient addresses, that handles the four email types in §15.
11. **First run.** Watch the first run end to end: pipeline → web pass → merge/verify → build → archive append → publish → draft card → sent-log → chat note.

## 19. Weekly run checklist

- [ ] Read `brief.md` (latest), `preferences.md` and `sent-log.md`.
- [ ] Run the pipeline and chatter for Monday–Sunday; check `stats.json` for failures.
- [ ] Do the web pass (journals, preprints, named researchers, policy/trials, conferences, funding, schools, ICYMI), including the **biorxiv-top** check.
- [ ] Merge, dedupe (DOI, else title), rank and **verify every item**.
- [ ] Write `content.py`: EEG second, explainer, Buzz, **Best reviews last**, and "Why it matters for you" on every paper. Normal voice.
- [ ] `render.py --full`, then `check_issue.py` (compact <80 KB, dark, no CJK, no barcodes) and the plain text.
- [ ] `ab/<date>/provenance.json` with found_by.
- [ ] Append to `archive/items.jsonl` (with found_by; dedupe; append only).
- [ ] In `site/`: `git pull --rebase`, add `issues/<nnn>.html` with favicons, update `index.html`, run `build_archive_site.py`, commit, push `main` (no force; never touch `user-state`).
- [ ] Prepare the email draft card: condensed basic-HTML body plus the link to the web issue.
- [ ] Append to `sent-log.md`.
- [ ] Post the chat note: sent/blocked status, link, 2–3 line summary with per-method counts.

## 20. Known gaps and unknowns

- `provenance.json` has no fixed schema yet (first one due 8 Nov 2026).
- The exact trigger configuration and prompt of the feedback email routine: **unknown** (not in the source files).
- Undermind query texts and any Edison plans: **unknown / not stored**.
- Exact cost per method: **unknown**; only a routine-level figure (~4% of 30 days) was observed.
- Format and timing of special editions: not yet decided.
- `pool.jsonl` has no abstracts; verification uses `candidates.json` and the sources.
- In the Issue 002 rows, `stage` was filled with publication status ("peer reviewed", "preprint", "registered", "reviewed preprint") instead of Clinical / Pre-clinical. New rows should follow the brief (Clinical / Pre-clinical / empty). Those 002 rows may need correcting; the build's stage rules in `tag_map.json` derive the chip where they can.
- Scripts hard-code `/workspace/newsletter` paths.

---

## Appendix A: the current routine prompt (verbatim)

This is the exact text of the scheduled Sunday routine as of 1 Nov 2026 (`/workspace/newsletter/docs/routine-prompt.txt`). The only change is that the two email addresses are replaced with `<SENDER_INBOX>` and `<RECIPIENT_EMAIL>`.

````text
Write and send Patrick's weekly science newsletter, so it lands in his inbox by 19:00 UK time on Sunday evening. Patrick wants the MOST THOROUGH approach: discovery uses BOTH methods (A: web search, B: database pipeline), merged into ONE combined issue for the most complete picture. (The A/B test is over; the 1 Nov 2026 issue was the last two-version issue.)

1. Read the current brief at /workspace/newsletter/brief.md. It is the source of truth for his interests (including his current analyses list and scope clarifications), priorities, sections (including the dedicated EEG section, the narrowed addiction scope and the FINAL "Best reviews of the week" section), the rule that every paper gets "Why it matters for you", tone, format model, visual style, source-access notes, archive rules and sync notes, and it changes over time, so always follow the latest version. Also read /workspace/newsletter/sent-log.md so you don't repeat items already covered. Reuse the build scripts in /workspace/newsletter/issue-001/build/ (content.py, render.py --full, compact.py, archive_items.py, section_icons.py) and the 1 Nov A/B build in /workspace/newsletter/ab/2026-11-01/ as templates.

2. DATABASE SWEEP (method B). Run `cd /workspace/newsletter/pipeline && python3 fetch_candidates.py --start <Monday> --end <Sunday>` then `python3 chatter.py --date <Sunday> --top 30` (see pipeline/README.md). Read out/<Sunday>/candidates.md (papers, reviews, trials, biorxiv-top) and chatter.md (use in-window counts as the weekly buzz signal). Shortlist the relevant items; ignore obvious pipeline noise (e.g. non-neuro 'MEG' acronym hits).

3. WEB PASS (method A). Research the past 7 days (Monday to Sunday) as before: journals (especially high-profile journals that index slowly in databases), preprint servers, researchers named in the brief, policy/trials news, ClinicalTrials.gov, conference and funding sources, summer schools, plus notable slightly older catch-up papers he may have missed. MANDATORY: the bioRxiv top neuro tracker (RobertoDF/biorxiv-top data branch usage.json, fallback chain in the brief). Aim to find what the database sweep missed rather than re-reading what it already found.

4. MERGE into one issue: union of both, deduped by DOI else title, ranked by relevance and study quality per the brief (venue only a small tie-breaking bump). Verify every item against its real source; never invent papers, authors, findings, numbers, deadlines or links. Write to the brief's format model (friendly, accurate, no overclaiming, normal voice only, never the bro voice), "Why it matters for you" on every paper tied to his actual analyses, a short "Buzz this week" note from the chatter data if worthwhile, and the Best reviews section last. Build email-safe HTML in the brief's visual style, a compact version under 80KB, and a plain-text fallback. Don't label items by method in the issue itself.

5. Provenance (internal, for judging the methods later): save /workspace/newsletter/ab/<date>/provenance.json listing each included item with found_by "A", "B" or "AB", plus a short note of counts and which notable items only one method found.

6. Archive: append one JSON object per item to /workspace/newsletter/archive/items.jsonl (dedupe against existing by DOI, else title; append only), using the brief's fields, with found_by: "A", "B" or "AB".

7. Publish before sending: in /workspace/newsletter/site, run `git pull --rebase` first (Patrick's synced marks live on the separate user-state branch, which builds and automation must never touch; never force-push), add issues/<nnn>.html, update index.html, rerun /workspace/newsletter/build/build_archive_site.py, commit and push to main (pull --rebase again and retry if rejected). View-in-browser link is https://pattricksk.github.io/neurodynamics-digest/issues/<nnn>.html. If publishing fails, still send and drop the link, and say so in the chat note.

8. Send one email from <SENDER_INBOX> to <RECIPIENT_EMAIL> with a subject like "Neurodynamics Digest #<n>: <highlights>". If sending needs his approval on a draft card, prepare the card so he can send it (cards accept only basic HTML, so use a condensed body linking the full web issue).

9. Append the items covered, with links and the date, to /workspace/newsletter/sent-log.md.

Result goes to Patrick by email at <RECIPIENT_EMAIL>; also post a short note in this Grok Bot chat that it went out (or what blocked it), with the browser link and a 2-3 line summary including how many items each method contributed. If a week is genuinely quiet, still send a shorter edition.
````

## Appendix B: what is in tools/

| Path | Source on the agent box | Changes in this copy |
|---|---|---|
| `tools/pipeline/fetch_candidates.py`, `sources.py`, `biorxiv_top.py`, `chatter.py`, `README.md` | `pipeline/` | none |
| `tools/pipeline/common.py` | `pipeline/common.py` | `MAILTO` now read from env `NDD_MAILTO` (placeholder default) instead of the real inbox |
| `tools/pipeline/queries.json` | `pipeline/queries.json` | `_why` comments describing the reader's specific current projects replaced by a generic note; queries, keywords and weights unchanged |
| `tools/issue-build/render.py`, `compact.py`, `section_icons.py` | `issue-001/build/` (identical in `issue-002b/build/`) | none |
| `tools/issue-build/house_style.py` | same | feedback addresses replaced by placeholders |
| `tools/issue-build/content_template.py` | new | skeleton `content.py` with every field and the section order (tested with render.py) |
| `tools/issue-build/check_issue.py` | new | pre-send checks (size, CJK, barcodes, light backgrounds, voice, Best reviews) |
| `tools/archive/build_archive_site.py`, `tag_map.json`, `favicon.py` | `build/` | none |
| `tools/brief/brief.sanitised.md` | `brief.md` | addresses replaced; specifics of unpublished projects removed or generalised |
| `tools/brief/preferences.template.md` | `preferences.md` | addresses replaced |

Not copied: pipeline outputs (`out/`), caches, per-issue drafts, the TEST "bro" edition files, A/B email files, the Issue 001 `archive_items.py` (depends on a temporary cache), any credentials.
