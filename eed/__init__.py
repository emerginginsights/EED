from flask import Flask, jsonify

from .api import stats_api_bp
from .models import db


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.cfg')

    db.init_app(app)

    app.register_blueprint(stats_api_bp)

    @app.route('/ping')
    def ping_pong():
        return jsonify('pong')

    return app

