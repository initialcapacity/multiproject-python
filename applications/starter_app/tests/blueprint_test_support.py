from uuid import UUID

from flask import Blueprint, Flask
from flask.testing import FlaskClient


def test_client(blueprint: Blueprint) -> FlaskClient:
    app = Flask(__name__, template_folder="../starter_app/templates")
    app.config["TESTING"] = True
    app.register_blueprint(blueprint)
    app.secret_key = "just testing"
    return app.test_client()


def log_in(
    client: FlaskClient,
    user_id: UUID = UUID("aaaa77eb-83ce-4b3d-9c7e-42559bd10834"),
    account_id: UUID = UUID("b49c77eb-83ce-4b3d-9c7e-42559bd10834"),
) -> None:
    with client.session_transaction() as session:
        session["user_id"] = user_id
        session["username"] = "test@example.com"
        session["account_name"] = "some account"
        session["account_id"] = account_id
