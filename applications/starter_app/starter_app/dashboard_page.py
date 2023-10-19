from typing import Union

from flask import Blueprint, session, redirect, render_template
from flask.typing import ResponseReturnValue

from authentication.authenticate_user import authenticate_user


def dashboard_page() -> Blueprint:
    api = Blueprint("dashboard_page", __name__)

    @api.before_request
    def authenticate_user_filter() -> Union[None, ResponseReturnValue]:
        return authenticate_user()

    @api.get("/dashboard")
    def dashboard() -> ResponseReturnValue:
        return render_template("dashboard.html")

    @api.get("/logout")
    def logout() -> ResponseReturnValue:
        session.clear()
        return redirect("/")

    return api
