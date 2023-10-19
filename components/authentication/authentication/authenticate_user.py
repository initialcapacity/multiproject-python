from typing import Union

from flask import session, redirect, g
from flask.typing import ResponseReturnValue


def authenticate_user() -> Union[None, ResponseReturnValue]:
    user_id = session.get("user_id", None)
    username = session.get("username", None)
    account_id = session.get("account_id", None)
    account_name = session.get("account_name", None)
    if username is None or account_name is None:
        return redirect("/")

    g.user_id = user_id
    g.username = username
    g.account_id = account_id
    g.account_name = account_name
    return None
