"""Check every internal link and asset on every built page.

python -I tools/links.py   -> lists broken hrefs/srcs and #anchors; exit 1 if any
404.html uses the site's absolute path, which is mapped back to the repo root here.
"""
import glob
import os
import re
import sys
from urllib.parse import urldefrag

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = '/al-qastal-prototype/'
pages = [p for p in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)
         if not os.path.relpath(p, ROOT).startswith(('tools', 'research', 'node_modules'))]
ids = {}
for p in pages:
    ids[os.path.normpath(p)] = set(re.findall(r'\sid="([^"]+)"', open(p, encoding='utf-8').read()))
bad = []
for p in pages:
    h = open(p, encoding='utf-8').read()
    for ref in re.findall(r'(?:href|src)="([^"]+)"', h):
        if ref.startswith(('http', 'mailto:', 'data:')) or "'" in ref:
            continue
        url, frag = urldefrag(ref)
        url = url.split('?')[0]
        if url.startswith(BASE):
            target = os.path.join(ROOT, url[len(BASE):])
        elif url:
            target = os.path.normpath(os.path.join(os.path.dirname(p), url))
        else:
            target = os.path.normpath(p)
        if url.endswith('/') or os.path.isdir(target):
            target = os.path.join(target, 'index.html')
        if not os.path.exists(target):
            bad.append((os.path.relpath(p, ROOT), ref))
        elif frag and frag not in ids.get(os.path.normpath(target), set()) and target.endswith('.html'):
            bad.append((os.path.relpath(p, ROOT), ref + '  (no such id)'))
print(len(pages), 'pages checked,', len(bad), 'broken')
for b in sorted(set(bad))[:60]:
    print('  ', *b)
sys.exit(1 if bad else 0)
