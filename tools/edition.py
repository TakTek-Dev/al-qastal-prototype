"""Compose tools/edition.json and tools/photos.json from the research.

python -I tools/edition.py
Reads research/news.json (sourced items), research/photos.json (Commons candidates) and tools/picks.json
(hand choices: lead, urgent, drops, story -> photo, gate -> photo). A story with no hand-picked photo takes
a photograph of its own place when one exists; on the site such a photo is captioned as a file photo of
the place, with the date it was really taken. Places with no photograph get a drawn door instead.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rd = lambda p: json.load(open(os.path.join(ROOT, p), encoding='utf-8'))
news, cand, picks = rd('research/news.json'), rd('research/photos.json')['photos'], rd('tools/picks.json')
# the site is Arabic: research/news-ar.json and photos-ar.json carry the Arabic text for every id and slug
AR, PAR = rd('research/news-ar.json'), rd('research/photos-ar.json')


def fig_kind(label):
    """Which corner a headline count belongs to, read from its English label."""
    t = label.lower()
    for k, words in (('prisoners', ('prisoner', 'detain', 'detention', 'custody')), ('exiled', ('ban', 'deport', 'expel', 'exile')),
                     ('aqsa', ('aqsa', 'storm', 'incursion')), ('martyrs', ('killed', 'martyr', 'death'))):
        if any(w in t for w in words):
            return k
    return 'jerusalem'


def arabic(s, a):
    """Lay the Arabic text over a story; facts the translation does not carry (dates, values, links) stay."""
    for k in ('headline', 'standfirst', 'body', 'place'):
        if a.get(k):
            s[k] = a[k]
    if s.get('figure') and a.get('figure_label'):
        s['figure'] = dict(s['figure'], label=a['figure_label'])
    if s.get('quote') and a.get('quote'):
        s['quote'] = dict(s['quote'], **{k: v for k, v in a['quote'].items() if v is not None})
    if s.get('person') and a.get('person'):
        ap, p = a['person'], dict(s['person'])
        for k in ('name', 'status', 'sentence', 'prison'):
            if ap.get(k):
                p[k] = ap[k]
        if p.get('ban'):
            p['ban'] = dict(p['ban'], length_en=p['ban'].get('length'), **{k2: ap[k1] for k1, k2 in (('ban_from', 'from'), ('ban_length', 'length')) if ap.get(k1)})
        s['person'] = p
    s['outlet_ar'] = a.get('outlet_ar')
    names = a.get('source_names') or []
    s['sources'] = [dict(o, name=names[i]) if i < len(names) and names[i] else o for i, o in enumerate(s.get('sources') or [])]
    return s

# what a corner may borrow when its story has no place photo of its own
# (only prison exteriors are honest stand-ins: a West Bank or Gaza photo names a different village)
CORNER_FALLBACK = {'prisoners': 'prison'}

by_gate = {}
for k, c in cand.items():
    by_gate.setdefault(c.get('gate'), []).append(k)

drop = set(picks.get('drop', []))
use_count = {}
stories = []
for it in news['items']:
    if it['id'] in drop:
        continue
    s = {k: it.get(k) for k in ('id', 'corner', 'kind', 'date', 'place', 'gate', 'headline', 'standfirst', 'body',
                                 'figure', 'quote', 'person', 'outlet_he', 'sources')}
    if it['id'] not in AR['items']:
        raise SystemExit(f'{it["id"]}: no Arabic text')
    s = arabic(s, AR['items'][it['id']])
    for k, v in picks.get('edit', {}).get(it['id'], {}).items():
        s[k] = v
    ph = picks.get('photo', {}).get(it['id'])
    if ph is None and it['id'] not in picks.get('no_photo', []):
        pool = by_gate.get(s.get('gate')) or by_gate.get(CORNER_FALLBACK.get(s['corner'])) or []
        if pool:   # spread the place's photographs across its stories
            ph = min(pool, key=lambda k: (use_count.get(k, 0), pool.index(k)))
    if ph:
        if ph not in cand:
            raise SystemExit(f'{it["id"]}: no candidate photo {ph}')
        s['photo'] = ph
        s['photo_own'] = it['id'] in picks.get('own', [])   # taken at this event, not a file photo
        use_count[ph] = use_count.get(ph, 0) + 1
    stories.append(s)

gate_photo = dict(picks.get('gate_photo', {}))
for g, pool in by_gate.items():
    gate_photo.setdefault(g, pool[0])

used = {s['photo'] for s in stories if s.get('photo')} | set(gate_photo.values()) | set(picks.get('pictures', []))
photos = {}
for k in sorted(used):
    c = cand[k]
    photos[k] = {f: c.get(f) for f in ('file', 'page_url', 'author', 'license', 'date', 'alt', 'caption', 'place', 'gate')}
    if picks.get('focus', {}).get(k):
        photos[k]['focus'] = picks['focus'][k]
    if k in PAR:
        photos[k].update({f: PAR[k][f] for f in ('alt', 'caption') if PAR[k].get(f)})
        photos[k]['place'] = PAR[k].get('place') or PAR[k]['caption'].split(':')[0].split('،')[0]

figures = []
for i, f in enumerate(news.get('figures', [])):
    fa = (AR.get('figures') or [])[i] if i < len(AR.get('figures') or []) else {}
    figures.append(dict(f, kind=fig_kind(f['label']), label=fa.get('label') or f['label'], source=fa.get('source') or f.get('source')))

ids = {s['id'] for s in stories}
for k in ('lead', 'urgent'):
    if picks.get(k):
        assert picks[k] in ids, (k, picks[k])
edition = {
    'date': picks['date'], 'lead': picks['lead'], 'urgent': picks.get('urgent'), 'top': picks.get('top', []),
    'stories': stories, 'figures': figures, 'gate_photo': gate_photo,
    'pictures': picks.get('pictures', []),
}
json.dump(edition, open(os.path.join(ROOT, 'tools', 'edition.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(photos, open(os.path.join(ROOT, 'tools', 'photos.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(stories), 'stories,', len(photos), 'photos,', sum(1 for s in stories if s.get('photo')), 'with a photo')
