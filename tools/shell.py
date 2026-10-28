"""The shell every built page shares: head, strip, masthead, the corners, footer, loader, the marks.

Imported by build.py. C.R is the path back to the site root: '' at the root, '../' in story/ and gate/,
the absolute site path on 404.html. The site is Arabic, right to left.
"""
import datetime as dt
import html
import json
import os
import random

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = '19'                                       # bump on any asset change (Chrome caches hard)
SITE = 'القسطل'
BASE_URL = 'https://taktek-dev.github.io/al-qastal-prototype/'
BASE_PATH = '/al-qastal-prototype/'
E = json.load(open(os.path.join(ROOT, 'tools', 'edition.json'), encoding='utf-8'))
MARKS = json.load(open(os.path.join(ROOT, 'tools', 'out', 'marks.json'), encoding='utf-8'))
PH = json.load(open(os.path.join(ROOT, 'tools', 'photos.json'), encoding='utf-8'))
DIM_P = os.path.join(ROOT, 'tools', 'out', 'photos.json')
DIM = json.load(open(DIM_P, encoding='utf-8')) if os.path.exists(DIM_P) else {}
esc = html.escape
D = dt.date.fromisoformat
TODAY = D(E['date'])
S = sorted(E['stories'], key=lambda s: s['date'], reverse=True)
BY = {s['id']: s for s in S}


class Ctx:
    R = ''


C = Ctx()

# slug, tab label, page title, standfirst, dot colour
CORNERS = [
    ('jerusalem', 'القدس', 'القدس', 'المدينة بابا بابا وحيا حيا: الهدم والاعتقالات ومخططات الاستيطان والحواجز، والعائلات التي تبقى.', 'var(--yellow)'),
    ('aqsa', 'الأقصى', 'المسجد الأقصى', 'المسجد وأبوابه: من دخل ومن منع، وإغلاقات الأعياد، والحراس والمصلون.', 'var(--yellow)'),
    ('prisoners', 'الأسرى', 'الأسرى', 'أسرى القدس والسجون التي تحتجزهم: الحكم والسجن وتاريخ الاعتقال، والعدد الذي لا يتوقف عن الارتفاع.', 'var(--prison)'),
    ('martyrs', 'الشهداء', 'الشهداء', 'أبناء المدينة الذين ارتقوا: أسماؤهم، وأين ومتى، كما توثقها العائلات ومحافظة القدس.', 'var(--red)'),
    ('exiled', 'المبعدون', 'المبعدون', 'القرارات التي تبعد المقدسيين عن الأقصى أو البلدة القديمة أو المدينة: من تسلمها، وعن أي مكان، ولكم من الوقت.', 'var(--yellow)'),
    ('westbank', 'الضفة', 'الضفة الغربية', 'بقية الضفة المحتلة، حين يصل الخبر إلى عتبة القدس أو يعم البلاد.', 'var(--yellow)'),
    ('gaza', 'غزة', 'غزة', 'القطاع في ظل وقف إطلاق النار: الشهداء والجرحى، والمعابر، والنازحون.', 'var(--yellow)'),
    ('hebrew', 'ترجمات عبرية', 'من الصحافة العبرية', 'ما تقوله الصحف والقنوات الإسرائيلية عن القدس، ملخصا بالعربية مع رابط الأصل.', 'var(--yellow)'),
    ('statements', 'تصريحات', 'تصريحات', 'الجملة كما قيلت، ومن قالها، ومتى.', 'var(--yellow)'),
]
CORNER = {c[0]: c for c in CORNERS}

# key, name, second name, zone, where
GATES = [
    ('damascus-gate', 'باب العامود', 'باب دمشق', 'gates', 'السور الشمالي'),
    ('herods-gate', 'باب الساهرة', 'باب الزهرة', 'gates', 'السور الشمالي'),
    ('lions-gate', 'باب الأسباط', 'باب الأسود', 'gates', 'السور الشرقي'),
    ('golden-gate', 'باب الرحمة', 'الباب الذهبي', 'gates', 'السور الشرقي، مغلق'),
    ('dung-gate', 'باب المغاربة', 'باب السور الجنوبي', 'gates', 'السور الجنوبي'),
    ('zion-gate', 'باب النبي داود', 'باب صهيون', 'gates', 'السور الجنوبي'),
    ('jaffa-gate', 'باب الخليل', 'باب يافا', 'gates', 'السور الغربي'),
    ('new-gate', 'الباب الجديد', 'باب عبد الحميد', 'gates', 'السور الشمالي الغربي'),
    ('chain-gate', 'باب السلسلة', 'من أبواب الأقصى', 'gates', 'إلى المسجد الأقصى'),
    ('aqsa', 'المسجد الأقصى', 'الحرم القدسي الشريف', 'gates', 'الساحات والمصليات'),
    ('old-city', 'البلدة القديمة', 'داخل السور', 'gates', 'الحارات والأسواق'),
    ('silwan', 'سلوان', 'البستان ووادي حلوة وبطن الهوى', 'around', 'جنوب الأقصى'),
    ('ras-al-amud', 'رأس العامود', 'رأس العامود', 'around', 'جنوب شرق'),
    ('al-tur', 'الطور', 'جبل الزيتون', 'around', 'شرق السور'),
    ('sheikh-jarrah', 'الشيخ جراح', 'الشيخ جراح', 'around', 'شمال السور'),
    ('issawiya', 'العيسوية', 'العيسوية', 'around', 'شمال شرق'),
    ('jabal-mukabber', 'جبل المكبر', 'جبل المكبر', 'around', 'جنوب شرق'),
    ('sur-baher', 'صور باهر', 'صور باهر', 'around', 'جنوب'),
    ('walaja', 'الولجة', 'الولجة', 'around', 'جنوب غرب'),
    ('beit-hanina', 'بيت حنينا', 'بيت حنينا', 'beyond', 'شمال'),
    ('shuafat', 'مخيم شعفاط', 'مخيم شعفاط', 'beyond', 'خلف الجدار'),
    ('anata', 'عناتا', 'عناتا', 'beyond', 'خلف الجدار'),
    ('kafr-aqab', 'كفر عقب', 'كفر عقب', 'beyond', 'خلف الجدار'),
    ('qalandiya', 'قلنديا', 'المخيم والحاجز', 'beyond', 'الحاجز'),
    ('ezariya', 'العيزرية', 'العيزرية', 'beyond', 'شرقا، خلف الجدار'),
]
GATE = {g[0]: g for g in GATES}
ZONES = [('gates', 'الأبواب والبلدة القديمة', 'سبعة أبواب مفتوحة وباب مغلق، وأبواب المسجد، والحارات بينها.'),
         ('around', 'حول السور', 'الأحياء التي ترى السور، وإليها تذهب معظم أوامر الهدم.'),
         ('beyond', 'خلف الجدار', 'أحياء مقدسية فصلها جدار الفصل عن المدينة التي تنتمي إليها.')]

MONTHS = ['كانون الثاني', 'شباط', 'آذار', 'نيسان', 'أيار', 'حزيران', 'تموز', 'آب', 'أيلول', 'تشرين الأول', 'تشرين الثاني', 'كانون الأول']
DAYS = ['الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد']


def n_ar(n, one, two, few, many):
    """Arabic counted noun: 1 قصة, 2 قصتان, 3-10 قصص, 11+ قصة."""
    if n == 1:
        return one
    if n == 2:
        return two
    return f'{n} {few if 3 <= n % 100 <= 10 else many}'


def stories_n(n):
    return n_ar(n, 'خبر واحد', 'خبران', 'أخبار', 'خبرا')


def num(v):
    """A figure like 1,000+ or 9,300 kept in its own left-to-right run inside Arabic."""
    return f'<bdi dir="ltr">{esc(str(v))}</bdi>'


def gate_of(s):
    g = s.get('gate')
    return g if g in GATE else None


def stories(corner=None, gate=None):
    return [s for s in S if (not corner or s['corner'] == corner) and (not gate or s.get('gate') == gate)]


def day(d, year=False):
    d = D(d) if isinstance(d, str) else d
    return f'{d.day} {MONTHS[d.month - 1]}' + (f' {d.year}' if year or d.year != TODAY.year else '')


def long_day(d):
    d = D(d) if isinstance(d, str) else d
    return f'{DAYS[d.weekday()]} {d.day} {MONTHS[d.month - 1]} {d.year}'


def ago(s):
    d = D(s['date'])
    n = (TODAY - d).days
    if n == 0:
        return 'اليوم'
    if n == 1:
        return 'أمس'
    if n < 6:
        return DAYS[d.weekday()]
    return day(d)


def tdate(s, long=False):
    return f'<time datetime="{s["date"]}">{esc(long_day(s["date"]) if long else ago(s))}</time>'


# ---------------------------------------------------------------- icons and marks
# right to left: "forward" points left, "back" points right
SPRITE = '''<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>
<symbol id="i-fwd" viewBox="0 0 16 16"><path d="M13 8H3M7.5 3.5 3 8l4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-back" viewBox="0 0 16 16"><path d="M3 8h10M8.5 3.5 13 8l-4.5 4.5" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></symbol>
<symbol id="i-search" viewBox="0 0 16 16"><path d="M9 2.5a4.5 4.5 0 1 0 0 9 4.5 4.5 0 0 0 0-9zM5.6 10.4 2 14" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"/></symbol>
<symbol id="i-send" viewBox="0 0 16 16"><path d="M13.5 7.6 2.5 2.5 6.2 13.5 8.4 8.6z M8.4 8.6 2.5 2.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/></symbol>
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


# ---------------------------------------------------------------- pieces from the client's own post templates
def _rip(seed, y, amp, w=1440):
    """A torn edge across the width: points at uneven steps, each a little above or below y."""
    rnd = random.Random(seed)
    pts, x = [], 0.0
    while x < w:
        pts.append(f'{x:.0f} {y + rnd.uniform(-amp, amp):.1f}')
        x += rnd.uniform(9, 26)
    pts.append(f'{w} {y + rnd.uniform(-amp, amp):.1f}')
    return 'M' + 'L'.join(pts) + 'V48H0Z'


TEAR_Y, TEAR_W = _rip(7, 13, 9), _rip(19, 25, 7)


def tear():
    """The paper tears out of the dark, with the yellow rip under its edge (the cover template)."""
    return (f'<svg class="tear" viewBox="0 0 1440 48" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">'
            f'<path d="{TEAR_Y}" fill="#FFDD36"/><path d="{TEAR_W}" fill="currentColor"/></svg>')


def _strand():
    twist = ''.join(f'Q{x + 15} {22 if k % 2 == 0 else 38} {x + 30} 30' for k, x in enumerate(range(0, 1200, 30)))
    twist2 = ''.join(f'Q{x + 15} {38 if k % 2 == 0 else 22} {x + 30} 30' for k, x in enumerate(range(0, 1200, 30)))
    barbs = ''.join(f'M{x - 11} 15L{x + 11} 45M{x + 11} 15L{x - 11} 45M{x - 5} 25h10v10h-10z' for x in range(75, 1200, 150))
    return f'M0 30{twist}M0 30{twist2}{barbs}'


STRAND = _strand()


def wire(cls=''):
    """A strand of barbed wire, as it crosses the corner of the prisoners' template."""
    return (f'<svg class="wire{(" " + cls) if cls else ""}" viewBox="0 0 1200 60" aria-hidden="true" focusable="false">'
            f'<path d="{STRAND}" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')


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
    return (f'{esc(p["caption"])} تصوير: <bdi>{esc(p["author"])}</bdi>، <span class="ltr">{esc(p["license"])}</span>، '
            f'عبر ويكيميديا كومنز.')


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


def doorway(mid):
    return (f'<svg class="mask-sv" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
            f'<defs><mask id="{mid}"><rect width="1000" height="1000" fill="#fff"/>'
            f'<path class="hole" d="{HOLE}" fill="#000"/></mask></defs>'
            f'<rect width="1000" height="1000" fill="#0E1724" mask="url(#{mid})"/></svg>')


def loader():
    t = MARKS['tower']
    tw = (f'<svg viewBox="{t["viewBox"]}"><path class="t-blk" d="{t["block"]}"/><path class="t-door" d="{t["door"]}"/>'
          f'<path class="t-sw" d="{t["swing"]}"/><path class="t-fold" d="{t["fold"]}"/></svg>')
    return (f'<div class="ldr" aria-hidden="true">{doorway("ldm")}<div class="tw">{tw}</div>'
            f'<p class="say"><b>{long_day(TODAY)}</b> · القدس</p></div>'
            f'<div class="gate-nav" aria-hidden="true">{doorway("gnm")}</div>')


# Swiper for the gates slider on the home page only (cdnjs, pinned and checked with SRI)
SWIPER = 'https://cdnjs.cloudflare.com/ajax/libs/Swiper/11.2.6/'
SWIPER_CSS = ('<link rel="stylesheet" href="' + SWIPER + 'swiper-bundle.min.css" crossorigin="anonymous" '
              'integrity="sha384-9kDDKx/5+oRQIb/Ce7grsjaS0AWcNd9aPYY7ubOmUBUO3GovHz5BO0RliSAPq2S/">\n')
SWIPER_JS = ('<script src="' + SWIPER + 'swiper-bundle.min.js" crossorigin="anonymous" defer '
             'integrity="sha384-Z8zwe4UlCA9xiPVMGPhmzBsPAEVtt/gabOsU+0A8Lf67I0MjHjP+UzNYng2CtJar"></script>\n')


def head(title, desc, og=None, swiper=False):
    t = esc(title if title == SITE else f'{title} · {SITE}')
    return f'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t}</title>
<meta name="description" content="{esc(desc)}">
<meta name="theme-color" content="#0E1724">
<link rel="icon" href="{C.R}favicon.svg?v={V}" type="image/svg+xml">
<link rel="preload" href="{C.R}assets/fonts/alexandria.woff2" as="font" type="font/woff2" crossorigin>
{SWIPER_CSS if swiper else ''}<link rel="stylesheet" href="{C.R}assets/css/aq.css?v={V}">
<meta property="og:type" content="website">
<meta property="og:locale" content="ar_AR">
<meta property="og:site_name" content="{SITE}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{BASE_URL}{og or 'assets/og.png'}">
<meta name="twitter:card" content="summary_large_image">
<meta name="robots" content="noindex">
<script>{EARLY}</script>
</head>
<body>
{loader()}<a class="skip" href="#main">انتقل إلى الأخبار</a>
{SPRITE}'''


def util():
    return (f'<div class="util"><div class="wrap"><span><b>{long_day(TODAY)}</b></span>'
            f'<span class="clock hide-s" data-clock>القدس</span><span class="sp"></span>'
            f'<a class="hide-s" href="{C.R}about.html">من نحن</a><a class="hide-s" href="{C.R}submit.html">أرسل خبرا</a>'
            f'<a class="hdl ltr" href="https://t.me/alqastalps" rel="noopener" target="_blank">@alqastalps</a></div></div>')


def mast(current=''):
    tabs = ([('index', 'اليوم', f'{C.R}index.html'), ('gates', 'الأبواب', f'{C.R}gates.html')] +
            [(k, l, f'{C.R}{k}.html') for k, l, *_ in CORNERS])
    lis = ''.join(
        f'<li{" class=\"last\"" if i == len(tabs) - 1 else ""}><a href="{u}"{" aria-current=\"page\"" if k == current else ""}>'
        f'{esc(l)}{swing()}</a></li>' for i, (k, l, u) in enumerate(tabs))
    return f'''<header class="mast on-ink">
<div class="wrap"><div class="row">
<a class="brand" href="{C.R}index.html" aria-label="{SITE}، اليوم">{lockup()}</a>
<p class="motto"><b>القدس أولا.</b> كل خبر من بابه.</p>
<div class="tools"><a class="btn icon" href="{C.R}search.html" aria-label="بحث">{icon("i-search")}</a><a class="btn y" href="{C.R}submit.html">{icon("i-send")}أرسل خبرا</a></div>
</div></div>
<nav class="corners" aria-label="الزوايا"><div class="wrap"><ul>{lis}</ul></div></nav>
</header>'''


def urgent():
    u = E.get('urgent')
    if not u or u not in BY:
        return ''
    s = BY[u]
    return (f'<div class="urgent" role="region" aria-label="عاجل"><div class="wrap"><span class="tag">عاجل</span>'
            f'<a href="{link(u)}">{esc(s["headline"])}</a>{tdate(s, long=True)}</div></div>')


def foot():
    corners = ''.join(f'<li><a href="{C.R}{k}.html">{esc(l)}</a></li>' for k, l, *_ in CORNERS)
    places = ''.join(f'<li><a href="{glink(k)}">{esc(n)}</a></li>' for k, n, *_ in GATES)
    return f'''<footer class="foot on-ink">
<div class="wrap">
<div class="top">
<div><a class="brand" href="{C.R}index.html" aria-label="{SITE}، اليوم">{lockup()}</a>
<p style="margin-top:18px;max-width:40ch">منصة إخبارية مقدسية. المدينة أولا، بابا بابا وحيا حيا، ثم البلاد من حولها.</p></div>
<div><h2>الزوايا</h2><ul>{corners}</ul></div>
<div><h2>{SITE}</h2><ul><li><a href="{C.R}gates.html">كل الأبواب والأحياء</a></li><li><a href="{C.R}about.html">من نحن وكيف نعمل</a></li><li><a href="{C.R}submit.html">أرسل خبرا</a></li><li><a href="{C.R}search.html">بحث</a></li><li><a href="{C.R}credits.html">حقوق الصور</a></li><li><a href="{C.R}identity.html">الهوية</a></li></ul></div>
<div><h2>نشرة الصباح</h2><p>أخبار القدس في بريدك كل صباح عند السابعة.</p>
<form class="sub" action="#" method="post" data-proto="اشتركت في النموذج فقط. لم يرسل شيء."><label class="vh" for="em-f">البريد الإلكتروني</label><input id="em-f" name="email" type="email" placeholder="بريدك الإلكتروني" autocomplete="email" dir="ltr" required><button type="submit">اشترك</button></form><p class="msg" role="status"></p></div>
</div>
<nav class="places" aria-label="الأبواب والأحياء"><h2>الأبواب والأحياء</h2><ul>{places}</ul></nav>
</div>
<div class="credits"><div class="wrap"><span>نموذج تصميم من تك تك لموقع القسطل. الأخبار حقيقية وموثقة بمصادرها، والموقع لم ينشر بعد.</span><span>الخطوط: الإسكندرية ونوتو نسخ (رخصة <span class="ltr">OFL</span>). الصور: ويكيميديا كومنز، <a href="{C.R}credits.html">بأسماء أصحابها</a>.</span></div></div>
</footer>'''


def page(title, desc, body, current='', og=None, top=True, swiper=False):
    return (head(title, desc, og=og, swiper=swiper) + util() + mast(current) + (urgent() if top else '') +
            f'<main id="main">{body}</main>' + foot() + (SWIPER_JS if swiper else '') +
            f'<script src="{C.R}assets/js/aq.js?v={V}" defer></script>\n</body>\n</html>\n')


def write(rel, text):
    path = os.path.join(ROOT, rel)
    os.makedirs(os.path.dirname(path) or ROOT, exist_ok=True)
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(text)
