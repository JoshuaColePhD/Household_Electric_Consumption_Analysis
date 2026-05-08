from mimetypes import guess_type
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def app(environ, start_response):
    """Serve the static dashboard when Vercel routes through Python."""
    request_path = environ.get("PATH_INFO", "/").lstrip("/")
    relative_path = "index.html" if request_path in {"", "/"} else request_path
    file_path = (ROOT / relative_path).resolve()

    if ROOT not in file_path.parents and file_path != ROOT:
        start_response("403 Forbidden", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Forbidden"]

    if not file_path.is_file():
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Not found"]

    content_type = guess_type(file_path.name)[0] or "application/octet-stream"
    body = file_path.read_bytes()
    start_response(
        "200 OK",
        [
            ("Content-Type", content_type),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]
