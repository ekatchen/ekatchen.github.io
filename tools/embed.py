#!/usr/bin/env python3
"""Embed headshot.jpg into index.html as a data URI.

The card is served as a single self-contained file, so the photo lives inside
the HTML rather than beside it. To change your headshot:

    1. Replace headshot.jpg (square crop, face slightly above centre)
    2. python3 tools/embed.py
    3. git commit and push

Re-running is safe — it swaps whatever image is currently embedded.
"""

import base64
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = ROOT / "index.html"
PHOTO = ROOT / "headshot.jpg"

# Matches either the build placeholder or an already-embedded data URI.
SRC_PATTERN = re.compile(
    r'(<img id="headshot" src=")(__HEADSHOT_SRC__|data:image/[^"]*)(")'
)


def main() -> int:
    if not PHOTO.exists():
        print(f"error: {PHOTO.name} not found in {ROOT}", file=sys.stderr)
        return 1

    raw = PHOTO.read_bytes()
    data_uri = "data:image/jpeg;base64," + base64.b64encode(raw).decode()

    html = HTML.read_text(encoding="utf-8")
    html, count = SRC_PATTERN.subn(lambda m: m.group(1) + data_uri + m.group(3), html)

    if count != 1:
        print(
            f"error: expected 1 headshot img tag, found {count}. "
            "Has index.html been restructured?",
            file=sys.stderr,
        )
        return 1

    HTML.write_text(html, encoding="utf-8")
    print(f"embedded {PHOTO.name} ({len(raw) // 1024} KB) into {HTML.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
