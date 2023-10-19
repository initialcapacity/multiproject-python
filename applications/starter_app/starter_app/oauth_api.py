import logging
import secrets

from flask import Blueprint, session, redirect, request, flash
from flask.typing import ResponseReturnValue

from accounts.accounts_service import AccountsService
from authentication.allowed_emails import AllowedEmails
from authentication.oauth_client import OAuthClient

logger = logging.getLogger(__name__)


def oauth_api(
    accounts_service: AccountsService,
    oauth_client: OAuthClient,
    allowed_email_addresses: AllowedEmails,
) -> Blueprint:
    api = Blueprint("oauth_api", __name__)

    @api.get("/authenticate")
    def authenticate() -> ResponseReturnValue:
        state = secrets.token_urlsafe(16)
        session["state"] = state

        return redirect(oauth_client.auth_url(state))

    @api.get("/oauth/callback")
    def callback() -> ResponseReturnValue:
        if request.args["state"] != session.pop("state", ""):
            session.clear()
            logger.error("state does not match")
            flash("Please try signing in again", "error")
            return redirect("/")
        access_token = oauth_client.fetch_access_token(request.args["code"])
        if access_token is None:
            logger.error("no access token found")
            flash("Please try signing in again", "error")
            return redirect("/")

        email = oauth_client.read_email_from_token(access_token)
        if email is None:
            logger.error("no email found on access token")
            flash("Please try signing in again", "error")
            return redirect("/")
        if not allowed_email_addresses.include(email):
            logger.error("email address %s not allowed", email)
            flash(f"You are not authorized to sign in as {email}", "error")
            return redirect("/")

        user = accounts_service.create_or_find_user(email)

        if user is None:
            logger.error("unable to create user for email address %s", email)
            flash(f"Unable to sign in as {email}", "error")
            return redirect("/")

        session["user_id"] = user.id
        session["username"] = user.email
        session["account_name"] = user.account_name
        session["account_id"] = user.account_id

        flash(f"Welcome, {email}", "success")
        return redirect("/dashboard")

    return api
