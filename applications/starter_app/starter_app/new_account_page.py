from typing import Union

from flask import Blueprint, render_template, g, flash, redirect, request, session
from flask.typing import ResponseReturnValue

from accounts.accounts_service import AccountsService


def new_account_page(accounts_service: AccountsService) -> Blueprint:
    api = Blueprint("new_account_page", __name__)

    @api.before_request
    def authenticate_user_filter() -> Union[None, ResponseReturnValue]:
        user_id = session.get("user_id", None)
        username = session.get("username", None)

        if username is None:
            return redirect("/")
        g.user_id = user_id
        g.username = username

        return None

    @api.get("/accounts/new")
    def new() -> ResponseReturnValue:
        return render_template("new_account.html")

    @api.post("/accounts")
    def create() -> ResponseReturnValue:
        name = request.form["name"]
        account = accounts_service.create_account(g.user_id, name)
        if account is None:
            flash(f"Unable to create account {name}", "error")
            return redirect("/accounts/new")

        flash(f"Account {name} created", "success")
        session["account_id"] = account.id
        session["account_name"] = account.name

        return redirect("/")

    return api
