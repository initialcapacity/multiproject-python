from unittest import TestCase

from accounts.accounts_gateway import AccountsGateway
from accounts.accounts_service import AccountsService
from accounts.memberships_gateway import MembershipsGateway
from accounts.users_gateway import UsersGateway
from test_support.db_template import test_db_template
from test_support.unwrap_optional import unwrap


class TestAccountsService(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.db = test_db_template()
        self.db.clear()

        self.users_gateway = UsersGateway(self.db)
        self.memberships_gateway = MembershipsGateway(self.db)
        self.accounts_gateway = AccountsGateway(self.db)

        self.service = AccountsService(
            db=self.db,
            accounts_gateway=self.accounts_gateway,
            users_gateway=self.users_gateway,
            memberships_gateway=self.memberships_gateway,
        )

    def test_create_or_find_user(self) -> None:
        user = unwrap(self, self.service.create_or_find_user("test@example.com"))

        self.assertEqual("test@example.com", user.email)

        users = self.db.query_to_dict("select id, email from users")
        self.assertEqual("test@example.com", users[0]["email"])

    def test_create_or_find_user_already_exists(self) -> None:
        existing_user = unwrap(
            self, self.service.create_or_find_user("test@example.com")
        )
        account = unwrap(
            self, self.service.create_account(existing_user.id, "some account")
        )

        user = unwrap(self, self.service.create_or_find_user("test@example.com"))

        self.assertEqual("test@example.com", user.email)
        self.assertEqual("some account", user.account_name)
        self.assertEqual(account.id, user.account_id)

        self.assertEqual(1, len(self.db.query_to_dict("select 1 from accounts")))
        self.assertEqual(1, len(self.db.query_to_dict("select 1 from users")))
        self.assertEqual(1, len(self.db.query_to_dict("select 1 from memberships")))

    def test_add_to_account(self) -> None:
        user = unwrap(self, self.service.create_or_find_user("test@example.com"))
        account = unwrap(self, self.service.create_account(user.id, "some account"))
        other_user = unwrap(self, self.service.create_or_find_user("other@example.com"))

        success = self.service.add_to_account("other@example.com", account.id)

        self.assertTrue(success)

        self.assertEqual(
            [{"owner": False}],
            self.db.query_to_dict(
                f"""
            select owner from memberships
                where user_id = '{other_user.id}'
                and account_id = '{account.id}'
        """
            ),
        )

    def test_add_to_account_not_found(self) -> None:
        user = unwrap(self, self.service.create_or_find_user("test@example.com"))
        account = unwrap(self, self.service.create_account(user.id, "some account"))

        success = self.service.add_to_account("other@example.com", account.id)

        self.assertFalse(success)

        self.assertEqual(
            1,
            len(
                self.db.query_to_dict(
                    f"""
            select owner from memberships
                where account_id = '{account.id}'
        """
                )
            ),
        )

    def test_create_account(self) -> None:
        user = unwrap(self, self.service.create_or_find_user("test@example.com"))

        account = unwrap(
            self, self.service.create_account(user.id, "some account name")
        )

        accounts = self.db.query_to_dict("select id, name from accounts")
        self.assertEqual("some account name", accounts[0]["name"])
        self.assertEqual("some account name", account.name)

        memberships = self.db.query_to_dict(
            "select user_id, account_id, owner from memberships"
        )
        self.assertEqual(
            [
                {
                    "user_id": user.id,
                    "account_id": account.id,
                    "owner": True,
                }
            ],
            memberships,
        )
