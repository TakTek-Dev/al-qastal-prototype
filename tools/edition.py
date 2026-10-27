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

ids = {s['id'] for s in stories}
for k in ('lead', 'urgent'):
    if picks.get(k):
        assert picks[k] in ids, (k, picks[k])
edition = {
    'date': picks['date'], 'lead': picks['lead'], 'urgent': picks.get('urgent'), 'top': picks.get('top', []),
    'stories': stories, 'figures': news.get('figures', []), 'gate_photo': gate_photo,
    'pictures': picks.get('pictures', []),
}
json.dump(edition, open(os.path.join(ROOT, 'tools', 'edition.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(photos, open(os.path.join(ROOT, 'tools', 'photos.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(stories), 'stories,', len(photos), 'photos,', sum(1 for s in stories if s.get('photo')), 'with a photo')
