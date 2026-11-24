# Anthem Wayfinder

An unofficial interactive 3D deck map of Anthem of the Seas. Pick where you are (your cabin or any place on board) and where you want to go, and it gives a lift-only route with distances for each option. Places are listed by name, with starred favourites at the top.

- `index.html` is the whole app in one file. It works offline once saved to a phone.
- `src/page.html` is the source; `data/decks.json` is the deck geometry.
- `python3 tools/build.py` rebuilds `index.html` after editing either.
- `tools/extract.py <svg-dir> data/decks.json` regenerates the geometry from the per-deck SVG plans.

Deck shapes, cabins, lifts and stairs come from the cruise line's published deck plans. Venue positions were placed by hand and are approximate. Distances are estimates. Not affiliated with Royal Caribbean.
