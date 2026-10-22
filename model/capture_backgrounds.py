"""Render the 1920x1080 deck background plates in headless Chromium (software WebGL).

    python model/capture_backgrounds.py [outdir] [scene ...]
Writes one JPG per scene in backgrounds.html to figures/backgrounds/ by default.
"""
import functools
import http.server
import socketserver
import sys
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "figures" / "backgrounds"
OUT.mkdir(parents=True, exist_ok=True)
SCENES = sys.argv[2:] or ["horizon", "night", "globe", "debris", "lanes", "limb"]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


httpd = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
threading.Thread(target=httpd.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{httpd.server_address[1]}/model/backgrounds.html"

errors = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium",
                          args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    for s in SCENES:
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        pg.on("console", lambda m: errors.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
        pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
        pg.goto(f"{base}#{s}")
        pg.wait_for_function("window.__ready === true", timeout=120000)
        pg.wait_for_timeout(300)
        pg.screenshot(path=str(OUT / f"bg_{s}.jpg"), type="jpeg", quality=90)
        pg.close()
        print("rendered", s, flush=True)
    b.close()
httpd.shutdown()
print("\n".join(errors) if errors else "no console errors")
