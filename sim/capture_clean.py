"""Capture clean 1920x1080 frames of the simulation (UI panels hidden) for the pitch deck.

    python sim/capture_clean.py
Writes figures/sim/clean_*.png.  Uses the offline build, so run sim/build_offline.py first.
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
OUT = ROOT / "figures" / "sim"
OUT.mkdir(parents=True, exist_ok=True)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


httpd = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(DEMO)))
port = httpd.server_address[1]
threading.Thread(target=httpd.serve_forever, daemon=True).start()
HIDE = "#story,#readout,#transport{display:none!important}"

with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium",
                          args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
    page = b.new_page(viewport={"width": 1920, "height": 1080})
    page.goto(f"http://127.0.0.1:{port}/index.html")
    page.wait_for_function("document.getElementById('loading').hidden === true", timeout=120000)
    page.add_style_tag(content=HIDE)
    time.sleep(5)
    shots = [("1", 6, None, "clean_problem"), ("2", 14, None, "clean_belt"), ("3", 10, None, "clean_truck"),
             ("3", 4, "#cam-truck", "clean_truck_close")]
    for key, wait, click, name in shots:
        page.keyboard.press(key)
        if click:
            page.evaluate(f"document.querySelector('{click}').click()")
        time.sleep(wait)
        page.screenshot(path=str(OUT / f"{name}.png"))
        print("captured", name)
    # closer view of the debris cloud for the "problem" slide
    page.keyboard.press("1"); time.sleep(3)
    page.mouse.move(960, 540)
    for _ in range(3):
        page.mouse.wheel(0, -150); time.sleep(0.6)
    time.sleep(5)
    page.screenshot(path=str(OUT / "clean_problem_close.png"))
    print("captured clean_problem_close")
    b.close()
httpd.shutdown()
