"""Serve the demo on http://localhost:8642 and open the browser. No internet needed."""
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
