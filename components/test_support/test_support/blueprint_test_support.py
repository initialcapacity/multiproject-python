from flask import Blueprint, Flask
from flask.testing import FlaskClient


def test_client(blueprint: Blueprint) -> FlaskClient:
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.register_blueprint(blueprint)
    return app.test_client()
