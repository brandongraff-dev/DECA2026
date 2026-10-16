"""Build a standalone copy of the pitch deck from deck/slides/*.html.

Outputs (in deck/):
  OrbitalCurbside_deck.html   all 20 slides, local images (fonts from Google Fonts if online)
  OrbitalCurbside_deck.pdf    1920x1080 pages, fonts embedded (works offline; bring on USB)
  speaker_notes.md            the word-for-word script for every slide

The live, editable deck is the Slides artifact; this is the backup copy.
Run: .venv/bin/python deck/build_deck.py
"""
import html
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent

# uploaded-asset id -> local file in deck/assets
BLOBS = {
    "22f05438ce0cbbffd3c66adfeab7de52": "benchmark_jpl.png",
    "301cfd22b385c2d7442a83cd2d463336": "problem_close.png",
    "57ea65aa645e772d65ad33cf6ff14895": "population.png",
    "59188352adb4a89141f5a37a44906225": "truck.png",
    "79154d65dd812c00d603007ed476b5bc": "belt.png",
    "a34e7e3c9f8ae33ba2a3e85e2965371d": "qr_demo.png",
    "a9b1630e2b13f2f52cadfa6c58727b48": "wait_vs_burn.png",
    "d8ebdef4c8b76418695354a601dad630": "truck_close.png",
    "dae0be946fe8ed361c01fc941ae1154f": "scaling.png",
    "ec3c3bfbb793325e6406c39c8a7d2686": "tornado.png",
}

CSS = """
@page { size: 1920px 1080px; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body { background: #101216; }
section { position: relative; width: 1920px; height: 1080px; overflow: hidden; page-break-after: always; break-after: page; }
section aside { display: none; }
section > :not([style*="position:absolute"]) { position: relative; }
img { display: block; }
table { width: 100%; border-collapse: collapse; }
th { text-align: left; font-weight: 600; padding: 14px 18px; border-bottom: 2px solid currentColor; }
td { padding: 14px 18px; vertical-align: top; border-bottom: 1px solid rgba(128,128,128,0.25); line-height: 1.3; }
u { text-decoration-color: #E8620C; text-decoration-thickness: 4px; text-underline-offset: 8px; }
"""


def main():
    deck = json.loads((HERE / "deck.json").read_text())
    faces = "".join(f'<link rel="stylesheet" href="{f["href"]}">' for f in deck["faces"].values())
    sections, notes = [], [f"# {deck['title']}: speaker notes\n",
                           "Word-for-word scripts. Text in [brackets] is a stage cue, not spoken. "
                           "\"Q&A backup\" lines are for judge questions.\n"]
    for i, sid in enumerate(deck["order"], 1):
        s = (HERE / "slides" / f"{sid}.html").read_text()
        for blob, name in BLOBS.items():
            s = s.replace(f"/_blob/{blob}", f"assets/{name}")
        assert "/_blob/" not in s, f"unmapped image on slide {sid}"
        sections.append(s)
        m = re.search(r"<aside>(.*?)</aside>", s, re.S)
        notes.append(f"\n## Slide {i}: {sid}\n\n{html.unescape(m.group(1)).strip() if m else '(no notes)'}\n")
    out = HERE / "OrbitalCurbside_deck.html"
    out.write_text(f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{deck['title']}</title>"
                   f"{faces}<style>{CSS}</style></head><body>{''.join(sections)}</body></html>")
    (HERE / "speaker_notes.md").write_text("".join(notes))

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.goto(out.as_uri(), wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(500)
        pg.pdf(path=str(HERE / "OrbitalCurbside_deck.pdf"), width="1920px", height="1080px",
               print_background=True, prefer_css_page_size=True)
        b.close()
    print("built", out.name, "+ pdf +", len(deck["order"]), "slides of notes")


if __name__ == "__main__":
    main()
