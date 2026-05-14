import os
from socketserver import ThreadingMixIn
from wsgiref.simple_server import WSGIServer, make_server

from app import create_app

app = create_app()


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True


def serve_with_stdlib(application, host, port):
    with make_server(host, port, application, server_class=ThreadingWSGIServer) as server:
        print(f"Serving with Python stdlib WSGI server on http://{host}:{port}")
        server.serve_forever()


if __name__ == "__main__":
    host = os.environ.get("WKU_HOST", "0.0.0.0")
    port = int(os.environ.get("WKU_PORT", "8000"))

    try:
        from waitress import serve as waitress_serve
    except ImportError:
        serve_with_stdlib(app, host, port)
    else:
        waitress_serve(
            app,
            host=host,
            port=port,
            threads=int(os.environ.get("WKU_THREADS", "8")),
        )
