#!/usr/bin/env python3
"""Render og.png (1200x630) for The Living Indexes — dark premium hub card. Pillow only."""
from __future__ import annotations

import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def _font(paths, size):
    from PIL import ImageFont
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def main() -> int:
    try:
        from PIL import Image, ImageDraw
    except Exception:
        print("Pillow not available — skipping og.png")
        return 0
    try:
        data = json.load(open(os.path.join(HERE, "data.json"), encoding="utf-8"))
        total = data.get("total_indexed", 0)
        idxs = data.get("indexes", [])
    except Exception:
        total, idxs = 0, []

    W, H = 1200, 630
    bg, ink, muted = (8, 9, 12), (238, 241, 246), (138, 146, 164)
    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    serif = ["/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
             "/System/Library/Fonts/Supplemental/Georgia.ttf", "/Library/Fonts/Georgia.ttf"]
    mono = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/System/Library/Fonts/Menlo.ttc", "/System/Library/Fonts/Monaco.ttf"]
    f_kick = _font(mono, 22)
    f_h1 = _font(serif, 72)
    f_big = _font(serif, 120)
    f_stat = _font(mono, 26)

    # four accent dots
    accents = [(179, 101, 31), (127, 174, 44), (31, 91, 255), (255, 59, 47)]
    for i, c in enumerate(accents):
        d.ellipse([70 + i * 30, 72, 70 + i * 30 + 18, 90], fill=c)
    d.text((70, 112), "THE LIVING INDEXES", font=f_kick, fill=muted)
    d.text((68, 156), "Living maps of what", font=f_h1, fill=ink)
    d.text((68, 236), "builders actually use.", font=f_h1, fill=ink)

    d.text((70, 380), str(total), font=f_big, fill=ink)
    tw = d.textlength(str(total), font=f_big)
    d.text((70 + tw + 24, 452), "entries indexed", font=f_stat, fill=muted)
    names = "  ·  ".join((ix.get("name", "") or "").replace("The ", "") for ix in idxs) or "Skill · Eval · Local LLM · Prompt"
    d.text((70, 552), names, font=f_stat, fill=muted)
    img.save(os.path.join(HERE, "og.png"))
    print(f"wrote og.png (total {total})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
