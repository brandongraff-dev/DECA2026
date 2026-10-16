"""Smoke-test the offline demo in headless Chromium and screenshot each scene.

    python sim/test_screens.py
Starts serve.py-style server on a free port, loads the page, captures console
errors, jumps through scenes 1-4, and writes PNGs to figures/sim/.
"""
import functools
import http.server
import socketserver
import threading
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "offline" / "OrbitalCurbside-Demo"
SHOTS = ROOT / "figures" / "sim"
SHOTS.mkdir(parents=True, exist_ok=True)

Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DEMO))
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
Handler = functools.partial(Quiet, directory=str(DEMO))
httpd = socketserver.TCPServer(("127.0.0.1", 0), Handler)
port = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()

errors = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium", args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                                "--ignore-gpu-blocklist"])
    page = b.new_page(viewport={"width": 1440, "height": 860})
    page.on("console", lambda m: errors.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    page.goto(f"http://127.0.0.1:{port}/index.html")
    page.wait_for_function("document.getElementById('loading').hidden === true", timeout=120000)
    time.sleep(6)
    for n, name in [(1, "scene1_problem"), (2, "scene2_belt"), (3, "scene3_truck"), (4, "scene4_compare")]:
        page.keyboard.press(str(n))
        time.sleep(9 if n in (2, 3) else 6)
        page.screenshot(path=str(SHOTS / f"{name}.png"))
        print("shot", name, "|", page.inner_text("#s-phase")[:120])
    page.set_viewport_size({"width": 400, "height": 860})
    time.sleep(3)
    page.screenshot(path=str(SHOTS / "phone.png"), full_page=True)
    b.close()
httpd.shutdown()
print("console problems:", len(errors))
for e in errors[:25]:
    print("  ", e[:300])
