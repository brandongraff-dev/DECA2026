"""Clean 1920x1080 renders of the 3D model (no on-screen panels) for the pitch deck.

    python model/capture_clean.py [outdir]
"""
import functools
import http.server
import socketserver
import sys
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "figures" / "model_clean"
OUT.mkdir(parents=True, exist_ok=True)
SHOTS = [("launch", 5.5), ("deploy", 12.0), ("climb", 24.0), ("closing", 34.5), ("grip", 41.5), ("latched", 49.5),
         ("burn", 57.5), ("smoke", 60.0), ("reentry", 65.5), ("driveon", 71.0)]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


httpd = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT / "model")))
threading.Thread(target=httpd.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{httpd.server_address[1]}/index.html"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium",
                          args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.goto(url)
    pg.wait_for_function("window.__ready === true", timeout=60000)
    pg.add_style_tag(content=".hud, #labels { display: none !important; }")
    pg.wait_for_timeout(1500)
    pg.screenshot(path=str(OUT / "truck_hero.jpg"), type="jpeg", quality=90)
    pg.evaluate("document.getElementById('tFire').click()")
    pg.wait_for_timeout(800)
    pg.screenshot(path=str(OUT / "truck_firing.jpg"), type="jpeg", quality=90)
    for name, t in SHOTS:
        pg.evaluate(f"window.__setJourney({t})")
        pg.add_style_tag(content=".hud, #labels { display: none !important; }")
        pg.wait_for_timeout(900)
        pg.screenshot(path=str(OUT / f"journey_{name}.jpg"), type="jpeg", quality=90)
        print("shot", name, flush=True)
    b.close()
httpd.shutdown()
