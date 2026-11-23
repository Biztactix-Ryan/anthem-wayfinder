"""Build the map page: inline data/decks.json into src/page.html.
Writes index.html (for GitHub Pages) and anthem-wayfinder.html (same page, for offline use), plus an optional fragment path."""
import sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
page = (root / 'src' / 'page.html').read_text()
data = (root / 'data' / 'decks.json').read_text()
assert page.count('/*DATA*/null') == 1
frag = page.replace('/*DATA*/null', data)
html = (
    '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
    '<style>html{color-scheme:light dark}body{margin:0}</style></head><body>\n' + frag + '\n</body></html>\n')
(root / 'anthem-wayfinder.html').write_text(html)  # offline copy
(root / 'index.html').write_text(html)              # served by GitHub Pages
if len(sys.argv) > 1:
    pathlib.Path(sys.argv[1]).write_text(frag)
print('built', len(frag), 'bytes')
