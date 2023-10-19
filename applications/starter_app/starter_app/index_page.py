from typing import Union

from flask import Blueprint, render_template, session, redirect
from flask.typing import ResponseReturnValue


def index_page() -> Blueprint:
    api = Blueprint("index_page", __name__)

    @api.before_request
    def authenticate_user_filter() -> Union[None, ResponseReturnValue]:
        if session.get("username", None) is not None:
            return redirect("/dashboard")

        return None

    @api.get("/")
    def index() -> ResponseReturnValue:
        return render_template("index.html")

    return api
