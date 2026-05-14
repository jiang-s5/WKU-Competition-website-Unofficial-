import os

from app import create_app

app = create_app()


if __name__ == "__main__":
    host = os.environ.get("WKU_HOST", "127.0.0.1")
    port = int(os.environ.get("WKU_PORT", "8000"))
    debug = os.environ.get("WKU_DEBUG", "1") == "1"
    app.run(host=host, port=port, debug=debug)
