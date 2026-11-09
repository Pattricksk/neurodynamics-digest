# -*- coding: utf-8 -*-
import re, html, random, sys
sys.path.insert(0,'.')
import content as C
from section_icons import icon_for, color_for, brainwave_html, HEADER_BG as HB
BG="#11161b"; PANEL="#1c252e"; PANEL2="#26323d"; RULE="#5f7180"; TXT="#e6e9ec"; META="#9aa7b2"; RED="#e0453b"; LINKC="#a9c7e0"; BAR="#9aa7b2"
INK=TXT; PAPER=PANEL
SANS="Arial, Helvetica, sans-serif"; MONO="'Courier New', Courier, monospace"
LINK=re.compile(r"\[\[(.+?)\|(.+?)\]\]")
def L(t):  # html-ify inline link markup
    return LINK.sub(lambda m:f'<a href="{html.escape(m.group(2))}" style="color:{LINKC};text-decoration:underline;">{m.group(1)}</a>', t)
def esc_code(t): return html.escape(t)
def icons(n=12, sq=False):
    out=""
    for i in range(n):
        r="0" if (sq or i%3==2) else "50%"
        out+=f'<td bgcolor="{BG}" style="padding:0 3px;background-color:{BG};"><div style="width:10px;height:10px;border:2px solid {RED};border-radius:{r};background-color:{BG};font-size:0;line-height:0;">&nbsp;</div></td>'
    return f'<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>{out}</tr></table>'
def corner(pos):
    b={"tl":"border-top:2px solid #9aa7b2;border-left:2px solid #9aa7b2;","tr":"border-top:2px solid #9aa7b2;border-right:2px solid #9aa7b2;",
       "bl":"border-bottom:2px solid #9aa7b2;border-left:2px solid #9aa7b2;","br":"border-bottom:2px solid #9aa7b2;border-right:2px solid #9aa7b2;"}[pos]
    return f'<div style="width:12px;height:12px;{b}font-size:0;line-height:0;">&nbsp;</div>'
def tag(t,kind,A=None):
    if kind==1: st=f"background-color:{PANEL};color:{TXT};border:1px solid {TXT};"
    elif kind==2: st=f"background-color:{RED};color:#ffffff;border:1px solid {RED};"
    else: st=f"background-color:{BG};color:{META};border:1px solid {A or RULE};"
    return f'<span style="display:inline-block;{st}font-family:{MONO};font-size:11px;font-weight:bold;letter-spacing:1px;padding:2px 6px;margin:0 4px 4px 0;">{html.escape(t)}</span>'
def bar_item(label, text):
    return f'''<tr><td valign="top" width="26" style="padding:6px 10px 0 0;"><table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td width="18" height="6" bgcolor="{BAR}" style="width:18px;height:6px;background-color:{BAR};font-size:0;line-height:0;">&nbsp;</td></tr></table></td>
<td valign="top" style="padding:0 0 14px 0;font-family:{SANS};font-size:15px;line-height:23px;color:{INK};"><b>{L(label)}</b> {L(text)}</td></tr>'''
def meta_row(k,v,A=META):
    return f'<tr><td width="110" valign="top" bgcolor="{BG}" style="border:1px solid {RULE};padding:6px 8px;font-family:{MONO};font-size:11px;font-weight:bold;letter-spacing:1px;color:{A};background-color:{BG};">{k}</td><td valign="top" bgcolor="{PANEL}" style="border:1px solid {RULE};padding:6px 10px;font-family:{SANS};font-size:14px;line-height:21px;color:{TXT};background-color:{PANEL};">{L(v)}</td></tr>'
def main_item(it, code, A):
    tags="".join(tag(t,k,A) for t,k in it["tags"])
    body="".join(f'<p style="margin:0 0 12px 0;font-family:{SANS};font-size:15px;line-height:23px;color:{INK};">{L(p)}</p>' for p in it["body"])
    refs=" \u00b7 ".join(f'<a href="{html.escape(u)}" style="color:{LINKC};text-decoration:underline;">{html.escape(t)}</a>' for t,u in it["ref"])
    return f'''<tr><td style="padding:0 0 22px 0;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{PANEL2}" style="border-collapse:collapse;border:1px solid {RULE};background-color:{PANEL2};">
<tr><td bgcolor="{BG}" style="padding:6px 10px;border-bottom:1px solid {RULE};font-family:{MONO};font-size:11px;color:{META};background-color:{BG};"><span style="color:{A};font-weight:bold;">{esc_code(code)}</span></td></tr>
<tr><td style="padding:14px 16px 4px 16px;">{tags}
<h3 style="margin:8px 0 6px 0;font-family:{SANS};font-size:19px;line-height:25px;font-weight:bold;color:{INK};">{it["head"]}</h3>
<p style="margin:0 0 12px 0;font-family:{MONO};font-size:12px;line-height:18px;color:{META};">{html.escape(it["byline"])}</p>
{body}</td></tr>
<tr><td style="padding:0 16px 14px 16px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-collapse:collapse;">
{meta_row("CAVEATS",it["caveats"],A)}{meta_row("WHY IT<br>MATTERS<br>FOR YOU",it["why"],A)}{"".join(meta_row(k,v,A) for k,v in it.get("extra",[]))}{meta_row("REF / ID",refs,A)}</table></td></tr>
</table></td></tr>'''
def section(i, s):
    num=f"{i:02d}"; A=color_for(s["title"])
    rows=[]; n=0
    for it in s["items"]:
        if it["kind"]=="main":
            n+=1; rows.append(main_item(it, f"<PKND_{C.NUM}.{num}.{n:02d}>", A))
        elif it["kind"]=="short":
            rows.append(f'<tr><td><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">{bar_item(it["label"],it["text"])}</table></td></tr>')
        elif it["kind"]=="explainer":
            ps="".join(f'<p style="margin:0 0 12px 0;font-family:{SANS};font-size:15px;line-height:23px;color:{INK};">{p}</p>' for p in it["paras"])
            rows.append(f'<tr><td style="padding:0 0 18px 0;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{PANEL2}" style="border:2px solid {RULE};background-color:{PANEL2};"><tr><td style="padding:16px;">{tag("EXPLAINER",2)}{tag("INFO THEORY 101",0,A)}<div style="height:8px;font-size:0;line-height:0;">&nbsp;</div>{ps}</td></tr></table></td></tr>')
    return f'''<tr><td style="padding:0 20px 18px 20px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{PANEL}" style="border-collapse:collapse;background-color:{PANEL};border:1px solid {RULE};">
<tr><td id="s{num}" style="padding:0 0 16px 0;"><a name="s{num}"></a><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{HB}" style="border-collapse:collapse;background-color:{HB};border-left:6px solid {A};border-bottom:2px solid {A};"><tr>
<td valign="middle" width="64" style="padding:12px 0 12px 12px;"><table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr><td width="44" height="44" align="center" valign="middle" bgcolor="{BG}" style="width:44px;height:44px;background-color:{BG};border:1px solid {A};font-family:{SANS};font-size:24px;line-height:44px;color:{A};">{icon_for(s["title"])}</td></tr></table></td>
<td valign="middle" style="padding:12px 16px 12px 12px;"><div style="font-family:{SANS};font-size:25px;line-height:30px;font-weight:bold;color:{INK};"><span style="font-family:{MONO};color:{A};">{num}</span>&nbsp; {html.escape(s["title"])}</div>
<div style="padding-top:4px;font-family:{MONO};font-size:12px;line-height:17px;color:{META};">SEC.{num} &nbsp;/&nbsp; {html.escape(s["sub"])}</div></td></tr></table></td></tr>
<tr><td style="padding:0 18px 6px 18px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">{"".join(rows)}</table>
</td></tr>
<tr><td align="right" style="padding:0 18px 14px 18px;font-family:{MONO};font-size:11px;"><a href="#contents" style="color:{LINKC};text-decoration:underline;">&uarr; contents</a></td></tr></table></td></tr>'''

intro="".join(f'<p style="margin:0 0 12px 0;font-family:{SANS};font-size:16px;line-height:24px;color:{INK};">{p}</p>' for p in C.INTRO)
signoff="".join(f'<p style="margin:0 0 10px 0;font-family:{SANS};font-size:15px;line-height:23px;color:{INK};">{p}</p>' for p in C.SIGNOFF)
sections="".join(section(i+1,s) for i,s in enumerate(C.SECTIONS))
toc="".join(f'<tr><td style="padding:2px 0;font-family:{MONO};font-size:12px;color:{INK};"><a href="#s{i+1:02d}" style="color:{INK};text-decoration:none;"><span style="color:{color_for(s["title"])};font-weight:bold;">{i+1:02d}</span>&nbsp;&nbsp;{html.escape(s["title"]).upper()}</a></td></tr>' for i,s in enumerate(C.SECTIONS))

doc=f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="x-apple-disable-message-reformatting">
<title>{html.escape(C.SUBJECT)}</title></head>
<body bgcolor="{BG}" style="margin:0;padding:0;background-color:{BG};">
<div style="display:none;max-height:0;overflow:hidden;">{html.escape(C.PREHEADER)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{BG}" style="background-color:{BG};"><tr><td align="center" bgcolor="{BG}" style="padding:20px 8px;background-color:{BG};">
<table role="presentation" width="680" cellpadding="0" cellspacing="0" border="0" bgcolor="{BG}" style="width:680px;max-width:100%;background-color:{BG};">
<!-- spec code + icon strip -->
<tr><td style="padding:0 20px 8px 20px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td style="font-family:{MONO};font-size:13px;font-weight:bold;color:{TXT};letter-spacing:1px;">{esc_code(C.ISSUE_CODE)}</td>
<td align="right" style="font-family:{MONO};font-size:11px;color:{META};">{C.TOPRIGHT} &middot; <a href="{C.VIEW_URL}" style="color:{META};text-decoration:underline;">View in browser</a></td></tr></table></td></tr>
<tr><td style="padding:0 20px 10px 20px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{BG}" style="background-color:{BG};border:1px solid {RULE};"><tr><td style="padding:7px 10px;">{brainwave_html(MONO, META, 12, 14)}</td></tr></table></td></tr>
<!-- title panel -->
<tr><td style="padding:0 20px 18px 20px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{PANEL}" style="background-color:{PANEL};border:1px solid {RULE};">
<tr><td width="14" style="padding:6px 0 0 6px;">{corner("tl")}</td><td></td><td width="14" align="right" style="padding:6px 6px 0 0;">{corner("tr")}</td></tr>
<tr><td></td><td style="padding:6px 14px 4px 14px;">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td valign="top"><div style="font-family:{MONO};font-size:12px;color:{RED};font-weight:bold;letter-spacing:2px;">WEEKLY SCIENCE EDIT · ISSUE {C.NUM}</div>
<h1 style="margin:6px 0 2px 0;font-family:{SANS};font-size:52px;line-height:54px;font-weight:bold;color:{INK};letter-spacing:-1px;">{html.escape(C.TITLE)}</h1>
<div style="font-family:{MONO};font-size:13px;color:{META};">{C.TITLE_JP}</div></td>
<td valign="top" align="right" width="92"><table role="presentation" cellpadding="0" cellspacing="0" border="0" bgcolor="{PANEL}" style="border:3px solid {RED};background-color:{PANEL};"><tr><td align="center" style="padding:6px 8px;font-family:{MONO};font-size:13px;font-weight:bold;color:{RED};letter-spacing:2px;">{C.STAMP}</td></tr></table></td>
</tr></table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:12px;border-top:2px solid {RULE};"><tr><td style="padding:10px 0 4px 0;font-family:{SANS};font-size:16px;font-weight:bold;color:{INK};">{html.escape(C.TAGLINE)}</td></tr>
<tr><td style="padding:2px 0 10px 0;font-family:{MONO};font-size:12px;color:{META};">{html.escape(C.COVER)}</td></tr></table>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td valign="bottom" style="font-family:{MONO};font-size:10px;color:{META};letter-spacing:2px;">{C.SPECLINE}</td>
<td valign="bottom" align="right" style="font-family:{MONO};font-size:10px;line-height:15px;color:{META};">EEG · PSYCHEDELICS · ADDICTION<br>BRAIN–BODY · COMPLEXITY · INFO THEORY</td></tr></table>
</td><td></td></tr>
<tr><td style="padding:0 0 6px 6px;" valign="bottom">{corner("bl")}</td><td></td><td align="right" valign="bottom" style="padding:0 6px 6px 0;">{corner("br")}</td></tr>
</table></td></tr>
<!-- intro -->
<tr><td style="padding:0 20px 18px 20px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{PANEL}" style="background-color:{PANEL};border:1px solid {RULE};"><tr><td style="padding:18px;">
<div style="font-family:{MONO};font-size:12px;font-weight:bold;color:{RED};letter-spacing:2px;margin-bottom:8px;">00 / BRIEFING</div>
{intro}
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{BG}" style="border:1px solid {RULE};margin-top:6px;background-color:{BG};"><tr><td bgcolor="{BG}" style="padding:8px 10px;font-family:{MONO};font-size:12px;line-height:18px;color:{META};background-color:{BG};">{html.escape(C.KEY)}</td></tr></table>
<div style="height:12px;font-size:0;line-height:0;">&nbsp;</div>
<a name="contents"></a><div id="contents" style="font-family:{MONO};font-size:12px;font-weight:bold;color:{INK};letter-spacing:2px;margin-bottom:4px;">CONTENTS</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">{toc}</table>
</td></tr></table></td></tr>
{sections}
<!-- sign-off -->
<tr><td style="padding:0 20px 18px 20px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{PANEL2}" style="background-color:{PANEL2};border:2px solid {RULE};"><tr><td style="padding:18px;">
<h2 style="margin:0 0 4px 0;font-family:{SANS};font-size:24px;font-weight:bold;color:{INK};">{html.escape(C.SIGNOFF_TITLE)}</h2>
<div style="font-family:{MONO};font-size:12px;color:{RED};font-weight:bold;margin-bottom:10px;">END OF TRANSMISSION</div>
{signoff}</td></tr></table></td></tr>
<!-- footer -->
<tr><td style="padding:0 20px 8px 20px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{BG}" style="background-color:{BG};border:1px solid {RULE};"><tr><td style="padding:7px 10px;">{brainwave_html(MONO, META, 12, 14)}</td></tr></table></td></tr>
<tr><td style="padding:4px 20px 6px 20px;font-family:{SANS};font-size:12px;line-height:18px;color:{META};">{html.escape(C.DISCLAIMER)}</td></tr>
<tr><td style="padding:6px 20px 24px 20px;"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-top:1px solid {RULE};"><tr>
<td style="padding-top:8px;font-family:{MONO};font-size:11px;line-height:16px;color:{META};">{html.escape(C.IMPRINT)}</td>
</tr></table></td></tr>
</table></td></tr></table></body></html>'''
# Default: compact inline-email version (use for regular issues). --full also writes the large attachment version.
import compact
PRE=C.PREHEADER
_out=[a.split("=",1)[1] for a in sys.argv if a.startswith("--out=")]
open(_out[0] if _out else C.OUT_COMPACT,'w').write(compact.render(C, PRE))
if "--full" in sys.argv:
    open(C.OUT_FULL,'w').write(doc)

# ---------- plain text ----------
def T(t):
    t=LINK.sub(lambda m:f"{m.group(1)} <{m.group(2)}>", t)
    t=re.sub(r"<[^>]+>","",t); return html.unescape(t)
import textwrap
W=lambda t,ind="": textwrap.fill(T(t),78,initial_indent=ind,subsequent_indent=ind)+"\n"
out=[f"Subject: {C.SUBJECT}\n", C.ISSUE_CODE, "="*78, C.TITLE.upper()+"  "+C.TITLE_JP, C.TAGLINE, C.COVER, "="*78,""]
for p in C.INTRO: out.append(W(p))
out.append(C.KEY+"\n")
out.append("CONTENTS")
for i,s in enumerate(C.SECTIONS): out.append(f"  {i+1:02d}  {s['title']}")
out.append("")
for i,s in enumerate(C.SECTIONS):
    out+=["-"*78, f"{i+1:02d} / {s['title'].upper()}  - {s['sub']}", "-"*78, ""]
    for it in s["items"]:
        if it["kind"]=="main":
            out.append("["+"] [".join(t for t,_ in it["tags"])+"]")
            out.append(W(it["head"]).upper())
            out.append(it["byline"]+"\n")
            for p in it["body"]: out.append(W(p))
            out.append(W("Caveats: "+it["caveats"]))
            out.append(W("Why it matters for you: "+it["why"]))
            for k,v in it.get("extra",[]): out.append(W(k.replace("<br>"," ").title()+": "+v))
            out.append("Links: "+" | ".join(f"{t} <{u}>" for t,u in it["ref"])+"\n")
        elif it["kind"]=="short":
            out.append(W(f"<b>{it['label']}</b> {it['text']}","  ").replace("  ","  ",1).replace("  ","- ",1))
        else:
            for p in it["paras"]: out.append(W(p))
out+=["-"*78, C.SIGNOFF_TITLE.upper(), ""]
for p in C.SIGNOFF: out.append(W(p))
out+=["-"*78, W(C.DISCLAIMER), C.IMPRINT]
open(C.OUT_TXT,'w').write("\n".join(out))
print("main items:",sum(1 for s in C.SECTIONS for it in s["items"] if it["kind"]=="main"),
      "short:",sum(1 for s in C.SECTIONS for it in s["items"] if it["kind"]=="short"))
