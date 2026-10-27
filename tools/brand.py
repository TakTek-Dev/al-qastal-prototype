"""The Al-Qastal marks, from the client's own logo file.

python -I tools/brand.py <dir-with-potracer>   (once; writes tools/out/marks.json + assets/img/*.svg)

The tower is redrawn from measurements of research/brand/stamp-white.png (block 548 px square at
2688,334 in the 4167 px file): a crenel 74 x 75 cut from the top, a round-headed door 175 wide,
and the yellow quarter disc hung under the block from the crenel's right edge, with its darker fold.
Read as a plan drawing, that quarter disc is a door's swing: the whole site is built on it.
The Arabic and Latin words are traced from the same file (potracer, pure Python) and kept as paths.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tools', 'out')
IMG = os.path.join(ROOT, 'assets', 'img')
os.makedirs(OUT, exist_ok=True)
os.makedirs(IMG, exist_ok=True)

YELLOW, FOLD = '#FFDD36', '#EBCD38'

# tower, in the logo's own pixels relative to the block's top-left corner
BLOCK = 'M0 0H237V75H311V0H548V548H0Z'
DOOR = 'M184 403V309.5A87.5 87.5 0 0 1 359 309.5V403Z'
SWING = 'M319 550H548A229 229 0 0 1 319 779Z'
FOLD_P = 'M319 550H548L319 580Z'
TOWER_VB = '0 0 548 779'


def trace(src, box, scale):
    """White pixels inside box -> one compound path, in the logo's pixel space."""
    sys.path.insert(0, sys.argv[1])
    import numpy as np
    import potrace
    from PIL import Image
    im = Image.open(src).convert('RGBA').crop(box)
    im = im.resize((im.width // scale, im.height // scale), Image.LANCZOS)
    a = np.asarray(im)
    bm = potrace.Bitmap(~((a[:, :, 3] > 127) & (a[:, :, 0] > 200)))   # potracer fills the False side
    plist = bm.trace(turdsize=4, alphamax=1.0, opticurve=True, opttolerance=0.2)
    f = lambda p: f'{p.x * scale + box[0]:.1f} {p.y * scale + box[1]:.1f}'
    d = []
    for curve in plist:
        d.append('M' + f(curve.start_point))
        for seg in curve.segments:
            if seg.is_corner:
                d.append('L' + f(seg.c) + 'L' + f(seg.end_point))
            else:
                d.append('C' + f(seg.c1) + ' ' + f(seg.c2) + ' ' + f(seg.end_point))
        d.append('Z')
    return ''.join(d)


def main():
    src = os.path.join(ROOT, 'research', 'brand', 'stamp-white.png')
    ar = trace(src, (740, 320, 2660, 812), 2)       # القسطل
    la = trace(src, (1170, 812, 2660, 1110), 2)     # AL Qastal
    # whole lockup in logo pixels: words left of the tower, tower at x 2688
    marks = {
        'tower': {'viewBox': TOWER_VB, 'block': BLOCK, 'door': DOOR, 'swing': SWING, 'fold': FOLD_P},
        'lockup': {'viewBox': '740 320 2500 795', 'ar': ar, 'la': la, 'tx': 2688, 'ty': 334},
        'yellow': YELLOW, 'fold': FOLD,
    }
    json.dump(marks, open(os.path.join(OUT, 'marks.json'), 'w', encoding='utf-8'))

    def tower(ink, door_fill=None):
        door = f'<path d="{DOOR}" fill="{door_fill}"/>' if door_fill else ''
        return (f'<path d="{BLOCK}{"" if door_fill else DOOR}" fill="{ink}" fill-rule="evenodd"/>{door}'
                f'<path d="{SWING}" fill="{YELLOW}"/><path d="{FOLD_P}" fill="{FOLD}"/>')

    def lockup(ink):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="740 320 2500 795">'
                f'<path d="{ar}" fill="{ink}"/><path d="{la}" fill="{ink}"/>'
                f'<g transform="translate(2688 334)">{tower(ink)}</g></svg>')

    open(os.path.join(IMG, 'logo-ink.svg'), 'w').write(lockup('#0E1724'))
    open(os.path.join(IMG, 'logo-white.svg'), 'w').write(lockup('#FFFFFF'))
    open(os.path.join(IMG, 'tower.svg'), 'w').write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{TOWER_VB}">{tower("#0E1724")}</svg>')
    # favicon: the tower on ink, the door left open to the ink
    open(os.path.join(ROOT, 'favicon.svg'), 'w').write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-130 -110 808 1000">'
        '<rect x="-130" y="-110" width="808" height="1000" rx="170" fill="#0E1724"/>'
        f'{tower("#FFFFFF")}</svg>')
    print('ar', len(ar), 'la', len(la))


if __name__ == '__main__':
    main()
