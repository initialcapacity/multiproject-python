from unittest import TestCase

from flask import session

from accounts.accounts_gateway import AccountsGateway
from accounts.accounts_service import AccountsService
from accounts.memberships_gateway import MembershipsGateway
from accounts.users_gateway import UsersGateway
from starter_app.accounts_page import accounts_page
from test_support.db_template import test_db_template
from tests.blueprint_test_support import test_client, log_in


class TestAccountsPage(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.db = test_db_template()
        self.db.clear()
        accounts_gateway = AccountsGateway(self.db)
        users_gateway = UsersGateway(self.db)
        memberships_gateway = MembershipsGateway(self.db)
        accounts_service = AccountsService(
            db=self.db,
            accounts_gateway=accounts_gateway,
            users_gateway=users_gateway,
            memberships_gateway=memberships_gateway,
        )
        self.accounts_page = accounts_page(
            accounts_gateway, users_gateway, accounts_service
        )

    def test_index(self) -> None:
        user_id, account_id = self.db.account_with_user(
            email="test@example.com", account_name="some account"
        )
        self.db.account("another account")
        client = test_client(self.accounts_page)
        log_in(client, user_id=user_id, account_id=account_id)

        response = client.get("/accounts")

        self.assertEqual(200, response.status_code)
        self.assertIn("some account", response.text)
        self.assertIn("owner", response.text)
        self.assertNotIn("another account", response.text)

    def test_show(self) -> None:
        user_id, account_id = self.db.account_with_user(
            email="test@example.com", account_name="some account"
        )
        self.db.add_user(email="other@example.com", account_id=account_id)
        client = test_client(self.accounts_page)
        log_in(client, user_id=user_id, account_id=account_id)

        response = client.get(f"/accounts/{account_id}")

        self.assertEqual(200, response.status_code)
        self.assertIn("some account", response.text)
        self.assertIn("Add user", response.text)
        self.assertIn("other@example.com", response.text)

    def test_show_not_owner(self) -> None:
        owner_id, account_id = self.db.account_with_user(
            email="test@example.com", account_name="some account"
        )
        user_id = self.db.add_user(email="other@example.com", account_id=account_id)
        client = test_client(self.accounts_page)
        log_in(client, user_id=user_id, account_id=account_id)

        response = client.get(f"/accounts/{account_id}")

        self.assertEqual(200, response.status_code)
        self.assertIn("some account", response.text)
        self.assertNotIn("Add user", response.text)

    def test_show_not_found(self) -> None:
        client = test_client(self.accounts_page)
        log_in(client)

        response = client.get("/accounts/9a8e7aeb-55f0-460f-9870-1ee73e26049e")

        self.assertEqual(302, response.status_code)
        self.assertEqual("/accounts", response.headers.get("Location"))

    def test_add_member(self) -> None:
        user_id, account_id = self.db.account_with_user(
            email="test@example.com", account_name="some account"
        )
        self.db.account_with_user(
            email="other@example.com", account_name="other_account"
        )
        client = test_client(self.accounts_page)
        log_in(client, user_id=user_id, account_id=account_id)

        add_response = client.post(
            f"/accounts/{account_id}/members", data={"email": "other@example.com"}
        )
        self.assertEqual(302, add_response.status_code)

        response = client.get(f"/accounts/{account_id}")

        self.assertEqual(200, response.status_code)
        self.assertIn("other@example.com", response.text)

    def test_add_member_not_owner(self) -> None:
        owner_id, account_id = self.db.account_with_user(
            email="test@example.com", account_name="some account"
        )
        user_id = self.db.add_user(email="other@example.com", account_id=account_id)
        self.db.account_with_user(
            email="another@example.com", account_name="another_account"
        )

        client = test_client(self.accounts_page)
        log_in(client, user_id=user_id, account_id=account_id)

        add_response = client.post(
            f"/accounts/{account_id}/members", data={"email": "another@example.com"}
        )
        self.assertEqual(302, add_response.status_code)

        response = client.get(f"/accounts/{account_id}")

        self.assertEqual(200, response.status_code)
        self.assertNotIn("another@example.com", response.text)

    def test_remove_member(self) -> None:
        user_id, account_id = self.db.account_with_user(
            email="test@example.com", account_name="some account"
        )
        other_user_id = self.db.add_user(
            email="other@example.com", account_id=account_id
        )
        client = test_client(self.accounts_page)
        log_in(client, user_id=user_id, account_id=account_id)

        add_response = client.post(
            f"/accounts/{account_id}/members/{other_user_id}/remove"
        )
        self.assertEqual(302, add_response.status_code)

        response = client.get(f"/accounts/{account_id}")

        self.assertEqual(200, response.status_code)
        self.assertNotIn("other@example.com", response.text)

    def test_remove_member_not_owner(self) -> None:
        owner_id, account_id = self.db.account_with_user(
            email="test@example.com", account_name="some account"
        )
        user_id = self.db.add_user(email="other@example.com", account_id=account_id)
        another_user_id = self.db.add_user(
            email="another@example.com", account_id=account_id
        )

        client = test_client(self.accounts_page)
        log_in(client, user_id=user_id, account_id=account_id)

        add_response = client.post(
            f"/accounts/{account_id}/members/{another_user_id}/remove"
        )
        self.assertEqual(302, add_response.status_code)

        response = client.get(f"/accounts/{account_id}")

        self.assertEqual(200, response.status_code)
        self.assertIn("another@example.com", response.text)

    def test_switch_to_account(self) -> None:
        user_id, account_id = self.db.account_with_user(
            email="test@example.com", account_name="some account"
        )
        other_account_id = self.db.account("other account")
        self.db.membership(user_id=user_id, account_id=other_account_id)

        client = test_client(self.accounts_page)
        log_in(client, user_id=user_id, account_id=account_id)
        with client:
            response = client.post(f"/accounts/{other_account_id}/switch")
            self.assertEqual(302, response.status_code)
            self.assertEqual(other_account_id, session.get("account_id"))
            self.assertEqual("other account", session.get("account_name"))

    def test_switch_to_account_not_member(self) -> None:
        user_id, account_id = self.db.account_with_user(
            email="test@example.com", account_name="some account"
        )
        other_account_id = self.db.account("other account")

        client = test_client(self.accounts_page)
        log_in(client, user_id=user_id, account_id=account_id)
        with client:
            response = client.post(f"/accounts/{other_account_id}/switch")
            self.assertEqual(302, response.status_code)
            self.assertEqual(account_id, session.get("account_id"))
            self.assertEqual("some account", session.get("account_name"))
