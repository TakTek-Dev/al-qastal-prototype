"""The shell every built page shares: head, strip, masthead, the corners, footer, loader, the marks.

Imported by build.py. C.R is the path back to the site root: '' at the root, '../' in story/ and gate/,
the absolute site path on 404.html.
"""
import datetime as dt
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = '4'                                       # bump on any asset change (Chrome caches hard)
SITE = 'Al-Qastal'
BASE_URL = 'https://taktek-dev.github.io/al-qastal-prototype/'
BASE_PATH = '/al-qastal-prototype/'
E = json.load(open(os.path.join(ROOT, 'tools', 'edition.json'), encoding='utf-8'))
MARKS = json.load(open(os.path.join(ROOT, 'tools', 'out', 'marks.json'), encoding='utf-8'))
PH = json.load(open(os.path.join(ROOT, 'tools', 'photos.json'), encoding='utf-8'))
DIM_P = os.path.join(ROOT, 'tools', 'out', 'photos.json')
DIM = json.load(open(DIM_P, encoding='utf-8')) if os.path.exists(DIM_P) else {}
_NB = re.compile(r"(?<![\w-])(al|Al|el|El|ad|ash|as|az|at|an|Abu|Ben|Bab|Umm|Beit|Ras|Wadi)-(?=\w)")  # particle at a word start


def esc(s, quote=True):
    """Escape, and keep Arabic name particles on the line with the name (al-Tur, Ben-Gvir). URLs stay as they are."""
    s = html.escape(s, quote)
    return s if '/' in s or s.startswith('http') else _NB.sub(lambda m: m.group(1) + '‑', s)


D = dt.date.fromisoformat
TODAY = D(E['date'])
S = sorted(E['stories'], key=lambda s: s['date'], reverse=True)
BY = {s['id']: s for s in S}


class Ctx:
    R = ''


C = Ctx()

# slug, tab label, page title, standfirst, dot colour
CORNERS = [
    ('jerusalem', 'Jerusalem', 'Jerusalem', 'The city gate by gate and quarter by quarter: demolitions, arrests, settlement plans, the checkpoints, and the families who stay.', 'var(--yellow)'),
    ('aqsa', 'Al-Aqsa', 'Al-Aqsa', 'The mosque and its gates: who was let in and who was kept out, the holiday closures, the guards and the worshippers.', 'var(--yellow)'),
    ('prisoners', 'Prisoners', 'Prisoners', 'Jerusalem’s prisoners and the prisons that hold them: the sentence, the prison, the date of arrest, and the count that keeps rising.', 'var(--prison)'),
    ('martyrs', 'Martyrs', 'Martyrs', 'The people of the city who were killed: their names, where it happened and when, as the families and the governorate record them.', 'var(--red)'),
    ('exiled', 'Exiled', 'Banned and exiled', 'The orders that keep Jerusalemites out of Al-Aqsa, the Old City or the city itself: who received them, from where, and for how long.', 'var(--yellow)'),
    ('westbank', 'West Bank', 'West Bank', 'The rest of the occupied West Bank, when it reaches Jerusalem’s doorstep or the whole country.', 'var(--yellow)'),
    ('gaza', 'Gaza', 'Gaza', 'The Strip under the ceasefire: the dead and the wounded, the crossings, the displaced.', 'var(--yellow)'),
    ('hebrew', 'Hebrew press', 'From the Hebrew press', 'What Israeli papers and broadcasters are saying about Jerusalem, summarised in English with a link to the original.', 'var(--yellow)'),
    ('statements', 'Statements', 'Statements', 'The sentence as it was said, who said it, and when.', 'var(--yellow)'),
]
CORNER = {c[0]: c for c in CORNERS}

# key, name, Arabic name in transliteration, zone, where
GATES = [
    ('damascus-gate', 'Damascus Gate', 'Bab al-Amud', 'gates', 'North wall'),
    ('herods-gate', 'Herod’s Gate', 'Bab al-Sahira', 'gates', 'North wall'),
    ('lions-gate', 'Lions’ Gate', 'Bab al-Asbat', 'gates', 'East wall'),
    ('golden-gate', 'Golden Gate', 'Bab al-Rahma', 'gates', 'East wall, sealed'),
    ('dung-gate', 'Dung Gate', 'Bab al-Maghariba', 'gates', 'South wall'),
    ('zion-gate', 'Zion Gate', 'Bab al-Nabi Dawud', 'gates', 'South wall'),
    ('jaffa-gate', 'Jaffa Gate', 'Bab al-Khalil', 'gates', 'West wall'),
    ('new-gate', 'New Gate', 'Bab al-Jadid', 'gates', 'North-west wall'),
    ('chain-gate', 'Chain Gate', 'Bab al-Silsila', 'gates', 'Into Al-Aqsa'),
    ('aqsa', 'Al-Aqsa', 'al-Masjid al-Aqsa', 'gates', 'The compound'),
    ('old-city', 'The Old City', 'al-Balda al-Qadima', 'gates', 'Inside the walls'),
    ('silwan', 'Silwan', 'Silwan', 'around', 'South of Al-Aqsa'),
    ('ras-al-amud', 'Ras al-Amud', 'Ras al-Amud', 'around', 'South-east'),
    ('al-tur', 'Al-Tur', 'al-Tur', 'around', 'Mount of Olives'),
    ('sheikh-jarrah', 'Sheikh Jarrah', 'al-Sheikh Jarrah', 'around', 'North of the walls'),
    ('issawiya', 'Issawiya', 'al-Issawiya', 'around', 'North-east'),
    ('jabal-mukabber', 'Jabal al-Mukabber', 'Jabal al-Mukabber', 'around', 'South-east'),
    ('sur-baher', 'Sur Baher', 'Sur Baher', 'around', 'South'),
    ('walaja', 'Al-Walaja', 'al-Walaja', 'around', 'South-west'),
    ('beit-hanina', 'Beit Hanina', 'Beit Hanina', 'beyond', 'North'),
    ('shuafat', 'Shuafat camp', 'Mukhayyam Shuafat', 'beyond', 'Behind the wall'),
    ('anata', 'Anata', 'Anata', 'beyond', 'Behind the wall'),
    ('kafr-aqab', 'Kafr Aqab', 'Kafr Aqab', 'beyond', 'Behind the wall'),
    ('qalandiya', 'Qalandiya', 'Qalandiya', 'beyond', 'The checkpoint'),
    ('ezariya', 'Al-Eizariya', 'al-Eizariya', 'beyond', 'East, behind the wall'),
]
GATE = {g[0]: g for g in GATES}
ZONES = [('gates', 'The gates and the Old City', 'Seven open gates, one sealed, the gates of the mosque, and the alleys between them.'),
         ('around', 'Around the walls', 'The quarters within sight of the walls, where most of the demolition orders land.'),
         ('beyond', 'Behind the wall', 'Jerusalem neighbourhoods the separation wall cut off from the city they belong to.')]


def gate_of(s):
    g = s.get('gate')
    return g if g in GATE else None


def stories(corner=None, gate=None):
    return [s for s in S if (not corner or s['corner'] == corner) and (not gate or s.get('gate') == gate)]


def day(d, year=False):
    d = D(d) if isinstance(d, str) else d
    return f"{d.day} {d.strftime('%b')}" + (f" {d.year}" if year or d.year != TODAY.year else '')


def long_day(d):
    d = D(d) if isinstance(d, str) else d
    return f"{d.strftime('%A')} {d.day} {d.strftime('%B')} {d.year}"


def ago(s):
    d = D(s['date'])
    n = (TODAY - d).days
    if n == 0:
        return 'Today'
    if n == 1:
        return 'Yesterday'
    if n < 6:
        return d.strftime('%A')
    return day(d)


def tdate(s, long=False):
    return f'<time datetime="{s["date"]}">{esc(long_day(s["date"]) if long else ago(s))}</time>'


# ---------------------------------------------------------------- icons and marks
SPRITE = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<symbol id="i-right" viewBox="0 0 16 16"><path d="M3 8h10M8.5 3.5 13 8l-4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-left" viewBox="0 0 16 16"><path d="M13 8H3M7.5 3.5 3 8l4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-search" viewBox="0 0 16 16"><path d="M7 2.5a4.5 4.5 0 1 1 0 9 4.5 4.5 0 0 1 0-9zM10.4 10.4 14 14" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></symbol>
<symbol id="i-out" viewBox="0 0 16 16"><path d="M6 3.5H3.5v9h9V10M9 3h4v4M13 3 7.5 8.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-send" viewBox="0 0 16 16"><path d="M2.5 7.6 13.5 2.5 9.8 13.5 7.6 8.6z M7.6 8.6l5.9-6.1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></symbol>
<symbol id="i-link" viewBox="0 0 16 16"><path d="M6.6 9.4 9.4 6.6M7.3 4.4l1-1a2.8 2.8 0 0 1 4 4l-1 1M8.7 11.6l-1 1a2.8 2.8 0 0 1-4-4l1-1" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></symbol>
</defs></svg>'''


def icon(name, cls='ic'):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#{name}"/></svg>'


def tower(door='none', cls='tower'):
    """The tower as a live element: block with its crenel, the door (cut through, or filled), the swing."""
    t = MARKS['tower']
    blk = t['block'] + (t['door'] if door == 'none' else '')
    dp = '' if door == 'none' else f'<path class="t-door" d="{t["door"]}" style="fill:{door}"/>'
    return (f'<svg class="{cls}" viewBox="{t["viewBox"]}" aria-hidden="true" focusable="false">'
            f'<path class="t-blk" d="{blk}" fill-rule="evenodd"/>{dp}<path class="t-sw" d="{t["swing"]}"/>'
            f'<path class="t-fold" d="{t["fold"]}"/></svg>')


def lockup(label=SITE):
    m = MARKS['lockup']
    t = MARKS['tower']
    return (f'<svg class="lockup" viewBox="{m["viewBox"]}" role="img" aria-label="{esc(label)}">'
            f'<path class="l-ink" d="{m["ar"]}"/><path class="l-ink" d="{m["la"]}"/>'
            f'<g transform="translate({m["tx"]} {m["ty"]})"><path class="l-ink" d="{t["block"]}{t["door"]}" fill-rule="evenodd"/>'
            f'<path d="{t["swing"]}" fill="{MARKS["yellow"]}"/><path d="{t["fold"]}" fill="{MARKS["fold"]}"/></g></svg>')


def swing(cls=''):
    return f'<i class="swing{(" " + cls) if cls else ""}" aria-hidden="true"></i>'


def stamp(s):
    g = GATE.get(gate_of(s) or '')
    where = s['place'] if s.get('place') else (g[1] if g else '')
    return f'<span class="stamp">{tower()}{esc(where)}<span>{esc(CORNER[s["corner"]][1])}</span></span>'


# ---------------------------------------------------------------- photographs
def photo(slug, sizes='100vw', cls='ph', eager=False, extra=''):
    if not slug or slug not in PH:
        return ''
    p = PH[slug]
    dm = DIM.get(slug, {'w': 1400, 'h': 933})
    pos = f' style="object-position:{p["focus"]}"' if p.get('focus') else ''
    load = 'fetchpriority="high"' if eager else 'loading="lazy" decoding="async"'
    base = f'{C.R}assets/img/photo/{slug}'
    srcset = f'{base}-640.webp?v={V} 640w, {base}.webp?v={V} {dm["w"]}w'
    img = (f'<img src="{base}.webp?v={V}" srcset="{srcset}" width="{dm["w"]}" height="{dm["h"]}" '
           f'alt="{esc(p["alt"])}" sizes="{sizes}" {load}{pos}>')
    return f'<div class="{cls}">{img}{extra}</div>' if cls else img


def plate(s, cls='plate'):
    g = GATE.get(gate_of(s) or '')
    return f'<div class="{cls}"><div><b>{esc(s.get("place") or (g[1] if g else ""))}</b><span>{esc(CORNER[s["corner"]][1])}</span></div></div>'


def picture(s, cls='ph', sizes='100vw', eager=False, stamped=False):
    img = photo(s.get('photo'), sizes=sizes, cls=cls, eager=eager, extra=stamp(s) if stamped else '')
    return img or plate(s, cls.replace('ph', 'plate'))


def caption(slug):
    p = PH[slug]
    return f'{esc(p["caption"])} Photo: {esc(p["author"])}, {esc(p["license"])}, via Wikimedia Commons.'


def link(sid):
    return f'{C.R}story/{sid}.html'


def glink(key):
    return f'{C.R}gate/{key}.html'


def kick(s, corner=True, place=True):
    c = CORNER[s['corner']]
    parts = []
    if corner:
        parts.append(f'<a class="c" style="--cc:{c[4]}" href="{C.R}{c[0]}.html">{esc(c[1])}</a>')
    if place and s.get('place'):
        g = gate_of(s)
        parts.append(f'<a href="{glink(g)}">{esc(s["place"])}</a>' if g else f'<span>{esc(s["place"])}</span>')
    parts.append(tdate(s))
    return f'<p class="kick">{"".join(parts)}</p>'


def src_link(o):
    name = esc(o.get('name') or o.get('source') or '')
    u = o.get('url')
    return f'<a href="{esc(u)}" rel="noopener" target="_blank">{name}</a>' if u else name


# ---------------------------------------------------------------- the shell
# Runs in <head> before first paint: first page of the session -> the loader (js-load);
# arriving from another page of the site -> start shut (aq-arrive) and aq.js opens the door.
EARLY = ("(function(){var d=document.documentElement,s;try{s=sessionStorage}catch(e){return}"
         "if(matchMedia('(prefers-reduced-motion: reduce)').matches){s.setItem('aq-in','1');s.removeItem('aq-nav');return}"
         "if(location.search.indexOf('loader')>-1||s.getItem('aq-in')!=='1')d.classList.add('js-load');"
         "else if(s.getItem('aq-nav')==='1')d.classList.add('aq-arrive');s.removeItem('aq-nav')})()")

# the doorway the page is seen through: a door-shaped hole in the dark, centred, 30 units wide
HOLE = 'M485 515.5V499.5A15 15 0 0 1 515 499.5V515.5Z'


def doorway(cls, mid):
    return (f'<svg class="mask-sv" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
            f'<defs><mask id="{mid}"><rect width="1000" height="1000" fill="#fff"/>'
            f'<path class="hole" d="{HOLE}" fill="#000"/></mask></defs>'
            f'<rect width="1000" height="1000" fill="#0E1724" mask="url(#{mid})"/></svg>')


def loader():
    t = MARKS['tower']
    tw = (f'<svg viewBox="{t["viewBox"]}"><path class="t-blk" d="{t["block"]}"/><path class="t-door" d="{t["door"]}"/>'
          f'<path class="t-sw" d="{t["swing"]}"/><path class="t-fold" d="{t["fold"]}"/></svg>')
    return (f'<div class="ldr" aria-hidden="true">{doorway("", "ldm")}<div class="tw">{tw}</div>'
            f'<p class="say"><b>{long_day(TODAY)}</b> · Jerusalem</p></div>'
            f'<div class="gate-nav" aria-hidden="true">{doorway("", "gnm")}</div>')


def head(title, desc, og=None):
    t = esc(title if title == SITE else f'{title} · {SITE}')
    return f'''<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#0E1724">
<link rel="icon" href="{C.R}favicon.svg?v={V}" type="image/svg+xml">
<link rel="preload" href="{C.R}assets/fonts/host.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{C.R}assets/css/aq.css?v={V}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{BASE_URL}{og or 'assets/og.png'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="noindex">
<script>{EARLY}</script>
</head>
<body>
{loader()}<a class="skip" href="#main">Skip to the news</a>
{SPRITE}'''


def util():
    return (f'<div class="util"><div class="wrap"><span><b>{long_day(TODAY)}</b></span>'
            f'<span class="clock hide-s" data-clock>Jerusalem</span><span class="sp"></span>'
            f'<a class="hide-s" href="{C.R}about.html">About</a><a class="hide-s" href="{C.R}submit.html">Send us news</a>'
            f'<a class="hdl" href="https://t.me/alqastalps" rel="noopener" target="_blank">@alqastalps</a></div></div>')


def mast(current=''):
    tabs = ([('index', 'Today', f'{C.R}index.html'), ('gates', 'Gates', f'{C.R}gates.html')] +
            [(k, l, f'{C.R}{k}.html') for k, l, *_ in CORNERS])
    lis = ''.join(
        f'<li{" class=\"last\"" if i == len(tabs) - 1 else ""}><a href="{u}"{" aria-current=\"page\"" if k == current else ""}>'
        f'{esc(l)}{swing()}</a></li>' for i, (k, l, u) in enumerate(tabs))
    return f'''<header class="mast on-ink">
<div class="wrap"><div class="row">
<a class="brand" href="{C.R}index.html" aria-label="{SITE}, today">{lockup()}</a>
<p class="motto"><b>Jerusalem first.</b> Every story through its own gate.</p>
<div class="tools"><a class="btn icon" href="{C.R}search.html" aria-label="Search">{icon("i-search")}</a><a class="btn y" href="{C.R}submit.html">{icon("i-send")}Send us news</a></div>
</div></div>
<nav class="corners" aria-label="Corners"><div class="wrap"><ul>{lis}</ul></div></nav>
</header>'''


def urgent():
    u = E.get('urgent')
    if not u or u not in BY:
        return ''
    s = BY[u]
    return (f'<div class="urgent" role="region" aria-label="Urgent"><div class="wrap"><span class="tag">Urgent</span>'
            f'<a href="{link(u)}">{esc(s["headline"])}</a>{tdate(s, long=True)}</div></div>')


def foot():
    corners = ''.join(f'<li><a href="{C.R}{k}.html">{esc(l)}</a></li>' for k, l, *_ in CORNERS)
    places = ''.join(f'<li><a href="{glink(k)}">{esc(n)}</a></li>' for k, n, *_ in GATES)
    return f'''<footer class="foot on-ink">
<div class="wrap">
<div class="top">
<div><a class="brand" href="{C.R}index.html" aria-label="{SITE}, today">{lockup()}</a>
<p style="margin-top:18px;max-width:40ch">A Jerusalem news platform. The city first, gate by gate and quarter by quarter, then the country around it.</p></div>
<div><h2>Corners</h2><ul>{corners}</ul></div>
<div><h2>{SITE}</h2><ul><li><a href="{C.R}gates.html">Every gate and quarter</a></li><li><a href="{C.R}about.html">About and how we work</a></li><li><a href="{C.R}submit.html">Send us news</a></li><li><a href="{C.R}search.html">Search</a></li><li><a href="{C.R}credits.html">Photo credits</a></li><li><a href="{C.R}identity.html">Identity</a></li></ul></div>
<div><h2>The morning gate</h2><p>Jerusalem’s news by email at 07:00, every morning.</p>
<form class="sub" action="#" method="post" data-proto="Subscribed in the prototype only. Nothing was sent."><label class="vh" for="em-f">Email address</label><input id="em-f" name="email" type="email" placeholder="you@example.com" autocomplete="email" required><button type="submit">Subscribe</button></form><p class="msg" role="status"></p></div>
</div>
<nav class="places" aria-label="Places"><h2>Gates and quarters</h2><ul>{places}</ul></nav>
</div>
<div class="credits"><div class="wrap"><span>Design prototype by TakTek for Al-Qastal. The stories are real and sourced; the publication is not live yet.</span><span>Type: Host Grotesk and Source Serif 4 (OFL). Photographs: Wikimedia Commons, <a href="{C.R}credits.html">credited here</a>.</span></div></div>
</footer>'''


def page(title, desc, body, current='', og=None, top=True):
    return (head(title, desc, og=og) + util() + mast(current) + (urgent() if top else '') +
            f'<main id="main">{body}</main>' + foot() +
            f'<script src="{C.R}assets/js/aq.js?v={V}" defer></script>\n</body>\n</html>\n')


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path) or ROOT, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
