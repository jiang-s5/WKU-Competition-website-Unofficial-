from flask import Flask

from .config import Config
from .db import close_db, init_app
from .routes import web


def create_app(config_object=None):
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder="static",
        template_folder="templates",
    )
    app.config.from_object(config_object or Config())
    init_app(app)
    app.register_blueprint(web)
    app.teardown_appcontext(close_db)
    return app
