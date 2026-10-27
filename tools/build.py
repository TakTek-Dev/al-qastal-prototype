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
from shell import C, CORNER, CORNERS, E, GATE, GATES, PH, S, BY, ZONES, esc  # noqa: E402

PER_PERSON = ('martyrs', 'prisoners')
FIGS = {}
for f in E['figures']:
    FIGS.setdefault(f['kind'], []).append(f)


# ---------------------------------------------------------------- shared pieces
def fact(f):
    src = f'<a href="{esc(f["url"])}" rel="noopener" target="_blank">{esc(f.get("source", ""))}</a>' if f.get('url') else esc(f.get('source', ''))
    when = f'، {sh.day(f["date"], year=True)}' if f.get('date') else ''
    return f'<div><b class="num">{sh.num(f["value"])}</b><span>{esc(f["label"])}</span><small>{src}{when}</small></div>'


def sec_h(title, sub='', more=None, h='h2', tw=True):
    m = f'<a class="more" href="{more[1]}">{esc(more[0])}{sh.icon("i-fwd")}</a>' if more else ''
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
    return (f'<article class="card rv"><a href="{sh.link(s["id"])}" tabindex="-1" aria-hidden="true">{sh.picture(s, sizes="(max-width:640px) 100vw, 33vw")}</a>'
            f'{sh.kick(s)}<{h} class="hl"><a href="{sh.link(s["id"])}">{esc(s["headline"])}</a></{h}>'
            + (f'<p class="sf">{esc(s["standfirst"])}</p>' if sf and s.get('standfirst') else '') + '</article>')


def feed_item(s):
    return (f'<li class="rv"><a href="{sh.link(s["id"])}" tabindex="-1" aria-hidden="true">{sh.picture(s, sizes="(max-width:640px) 100vw, 240px")}</a>'
            f'<div>{sh.kick(s)}<h2 class="hl"><a href="{sh.link(s["id"])}">{esc(s["headline"])}</a></h2>'
            + (f'<p class="sf">{esc(s["standfirst"])}</p>' if s.get('standfirst') else '') + '</div></li>')


def gate_count(key):
    return len(sh.stories(gate=key))


def door(key, sizes='(max-width:767px) 72vw, 260px'):
    g = GATE[key]
    ss = sh.stories(gate=key)
    ph = E['gate_photo'].get(key)
    img = sh.photo(ph, sizes=sizes, cls='') if ph else ''
    n = len(ss)
    cnt = f'<span class="cnt">{sh.stories_n(n)}</span>' if n else ''
    last = (f'<span class="last">{esc(ss[0]["headline"])}<time datetime="{ss[0]["date"]}">{esc(sh.ago(ss[0]))}</time></span>'
            if ss else f'<span class="last">{esc(g[4])}</span>')
    second = '' if g[2] == g[1] else f'{esc(g[2])} · '
    return (f'<a class="door" href="{sh.glink(key)}"><span class="dw"><span class="arch">{img}{cnt}</span>{sh.swing("m")}</span>'
            f'<span class="gname">{esc(g[1])}<small>{second}{esc(g[4])}</small></span>{last}</a>')


def person_rows(p, s):
    rows = []
    if p.get('age'):
        rows.append(('العمر', str(p['age'])))
    if s['corner'] == 'martyrs':
        rows.append(('المكان', s.get('place') or '—'))
        rows.append(('التاريخ', sh.day(s['date'], year=True)))
    else:
        for k, lab in (('sentence', 'الحكم'), ('prison', 'السجن'), ('arrested', 'الاعتقال')):
            v = p.get(k)
            if v:
                rows.append((lab, sh.day(v, year=True) if k == 'arrested' and re.match(r'\d{4}-\d\d-\d\d$', v) else v))
        if s.get('place'):
            rows.append(('من', s['place']))
    return ''.join(f'<dt>{esc(a)}</dt><dd>{esc(b)}</dd>' for a, b in rows)


def frame(s):
    p = s['person']
    ph = s.get('photo') or E['gate_photo'].get(s.get('gate') or '')
    img = sh.photo(ph, sizes='(max-width:1023px) 50vw, 300px', cls='') if ph else ''
    note = f'<span class="place-note">{esc(PH[ph]["place"] or "")}، صورة أرشيفية</span>' if img else f'<span class="no-ph">{sh.tower()}</span>'
    src = s['sources'][0] if s.get('sources') else None
    return (f'<article class="frame rv"><a href="{sh.link(s["id"])}" class="niche" aria-label="{esc(p["name"])}">{img}{note}</a>'
            f'<div class="band"><b>{esc(p["name"])}</b><span>{esc(p.get("status") or "")}</span></div>'
            f'<dl>{person_rows(p, s)}</dl>'
            + (f'<p class="src">المصدر: {sh.src_link(src)}</p>' if src else '') + '</article>')


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
    return (f'<article class="order rv"><span class="from">إبعاد عن {esc(ban.get("from") or "الأقصى")}</span>'
            f'<b>{esc(p.get("name") or "")}</b><span class="who">{esc(s.get("place") or "")}</span>'
            f'<a href="{sh.link(s["id"])}">{esc(s["headline"])}</a>'
            f'<div class="len"><span>{esc(ban.get("length") or "المدة غير معلنة")}</span>{sh.tdate(s)}</div>'
            f'<div class="bar" aria-hidden="true"><i style="--w:{months(ban.get("length_en"))}%"></i></div></article>')


def quotes(limit=None):
    out = [(s, s['quote']) for s in S if s.get('quote') and s['quote'].get('text')]
    return out[:limit] if limit else out


def said(items):
    return '<div class="said">' + ''.join(
        f'<blockquote class="rv"><q>{esc(q["text"])}</q><cite><b>{esc(q.get("who") or "")}</b>'
        f'{"، " + esc(q["role"]) if q.get("role") else ""} · {esc(sh.day(q.get("date") or s["date"], year=True))}'
        f'{" · ترجمة القسطل" if q.get("translated") else ""} · <a href="{sh.link(s["id"])}">الخبر</a></cite></blockquote>' for s, q in items) + '</div>'


def outlet(s):
    he = f'<span lang="he" dir="rtl">{esc(s["outlet_he"])}</span>' if s.get('outlet_he') else ''
    return f'<div class="out">{he}{esc(s.get("outlet_ar") or (s.get("sources") or [{}])[0].get("name", ""))}</div>'


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
    ph = lead.get('photo')
    bg = f'<div class="bg" aria-hidden="true">{sh.photo(ph, cls="", sizes="40vw")}</div>' if ph else ''
    door_img = sh.photo(ph, cls='', sizes='(max-width:900px) 86vw, 500px', eager=True) if ph else ''
    gk = sh.gate_of(lead)
    place = f'<a href="{sh.glink(gk)}">{esc(lead["place"])}</a>' if gk else f'<span>{esc(lead.get("place") or "")}</span>'
    more = ''.join(f'<li><a href="{sh.link(s["id"])}">{sh.picture(s, sizes="72px")}<div>{kick_plain(s)}<h3 class="hl">{esc(s["headline"])}</h3></div></a></li>' for s in top[:4])
    first = f'''<section class="hero on-ink" aria-label="الخبر الأول" data-hero>{bg}
<div class="wrap hero-g">
<div class="hero-t">
<p class="hero-k"><span class="first-tag">{sh.tower()}الخبر الأول</span>{place}<a href="{CORNER[lead["corner"]][0]}.html">{esc(CORNER[lead["corner"]][1])}</a>{sh.tdate(lead, long=True)}</p>
<h1 class="hero-h"><a href="{sh.link(lead["id"])}">{esc(lead["headline"])}</a></h1>
<p class="hero-s">{esc(lead.get("standfirst") or "")}</p>
{f'<div class="hero-f"><b class="num">{sh.num(fg["value"])}</b><span>{esc(fg["label"])}</span></div>' if fg else ''}
<p class="hero-cta"><a class="btn y" href="{sh.link(lead["id"])}">اقرأ الخبر{sh.icon("i-fwd")}</a><a class="btn" href="{sh.glink(gk) if gk else "gates.html"}">كل ما جرى في {esc(sh.GATE[gk][1] if gk else "القدس")}</a></p>
</div>
<a class="hero-door" href="{sh.link(lead["id"])}" tabindex="-1" aria-hidden="true"><span class="arch">{door_img}</span>{sh.swing()}{sh.stamp(lead)}</a>
</div>
<div class="wrap"><ul class="hero-more" aria-label="أيضا من القدس">{more}</ul></div>
</section>'''

    # the gates: places with news, latest first
    seen = []
    for s in S:
        g = sh.gate_of(s)
        if g and g not in seen:
            seen.append(g)
    rail = ''.join(f'<li>{door(k)}</li>' for k in seen)
    gates = f'''<section class="gates on-ink" data-rail><div class="wrap">
<div class="sec-h"><div><h2>{sh.tower()}أبواب المدينة</h2><p>آخر خبر من كل باب وحي في القدس، الأحدث أولا. افتح الباب لترى كل ما جرى هناك.</p></div><div class="rail-ctl"><button type="button" data-prev aria-label="الأبواب السابقة">{sh.icon("i-back")}</button><button type="button" data-next aria-label="أبواب أخرى">{sh.icon("i-fwd")}</button></div></div>
<ul class="rail">{rail}</ul>
<p class="gates-foot"><span>في هذا العدد أخبار من {len(seen)} مكانا من أصل {len(GATES)}.</span><a href="gates.html">كل الأبواب والأحياء</a></p>
</div></section>'''

    def vigil(corner, cls, title, sub, more):
        people = [s for s in sh.stories(corner) if s.get('person')]
        figs = FIGS.get(corner, [])
        head_n = figs[0] if figs else None
        cnt = (f'<div class="count"><b class="num">{sh.num(head_n["value"])}</b><span>{esc(head_n["label"])}</span></div>' if head_n else '')
        rest = figs[1:5]
        facts = f'<div class="facts">{"".join(fact(f) for f in rest)}</div>' if rest else ''
        news = [s for s in sh.stories(corner) if not s.get('person')][:3]
        nl = f'<ul class="list" style="margin-top:36px">{"".join(headline_li(s) for s in news)}</ul>' if news else ''
        return f'''<section class="vigil {cls} on-ink"><div class="wrap">
{sec_h(title, sub, more)}{cnt}
<div class="frames">{"".join(frame(s) for s in people[:4])}</div>{facts}{nl}
</div></section>'''

    martyrs = vigil('martyrs', 'm', 'شهداء القدس', 'الإطار والاسم كما ينشرهما القسطل: أين ومتى، ومن وثق.', ('كل الأسماء', 'martyrs.html'))
    prisoners = vigil('prisoners', 'p', 'أسرى القدس', 'الاسم على الشريط الأصفر، وتحته بطاقة الاعتقال: الحكم، والسجن، وتاريخ الاعتقال.', ('زاوية الأسرى', 'prisoners.html'))

    aq = sh.stories('aqsa')
    aqsa = ''
    if aq:
        a0 = aq[0]
        tally = ''.join(fact(f).replace('<div><b', '<div class="rv"><b', 1) for f in FIGS.get('aqsa', [])[:4])
        aqsa = f'''<section class="sec tint aqsa"><div class="wrap">
{sec_h('المسجد الأقصى', 'المسجد وأبوابه: من دخل ومن منع، والأعداد التي ترصدها الأوقاف ومحافظة القدس.', ('زاوية الأقصى', 'aqsa.html'))}
<div class="grid"><article class="rv"><a href="{sh.link(a0["id"])}" tabindex="-1" aria-hidden="true">{sh.picture(a0, cls="ph r32", sizes="(max-width:1023px) 100vw, 55vw", stamped=True)}</a>{sh.kick(a0)}<h3 class="hl" style="font-size:clamp(24px,2.4vw,32px);margin-top:10px"><a href="{sh.link(a0["id"])}">{esc(a0["headline"])}</a></h3><p class="sf" style="margin-top:10px">{esc(a0.get("standfirst") or "")}</p></article>
<div>{f'<div class="tally">{tally}</div>' if tally else ''}<ul class="stack" style="margin-top:24px">{"".join(row(s) for s in aq[1:4])}</ul></div></div>
</div></section>'''

    ex = [s for s in sh.stories('exiled') if (s.get('person') or {}).get('ban')]
    exf = FIGS.get('exiled', [])
    exiled = ''
    if ex or sh.stories('exiled'):
        extra = ''.join(row(s) for s in sh.stories('exiled') if s not in ex)
        exiled = f'''<section class="sec"><div class="wrap">
{sec_h('المبعدون', 'القرار كما يسلم: الإبعاد عن أي مكان، ولكم من الوقت، ومن تسلمه.', ('زاوية المبعدين', 'exiled.html'))}
{f'<div class="tally" style="margin:0 0 24px">{"".join(fact(f) for f in exf[:2])}</div>' if exf else ''}
<div class="orders">{"".join(order(s) for s in ex[:4])}</div>
{f'<ul class="stack" style="margin-top:28px">{extra}</ul>' if extra else ''}
</div></section>'''

    st = [x for x in quotes() if x[0]['corner'] == 'statements'] or quotes()
    heb = sh.stories('hebrew')
    voices = f'''<section class="sec tint"><div class="wrap"><div class="split">
<div>{sec_h('تصريحات', 'الجملة كما قيلت.', ('كل التصريحات', 'statements.html'))}{said(st[:3])}</div>
<div>{sec_h('ترجمات عبرية', 'ما تقوله الصحف الإسرائيلية عن القدس، بالعربية.', ('كل الترجمات', 'hebrew.html'))}{hebrew(heb[:4])}</div>
</div></div></section>'''

    wb, gz = sh.stories('westbank'), sh.stories('gaza')
    country = f'''<section class="sec"><div class="wrap">
{sec_h('خارج المدينة', 'الضفة الغربية وغزة، حين يصل الخبر إلى عتبة القدس أو يعم البلاد.', ('الضفة الغربية', 'westbank.html'))}
<div class="cards c4">{"".join(card(s, sf=False) for s in (wb[:2] + gz[:2]))}</div>
<p style="margin-top:20px"><a class="more" href="gaza.html">غزة{sh.icon("i-fwd")}</a></p>
</div></section>'''

    pics = [p for p in E.get('pictures', []) if p in PH][:5]
    pictures = ''
    if pics:
        pictures = f'''<section class="sec"><div class="wrap">
{sec_h('بالصور', 'المدينة كما وثقها المصورون، بمكانها وتاريخها الحقيقيين.')}
<div class="pics">{"".join(f'<figure class="rv">{sh.photo(p, sizes="(max-width:900px) 50vw, 33vw", cls="ph")}<figcaption>{sh.caption(p)}</figcaption></figure>' for p in pics)}</div>
</div></section>'''

    body = first + gates + martyrs + prisoners + aqsa + exiled + voices + country + pictures
    sh.write('index.html', sh.page(sh.SITE, 'القدس أولا: أخبار المدينة بابا بابا وحيا حيا.', body, current='index'))


# ---------------------------------------------------------------- corners
def side_boxes(items, corner=None):
    gates = []
    for s in items:
        g = sh.gate_of(s)
        if g and g not in gates:
            gates.append(g)
    gl = ''.join(f'<li><a href="{sh.glink(g)}">{esc(GATE[g][1])}</a> <span class="num" style="color:var(--mute)">· {sum(1 for s in items if s.get("gate") == g)}</span></li>' for g in gates[:10])
    figs = FIGS.get(corner, []) if corner else []
    ff = ''.join(f'<li><b class="num" style="font-size:22px;display:block">{sh.num(f["value"])}</b>{esc(f["label"])}</li>' for f in figs[:4])
    others = ''.join(f'<li><a href="{C.R}{k}.html">{esc(l)}</a></li>' for k, l, *_ in CORNERS if k != corner)
    return ('<aside class="side">'
            + (f'<div class="box"><h2>أين جرى</h2><ul>{gl}</ul></div>' if gl else '')
            + (f'<div class="box"><h2>بالأرقام</h2><ul>{ff}</ul></div>' if ff else '')
            + f'<div class="box"><h2>زوايا أخرى</h2><ul>{others}</ul></div></aside>')


def corner_page(c):
    C.R = ''
    key, tab, title, sub, _ = c
    items = sh.stories(key)
    tone = ' red' if key == 'martyrs' else ' blue' if key == 'prisoners' else ''
    figs = FIGS.get(key, [])
    meta = (f'<div class="meta"><div><b class="num">{len(items)}</b><span>{"خبرا" if len(items) > 10 else "أخبار"}</span></div>'
            + (f'<div><b class="num">{sh.num(figs[0]["value"])}</b><span>{esc(figs[0]["label"])}</span></div>' if figs else '') + '</div>')
    bgp = next((s['photo'] for s in items if s.get('photo')), None)
    bg = f'<div class="bg" aria-hidden="true">{sh.photo(bgp, cls="", sizes="100vw")}</div>' if bgp and not tone else ''
    head = (f'<section class="chead{tone} on-ink">{bg}<div class="wrap"><div><p class="crumb"><a href="index.html">اليوم</a><span>/</span><span>زاوية</span></p>'
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
        main = f'<div class="wrap"><div class="feed"><div class="main">{said(quotes())}</div>{side_boxes(items, key)}</div></div>'
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
        f'<div class="doors light">{"".join(door(k, sizes="(max-width:640px) 50vw, 25vw") for k, _, _, z, _ in GATES if z == zk)}</div></section>'
        for zk, t, d in ZONES)
    head = ('<section class="chead on-ink"><div class="wrap"><div><p class="crumb"><a href="index.html">اليوم</a><span>/</span><span>الأماكن</span></p>'
            f'<h1>{sh.tower()}الأبواب والأحياء</h1><p>يحفظ القسطل كل خبر تحت المكان الذي جرى فيه: أبواب البلدة القديمة وأبواب المسجد، '
            'والأحياء حول السور، والأحياء التي عزلها الجدار.</p></div>'
            f'<div class="meta"><div><b class="num">{len(GATES)}</b><span>مكانا</span></div><div><b class="num">{len(S)}</b><span>خبرا</span></div></div></div></section>')
    sh.write('gates.html', sh.page('الأبواب والأحياء', 'كل باب وحي في القدس، وآخر خبر من كل منها.',
                                   head + f'<div class="wrap page-in">{zones}</div>', current='gates'))


def gate_page(g):
    C.R = '../'
    key, name, second, zone, where = g
    items = sh.stories(gate=key)
    ph = E['gate_photo'].get(key)
    bg = f'<div class="bg" aria-hidden="true">{sh.photo(ph, cls="", sizes="100vw")}</div>' if ph else ''
    zt = next(z[1] for z in ZONES if z[0] == zone)
    lead = '' if second == name else f'{esc(second)} · '
    head = (f'<section class="chead on-ink">{bg}<div class="wrap"><div><p class="crumb"><a href="../gates.html">الأبواب والأحياء</a><span>/</span><span>{esc(zt)}</span></p>'
            f'<h1>{sh.tower()}{esc(name)}</h1><p>{lead}{esc(where)}.'
            + (f' {sh.stories_n(len(items))} في هذا العدد.' if items else ' لا أخبار من هنا في هذا العدد بعد.') + '</p></div>'
            f'<div class="meta"><div><b class="num">{len(items)}</b><span>{"خبرا" if len(items) > 10 else "أخبار"}</span></div></div></div></section>')
    same = [x for x in GATES if x[3] == zone and x[0] != key]
    nb = ''.join(f'<li><a href="{x[0]}.html">{esc(x[1])}</a> <span class="num" style="color:var(--mute)">· {gate_count(x[0])}</span></li>' for x in same)
    capt = f'<div class="box"><h2>الصورة</h2><p style="font-size:14px;color:var(--mute)">{sh.caption(ph)}</p></div>' if ph else ''
    side = f'<aside class="side">{capt}<div class="box"><h2>{esc(zt)}</h2><ul>{nb}</ul></div><div class="box"><h2>كل الأماكن</h2><ul><li><a href="../gates.html">كل الأبواب والأحياء</a></li></ul></div></aside>'
    empty = '<li><p class="sf">لا خبر من هنا في هذا العدد. تمتلئ الصفحة كلما حفظ المحررون خبرا تحت هذا المكان.</p></li>'
    main = f'<div class="wrap"><div class="feed"><ul class="main">{"".join(feed_item(s) for s in items) or empty}</ul>{side}</div></div>'
    sh.write(f'gate/{key}.html', sh.page(name, f'{name}، القدس: كل أخبار القسطل من هنا.', head + main, current='gates'))


# ---------------------------------------------------------------- stories
def story_page(s, i):
    C.R = '../'
    c = CORNER[s['corner']]
    words = sum(len(p.split()) for p in s.get('body') or [])
    mins = max(1, round(words / 180))
    ph = s.get('photo')
    lead_ph = ''
    if ph:
        note = '' if s.get('photo_own') else 'صورة أرشيفية. '
        lead_ph = f'<figure class="lead-ph">{sh.photo(ph, sizes="(max-width:1300px) 100vw, 1280px", eager=True, extra=sh.stamp(s))}<figcaption>{note}{sh.caption(ph)}</figcaption></figure>'
    prose = []
    for n, p in enumerate(s.get('body') or []):
        prose.append(f'<p>{esc(p)}</p>')
        if n == 1 and s.get('figure'):
            f = s['figure']
            prose.append(f'<div class="pull"><b class="fig-n num">{sh.num(f["value"])}</b><p class="fig-l">{esc(f["label"])}</p></div>')
        if n == 2 and s.get('quote') and s['quote'].get('text'):
            q = s['quote']
            prose.append(f'<blockquote>«{esc(q["text"])}»<cite>{esc(q.get("who") or "")}{"، " + esc(q["role"]) if q.get("role") else ""}'
                         f'{" (ترجمة القسطل)" if q.get("translated") else ""}</cite></blockquote>')
    srcs = ''.join(f'<li>{sh.src_link(o)}{"، " + esc(sh.day(o["date"], year=True)) if o.get("date") else ""}</li>' for o in s.get('sources') or [])
    pcard = ''
    p = s.get('person')
    if p and p.get('name'):
        m = ' m' if s['corner'] == 'martyrs' else ''
        rows = person_rows(p, s)
        ban = p.get('ban') or {}
        if ban:
            rows += f'<dt>الإبعاد عن</dt><dd>{esc(ban.get("from") or "")}</dd><dt>المدة</dt><dd>{esc(ban.get("length") or "غير معلنة")}</dd>'
        pcard = f'<div class="card-p{m} on-ink"><span class="band">{esc(p["name"])}</span><dl><dt>الصفة</dt><dd>{esc(p.get("status") or "")}</dd>{rows}</dl></div>'
    g = sh.gate_of(s)
    gbox = f'<div class="box"><h2>من المكان</h2>{door(g, sizes="300px")}</div>' if g else ''
    related = [x for x in S if x['id'] != s['id'] and (x.get('gate') == s.get('gate') or x['corner'] == s['corner'])][:3]
    rel_name = GATE[g][1] if g and any(x.get('gate') == g for x in related) else c[1]
    rel = (f'<section class="sec" style="padding-top:56px;padding-bottom:0"><h2 style="font-size:26px;margin-bottom:20px">المزيد من {esc(rel_name)}</h2>'
           f'<div class="cards">{"".join(card(x, sf=False) for x in related)}</div></section>') if related else ''
    prev, nxt = (S[i - 1] if i > 0 else None), (S[i + 1] if i + 1 < len(S) else None)
    pn = ('<nav class="pn" aria-label="الخبر التالي والسابق">'
          + (f'<a href="{prev["id"]}.html"><small>الأحدث</small><b>{esc(prev["headline"])}</b></a>' if prev else '<span></span>')
          + (f'<a href="{nxt["id"]}.html"><small>الأقدم</small><b>{esc(nxt["headline"])}</b></a>' if nxt else '') + '</nav>')
    body = f'''<article class="story"><div class="wrap">
<header class="hd">{sh.kick(s)}<h1 class="hl">{esc(s["headline"])}</h1>{f'<p class="sf">{esc(s["standfirst"])}</p>' if s.get("standfirst") else ''}
<p class="by"><span><b>القسطل</b>، مكتب القدس</span>{sh.tdate(s, long=True)}<span>قراءة في {"دقيقة" if mins == 1 else "دقيقتين" if mins == 2 else f"{mins} دقائق"}</span></p></header>
{lead_ph}
<div class="body-grid"><div><div class="prose">{"".join(prose)}</div>
<div class="srcs"><h2 class="lbl">المصادر</h2><ul>{srcs}</ul></div>{pn}</div>
<aside class="aside-sticky side">{pcard}{gbox}<div class="box"><h2>شارك</h2><div class="share"><button type="button" data-copy>{sh.icon("i-link")}انسخ الرابط</button><a href="https://t.me/alqastalps" rel="noopener" target="_blank">تلغرام</a></div></div></aside></div>
{rel}
</div></article>'''
    sh.write(f'story/{s["id"]}.html', sh.page(s['headline'], s.get('standfirst') or s['headline'], body, current=s['corner'], top=False))


# ---------------------------------------------------------------- utility pages
def simple(rel, title, desc, inner, current=''):
    head = (f'<section class="chead on-ink"><div class="wrap"><div><p class="crumb"><a href="{C.R}index.html">اليوم</a><span>/</span><span>{esc(title)}</span></p>'
            f'<h1>{sh.tower()}{esc(title)}</h1><p>{esc(desc)}</p></div></div></section>')
    sh.write(rel, sh.page(title, desc, head + f'<div class="wrap page-in">{inner}</div>', current=current))


def about():
    C.R = ''
    steps = [('01', 'الرصد', 'يتابع نظام الرصد في غرفة الأخبار الوكالات ومحافظة القدس ومؤسسات الأسرى والأوقاف والصحافة العبرية على مدار الساعة، ويحفظ كل خبر تحت مكانه وزاويته.'),
             ('02', 'المسودة', 'يكتب مساعد ذكي مسودة الخبر ومعها مصادره: من قال ماذا، ومتى، وأين نشر. لا ينشر شيء في هذه الخطوة.'),
             ('03', 'التحرير اليدوي', 'يراجع المحرر كل اسم ورقم واقتباس على مصدره، ويضيف ما لا تعرفه الآلة، ثم ينشر. ويستطيع المحررون إضافة أي خبر يدويا.')]
    inner = f'''<div class="narrow prose" style="font-size:19px"><p>القسطل منصة إخبارية مقدسية تغطي المدينة أولا وبالتفصيل: كل باب من أبواب البلدة القديمة، وكل حي حول السور، وكل حي عزله الجدار. تحمل اسم القسطل، القرية والقلعة على التلة عند الطريق الغربي إلى القدس، وعلامتها برج بابه مفتوح.</p>
<p>يتوزع الموقع على الزوايا التي تعرف بها المنصة: القدس، والأقصى، والأسرى، والشهداء، والمبعدون، والترجمات العبرية، والتصريحات، ومعها الضفة وغزة حين يصل الخبر إلى المدينة.</p></div>
<h2 style="font-size:30px;margin-top:56px">كيف يصل الخبر إلى هنا</h2>
<ol class="steps">{"".join(f'<li class="rv"><span class="k">{k}</span><b>{esc(t)}</b><p>{esc(d)}</p></li>' for k, t, d in steps)}</ol>
<div class="narrow" style="margin-top:56px"><h2 style="font-size:30px">التصويبات</h2><p class="sf" style="margin-top:12px">حين نخطئ نصحح في الخبر نفسه، ونذكر ما تغير ومتى، ولا نحذف بصمت. راسل غرفة الأخبار من صفحة <a href="submit.html" style="text-decoration:underline">أرسل خبرا</a>.</p>
<h2 style="font-size:30px;margin-top:40px">عن هذا النموذج</h2><p class="sf" style="margin-top:12px">هذا الموقع نموذج تصميم من تك تك. كل خبر فيه حقيقي ومربوط بمصادره، والصور من ويكيميديا كومنز بأسماء أصحابها. وطريقة النشر أعلاه هي المقترحة للمنصة عند إطلاقها.</p></div>'''
    simple('about.html', 'من نحن', 'منصة إخبارية مقدسية: المدينة أولا، بابا بابا.', inner)


def submit():
    C.R = ''
    opts = ''.join(f'<option value="{k}">{esc(n)}</option>' for k, n, *_ in GATES)
    corners = ''.join(f'<option value="{k}">{esc(l)}</option>' for k, l, *_ in CORNERS)
    opt = '<span style="font-weight:400;color:var(--mute)">(اختياري)</span>'
    inner = f'''<div class="narrow"><p class="sf">رأيت شيئا يحدث في القدس؟ أخبر غرفة الأخبار. يقرأ محرر كل رسالة ويتحقق منها ويتواصل معك قبل نشر أي شيء. ويمكنك ألا تذكر اسمك.</p>
<form class="form" action="#" method="post" data-proto="وصلت رسالتك في النموذج فقط. في الموقع الحي تذهب إلى بريد غرفة الأخبار.">
<div><label for="f-what">ماذا حدث؟</label><textarea id="f-what" name="what" required></textarea><p class="hint">من، وماذا، وما رأيته بنفسك.</p></div>
<div class="row2"><div><label for="f-where">أين</label><select id="f-where" name="where">{opts}<option value="other">مكان آخر</option></select></div>
<div><label for="f-when">متى</label><input id="f-when" name="when" type="datetime-local"></div></div>
<div class="row2"><div><label for="f-corner">الزاوية</label><select id="f-corner" name="corner">{corners}</select></div>
<div><label for="f-file">صورة أو فيديو {opt}</label><input id="f-file" name="file" type="file" accept="image/*,video/*"></div></div>
<div class="row2"><div><label for="f-name">اسمك {opt}</label><input id="f-name" name="name" autocomplete="name"></div>
<div><label for="f-contact">البريد أو الهاتف {opt}</label><input id="f-contact" name="contact" autocomplete="email" dir="ltr"></div></div>
<label class="chk"><input type="checkbox" name="ok" required> رأيت هذا بنفسي أو أعرفه من مصدر مباشر، ويمكن للقسطل التواصل معي للتحقق.</label>
<div><button class="btn y" type="submit" style="min-width:180px">{sh.icon("i-send")}أرسل إلى غرفة الأخبار</button></div>
<p class="msg" role="status"></p></form></div>'''
    simple('submit.html', 'أرسل خبرا', 'أخبر غرفة أخبار القدس بما رأيت. كل رسالة تقرأ ويتحقق منها.', inner)


def search():
    C.R = ''
    idx = [{'u': f'story/{s["id"]}.html', 'h': s['headline'], 'c': CORNER[s['corner']][1], 'cc': CORNER[s['corner']][4],
            'p': s.get('place') or '', 'd': sh.day(s['date'], year=True),
            't': ' '.join([s['headline'], s.get('standfirst') or '', s.get('place') or '', CORNER[s['corner']][1],
                           (s.get('person') or {}).get('name') or '', GATE.get(s.get('gate') or '', ('', '', ''))[1], GATE.get(s.get('gate') or '', ('', '', ''))[2]])}
           for s in S]
    sh.write('assets/search.json', json.dumps(idx, ensure_ascii=False))
    chips = ''.join(f'<button type="button" data-q="{q}">{q}</button>' for q in ('سلوان', 'الأقصى', 'باب العامود', 'هدم', 'الاعتقال الإداري', 'إبعاد'))
    inner = f'''<div class="narrow"><form class="srch" data-search="assets/search.json?v={sh.V}" role="search"><label class="vh" for="q">ابحث في القسطل</label><input id="q" type="search" placeholder="اسم، مكان، باب…" autocomplete="off"><button type="submit">ابحث</button></form>
<div class="chips">{chips}</div><div class="results" data-results aria-live="polite"></div></div>'''
    simple('search.html', 'بحث', 'كل أخبار هذا العدد، بالاسم أو المكان أو الباب أو الزاوية.', inner)


def credits():
    C.R = ''
    rows = ''.join(f'<li><a href="{esc(p["page_url"])}" rel="noopener" target="_blank" dir="ltr">{esc(p["file"][5:])}</a> · <bdi>{esc(p["author"])}</bdi> · <span class="ltr">{esc(p["license"])}</span> · {esc(str(p.get("date") or ""))}</li>' for p in PH.values())
    simple('credits.html', 'حقوق الصور', 'كل صورة في الموقع من ويكيميديا كومنز، مستخدمة بالرخصة المذكورة.',
           f'<ul class="list" style="font-size:15px">{rows}</ul>')


def identity():
    C.R = ''
    t = sh.MARKS['tower']
    big = (f'<svg viewBox="-60 -40 668 860" style="width:100%;max-width:360px;margin:auto" role="img" aria-label="البرج وأجزاؤه مرقمة">'
           f'<path d="{t["block"]}{t["door"]}" fill="#0E1724" fill-rule="evenodd"/><path d="{t["swing"]}" fill="#FFDD36"/><path d="{t["fold"]}" fill="#EBCD38"/>'
           f'<path d="M319 550A229 229 0 0 0 548 779" fill="none" stroke="#0E1724" stroke-width="3" stroke-dasharray="10 9" transform="rotate(-90 319 550)"/>'
           + ''.join(f'<g><circle cx="{x}" cy="{y}" r="26" fill="#fff" stroke="#0E1724" stroke-width="3"/><text x="{x}" y="{y + 10}" text-anchor="middle" font-family="Alexandria,Arial" font-weight="700" font-size="28" fill="#0E1724">{n}</text></g>'
                     for n, x, y in ((1, 80, 470), (2, 274, 150), (3, 271, 330), (4, 470, 680)))
           + '</svg>')
    sw = [('الليل', '#0E1724', 'البرج. الترويسة والتذييل والأبواب.'), ('الورق', '#FFFFFF', 'الصفحة. أبيض، لا كريمي.'),
          ('الحجر', '#F3F5F8', 'الأقسام الملونة، ومعه رماديا الحجر #E7EBF0 و#D5DBE3.'), ('الفتحة', '#FFDD36', 'أصفر العميل: الباب المفتوح. تعبئة فقط، لا نص به على الأبيض.'),
          ('الثنية', '#EBCD38', 'الطية على كل قطعة صفراء.'), ('الشهداء', '#BE0000', 'من قالب العميل. شريط العاجل وشريط الشهداء.'),
          ('السجن', '#113350', 'من قالب الأسرى. زاوية الأسرى.'), ('الرمادي', '#566173', 'النص الثانوي، تباين 6:1 على الأبيض.')]
    swatches = ''.join(f'<div class="sw"><i style="background:{c}"></i><div><b>{n}</b><span class="num ltr">{c}</span><p style="color:var(--mute);margin-top:4px">{esc(d)}</p></div></div>' for n, c, d in sw)
    demo = next((s for s in S if s.get('person') and s['corner'] == 'prisoners'), None) or next((s for s in S if s.get('person')), None)
    lead = BY[E['lead']]
    inner = f'''<section class="book">
<div class="marks"><div style="background:#0E1724;color:#fff">{sh.lockup()}</div><div style="color:#0E1724">{sh.lockup()}</div><div style="background:#FFDD36;color:#0E1724"><span style="font-size:110px;line-height:1">{sh.tower()}</span></div></div>
<div class="anat" style="margin-top:64px"><div>{big}</div><div><h2 style="font-size:34px">برج بابه مفتوح</h2>
<p class="sf" style="margin:12px 0 24px">علامة القسطل مرسومة كمسقط معماري. ومن هذه القراءة، فإن ربع الدائرة الأصفر تحت البرج هو مسار فتحة باب مفتوح: الرمز المعتمد للباب في أي مخطط معماري. والقسطل هي البوابة على طريق القدس، والموقع مبني على هذه الحركة الواحدة.</p>
<ol><li><span><b>الكتلة.</b> زاوية من زوايا الموقع: التبويبات، والإطارات، والترويسة.</span></li><li><span><b>الشرفة.</b> القطع الوحيد في البرج. يبقى في العلامة ولا يتكرر في غيرها.</span></li><li><span><b>الباب.</b> مكان في القدس. كل باب وحي هو باب مقوس تفتحه.</span></li><li><span><b>الفتحة.</b> حالة الفتح. تتدلى من الزاوية المفتوحة، وتنفتح على الباب حين تمر عليه، وتفتح كل قسم حين يصل.</span></li></ol></div></div>
<h2 style="font-size:34px;margin-top:72px">الألوان</h2><div class="swatches" style="margin-top:20px">{swatches}</div>
<h2 style="font-size:34px;margin-top:72px">الخط</h2>
<div class="specimen"><p class="lbl">الإسكندرية · محمد جابر · الأسماء والعناوين والأرقام</p><p style="font-size:clamp(40px,6vw,76px);font-weight:700;line-height:1.3;margin-top:12px">باب الأسباط، سلوان، الشيخ جراح</p><p style="font-size:21px;margin-top:10px">اخترناه بالمقارنة إلى جانب علامة القسطل: كوفي هندسي بخط قاعدة مستقيم ومدات أفقية كحروف الشعار، وواضح بما يكفي لتقرأ اسم الزاوية من النظرة الأولى، كما طلب العميل في ملاحظاته على النماذج السابقة.</p><p class="num" style="font-size:44px;font-weight:800;margin-top:14px">9,300 · 6 أشهر · 27 تشرين الأول 2026</p></div>
<div class="specimen"><p class="lbl">نوتو نسخ عربي · جوجل · القراءة</p><p class="prose" style="margin-top:12px;max-width:680px">المقدمات ونص الخبر بخط نسخ واضح وسطور مريحة. يبقى النسخ للقراءة الطويلة، ويبقى الكوفي للأسماء: المكان والشخص يكتبان دائما بصوت الزاوية التي ينتميان إليها.</p></div>
<h2 style="font-size:34px;margin-top:72px">القطع</h2>
<div class="split" style="margin-top:24px;align-items:start"><div><p class="lbl" style="margin-bottom:12px">ختم المكان</p><p style="background:var(--ink);padding:24px;border-radius:14px">{sh.stamp(lead)}</p>
<p class="lbl" style="margin:28px 0 12px">الباب</p><div style="max-width:260px;background:var(--ink);padding:24px 24px 64px;border-radius:14px" class="on-ink">{door(sh.gate_of(lead) or "old-city")}</div></div>
<div>{f'<p class="lbl" style="margin-bottom:12px">الإطار والشريط</p><div class="vigil p on-ink" style="padding:28px;border-radius:14px"><div style="max-width:300px;position:relative">{frame(demo)}</div></div>' if demo else ''}</div></div>
<h2 style="font-size:34px;margin-top:72px">الحركة</h2><p class="sf" style="margin-top:12px;max-width:62ch">أول صفحة في الزيارة تفتح من البوابة: يقوم البرج، وينفتح بابه، وترى الصفحة من خلال الباب وهو يكبر حتى يملأ الشاشة. وبين صفحة وأخرى تنفتح الصفحة التالية من العتمة من خلال الباب نفسه. وتتوقف الحركة لكل من يطلب من جهازه حركة أقل.</p>
<p style="margin-top:20px"><a class="btn y" href="index.html?loader">أعد الافتتاحية</a></p>
</section>'''
    simple('identity.html', 'الهوية', 'برج بابه مفتوح: كيف صارت علامة القسطل موقعا.', inner)


def not_found():
    C.R = sh.BASE_PATH
    inner = f'<div class="narrow"><p class="sf">هذا الباب مغلق: ربما انتقلت الصفحة، أو في العنوان خطأ.</p><p style="margin-top:24px;display:flex;gap:12px;flex-wrap:wrap"><a class="btn y" href="{C.R}index.html">أخبار اليوم</a><a class="btn ink" href="{C.R}gates.html">كل الأبواب والأحياء</a><a class="btn ink" href="{C.R}search.html">بحث</a></p></div>'
    simple('404.html', 'الصفحة غير موجودة', 'لا توجد صفحة على هذا العنوان.', inner)


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
