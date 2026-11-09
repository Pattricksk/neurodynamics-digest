#!/usr/bin/env python3
"""Pre-send checks for a built issue: size limits, no CJK text, no barcodes, no light backgrounds, no bro voice markers, Best reviews then Catch-up present.
Usage: python3 check_issue.py issue-003-compact.html [issue-003-full.html issue-003.txt]"""
import re, sys, os
bad = 0
for f in sys.argv[1:]:
    s = open(f, encoding="utf-8").read(); kb = os.path.getsize(f) / 1024
    msgs = []
    if f.endswith("compact.html") and kb > 80: msgs.append(f"compact HTML is {kb:.1f} KB (hard limit 80, target <60)")
    if re.search(r"[\u2E80-\u2FFF\u3000-\u30FF\u3100-\u9FFF\uAC00-\uD7AF\uF900-\uFAFF\uFF00-\uFFEF]", s): msgs.append("CJK characters found")
    if "barcode" in s.lower() or len(re.findall(r'<td width="[1-4]" bgcolor', s)) > 8: msgs.append("barcode-like markup")
    if re.search(r'(background(-color)?\s*:\s*|bgcolor\s*=\s*")#(fff|ffffff|fafafa|f5f5f5|f7f5f0)\b', s, re.I): msgs.append("light background")
    if re.search(r"\bbro\b|\bbruh\b", s, re.I): msgs.append("possible bro-voice wording")
    if f.endswith(".html") and "Best reviews of the week" not in s: msgs.append("missing 'Best reviews of the week'")
    if f.endswith(".html") and "Catch-up" not in s: msgs.append("missing 'Catch-up' section")
    if f.endswith(".html") and "Catch-up" in s and "Best reviews of the week" in s and s.rfind("Best reviews of the week") > s.rfind("Catch-up"): msgs.append("'Catch-up' should come after 'Best reviews of the week'")
    print(f"{f}: {kb:.1f} KB", "OK" if not msgs else "; ".join(msgs)); bad += len(msgs)
sys.exit(1 if bad else 0)
