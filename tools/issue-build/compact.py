# -*- coding: utf-8 -*-
"""Compact inline-email renderer (default output of render.py). Same look, lean markup."""
import re, html
from section_icons import icon_for, color_for, brainwave_html, HEADER_BG as HB
BG="#11161b"; P1="#1c252e"; P2="#26323d"; RU="#5f7180"; TX="#e6e9ec"; ME="#9aa7b2"; RD="#e0453b"; LK="#a9c7e0"
SANS="Arial"; MONO="monospace"
LINK=re.compile(r"\[\[(.+?)\|(.+?)\]\]")
def L(t): return LINK.sub(lambda m:f'<a href="{html.escape(m.group(2))}" style="color:{LK}">{m.group(1)}</a>',t)
def F(sz,lh,c=TX,mono=False,extra="",w=""): return f'font:{w}{sz}px/{lh}px {MONO if mono else SANS};color:{c}'+(";"+extra if extra else "")
def tag(t,k,A=RU):
    c={2:f"background-color:{RD};color:#fff;border:1px solid {RD}",1:f"color:{TX};border:1px solid {TX}"}.get(k,f"border:1px solid {A}")
    return f'<span style="{c}"> {html.escape(t)} </span> '
def tags(lst,A=RU,pre=""): return f'<span style="font:bold 11px/20px {MONO};color:{ME}">'+pre+"".join(tag(t,k,A) for t,k in lst)+'</span>'
def td(content, bg, style="", colspan=1):
    return f'<tr><td style="{style}">{content}</td></tr>'
def P(t,size=15,lh=23,c=TX): return f'<p style="margin:0 0 10px">{L(t)}</p>'
def PS(ps): return "<br><br>".join(L(p) for p in ps)
def bullet(label,text,bg):
    return (f'<tr><td width="22" valign="top" style="padding:0 0 12px 18px;color:{ME}">&#9644;</td>'
            f'<td style="padding:0 18px 12px 6px;{F(15,23)}"><b>{L(label)}</b> {L(text)}</td></tr>')
def meta(rows,A=RD):
    lab=lambda k:f'<b style="color:{A}">{k}:</b> '
    inner="<br><br>".join(lab(k)+L(v) for k,v in rows)
    return f'<table width="100%" cellpadding="8" cellspacing="0" style="background-color:{P1};border:1px solid {RU};margin:12px 0"><tr><td style="{F(14,21)}">{inner}</td></tr></table>'
def main_item(it,code,A):
    tg=tags(it["tags"],A,f'<b style="color:{A}">{html.escape(code)}</b><br>')
    body=PS(it["body"])
    refs=" &middot; ".join(f'<a href="{html.escape(u)}" style="color:{LK}">{html.escape(t)}</a>' for t,u in it["ref"])
    box=(f'<table width="100%" cellpadding="0" cellspacing="0" style="background-color:{P2};border:1px solid {RU}">'
         f'<tr><td style="padding:10px 14px 4px;{F(15,23)}">{tg}<h3 style="margin:8px 0 6px;{F(19,25,w="bold ")}">{it["head"]}</h3>'
         f'<p style="margin:0 0 10px;{F(12,18,ME,True)}">{html.escape(it["byline"])}</p>{body}'+
         meta([("CAVEATS",it["caveats"]),("WHY IT MATTERS",it["why"]),("REF / ID",refs)],A)+'</td></tr></table>')
    return td(box,P1,"padding:0 18px 16px")
def section(i,s,C):
    n=f"{i:02d}"; rows=[]; k=0; buf=[]; A=color_for(s["title"])
    def flush():
        if buf: rows.append(f'<tr><td style="padding:0 18px 20px;{F(15,23)}">'+"<br><br>".join(buf)+'</td></tr>'); buf.clear()
    for it in s["items"]:
        if it["kind"]=="short": buf.append(f'<b style="color:{ME}">\u25ac </b><b>{L(it["label"])}</b> {L(it["text"])}'); continue
        flush()
        if it["kind"]=="main": k+=1; rows.append(main_item(it,f"<PKND_{C.NUM}.{n}.{k:02d}>",A))
        else:
            inner=tags([("EXPLAINER",2),("INFO THEORY 101",0)],A)+"<br><br>"+PS(it["paras"])
            rows.append(td(f'<table width="100%" cellpadding="14" cellspacing="0" style="background-color:{P2};border:2px solid {RU}"><tr><td style="{F(15,23)}">{inner}</td></tr></table>',P1,"padding:0 18px 16px",1))
    flush()
    rows.append(f'<tr><td align="right" style="padding:0 18px 12px;font:11px {MONO}"><a href="#contents" style="color:{LK}">↑ contents</a></td></tr>')
    ic=icon_for(s["title"])
    head=(f'<tr><td id="s{n}" style="padding:0 0 14px"><a name="s{n}"></a><table width="100%" cellpadding="0" cellspacing="10" style="background-color:{HB};border-left:5px solid {A}"><tr>'
          f'<td width="40" height="40" align="center" style="background-color:{BG};border:1px solid {A};font:22px/40px Arial;color:{A}">{ic}</td>'
          f'<td style="font:bold 23px/27px {SANS};color:{TX}"><span style="color:{A}">{n}</span> {html.escape(s["title"])}<div style="font:12px/17px {MONO};color:{ME}">{html.escape(s["sub"])}</div></td></tr></table></td></tr>')
    return f'<tr><td style="padding:0 0 16px"><table width="100%" cellpadding="0" cellspacing="0" style="background-color:{P1};border:1px solid {RU}">{head}{"".join(rows)}</table></td></tr>'
def corner(b): return f'<td width="12" height="12" style="{b}font-size:0;line-height:0">&nbsp;</td>'
def render(C, preheader):
    icons=f'<tr><td style="padding:0 0 10px">{brainwave_html(MONO,ME,tstyle=f"border:1px solid {RU};",pad=6)}</td></tr>'
    c1=f"border-top:2px solid {ME};border-left:2px solid {ME};"; c2=f"border-top:2px solid {ME};border-right:2px solid {ME};"
    c3=f"border-bottom:2px solid {ME};border-left:2px solid {ME};"; c4=f"border-bottom:2px solid {ME};border-right:2px solid {ME};"
    title=(f'<tr><td style="padding:0 0 16px"><table width="100%" cellpadding="0" cellspacing="0" bgcolor="{P1}" style="background-color:{P1};border:1px solid {RU}">'
      f'<tr>{corner(c1)}<td></td>{corner(c2)}</tr><tr><td></td><td style="padding:4px 12px">'
      f'<table width="100%" cellpadding="0" cellspacing="0"><tr><td valign="top"><div style="font:bold 12px {MONO};color:{RD};letter-spacing:2px">WEEKLY SCIENCE EDIT &middot; ISSUE {C.NUM}</div>'
      f'<h1 style="margin:6px 0 2px;{F(48,52,w="bold ")}">{html.escape(C.TITLE)}</h1>'
      f'<div style="font:13px {MONO};color:{ME}">{html.escape(C.TITLE_JP)}</div></td>'
      f'<td valign="top" align="right" width="86"><table cellpadding="6" cellspacing="0" style="background-color:{P1};border:3px solid {RD}"><tr><td align="center" style="font:bold 13px/18px {MONO};color:{RD}">{C.STAMP}</td></tr></table></td></tr></table>'
      f'<div style="border-top:2px solid {RU};margin-top:10px;padding-top:8px;{F(16,22,w="bold ")}">{html.escape(C.TAGLINE)}</div>'
      f'<div style="padding:4px 0 8px;font:12px/18px {MONO};color:{ME}">{html.escape(C.COVER)}<br>EEG &middot; PSYCHEDELICS &middot; ADDICTION &middot; BRAIN&ndash;BODY &middot; COMPLEXITY &middot; INFO THEORY</div>'
      f'</td><td></td></tr><tr>{corner(c3)}<td></td>{corner(c4)}</tr></table></td></tr>')
    toc="<br>".join(f'<a href="#s{i+1:02d}" style="color:{TX}"><b style="color:{color_for(s["title"])}">{i+1:02d}</b> {html.escape(s["title"]).upper()}</a>' for i,s in enumerate(C.SECTIONS))
    intro=(f'<tr><td style="padding:0 0 16px"><table width="100%" cellpadding="16" cellspacing="0" bgcolor="{P1}" style="background-color:{P1};border:1px solid {RU}"><tr><td>'
      f'<div style="font:bold 12px {MONO};color:{RD};letter-spacing:2px;margin-bottom:8px">00 / BRIEFING</div>'
      + f'<div style="{F(16,24)}">'+PS(C.INTRO)+'</div><br>' +
      f'<table width="100%" cellpadding="8" cellspacing="0" style="background-color:{BG};border:1px solid {RU}"><tr><td style="font:12px/18px {MONO};color:{ME}">{html.escape(C.KEY)}</td></tr></table>'
      f'<div style="margin-top:12px;font:12px/19px {MONO};color:{TX}"><a name="contents"></a><b id="contents">CONTENTS</b><br>{toc}</div></td></tr></table></td></tr>')
    sign=(f'<tr><td style="padding:0 0 14px"><table width="100%" cellpadding="16" cellspacing="0" bgcolor="{P2}" style="background-color:{P2};border:2px solid {RU}"><tr><td>'
      f'<h2 style="margin:0 0 4px;{F(24,28,w="bold ")}">{html.escape(C.SIGNOFF_TITLE)}</h2><div style="font:bold 12px {MONO};color:{RD};margin-bottom:10px">END OF TRANSMISSION</div>'
      + f'<div style="{F(15,23)}">'+PS(C.SIGNOFF)+'</div></td></tr></table></td></tr>')
    foot=(f'<tr><td style="padding:0 0 8px;{F(12,18,ME)}">{html.escape(C.DISCLAIMER)}</td></tr>'
      f'<tr><td style="border-top:1px solid {RU};padding:8px 0 20px;font:11px/16px {MONO};color:{ME}">{html.escape(C.IMPRINT)}</td></tr>')
    secs="".join(section(i+1,s,C) for i,s in enumerate(C.SECTIONS))
    doc=(f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
      f'<title>{html.escape(C.SUBJECT)}</title></head><body bgcolor="{BG}" style="margin:0;padding:0;background-color:{BG}">'
      f'<div style="display:none;max-height:0;overflow:hidden">{html.escape(preheader)}</div>'
      f'<table width="100%" cellpadding="0" cellspacing="0" bgcolor="{BG}" style="background-color:{BG}"><tr><td align="center" bgcolor="{BG}" style="background-color:{BG};padding:16px 8px">'
      f'<table width="680" cellpadding="0" cellspacing="0" bgcolor="{BG}" style="width:680px;max-width:100%;background-color:{BG}">'
      f'<tr><td style="padding:0 0 8px;font:bold 13px {MONO};color:{TX}">{html.escape(C.ISSUE_CODE)} <span style="float:right;font-weight:normal;font-size:11px;color:{ME}">{html.escape(C.TOPRIGHT)} &middot; <a href="{C.VIEW_URL}" style="color:{ME}">View in browser</a></span></td></tr>'
      + icons + title + intro + secs + sign + foot + '</table></td></tr></table></body></html>')
    return re.sub(r">\s*\n\s*<","><",doc)  # keep single spaces between inline tags (tag gaps, labels)
