# -*- coding: utf-8 -*-
"""Skeleton issue content for render.py / compact.py. Copy to content.py in a per-issue build folder,
fill every field, then run `python3 render.py [--full]` from that folder.
Inline links use the markup [[link text|https://url]]. Body text may use <b> and <i>.
Item kinds: "main" (full write-up), "short" (label + one paragraph), "explainer" (paras=[...]; rendered with EXPLAINER / INFO THEORY 101 badges).
Tags: list of (TEXT, kind) where kind 2 = red badge (PREPRINT), 1 = outlined light (PEER REVIEWED), 0 = muted (topic/study type)."""
from house_style import signoff_lines

NUM = "003"
SUBJECT = "Neurodynamics Digest #003: <two or three highlights>"
ISSUE_CODE = "<PKND_ISSUE_003>"
TITLE = "Neurodynamics Digest."
TITLE_JP = "Psychedelics, EEG, information theory and addiction: weekly field notes"   # subtitle line (English only; name is historical)
TAGLINE = "A weekly science digest for a psychedelic EEG researcher at Imperial."
COVER = "Issue 003 \u00b7 Sun 8 Nov 2026 \u00b7 Coverage: 2\u20138 Nov 2026"
VIEW_URL = "https://pattricksk.github.io/neurodynamics-digest/issues/003.html"
TOPRIGHT = "ISSUE 003"
STAMP = "No.<br>003"
SPECLINE = "SPEC REV. 003 \u00b7 COVERAGE 2\u20138 NOV 2026"
PREHEADER = "One-sentence inbox preview of the week's highlights."
OUT_COMPACT = "/workspace/newsletter/issue-003/issue-003-compact.html"   # inline-email version (<80 KB)
OUT_FULL = "/workspace/newsletter/issue-003/issue-003-full.html"         # web version -> site/issues/003.html
OUT_TXT = "/workspace/newsletter/issue-003/issue-003.txt"                # plain-text fallback

INTRO = [
 "Hi Patrick, this covers <dates>. <One short themed paragraph tying the week's picks together.>",
]
KEY = "Key: PREPRINT = not peer reviewed \u00b7 PEER REVIEWED = journal published \u00b7 ICYMI = slightly older than this week"

EXAMPLE_MAIN = dict(kind="main",
  tags=[("PEER REVIEWED",1),("EEG",0),("METHODS",0)],
  head="Punchy, accurate headline",
  byline="First, \u2026 Last (Affiliation) \u00b7 Journal \u00b7 DD Mon YYYY",
  body=["What they did, with concrete numbers (n, design, effect sizes, CIs, p).", "What they found."],
  caveats="Honest caveats: sample size, preprint status, conflicts, animal-only, etc.",
  why="Concrete link to Patrick's PhD work (never generic).",
  ref=[("Journal, DD Mon YYYY \u00b7 doi:10.xxxx/yyyy","https://doi.org/10.xxxx/yyyy")])
EXAMPLE_SHORT = dict(kind="short", label="Short item headline (venue, date).",
  text="Authors. One paragraph incl. a <i>Why it matters for you</i> clause. [[doi:10.xxxx/yyyy|https://doi.org/10.xxxx/yyyy]]")
QUIET = dict(kind="short", label="Quiet week.", text="Nothing verified worth your time this week.")

# Order used since Issue 002. Drop sections with nothing to say; EEG always comes right after the headline act;
# "Best reviews of the week" is ALWAYS the last section.
SECTIONS = [
 dict(title="The headline act", sub="", items=[EXAMPLE_MAIN]),
 dict(title="EEG", sub="your core modality", items=[EXAMPLE_SHORT]),
 dict(title="Your own corner", sub="Centre for Psychedelic Research, Mediano group, collaborators", items=[]),
 dict(title="Psychedelic neuroimaging", sub="", items=[]),
 dict(title="Complexity and methods", sub="", items=[]),
 dict(title="Weekly explainer", sub="one concept, explained", items=[dict(kind="explainer", paras=["Paragraph 1 ...", "Paragraph 2 ..."])]),
 dict(title="Addiction", sub="imaging and psychedelic studies only", items=[]),
 dict(title="Brain\u2013body coupling", sub="", items=[]),
 dict(title="Preclinical", sub="", items=[]),
 dict(title="Critiques and nulls", sub="", items=[]),
 dict(title="Wildcards", sub="incl. bioRxiv most-read pick", items=[]),
 dict(title="Datasets and tools", sub="", items=[]),
 dict(title="Policy pulse", sub="", items=[]),
 dict(title="Conferences on the horizon", sub="dates as published", items=[]),
 dict(title="Summer schools and training", sub="", items=[QUIET]),
 dict(title="Funding radar", sub="", items=[QUIET]),
 dict(title="Buzz this week", sub="what got shared", items=[]),
 dict(title="Best reviews of the week", sub="syntheses worth your time", items=[]),
]
SECTIONS = [s for s in SECTIONS if s["items"]]

SIGNOFF_TITLE = "That's a wrap"
SIGNOFF = signoff_lines(first_issue=False)
DISCLAIMER = "Summaries draw on abstracts and, where available, full text or publisher pages (accessed <date>). Preprints aren't peer reviewed. Check sources before citing."
IMPRINT = "<PKND_003_2026-11-08> \u00b7 Neurodynamics Digest for P. Kleine \u00b7 Neurodynamics Engineering Desk, London"
