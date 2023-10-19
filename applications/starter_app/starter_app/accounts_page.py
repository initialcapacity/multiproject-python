from typing import Union
from uuid import UUID

from flask import Blueprint, render_template, g, flash, redirect, request, session
from flask.typing import ResponseReturnValue

from accounts.accounts_gateway import AccountsGateway
from accounts.accounts_service import AccountsService
from accounts.users_gateway import UsersGateway
from authentication.authenticate_user import authenticate_user


def accounts_page(
    accounts_gateway: AccountsGateway,
    users_gateway: UsersGateway,
    accounts_service: AccountsService,
) -> Blueprint:
    api = Blueprint("accounts_page", __name__)

    @api.before_request
    def authenticate_user_filter() -> Union[None, ResponseReturnValue]:
        return authenticate_user()

    @api.get("/accounts")
    def index() -> ResponseReturnValue:
        return render_template(
            "accounts.html", accounts=accounts_gateway.list_for_user(g.user_id)
        )

    @api.get("/accounts/<account_id>")
    def show(account_id: UUID) -> ResponseReturnValue:
        account = accounts_gateway.find_for_user(
            account_id=account_id, user_id=g.user_id
        )
        if account is None:
            flash("Account not found", "error")
            return redirect("/accounts")

        return render_template(
            "account.html",
            account=account,
            users=users_gateway.find_for_account(account_id),
        )

    @api.post("/accounts/<account_id>/members")
    def add_member(account_id: UUID) -> ResponseReturnValue:
        account = accounts_gateway.find_for_owner(
            account_id=account_id, user_id=g.user_id
        )
        if account is None:
            flash("Must be owner to add a member", "error")
            return redirect(f"/accounts/{account_id}")

        email = request.form["email"]
        success = accounts_service.add_to_account(email=email, account_id=account_id)
        if not success:
            flash("User not found", "error")

        return redirect(f"/accounts/{account_id}")

    @api.post("/accounts/<account_id>/members/<user_id>/remove")
    def remove_member(account_id: UUID, user_id: UUID) -> ResponseReturnValue:
        account = accounts_gateway.find_for_owner(
            account_id=account_id, user_id=g.user_id
        )
        if account is None:
            flash("Must be owner to remove a member", "error")
            return redirect(f"/accounts/{account_id}")

        accounts_service.remove_from_account(user_id=user_id, account_id=account_id)

        return redirect(f"/accounts/{account_id}")

    @api.post("/accounts/<account_id>/switch")
    def switch_to_account(account_id: UUID) -> ResponseReturnValue:
        account = accounts_gateway.find_for_user(
            account_id=account_id, user_id=g.user_id
        )
        if account is None:
            flash("Account not found", "error")
            return redirect("/accounts")

        session["account_id"] = account.id
        session["account_name"] = account.name

        g.account_id = account.id
        g.account_name = account.name

        return redirect("/accounts")

    return api
