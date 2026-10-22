"""Build the OFFLINE demo package from the same sources the hosted artifact uses.

    python sim/build_offline.py
Creates offline/OrbitalCurbside-Demo/ with:
  index.html            full HTML document (doctype + head) wrapping sim/index.html
  app.js, lib/, data/   copied as-is (Cesium engine, imagery, satellite.js, orbit data)
  Start Demo.bat        Windows double-click launcher -> serve.ps1 (built into Windows, no installs)
  serve.ps1             PowerShell local web server (the 3D engine needs http://, not file://)
  serve.py / Start Demo (Mac).command   fallbacks for computers that have Python
  lib/fonts/            bundled fonts (the hosted artifact loads them from Google Fonts instead)
  README.txt
"""
import shutil
from pathlib import Path

SIM = Path(__file__).resolve().parent
OUT = SIM.parent / "offline" / "OrbitalCurbside-Demo"
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir(parents=True)

body = (SIM / "index.html").read_text()
# offline: swap Google Fonts for the bundled copies
import re
body = re.sub(r'<link rel="preconnect" href="https://fonts.googleapis.com">\n', "", body)
body = re.sub(r'<link rel="stylesheet" href="https://fonts.googleapis.com/[^"]*">',
              '<link rel="stylesheet" href="lib/fonts/fonts.css">', body)
assert "fonts.googleapis.com" not in body
(OUT / "index.html").write_text(
    "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
    "</head>\n<body>\n" + body + "\n</body>\n</html>\n")
shutil.copy(SIM / "app.js", OUT / "app.js")
shutil.copytree(SIM / "lib", OUT / "lib")
shutil.copytree(SIM / "data", OUT / "data")
shutil.copytree(SIM / "fonts", OUT / "lib" / "fonts")
shutil.copy(SIM / "serve.ps1", OUT / "serve.ps1")
# the 3D truck model (model/), served at /truck/ next to the mission demo
MODEL = SIM.parent / "model"
shutil.copytree(MODEL, OUT / "truck", ignore=shutil.ignore_patterns("capture*.py", "backgrounds.html", "__pycache__"))
mbody = (MODEL / "index.html").read_text()
(OUT / "truck" / "index.html").write_text(
    "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
    "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
    "<style>body{margin:0}</style>\n</head>\n<body>\n" + mbody + "\n</body>\n</html>\n")
# in the offline copy the "See the truck" link points at the local model
idx = OUT / "index.html"
idx.write_text(re.sub(r'href="https://claude\.ai/[^"]*" id="truckLink"', 'href="truck/index.html" id="truckLink"', idx.read_text()))
(OUT / "Start Demo.bat").write_text(
    '@echo off\r\n'
    'title Orbital Curbside demo\r\n'
    'cd /d "%~dp0"\r\n'
    'powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0serve.ps1"\r\n'
    'if errorlevel 1 pause\r\n')

(OUT / "serve.py").write_text('''"""Serve the demo on http://localhost:8642 and open the browser. No internet needed."""
import http.server, socketserver, os, threading, webbrowser, functools
PORT = 8642
os.chdir(os.path.dirname(os.path.abspath(__file__)))
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=".")
Handler.extensions_map[".js"] = "text/javascript"
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    url = f"http://localhost:{PORT}/index.html"
    print("Orbital Curbside demo running at", url, "- close this window to stop.")
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    httpd.serve_forever()
''')
mac = OUT / "Start Demo (Mac).command"
mac.write_text('#!/bin/bash\ncd "$(dirname "$0")"\npython3 serve.py\n')
mac.chmod(0o755)
(OUT / "README.txt").write_text("""ORBITAL CURBSIDE - OFFLINE MISSION DEMO
=======================================
Runs with NO internet and NO power outlet (battery is fine).

WINDOWS (nothing to install):
1. Unzip the folder first (right-click the .zip > Extract All). Do not run it from inside the zip.
2. Double-click "Start Demo.bat".
   If Windows says "Windows protected your PC": click "More info" > "Run anyway".
   (Or once, before unzipping: right-click the .zip > Properties > tick "Unblock" > OK.)
3. Your browser opens http://localhost:8642. Edge or Chrome both work.
4. Keys: 1-4 jump to scenes, Space = play/pause. Close the black window to stop.
5. The 3D truck and its launch-to-first-stop journey: click "See the truck in 3D" in the demo,
   or open http://localhost:8642/truck/index.html

MAC: double-click "Start Demo (Mac).command" (uses the Python that ships with macOS developer tools).

COMPETITION-DAY CHECKLIST
- Rehearse once with Wi-Fi OFF and the charger unplugged.
- Set Windows power mode to "Best performance" while plugged in at home to check smoothness,
  then test on battery; close other apps. If it stutters, use the 1 day/s speed instead of 6 days/s.
- Start the demo BEFORE you walk in (setup time counts toward your 15 minutes), leave it paused on scene 1.
- Backup: the screen recording (see recording plan) on the desktop.

Data: CelesTrak catalogue snapshot of 16 Oct 2026. 3D engine: CesiumJS (Apache-2.0).
Orbit propagation: satellite.js (MIT). Earth imagery: Natural Earth II (public domain).
""")
print("built", OUT, sum(1 for _ in OUT.rglob('*') if _.is_file()), "files")
