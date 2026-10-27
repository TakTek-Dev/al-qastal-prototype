"""Build every page of the prototype from tools/edition.json.

python -I tools/build.py
home (index.html), the gates index and one page per gate or quarter, one page per corner, one page per
story, about, send us news, search (+ assets/search.json), credits, identity, 404.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))   # -I leaves the script's folder off the path
import shell as sh  # noqa: E402
from shell import C, CORNER, CORNERS, E, GATE, GATES, PH, S, BY, ZONES, esc

PER_PERSON = ('martyrs', 'prisoners')


# ---------------------------------------------------------------- shared pieces
def fig_kind(f):
    t = (f.get('label', '') + ' ' + f.get('source', '')).lower()
    for k, words in (('prisoners', ('prisoner', 'detain', 'detention', 'custody')), ('exiled', ('ban', 'deport', 'expel', 'exile')),
                     ('aqsa', ('aqsa', 'storm', 'incursion')), ('martyrs', ('killed', 'martyr', 'death')),
                     ('jerusalem', ('demoli', 'home', 'arrest', 'settlement', 'housing'))):
        if any(w in t for w in words):
            return k
    return 'jerusalem'


FIGS = {}
for f in E['figures']:
    FIGS.setdefault(fig_kind(f), []).append(f)


def fact(f):
    src = f'<a href="{esc(f["url"])}" rel="noopener" target="_blank">{esc(f.get("source", ""))}</a>' if f.get('url') else esc(f.get('source', ''))
    when = f', {sh.day(f["date"], year=True)}' if f.get('date') else ''
    return f'<div><b class="num">{esc(f["value"])}</b><span>{esc(f["label"])}</span><small>{src}{when}</small></div>'


def sec_h(title, sub='', more=None, h='h2', tw=True):
    m = f'<a class="more" href="{more[1]}">{esc(more[0])}{sh.icon("i-right")}</a>' if more else ''
    p = f'<p>{esc(sub)}</p>' if sub else ''
    return f'<div class="sec-h"><div><{h}>{sh.tower() if tw else ""}{esc(title)}</{h}>{p}</div>{m}</div>'


def kick_plain(s):
    """The kicker inside a link: no nested anchors."""
    c = CORNER[s['corner']]
    pl = f'<span>{esc(s["place"])}</span>' if s.get('place') else ''
    return f'<p class="kick"><span class="c" style="--cc:{c[4]}">{esc(c[1])}</span>{pl}{sh.tdate(s)}</p>'


def row(s, h='h3'):
    return (f'<li><a class="row-s" href="{sh.link(s["id"])}"><div>{kick_plain(s)}<{h} class="hl">{esc(s["headline"])}</{h}></div>'
            f'{sh.picture(s, sizes="112px")}</a></li>')


def card(s, h='h3', sf=True):
    return (f'<article class="card rv"><a href="{sh.link(s["id"])}">{sh.picture(s, sizes="(max-width:640px) 100vw, 33vw")}</a>'
            f'{sh.kick(s)}<{h} class="hl"><a href="{sh.link(s["id"])}">{esc(s["headline"])}</a></{h}>'
            + (f'<p class="sf">{esc(s["standfirst"])}</p>' if sf and s.get('standfirst') else '') + '</article>')


def feed_item(s):
    return (f'<li class="rv"><a href="{sh.link(s["id"])}" tabindex="-1" aria-hidden="true">{sh.picture(s, sizes="(max-width:640px) 100vw, 240px")}</a>'
            f'<div>{sh.kick(s)}<h2 class="hl"><a href="{sh.link(s["id"])}">{esc(s["headline"])}</a></h2>'
            + (f'<p class="sf">{esc(s["standfirst"])}</p>' if s.get('standfirst') else '') + '</div></li>')


def gate_count(key):
    return len(sh.stories(gate=key))


def door(key, light=False, sizes='(max-width:767px) 72vw, 260px'):
    g = GATE[key]
    ss = sh.stories(gate=key)
    ph = E['gate_photo'].get(key)
    img = sh.photo(ph, sizes=sizes, cls='') if ph else ''
    n = len(ss)
    cnt = f'<span class="cnt">{n} {"story" if n == 1 else "stories"}</span>' if n else ''
    last = (f'<span class="last">{esc(ss[0]["headline"])}<time datetime="{ss[0]["date"]}">{esc(sh.ago(ss[0]))}</time></span>'
            if ss else f'<span class="last">{esc(g[4])}</span>')
    return (f'<a class="door" href="{sh.glink(key)}"><span class="dw"><span class="arch">{img}{cnt}</span>{sh.swing()}</span>'
            f'<span class="gname">{esc(g[1])}<small>{esc(g[2])} · {esc(g[4])}</small></span>{last}</a>')


def person_rows(p, s):
    rows = []
    if p.get('age'):
        rows.append(('Age', str(p['age'])))
    if s['corner'] == 'martyrs':
        rows.append(('Place', s.get('place') or '—'))
        rows.append(('Date', sh.day(s['date'], year=True)))
    else:
        for k, lab in (('sentence', 'Sentence'), ('prison', 'Prison'), ('arrested', 'Arrested')):
            v = p.get(k)
            if v:
                rows.append((lab, sh.day(v, year=True) if k == 'arrested' and re.match(r'\d{4}-\d\d-\d\d$', v) else v))
        if s.get('place'):
            rows.append(('From', s['place']))
    return ''.join(f'<dt>{esc(a)}</dt><dd>{esc(b)}</dd>' for a, b in rows)


def frame(s):
    p = s['person']
    status = p.get('status') or ''
    ph = s.get('photo') or E['gate_photo'].get(s.get('gate') or '')
    img = sh.photo(ph, sizes='(max-width:1023px) 50vw, 300px', cls='') if ph else ''
    note = f'<span class="place-note">{esc(PH[ph]["place"] or "")}, file photo</span>' if img else f'<span class="no-ph">{sh.tower()}</span>'
    src = s['sources'][0] if s.get('sources') else None
    return (f'<article class="frame rv"><a href="{sh.link(s["id"])}" class="niche" aria-label="{esc(p["name"])}">{img}{note}</a>'
            f'<div class="band"><b>{esc(p["name"])}</b><span>{esc(status.capitalize())}</span></div>'
            f'<dl>{person_rows(p, s)}</dl>'
            + (f'<p class="src">Source: {sh.src_link(src)}</p>' if src else '') + '</article>')


def months(length):
    m = re.search(r'(\d+)\s*(day|week|month|year)', (length or '').lower())
    if not m:
        return 50
    n, u = int(m.group(1)), m.group(2)
    mo = n / 30 if u == 'day' else n / 4.3 if u == 'week' else n if u == 'month' else n * 12
    return max(4, min(100, round(mo / 12 * 100)))


def order(s):
    p = s.get('person') or {}
    ban = p.get('ban') or {}
    return (f'<article class="order rv"><span class="from">Banned from {esc(ban.get("from") or "Al-Aqsa")}</span>'
            f'<b>{esc(p.get("name") or "")}</b><span class="who">{esc(s.get("place") or "")}</span>'
            f'<a href="{sh.link(s["id"])}">{esc(s["headline"])}</a>'
            f'<div class="len"><span>{esc(ban.get("length") or "Length not stated")}</span>{sh.tdate(s)}</div>'
            f'<div class="bar" aria-hidden="true"><i style="--w:{months(ban.get("length"))}%"></i></div></article>')


def quotes(limit=None):
    out = []
    for s in S:
        q = s.get('quote')
        if q and q.get('text'):
            out.append((s, q))
    return out[:limit] if limit else out


def said(items):
    return '<div class="said">' + ''.join(
        f'<blockquote class="rv"><q>{esc(q["text"])}</q><cite><b>{esc(q.get("who") or "")}</b>'
        f'{", " + esc(q["role"]) if q.get("role") else ""} · {esc(sh.day(q.get("date") or s["date"], year=True))} · '
        f'<a href="{sh.link(s["id"])}">the story</a></cite></blockquote>' for s, q in items) + '</div>'


def outlet(s):
    he = f'<span lang="he">{esc(s["outlet_he"])}</span>' if s.get('outlet_he') else ''
    return f'<div class="out">{he}{esc((s.get("sources") or [{}])[0].get("name", ""))}</div>'


def hebrew(items):
    return '<ul class="list heb">' + ''.join(
        f'<li class="rv">{outlet(s)}<div><h3 class="hl"><a href="{sh.link(s["id"])}">{esc(s["headline"])}</a></h3>'
        f'<p>{esc(sh.day(s["date"], year=True))}</p></div></li>' for s in items) + '</ul>'


def headline_li(s):
    return f'<li><h3 class="hl" style="font-size:19px"><a href="{sh.link(s["id"])}">{esc(s["headline"])}</a></h3>{kick_plain(s)}</li>'


# ---------------------------------------------------------------- home
def home():
    C.R = ''
    lead = BY[E['lead']]
    top = [BY[i] for i in E.get('top', []) if i in BY and i != lead['id']]
    if len(top) < 5:
        top += [s for s in S if s['corner'] in ('jerusalem', 'aqsa') and s['id'] != lead['id'] and s not in top][:5 - len(top)]
    fg = lead.get('figure')
    first = f'''<section class="first" aria-label="The first story"><div class="wrap"><div class="grid">
<article class="lead"><a href="{sh.link(lead["id"])}">{sh.picture(lead, sizes="(max-width:1023px) 100vw, 60vw", eager=True, stamped=True)}</a>
{sh.kick(lead)}<h1 class="hl"><a href="{sh.link(lead["id"])}">{esc(lead["headline"])}</a></h1>
<p class="sf">{esc(lead.get("standfirst") or "")}</p>
{f'<div class="fig"><b class="fig-n num">{esc(fg["value"])}</b><span class="fig-l">{esc(fg["label"])}</span></div>' if fg else ''}
</article>
<aside aria-label="Also in Jerusalem today"><ul class="stack">{"".join(row(s) for s in top[:5])}</ul></aside>
</div></div></section>'''

    # the gates: places with news, latest first
    seen = []
    for s in S:
        g = sh.gate_of(s)
        if g and g not in seen:
            seen.append(g)
    rail = ''.join(f'<li>{door(k)}</li>' for k in seen)
    gates = f'''<section class="gates on-ink" data-rail><div class="wrap">
<div class="sec-h"><div><h2>{sh.tower()}The gates</h2><p>The latest from each gate and quarter of the city, newest first. Open a door for everything that happened there.</p></div><div class="rail-ctl"><button type="button" data-prev aria-label="Earlier gates">{sh.icon("i-left")}</button><button type="button" data-next aria-label="More gates">{sh.icon("i-right")}</button></div></div>
<ul class="rail">{rail}</ul>
<p class="gates-foot"><span>{len(seen)} of {len(GATES)} places have news in this edition.</span><a href="gates.html">Every gate and quarter</a></p>
</div></section>'''

    def vigil(corner, cls, title, sub, more):
        people = [s for s in sh.stories(corner) if s.get('person')]
        figs = FIGS.get(corner, [])
        head_n = figs[0] if figs else None
        cnt = (f'<div class="count"><b class="num">{esc(head_n["value"])}</b><span>{esc(head_n["label"])}</span></div>' if head_n else '')
        rest = figs[1:5]
        facts = f'<div class="facts">{"".join(fact(f) for f in rest)}</div>' if rest else ''
        news = [s for s in sh.stories(corner) if not s.get('person')][:3]
        nl = f'<ul class="list" style="margin-top:36px">{"".join(headline_li(s) for s in news)}</ul>' if news else ''
        return f'''<section class="vigil {cls} on-ink"><div class="wrap">
{sec_h(title, sub, more)}{cnt}
<div class="frames">{"".join(frame(s) for s in people[:4])}</div>{facts}{nl}
</div></section>'''

    martyrs = vigil('martyrs', 'm', 'Martyrs of Jerusalem', 'The frame and the name, as Al-Qastal publishes them: where and when, and who recorded it.', ('Every name', 'martyrs.html'))
    prisoners = vigil('prisoners', 'p', 'Prisoners of Jerusalem', 'The name on the yellow band and the arrest card under it: the sentence, the prison, the date they were taken.', ('The prisoners’ corner', 'prisoners.html'))

    aq = sh.stories('aqsa')
    aqsa = ''
    if aq:
        a0 = aq[0]
        tally = ''.join(fact(f) for f in FIGS.get('aqsa', [])[:4])
        aqsa = f'''<section class="sec tint aqsa"><div class="wrap">
{sec_h('Al-Aqsa', 'The mosque and its gates: who was let in, who was kept out, and the counts the Waqf and the governorate keep.', ('The Al-Aqsa corner', 'aqsa.html'))}
<div class="grid"><article class="rv"><a href="{sh.link(a0["id"])}">{sh.picture(a0, cls="ph r32", sizes="(max-width:1023px) 100vw, 55vw", stamped=True)}</a>{sh.kick(a0)}<h3 class="hl" style="font-size:clamp(24px,2.4vw,32px);margin-top:10px"><a href="{sh.link(a0["id"])}">{esc(a0["headline"])}</a></h3><p class="sf" style="margin-top:10px">{esc(a0.get("standfirst") or "")}</p></article>
<div>{f'<div class="tally">{tally.replace("<div><b", "<div class=rv><b")}</div>' if tally else ''}<ul class="stack" style="margin-top:24px">{"".join(row(s) for s in aq[1:4])}</ul></div></div>
</div></section>'''

    ex = [s for s in sh.stories('exiled') if (s.get('person') or {}).get('ban')]
    exf = FIGS.get('exiled', [])
    exiled = ''
    if ex or sh.stories('exiled'):
        extra = ''.join(row(s) for s in sh.stories('exiled') if s not in ex)
        exiled = f'''<section class="sec"><div class="wrap">
{sec_h('Banned and exiled', 'The order as it is handed over: kept out of where, for how long, and who received it.', ('The exiled corner', 'exiled.html'))}
{f'<div class="tally" style="margin:0 0 24px">{"".join(fact(f) for f in exf[:2])}</div>' if exf else ''}
<div class="orders">{"".join(order(s) for s in ex[:4])}</div>
{f'<ul class="stack" style="margin-top:28px">{extra}</ul>' if extra else ''}
</div></section>'''

    st = [x for x in quotes() if x[0]['corner'] == 'statements'] or quotes()
    heb = sh.stories('hebrew')
    voices = f'''<section class="sec tint"><div class="wrap"><div class="split">
<div>{sec_h('Statements', 'The sentence as it was said.', ('All statements', 'statements.html'))}{said(st[:3])}</div>
<div>{sec_h('From the Hebrew press', 'What the Israeli papers say about Jerusalem, in English.', ('All translations', 'hebrew.html'))}{hebrew(heb[:4])}</div>
</div></div></section>'''

    wb, gz = sh.stories('westbank'), sh.stories('gaza')
    country = f'''<section class="sec"><div class="wrap">
{sec_h('Beyond the city', 'The West Bank and Gaza, when the news reaches Jerusalem’s doorstep or the whole country.', ('West Bank', 'westbank.html'))}
<div class="cards c4">{"".join(card(s, sf=False) for s in (wb[:2] + gz[:2]))}</div>
<p style="margin-top:20px"><a class="more" href="gaza.html">Gaza{sh.icon("i-right")}</a></p>
</div></section>'''

    pics = [p for p in E.get('pictures', []) if p in PH][:5]
    pictures = ''
    if pics:
        pictures = f'''<section class="sec"><div class="wrap">
{sec_h('In pictures', 'The city as photographers recorded it, captioned with the real place and date.')}
<div class="pics">{"".join(f'<figure class="rv">{sh.photo(p, sizes="(max-width:900px) 50vw, 33vw", cls="ph")}<figcaption>{sh.caption(p)}</figcaption></figure>' for p in pics)}</div>
</div></section>'''

    body = first + gates + martyrs + prisoners + aqsa + exiled + voices + country + pictures
    sh.write('index.html', sh.page('Al-Qastal', 'Jerusalem first: the city’s news gate by gate and quarter by quarter, in English.', body, current='index'))


# ---------------------------------------------------------------- corners
def side_boxes(items, corner=None):
    gates = []
    for s in items:
        g = sh.gate_of(s)
        if g and g not in gates:
            gates.append(g)
    gl = ''.join(f'<li><a href="{sh.glink(g)}">{esc(GATE[g][1])}</a> <span class="num" style="color:var(--mute)">· {sum(1 for s in items if s.get("gate") == g)}</span></li>' for g in gates[:10])
    figs = FIGS.get(corner, []) if corner else []
    ff = ''.join(f'<li><b class="num" style="font-size:22px;display:block">{esc(f["value"])}</b>{esc(f["label"])}</li>' for f in figs[:4])
    others = ''.join(f'<li><a href="{C.R}{k}.html">{esc(l)}</a></li>' for k, l, *_ in CORNERS if k != corner)
    return ('<aside class="side">'
            + (f'<div class="box"><h2>Where it happened</h2><ul>{gl}</ul></div>' if gl else '')
            + (f'<div class="box"><h2>The numbers</h2><ul>{ff}</ul></div>' if ff else '')
            + f'<div class="box"><h2>Other corners</h2><ul>{others}</ul></div></aside>')


def corner_page(c):
    C.R = ''
    key, tab, title, sub, _ = c
    items = sh.stories(key)
    tone = ' red' if key == 'martyrs' else ' blue' if key == 'prisoners' else ''
    figs = FIGS.get(key, [])
    meta = (f'<div class="meta"><div><b class="num">{len(items)}</b><span>stories</span></div>'
            + (f'<div><b class="num">{esc(figs[0]["value"])}</b><span>{esc(figs[0]["label"])}</span></div>' if figs else '') + '</div>')
    bgp = next((s['photo'] for s in items if s.get('photo')), None)
    bg = f'<div class="bg" aria-hidden="true">{sh.photo(bgp, cls="", sizes="100vw")}</div>' if bgp and not tone else ''
    head = (f'<section class="chead{tone} on-ink">{bg}<div class="wrap"><div><p class="crumb"><a href="index.html">Today</a><span>/</span><span>Corner</span></p>'
            f'<h1>{sh.tower()}{esc(title)}</h1><p>{esc(sub)}</p></div>{meta}</div></section>')
    extra = ''
    if key in PER_PERSON:
        people = [s for s in items if s.get('person')]
        if people:
            cls = 'm' if key == 'martyrs' else 'p'
            facts = ''.join(fact(f) for f in figs[:4])
            extra = (f'<section class="vigil {cls} on-ink" style="padding-top:48px"><div class="wrap">'
                     f'<div class="frames" style="margin-top:0">{"".join(frame(s) for s in people)}</div>'
                     + (f'<div class="facts">{facts}</div>' if facts else '') + '</div></section>')
        items = [s for s in items if not s.get('person')] or items
    if key == 'exiled':
        ex = [s for s in items if (s.get('person') or {}).get('ban')]
        if ex:
            extra = f'<section class="sec tint"><div class="wrap"><div class="orders">{"".join(order(s) for s in ex)}</div></div></section>'
    if key == 'statements':
        body_list = said(quotes()) if quotes() else ''
        main = f'<div class="wrap"><div class="feed"><div class="main">{body_list}</div>{side_boxes(items, key)}</div></div>'
    elif key == 'hebrew':
        main = f'<div class="wrap"><div class="feed"><div class="main">{hebrew(items)}</div>{side_boxes(items, key)}</div></div>'
    else:
        main = (f'<div class="wrap"><div class="feed"><ul class="main">{"".join(feed_item(s) for s in items)}</ul>'
                f'{side_boxes(sh.stories(key), key)}</div></div>')
    sh.write(f'{key}.html', sh.page(title, sub, head + extra + main, current=key))


# ---------------------------------------------------------------- gates
def gates_index():
    C.R = ''
    zones = ''.join(
        f'<section class="zone"><h2>{esc(t)} <span style="font-weight:500;color:var(--mute);font-size:16px">· {esc(d)}</span></h2>'
        f'<div class="doors light">{"".join(door(k, light=True, sizes="(max-width:640px) 50vw, 25vw") for k, _, _, z, _ in GATES if z == zk)}</div></section>'
        for zk, t, d in ZONES)
    head = ('<section class="chead on-ink"><div class="wrap"><div><p class="crumb"><a href="index.html">Today</a><span>/</span><span>Places</span></p>'
            f'<h1>{sh.tower()}Gates and quarters</h1><p>Al-Qastal files every story under the place it happened: the gates of the Old City and of the mosque, '
            'the quarters around the walls, and the neighbourhoods the wall cut off.</p></div>'
            f'<div class="meta"><div><b class="num">{len(GATES)}</b><span>places</span></div><div><b class="num">{len(S)}</b><span>stories</span></div></div></div></section>')
    sh.write('gates.html', sh.page('Gates and quarters', 'Every gate and quarter of Jerusalem, with the latest story from each.',
                                   head + f'<div class="wrap page-in">{zones}</div>', current='gates'))


def gate_page(g):
    C.R = '../'
    key, name, ar, zone, where = g
    items = sh.stories(gate=key)
    ph = E['gate_photo'].get(key)
    bg = f'<div class="bg" aria-hidden="true">{sh.photo(ph, cls="", sizes="100vw")}</div>' if ph else ''
    zt = next(z[1] for z in ZONES if z[0] == zone)
    head = (f'<section class="chead on-ink">{bg}<div class="wrap"><div><p class="crumb"><a href="../gates.html">Gates and quarters</a><span>/</span><span>{esc(zt)}</span></p>'
            f'<h1>{sh.tower()}{esc(name)}</h1><p>{esc(ar)} · {esc(where)}.'
            + (f' {len(items)} {"story" if len(items) == 1 else "stories"} filed here.' if items else ' Nothing filed here in this edition yet.') + '</p></div>'
            f'<div class="meta"><div><b class="num">{len(items)}</b><span>stories</span></div></div></div></section>')
    same = [x for x in GATES if x[3] == zone and x[0] != key]
    nb = ''.join(f'<li><a href="{x[0]}.html">{esc(x[1])}</a> <span class="num" style="color:var(--mute)">· {gate_count(x[0])}</span></li>' for x in same)
    capt = f'<div class="box"><h2>The photograph</h2><p style="font-size:14px;color:var(--mute)">{sh.caption(ph)}</p></div>' if ph else ''
    side = f'<aside class="side">{capt}<div class="box"><h2>{esc(zt)}</h2><ul>{nb}</ul></div><div class="box"><h2>All places</h2><ul><li><a href="../gates.html">Every gate and quarter</a></li></ul></div></aside>'
    main = (f'<div class="wrap"><div class="feed"><ul class="main">{"".join(feed_item(s) for s in items) or "<li><p class=sf>No story from here in this edition. The page fills as the newsroom files under this place.</p></li>"}</ul>{side}</div></div>')
    sh.write(f'gate/{key}.html', sh.page(name, f'{name}, Jerusalem: every Al-Qastal story filed here.', head + main, current='gates'))


# ---------------------------------------------------------------- stories
def story_page(s, i):
    C.R = '../'
    c = CORNER[s['corner']]
    words = sum(len(p.split()) for p in s.get('body') or [])
    mins = max(1, round(words / 220))
    ph = s.get('photo')
    lead_ph = ''
    if ph:
        note = '' if s.get('photo_own') else 'File photo. '
        lead_ph = f'<figure class="lead-ph">{sh.photo(ph, sizes="(max-width:1300px) 100vw, 1280px", eager=True, extra=sh.stamp(s))}<figcaption>{note}{sh.caption(ph)}</figcaption></figure>'
    paras = s.get('body') or []
    prose = []
    for n, p in enumerate(paras):
        prose.append(f'<p>{esc(p)}</p>')
        if n == 1 and s.get('figure'):
            f = s['figure']
            prose.append(f'<div class="pull"><b class="fig-n num">{esc(f["value"])}</b><p class="fig-l">{esc(f["label"])}</p></div>')
        if n == 2 and s.get('quote') and s['quote'].get('text'):
            q = s['quote']
            prose.append(f'<blockquote>“{esc(q["text"])}”<cite>{esc(q.get("who") or "")}{", " + esc(q["role"]) if q.get("role") else ""}</cite></blockquote>')
    srcs = ''.join(f'<li>{sh.src_link(o)}{", " + esc(sh.day(o["date"], year=True)) if o.get("date") else ""}</li>' for o in s.get('sources') or [])
    pcard = ''
    p = s.get('person')
    if p and p.get('name'):
        m = ' m' if s['corner'] == 'martyrs' else ''
        rows = person_rows(p, s)
        ban = p.get('ban') or {}
        if ban:
            rows += f'<dt>Banned from</dt><dd>{esc(ban.get("from") or "")}</dd><dt>For</dt><dd>{esc(ban.get("length") or "not stated")}</dd>'
        pcard = f'<div class="card-p{m} on-ink"><span class="band">{esc(p["name"])}</span><dl><dt>Status</dt><dd>{esc((p.get("status") or "").capitalize())}</dd>{rows}</dl></div>'
    g = sh.gate_of(s)
    gbox = ''
    if g:
        gbox = f'<div class="box"><h2>Filed under</h2>{door(g, light=True, sizes="300px")}</div>'.replace('class="door"', 'class="door" style="color:var(--text)"')
    related = [x for x in S if x['id'] != s['id'] and (x.get('gate') == s.get('gate') or x['corner'] == s['corner'])][:3]
    rel = (f'<section class="sec" style="padding-top:56px;padding-bottom:0"><h2 style="font-size:26px;margin-bottom:20px">More from {esc(GATE[g][1] if g and any(x.get("gate") == g for x in related) else c[1])}</h2>'
           f'<div class="cards">{"".join(card(x, sf=False) for x in related)}</div></section>') if related else ''
    prev, nxt = (S[i - 1] if i > 0 else None), (S[i + 1] if i + 1 < len(S) else None)
    pn = ('<nav class="pn" aria-label="Next and previous">'
          + (f'<a href="{prev["id"]}.html"><small>Newer</small><b>{esc(prev["headline"])}</b></a>' if prev else '<span></span>')
          + (f'<a href="{nxt["id"]}.html"><small>Older</small><b>{esc(nxt["headline"])}</b></a>' if nxt else '') + '</nav>')
    body = f'''<article class="story"><div class="wrap">
<header class="hd">{sh.kick(s)}<h1 class="hl">{esc(s["headline"])}</h1>{f'<p class="sf">{esc(s["standfirst"])}</p>' if s.get("standfirst") else ''}
<p class="by"><span>By <b>Al-Qastal</b>, Jerusalem desk</span>{sh.tdate(s, long=True)}<span>{mins} min read</span></p></header>
{lead_ph}
<div class="body-grid"><div><div class="prose">{"".join(prose)}</div>
<div class="srcs"><h2 class="lbl">Sources</h2><ul>{srcs}</ul></div>{pn}</div>
<aside class="aside-sticky side">{pcard}{gbox}<div class="box"><h2>Share</h2><div class="share"><button type="button" data-copy>{sh.icon("i-link")}Copy link</button><a href="https://t.me/alqastalps" rel="noopener" target="_blank">Telegram</a></div></div></aside></div>
{rel}
</div></article>'''
    sh.write(f'story/{s["id"]}.html', sh.page(s['headline'], s.get('standfirst') or s['headline'], body, current=s['corner'], top=False))


# ---------------------------------------------------------------- utility pages
def simple(rel, title, desc, inner, current=''):
    head = (f'<section class="chead on-ink"><div class="wrap"><div><p class="crumb"><a href="{C.R}index.html">Today</a><span>/</span><span>{esc(title)}</span></p>'
            f'<h1>{sh.tower()}{esc(title)}</h1><p>{esc(desc)}</p></div></div></section>')
    sh.write(rel, sh.page(title, desc, head + f'<div class="wrap page-in">{inner}</div>', current=current))


def about():
    C.R = ''
    steps = [('01', 'Watch', 'The newsroom’s monitor reads the wires, the Jerusalem Governorate, the prisoners’ institutions, the Waqf and the Hebrew press around the clock, and files every item under its place and corner.'),
             ('02', 'Draft', 'An assistant drafts the English story with its sources attached: who said what, when, and where it was published. Nothing is published at this step.'),
             ('03', 'Edit by hand', 'An editor checks every name, number and quote against the source, adds what the machine cannot know, and publishes. Editors can also add any story by hand.')]
    inner = f'''<div class="narrow prose" style="font-size:19px"><p>Al-Qastal is a Jerusalem news platform. It covers the city first and in detail: each gate of the Old City, each quarter around the walls, each neighbourhood the wall cut off. It is named after al-Qastal, the hilltop village and fortress on the western road into Jerusalem, and its mark is a tower with its door standing open.</p>
<p>This English edition follows the corners the Arabic platform is known for: Jerusalem, Al-Aqsa, the prisoners, the martyrs, the banned and exiled, the Hebrew press and statements, with the West Bank and Gaza when they reach the city.</p></div>
<h2 style="font-size:30px;margin-top:56px">How a story gets here</h2>
<ol class="steps">{"".join(f'<li class="rv"><span class="k">{k}</span><b>{esc(t)}</b><p>{esc(d)}</p></li>' for k, t, d in steps)}</ol>
<div class="narrow" style="margin-top:56px"><h2 style="font-size:30px">Corrections</h2><p class="sf" style="margin-top:12px">When we get something wrong we correct it on the story, say what changed and when, and never quietly delete. Write to the newsroom from the <a href="submit.html" style="text-decoration:underline">send us news</a> page.</p>
<h2 style="font-size:30px;margin-top:40px">About this prototype</h2><p class="sf" style="margin-top:12px">This site is a design prototype made by TakTek. Every story in it is real and links to its sources; the photographs are from Wikimedia Commons and credited. The publishing workflow above is the one proposed for the live platform.</p></div>'''
    simple('about.html', 'About Al-Qastal', 'A Jerusalem news platform: the city first, gate by gate.', inner)


def submit():
    C.R = ''
    opts = ''.join(f'<option value="{k}">{esc(n)}</option>' for k, n, *_ in GATES)
    corners = ''.join(f'<option value="{k}">{esc(l)}</option>' for k, l, *_ in CORNERS)
    inner = f'''<div class="narrow"><p class="sf">Saw something happen in Jerusalem? Tell the newsroom. An editor reads every message, checks it, and contacts you before anything is published. You can stay anonymous.</p>
<form class="form" action="#" method="post" data-proto="Received in the prototype only. In the live site this goes to the newsroom inbox.">
<div><label for="f-what">What happened?</label><textarea id="f-what" name="what" required></textarea><p class="hint">Who, what, and what you saw yourself.</p></div>
<div class="row2"><div><label for="f-where">Where</label><select id="f-where" name="where">{opts}<option value="other">Somewhere else</option></select></div>
<div><label for="f-when">When</label><input id="f-when" name="when" type="datetime-local"></div></div>
<div class="row2"><div><label for="f-corner">Corner</label><select id="f-corner" name="corner">{corners}</select></div>
<div><label for="f-file">Photo or video <span style="font-weight:400;color:var(--mute)">(optional)</span></label><input id="f-file" name="file" type="file" accept="image/*,video/*"></div></div>
<div class="row2"><div><label for="f-name">Your name <span style="font-weight:400;color:var(--mute)">(optional)</span></label><input id="f-name" name="name" autocomplete="name"></div>
<div><label for="f-contact">Email or phone <span style="font-weight:400;color:var(--mute)">(optional)</span></label><input id="f-contact" name="contact" autocomplete="email"></div></div>
<label class="chk"><input type="checkbox" name="ok" required> I saw this or know it first-hand, and Al-Qastal may contact me to check it.</label>
<div><button class="btn y" type="submit" style="min-width:180px">{sh.icon("i-send")}Send to the newsroom</button></div>
<p class="msg" role="status"></p></form></div>'''
    simple('submit.html', 'Send us news', 'Tell the Jerusalem newsroom what you saw. Every message is read and checked.', inner)


def search():
    C.R = ''
    idx = [{'u': f'story/{s["id"]}.html', 'h': s['headline'], 'c': CORNER[s['corner']][1], 'cc': CORNER[s['corner']][4],
            'p': s.get('place') or '', 'd': sh.day(s['date'], year=True),
            't': ' '.join([s['headline'], s.get('standfirst') or '', s.get('place') or '', CORNER[s['corner']][1],
                           (s.get('person') or {}).get('name') or '', GATE.get(s.get('gate') or '', ('', '', ''))[1], GATE.get(s.get('gate') or '', ('', '', ''))[2]])}
           for s in S]
    sh.write('assets/search.json', json.dumps(idx, ensure_ascii=False))
    chips = ''.join(f'<button type="button" data-q="{q}">{q}</button>' for q in ('Silwan', 'Al-Aqsa', 'Damascus Gate', 'demolition', 'administrative detention', 'ban'))
    inner = f'''<div class="narrow"><form class="srch" data-search="assets/search.json?v={sh.V}" role="search"><label class="vh" for="q">Search Al-Qastal</label><input id="q" type="search" placeholder="A name, a place, a gate…" autocomplete="off"><button type="submit">Search</button></form>
<div class="chips">{chips}</div><div class="results" data-results aria-live="polite"></div></div>'''
    simple('search.html', 'Search', 'Every story in this edition, by name, place, gate or corner.', inner)


def credits():
    C.R = ''
    rows = ''.join(f'<li><a href="{esc(p["page_url"])}" rel="noopener" target="_blank">{esc(p["file"][5:])}</a> · {esc(p["author"])} · {esc(p["license"])} · {esc(str(p.get("date") or ""))}</li>' for p in PH.values())
    simple('credits.html', 'Photo credits', 'Every photograph on this site is from Wikimedia Commons and used under the licence shown.',
           f'<ul class="list" style="font-size:15px">{rows}</ul>')


def identity():
    C.R = ''
    t = sh.MARKS['tower']
    big = (f'<svg viewBox="-60 -40 668 860" style="width:100%;max-width:360px;margin:auto" role="img" aria-label="The tower, its parts numbered">'
           f'<path d="{t["block"]}{t["door"]}" fill="#0E1724" fill-rule="evenodd"/><path d="{t["swing"]}" fill="#FFDD36"/><path d="{t["fold"]}" fill="#EBCD38"/>'
           f'<path d="M319 550A229 229 0 0 0 548 779" fill="none" stroke="#0E1724" stroke-width="3" stroke-dasharray="10 9" transform="rotate(-90 319 550)"/>'
           + ''.join(f'<g><circle cx="{x}" cy="{y}" r="26" fill="#fff" stroke="#0E1724" stroke-width="3"/><text x="{x}" y="{y + 10}" text-anchor="middle" font-family="Host Grotesk,Arial" font-weight="700" font-size="28" fill="#0E1724">{n}</text></g>'
                     for n, x, y in ((1, 80, 470), (2, 274, 150), (3, 271, 330), (4, 470, 680)))
           + '</svg>')
    sw = [('Night', '#0E1724', 'The tower. Masthead, footer, the gates.'), ('Paper', '#FFFFFF', 'The page. Never cream.'),
          ('Stone', '#F3F5F8', 'Tinted sections; stone greys #E7EBF0, #D5DBE3.'), ('Swing', '#FFDD36', 'The client’s yellow: the open door. Fill only, never text on white.'),
          ('Fold', '#EBCD38', 'The crease on every yellow piece.'), ('Martyrs', '#BE0000', 'From the client’s template. Urgent bar and the martyrs’ band.'),
          ('Prison', '#113350', 'From the prisoners’ template. The prisoners’ corner.'), ('Mute', '#566173', 'Secondary text, 6:1 on white.')]
    swatches = ''.join(f'<div class="sw"><i style="background:{c}"></i><div><b>{n}</b><span class="num">{c}</span><p style="color:var(--mute);margin-top:4px">{esc(d)}</p></div></div>' for n, c, d in sw)
    demo = next((s for s in S if s.get('person') and s['corner'] == 'prisoners'), None) or next((s for s in S if s.get('person')), None)
    inner = f'''<section class="book">
<div class="marks"><div style="background:#0E1724;color:#fff">{sh.lockup()}</div><div style="color:#0E1724">{sh.lockup()}</div><div style="background:#FFDD36;color:#0E1724"><span style="font-size:110px;line-height:1">{sh.tower()}</span></div></div>
<div class="anat" style="margin-top:64px"><div>{big}</div><div><h2 style="font-size:34px">A tower with its door open</h2>
<p class="sf" style="margin:12px 0 24px">The client’s mark is drawn like a plan. Read that way, the yellow quarter disc under the tower is the swing of a door that stands open: the standard sign for a door on any architect’s drawing. Al-Qastal is the gatehouse on the road into Jerusalem, and the site is built on that one gesture.</p>
<ol><li><span><b>The block.</b> A corner of the site. Tabs, frames, the masthead.</span></li><li><span><b>The crenel.</b> The tower’s one cut. It stays on the mark and nowhere else.</span></li><li><span><b>The door.</b> A place in Jerusalem. Every gate and quarter is a round-headed door you open.</span></li><li><span><b>The swing.</b> The open state. It hangs from the active corner, swings open on a door you point at, and opens each section as it arrives.</span></li></ol></div></div>
<h2 style="font-size:34px;margin-top:72px">Colour</h2><div class="swatches" style="margin-top:20px">{swatches}</div>
<h2 style="font-size:34px;margin-top:72px">Type</h2>
<div class="specimen"><p class="lbl">Host Grotesk · Element Type · names, headlines, figures</p><p style="font-size:clamp(40px,6vw,76px);font-weight:700;letter-spacing:-.03em;line-height:1.05;margin-top:12px">Lions’ Gate, Silwan, Sheikh Jarrah</p><p style="font-size:22px;margin-top:10px">Chosen because the corner names had to be read at a glance, not deciphered (the client’s note on the earlier samples). Its round Q and two-storey a sit beside the Latin of the lockup.</p><p class="num" style="font-size:44px;font-weight:800;margin-top:14px">9,350 · 6 months · 27 Oct 2026</p></div>
<div class="specimen"><p class="lbl">Source Serif 4 · Adobe · reading</p><p class="prose" style="margin-top:12px;max-width:680px">Standfirsts and story text, at its text optical size, 19.5 px on 1.68. A serif for the long read keeps the grotesque for the names: the place and the person are always set in the same voice as the corner they belong to.</p></div>
<h2 style="font-size:34px;margin-top:72px">The pieces</h2>
<div class="split" style="margin-top:24px;align-items:start"><div><p class="lbl" style="margin-bottom:12px">The place stamp</p><p style="background:var(--ink);padding:24px;border-radius:14px">{sh.stamp(BY[E["lead"]])}</p>
<p class="lbl" style="margin:28px 0 12px">The gate</p><div style="max-width:260px;background:var(--ink);padding:24px 24px 64px;border-radius:14px" class="on-ink">{door(sh.gate_of(BY[E["lead"]]) or "old-city")}</div></div>
<div>{f'<p class="lbl" style="margin-bottom:12px">The frame and the band</p><div class="vigil p on-ink" style="padding:28px;border-radius:14px"><div style="max-width:300px;position:relative">{frame(demo)}</div></div>' if demo else ''}</div></div>
<h2 style="font-size:34px;margin-top:72px">Motion</h2><p class="sf" style="margin-top:12px;max-width:62ch">The first page of a visit opens through the gate: the tower stands up, its door swings open, and the page is seen through the doorway as it grows to fill the screen. Moving between pages, the next page opens out of the dark through the same door. Motion is off for anyone who asks their system for less.</p>
<p style="margin-top:20px"><a class="btn y" href="index.html?loader">Replay the opening</a></p>
</section>'''
    simple('identity.html', 'Identity', 'The tower with its door open: how Al-Qastal’s mark became the site.', inner)


def not_found():
    C.R = sh.BASE_PATH
    inner = f'<div class="narrow"><p class="sf">This door is shut: the page may have moved, or the address has a typo.</p><p style="margin-top:24px;display:flex;gap:12px;flex-wrap:wrap"><a class="btn y" href="{C.R}index.html">Today’s news</a><a class="btn ink" href="{C.R}gates.html">Every gate and quarter</a><a class="btn ink" href="{C.R}search.html">Search</a></p></div>'
    simple('404.html', 'Page not found', 'There is no page at this address.', inner)


def main():
    home()
    gates_index()
    for g in GATES:
        gate_page(g)
    for c in CORNERS:
        corner_page(c)
    for i, s in enumerate(S):
        story_page(s, i)
    about()
    submit()
    search()
    credits()
    identity()
    not_found()
    print('built', 2 + len(GATES) + len(CORNERS) + len(S) + 6, 'pages')


if __name__ == '__main__':
    main()
