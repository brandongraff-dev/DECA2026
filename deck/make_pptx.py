"""PowerPoint backup of the deck: one full-slide image per slide, the demo video embedded on the demo slide.

    node deck/build_deck.js --png /tmp/oc_png      # renders the slide images
    python3 deck/make_pptx.py /tmp/oc_png           # writes deck/OrbitalCurbside_deck.pptx

Works offline in PowerPoint (Windows/Mac) and Keynote. On the demo slide, click the video to play it.
Speaker notes are copied into each slide's notes.
"""
import json
import pathlib
import re
import sys
import html

from pptx import Presentation
from pptx.util import Emu

HERE = pathlib.Path(__file__).resolve().parent
png = pathlib.Path(sys.argv[1])
order = json.loads((HERE / "deck.json").read_text())["order"]
video = HERE / "assets" / "demo_pickup.mp4"
PX = 6350  # EMU per pixel at 1920 px = 13.333 in

prs = Presentation()
prs.slide_width, prs.slide_height = Emu(1920 * PX), Emu(1080 * PX)
blank = prs.slide_layouts[6]
for k, sid in enumerate(order, 1):
    s = prs.slides.add_slide(blank)
    s.shapes.add_picture(str(png / f"slide{k:02d}.png"), 0, 0, prs.slide_width, prs.slide_height)
    src = (HERE / "slides" / f"{sid}.html").read_text()
    if 'data-video' in src and video.exists():
        # video in the right part of the slide, 16:9, beside the text column
        w, h = 1180, 664
        s.shapes.add_movie(str(video), Emu((1920 - w) * PX), Emu((1080 - h) // 2 * PX), Emu(w * PX), Emu(h * PX),
                           poster_frame_image=str(HERE / "assets" / "journey_grip.jpg"), mime_type="video/mp4")
    m = re.search(r"<aside>(.*?)</aside>", src, re.S)
    if m:
        s.notes_slide.notes_text_frame.text = html.unescape(m.group(1)).strip()
out = HERE / "OrbitalCurbside_deck.pptx"
prs.save(out)
print("wrote", out, f"({out.stat().st_size / 1e6:.1f} MB)")
