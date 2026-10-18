"""Screenshot the 3D truck model in headless Chromium (software WebGL).

    python model/capture.py [outdir]
Writes truck views and one frame per journey chapter to figures/model/ by default.
"""
import functools
import http.server
import socketserver
import sys
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "figures" / "model"
OUT.mkdir(parents=True, exist_ok=True)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


httpd = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT / "model")))
threading.Thread(target=httpd.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{httpd.server_address[1]}/index.html"

errors = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium",
                          args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    pg = b.new_page(viewport={"width": 1600, "height": 900})
    pg.on("console", lambda m: errors.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    pg.goto(url)
    pg.wait_for_function("window.__ready === true", timeout=60000)
    pg.wait_for_timeout(1500)
    pg.screenshot(path=str(OUT / "truck_hero.png"))
    pg.click("#tXray"); pg.wait_for_timeout(600)
    pg.screenshot(path=str(OUT / "truck_inside.png"))
    pg.click("#tXray"); pg.click("#tFire"); pg.click("#tLabels")
    pg.evaluate("() => { const c = document.querySelector('canvas'); }")
    pg.wait_for_timeout(800)
    pg.screenshot(path=str(OUT / "truck_firing.png"))
    shots = [("1_launch", 5.5), ("2_deploy", 12.0), ("3_climb", 24.0), ("4a_hold", 29.0), ("4b_closing", 34.5),
             ("4c_reach", 38.3), ("5a_grip", 41.5), ("5b_detumble", 45.0), ("5c_kit_out", 47.8), ("5d_latched", 49.5),
             ("5e_backoff", 52.8), ("6a_burn", 57.5), ("6b_smoke", 60.0), ("6c_reentry_a", 63.6), ("6c_reentry", 65.5), ("7_driveon", 71.0)]
    for name, t in shots:
        pg.evaluate(f"window.__setJourney({t})")
        pg.wait_for_timeout(900)
        pg.screenshot(path=str(OUT / f"journey_{name}.png"))
    pg.set_viewport_size({"width": 390, "height": 844})
    pg.evaluate("window.__setMode('truck')")
    pg.wait_for_timeout(900)
    pg.screenshot(path=str(OUT / "phone_truck.png"))
    b.close()
httpd.shutdown()
print("\n".join(errors) if errors else "no console errors")
