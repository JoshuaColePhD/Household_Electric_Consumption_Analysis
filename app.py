from http.server import BaseHTTPRequestHandler
from mimetypes import guess_type
from pathlib import Path


ROOT = Path(__file__).resolve().parent


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        request_path = self.path.split("?", 1)[0].lstrip("/")
        relative_path = "index.html" if request_path in {"", "/"} else request_path
        file_path = (ROOT / relative_path).resolve()

        if ROOT not in file_path.parents and file_path != ROOT:
            self.send_error(403)
            return

        if not file_path.is_file():
            self.send_error(404)
            return

        body = file_path.read_bytes()
        content_type = guess_type(file_path.name)[0] or "application/octet-stream"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
