def app(environ, start_response):
    """Minimal WSGI entrypoint so Vercel does not treat analysis scripts as app files."""
    start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
    return [b"Static dashboard build artifact. See index.html."]
