def app(environ, start_response):
    """Minimal WSGI entrypoint for Vercel's Python runtime scanner."""
    start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
    return [b"Static dashboard build artifact. Open index.html."]
