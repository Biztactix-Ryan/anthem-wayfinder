# Anthem Wayfinder

An unofficial interactive 3D deck map of Anthem of the Seas. Type a cabin number, pick a place, and it gives a lift-only route with distances for each option.

- `index.html` is the whole app in one file. It works offline once saved to a phone.
- `src/page.html` is the source; `data/decks.json` is the deck geometry.
- `python3 tools/build.py` rebuilds `index.html` after editing either.
- `tools/extract.py <svg-dir> data/decks.json` regenerates the geometry from the per-deck SVG plans.

Deck shapes, cabins, lifts and stairs come from the cruise line's published deck plans. Venue positions were placed by hand and are approximate. Distances are estimates. Not affiliated with Royal Caribbean.
