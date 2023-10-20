from unittest import TestCase

from flask import session

from accounts.accounts_gateway import AccountsGateway
from accounts.accounts_service import AccountsService
from accounts.memberships_gateway import MembershipsGateway
from accounts.users_gateway import UsersGateway
from starter_app.new_account_page import new_account_page
from test_support.db_template import test_db_template
from tests.blueprint_test_support import test_client, log_in_user


class TestNewAccountPage(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.db = test_db_template()
        self.db.clear()
        accounts_service = AccountsService(
            db=self.db,
            accounts_gateway=(AccountsGateway(self.db)),
            users_gateway=(UsersGateway(self.db)),
            memberships_gateway=(MembershipsGateway(self.db)),
        )
        self.new_account_page = new_account_page(accounts_service)

    def test_new(self) -> None:
        user_id = self.db.user(email="test@example.com")
        client = test_client(self.new_account_page)
        log_in_user(client, user_id=user_id)

        response = client.get("/accounts/new")

        self.assertEqual(200, response.status_code)
        self.assertIn("Create account", response.text)
        self.assertIn("test@example.com", response.text)

    def test_new_not_authenticated(self) -> None:
        client = test_client(self.new_account_page)

        response = client.get("/accounts/new")

        self.assertEqual(302, response.status_code)
        self.assertEqual("/", response.headers.get("Location"))

    def test_create(self) -> None:
        user_id = self.db.user(email="test@example.com")
        client = test_client(self.new_account_page)
        log_in_user(client, user_id=user_id)

        response = client.post("/accounts", data={"name": "some account name"})

        self.assertEqual(302, response.status_code)
        self.assertEqual("/", response.headers.get("Location"))

        accounts = self.db.query_to_dict("select id, name from accounts")
        self.assertEqual("some account name", accounts[0]["name"])

    def test_create_adds_to_session(self) -> None:
        user_id = self.db.user(email="test@example.com")
        client = test_client(self.new_account_page)
        log_in_user(client, user_id=user_id)

        with client:
            client.post("/accounts", data={"name": "some account name"})

            self.assertEqual("some account name", session.get("account_name"))
            self.assertIsNotNone(session.get("account_id"))
