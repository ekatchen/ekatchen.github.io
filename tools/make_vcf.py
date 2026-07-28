#!/usr/bin/env python3
"""Generate contact.vcf, with the headshot embedded as a vCard PHOTO.

Deliberately minimal: name, phone, email, photo. No job title, school, or
LinkedIn — those live on the card page, not in someone's address book.

Run after changing any detail below or replacing headshot.jpg:

    python3 tools/make_vcf.py
"""

import base64
import io
import pathlib
import sys

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
PHOTO = ROOT / "headshot.jpg"
OUT = ROOT / "contact.vcf"

FIRST = "Estela"
LAST = "Katchen"
PHONE = "+14168898190"
EMAIL = "ekatchen.hba2028@ivey.ca"

# Contact photos render small; 300px keeps the file light enough to stay
# comfortable over conference wifi.
PHOTO_PX = 300
PHOTO_QUALITY = 82


def fold(line: str, limit: int = 75) -> list[str]:
    """Fold a long content line per RFC 2426: continuations start with a space."""
    out = [line[:limit]]
    rest = line[limit:]
    while rest:
        out.append(" " + rest[: limit - 1])
        rest = rest[limit - 1 :]
    return out


def photo_line() -> str:
    img = Image.open(PHOTO).convert("RGB")
    img = img.resize((PHOTO_PX, PHOTO_PX), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=PHOTO_QUALITY, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return "\r\n".join(fold("PHOTO;ENCODING=b;TYPE=JPEG:" + b64))


def main() -> int:
    if not PHOTO.exists():
        print(f"error: {PHOTO.name} not found", file=sys.stderr)
        return 1

    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{LAST};{FIRST};;;",
        f"FN:{FIRST} {LAST}",
        f"TEL;TYPE=CELL,VOICE:{PHONE}",
        f"EMAIL;TYPE=INTERNET,PREF:{EMAIL}",
        photo_line(),
        "END:VCARD",
    ]

    OUT.write_bytes(("\r\n".join(lines) + "\r\n").encode("utf-8"))
    print(f"wrote {OUT.name} ({OUT.stat().st_size // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
