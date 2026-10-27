"""Self-hosted WOFF2 subsets of the two faces.

python -I tools/fonts.py   (from the project root; sources in research/font-src, gitignored)

Host Grotesk (Element Type, OFL) is the voice of the masthead: corner names, gate names, headlines,
labels and every figure. It sits closest to the Latin of the client's lockup (round Q, two-storey a)
and stays plain enough that a corner name is read, not deciphered. Source Serif 4 (Adobe, OFL)
carries the reading: standfirsts and story text, at its text optical size.
"""
import io
import os
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'research', 'font-src')
OUT = os.path.join(ROOT, 'assets', 'fonts')
os.makedirs(OUT, exist_ok=True)

# Latin + Latin-1 + Extended-A, the transliteration letters Arabic names use, typographic punctuation,
# arrows, the shekel, multiplication and degree signs.
UNICODES = (
    list(range(0x20, 0x7F)) + list(range(0xA0, 0x180)) +
    [0x1E0C, 0x1E0D, 0x1E24, 0x1E25, 0x1E62, 0x1E63, 0x1E6C, 0x1E6D, 0x1E92, 0x1E93, 0x02BE, 0x02BF, 0x02BC,
     0x2009, 0x200A, 0x2010, 0x2011, 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026,
     0x2032, 0x2033, 0x2039, 0x203A, 0x20AC, 0x20AA, 0x2116, 0x2190, 0x2191, 0x2192, 0x2193,
     0x2197, 0x2212, 0x00D7, 0x00B0, 0x00B7, 0x00BD]
)

JOBS = [
    ('HostGrotesk[wght].ttf', 'host.woff2', {'wght': (400, 800)}),
    ('SourceSerif4[opsz,wght].ttf', 'serif.woff2', {'opsz': (8, 40), 'wght': (400, 600)}),
    ('SourceSerif4-Italic[opsz,wght].ttf', 'serif-italic.woff2', {'opsz': (8, 24), 'wght': 400}),
]


def options():
    o = subset.Options()
    o.flavor = 'woff2'
    o.layout_features = ['*']
    o.name_IDs = ['*']
    o.notdef_outline = True
    o.glyph_names = False
    o.hinting = False
    o.desubroutinize = True
    return o


for src, out, limits in JOBS:
    font = instancer.instantiateVariableFont(TTFont(os.path.join(SRC, src)), limits)
    buf = io.BytesIO()
    font.save(buf)
    buf.seek(0)
    font = TTFont(buf)
    sub = subset.Subsetter(options())
    sub.populate(unicodes=UNICODES)
    sub.subset(font)
    font.flavor = 'woff2'
    font.save(os.path.join(OUT, out))
    print(out, os.path.getsize(os.path.join(OUT, out)) // 1024, 'KB')
