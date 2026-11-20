# news-image-20261119 — Top-10 version

"Thursday 19 November 2026, one day, 17 stories" — a separate entry built
from Claude's top-10 concept (17 stories, one big hero scene, no body text).

`main.py` (Python stdlib + PIL, no network) renders the 1024x1024 entry
image deterministically to `assets/entry.png` and to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`):

```sh
python3 main.py
```

Layout: masthead with the full date as the largest text; hero row with a
flat-vector Shenzhen summit scene (skyline, three flags, three faceless
seated figures, declaration paper) plus GTA VI and Anthropic cards; a 3x2
mid grid with REPORTED / CLAIM / FORECAST tags; an "Also on Thursday
19 November" strip of 8 items; footer with the tag legend.
