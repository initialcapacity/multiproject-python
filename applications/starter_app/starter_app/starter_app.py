import sqlalchemy
from flask import Flask

from accounts.accounts_gateway import AccountsGateway
from accounts.accounts_service import AccountsService
from accounts.memberships_gateway import MembershipsGateway
from accounts.random_name_generator import RandomNameGenerator
from accounts.users_gateway import UsersGateway
from authentication.allowed_emails import AllowedEmails
from authentication.oauth_client import OAuthClient
from database_support.database_template import DatabaseTemplate
from starter_app.accounts_page import accounts_page
from starter_app.dashboard_page import dashboard_page
from starter_app.environment import Environment
from starter_app.health_api import health_api
from starter_app.index_page import index_page
from starter_app.oauth_api import oauth_api


def create_app(env: Environment = Environment.from_env()) -> Flask:
    app = Flask(__name__)

    app = Flask(__name__)
    app.secret_key = env.secret_key

    oauth_client = OAuthClient(env.client_id, env.client_secret, env.host_url)
    allowed_emails = AllowedEmails(
        domains=env.allowed_domains,
        addresses=env.allowed_addresses,
    )

    db = sqlalchemy.create_engine(env.database_url, pool_size=2)
    db_template = DatabaseTemplate(db)

    accounts_gateway = AccountsGateway(db_template)
    users_gateway = UsersGateway(db_template)
    accounts_service = AccountsService(
        db=db_template,
        accounts_gateway=accounts_gateway,
        users_gateway=users_gateway,
        memberships_gateway=MembershipsGateway(db_template),
        name_generator=RandomNameGenerator(),
    )

    app.register_blueprint(index_page())
    app.register_blueprint(oauth_api(accounts_service, oauth_client, allowed_emails))
    app.register_blueprint(dashboard_page())
    app.register_blueprint(
        accounts_page(accounts_gateway, users_gateway, accounts_service)
    )

    app.register_blueprint(health_api())

    return app
