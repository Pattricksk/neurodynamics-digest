# -*- coding: utf-8 -*-
"""Template constants carried over to every issue (Neurodynamics Digest)."""
SIGNOFF_NAME = "Mochi"                      # closing-panel sign-off: "— Mochi" (changed from "— Grok Bot", 27 Oct 2026)
FEEDBACK_ADDRESSES = ("<RECIPIENT_EMAIL>", "<RECIPIENT_ALT_EMAIL>")  # replace with the real addresses locally; do not commit them  # replies from either address count as feedback
def signoff_lines(first_issue=False):
    a, b = FEEDBACK_ADDRESSES
    return [
        ("Thanks for reading the first issue. " if first_issue else "Thanks for reading. ")
        + f"Reply if you'd like more or less of something, a deeper dive, or a different mix. Replies from {a} or {b}, and Grok Bot chat messages, update your brief.",
        "The next issue arrives Sunday at 19:00 (UK time).",
        "\u2014 " + SIGNOFF_NAME,
    ]
