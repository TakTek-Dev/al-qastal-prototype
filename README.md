# Al-Qastal — English site prototype

A Jerusalem-first news site for **Al-Qastal (القسطل)**, built on the client's own identity: the tower with its
crenel and round-headed door, and the yellow quarter disc under it, read as the swing of an open door.

- Home `index.html`, the gates `gates.html` and one page per gate or quarter in `gate/`, one page per corner,
  one page per story in `story/`, about, send us news, search, photo credits, identity, 404.
- Brief and feedback: the client liked sample 3 of an earlier designer ("every story in its template") and asked to
  fold in the gates of sample 1, to set corner names in a clearer type, and to give the prisoners a corner like the
  martyrs'. Earlier samples are in `research/prior-designer/`, the client's templates in `research/brand/`.

## Build

```
python -I tools/fonts.py      # WOFF2 subsets from research/font-src (gitignored)
python -I tools/brand.py <dir-with-potracer>   # once: marks.json + logo SVGs, traced from the client's PNG
python -I tools/edition.py    # research/news.json + photos.json + tools/picks.json -> tools/edition.json
python -I tools/photos.py     # Commons photos -> assets/img/photo/*.webp + CREDITS.md
python -I tools/build.py      # every page
python -I tools/links.py      # broken-link check
```

Bump `V` in `tools/shell.py` after any CSS or JS change. Never hand-edit built HTML.

Type: Host Grotesk and Source Serif 4 (SIL OFL). Photographs: Wikimedia Commons, credited in `credits.html`.
