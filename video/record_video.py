"""Render the 2½-minute demo video (no internet needed): title cards, the orbit simulation
(sim/) and the 3D truck journey (model/), frame by frame in headless Chromium, encoded with ffmpeg.

    python video/record_video.py [out.mp4]

Silent on purpose: narrate it live, or record a voice-over (see 05_recording_plan.md).
Takes about an hour with software WebGL.
"""
import base64
import functools
import http.server
import io
import json
import os
import socketserver
import subprocess
import sys
import threading
import urllib.parse
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "video" / "OrbitalCurbside_demo.mp4"
W, H = 1280, 720
FPS = int(os.environ.get("VIDEO_FPS", 24))   # set VIDEO_FPS=2 for a quick test run
WAIT_RENDER = "() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)))"


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
threading.Thread(target=httpd.serve_forever, daemon=True).start()
BASE = f"http://127.0.0.1:{httpd.server_address[1]}"

ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-profile:v", "main", "-level", "4.0", "-pix_fmt", "yuv420p", "-crf", "20",
                       "-preset", "medium", "-movflags", "+faststart", str(OUT)], stdin=subprocess.PIPE)
count = 0


def emit(jpeg: bytes, n: int = 1):
    global count
    for _ in range(n):
        ff.stdin.write(jpeg)
        count += 1


def faded(jpeg: bytes, k: float) -> bytes:
    im = Image.open(io.BytesIO(jpeg)).convert("RGB")
    im = Image.blend(Image.new("RGB", im.size), im, k)
    b = io.BytesIO(); im.save(b, "JPEG", quality=92)
    return b.getvalue()


def shot(cdp) -> bytes:
    return base64.b64decode(cdp.send("Page.captureScreenshot", {"format": "jpeg", "quality": 92})["data"])


def card(page, cdp, seconds, fade=10, **text):
    page.goto(f"{BASE}/video/card.html#" + urllib.parse.quote(json.dumps(text)))
    page.wait_for_function("window.__ready === true")
    page.wait_for_timeout(300)
    img = shot(cdp)
    total = int(seconds * FPS)
    fade = min(fade, total // 3)
    for k in range(fade):
        emit(faded(img, (k + 1) / fade))
    emit(img, total - 2 * fade)
    for k in range(fade):
        emit(faded(img, 1 - (k + 1) / fade))
    print(f"card {text.get('title', '')[:30]!r} -> {count} frames", flush=True)


with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/opt/pw-browsers/chromium",
                          args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
    page = b.new_page(viewport={"width": W, "height": H})
    cdp = page.context.new_cdp_session(page)

    card(page, cdp, 4, eye="DECA Innovation Plan · Demo", title="Orbital <span>Curbside</span>",
         sub="The garbage truck for space. One spacecraft, ten pickups per trip, and Earth does the steering.",
         foot="Real orbits from the public catalogue (CelesTrak, 16 Oct 2026). Truck: concept design sized by our model, not a flight design.")

    # ---------------------------------------------------------------- the orbit simulation
    def sim_segment(scene, seconds, advance, rotate=0.0, setup=""):
        page.evaluate(f"""() => {{ const S = window.__sim; S.setScene({scene}); S.setPlaying(false); {setup} }}""")
        page.wait_for_timeout(500)
        for k in range(int(seconds * FPS)):
            page.evaluate(f"""() => {{ const S = window.__sim; S.state.ms += {advance};
                                       if ({rotate}) S.viewer.camera.rotateLeft({rotate}); }}""")
            page.evaluate(WAIT_RENDER)
            emit(shot(cdp))
            if k % 48 == 0:
                print(f"  sim scene {scene}: {k}/{int(seconds * FPS)}", flush=True)

    def open_sim():
        page.goto(f"{BASE}/offline/OrbitalCurbside-Demo/index.html")
        page.wait_for_function("window.__sim && window.__sim.state.mission && document.getElementById('loading').hidden", timeout=120000)
        page.wait_for_timeout(1500)

    card(page, cdp, 3, eye="1 of 5", title="What's up there", sub="Every tracked object in low orbit, from this October's catalogue.")
    open_sim()
    sim_segment(1, 11, 1000 / FPS * 60, rotate=0.0022)

    card(page, cdp, 3, eye="2 of 5", title="Earth does the <span>steering</span>",
         sub="Earth's bulge slowly swings every orbit around. Lower orbits swing faster.")
    open_sim()
    sim_segment(2, 13, 1000 / FPS * 172800)

    card(page, cdp, 3, eye="3 of 5", title="One truck, <span>ten stops</span>",
         sub="Our first route: 10 old rocket stages from the US, India and France.")
    open_sim()
    span = page.evaluate("() => window.__sim.state.mission.end_ms - window.__sim.state.mission.start_ms")
    sim_segment(3, 24, (span + 20 * 86400000) / (24 * FPS))

    card(page, cdp, 3, eye="4 of 5", title="The <span>money</span>",
         sub="Same job, two ways: one mission per piece, or one truck for ten.")
    open_sim()
    sim_segment(4, 8, 0)

    # ---------------------------------------------------------------- the 3D truck journey
    card(page, cdp, 3, eye="5 of 5", title="Up close: <span>one pickup</span>",
         sub="Launch, climb, grab an old rocket stage, attach a kit, send it down to burn up.")
    page.goto(f"{BASE}/offline/OrbitalCurbside-Demo/truck/index.html#journey")
    page.wait_for_function("window.__ready === true", timeout=120000)
    page.wait_for_timeout(1500)
    total = page.evaluate("() => window.__chapters().reduce((s, c) => s + c[1], 0)")
    n = int(total * FPS)
    for k in range(n):
        page.evaluate(f"() => window.__setJourney({k / FPS + 0.001})")
        page.evaluate(WAIT_RENDER)
        emit(shot(cdp))
        if k % 96 == 0:
            print(f"  journey {k}/{n}", flush=True)

    card(page, cdp, 5, eye="Orbital Curbside", title="$12.2M <span>per piece</span>",
         sub="vs $40–93M for one custom mission per piece today. Our model's estimate, launch included.",
         foot="Sources and assumptions: see the pitch deck bibliography and appendix.")
    b.close()

ff.stdin.close()
ff.wait()
httpd.shutdown()
print(f"wrote {OUT} ({count} frames, {count / FPS:.0f} s)")
