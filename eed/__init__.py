import os

from flask import Flask, jsonify

from eed.admin import setup_admin
from eed.api import stats_api_bp
from eed.models import db


def create_app(**kwargs):
    app = Flask(__name__, **kwargs)
    app.config.from_pyfile("config.cfg")

    # Configure by environment variables
    if os.getenv("EED_DB_NAME", None) or os.getenv("EED_DB_HOST", None):
        db_name = os.getenv("EED_DB_NAME", "test_worldbank")
        db_host = os.getenv("EED_DB_HOST", "localhost")
        db_user = os.getenv("EED_DB_USER", "postgres")
        db_pass = os.getenv("EED_DB_PASS", "postgres")
        app.config[
            "SQLALCHEMY_DATABASE_URI"
        ] = f"postgresql://{db_user}:{db_pass}@{db_host}/{db_name}"

    db.init_app(app)

    app.register_blueprint(stats_api_bp)

    setup_admin(app, db)

    @app.route("/ping")
    def ping_pong():
        return jsonify("pong")

    @app.route("/")
    def index():
        return app.send_static_file("index.html")

    return app
