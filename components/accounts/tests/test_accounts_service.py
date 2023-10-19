from unittest import TestCase

from accounts.accounts_gateway import AccountsGateway
from accounts.accounts_service import AccountsService
from accounts.memberships_gateway import MembershipsGateway
from accounts.random_name_generator import RandomNameGenerator
from accounts.users_gateway import UsersGateway
from test_support.db_template import test_db_template
from test_support.unwrap_optional import unwrap


class TestNameGenerator(RandomNameGenerator):
    def next(self) -> str:
        return "some account name"


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
            name_generator=TestNameGenerator(),
        )

    def test_create_or_find_user(self) -> None:
        user = unwrap(self, self.service.create_or_find_user("test@example.com"))

        self.assertEqual("test@example.com", user.email)

        accounts = self.db.query_to_dict("select id, name from accounts")
        self.assertEqual("some account name", accounts[0]["name"])

        users = self.db.query_to_dict("select id, email from users")
        self.assertEqual("test@example.com", users[0]["email"])

        memberships = self.db.query_to_dict(
            "select user_id, account_id, owner from memberships"
        )
        self.assertEqual(
            [
                {
                    "user_id": users[0].id,
                    "account_id": accounts[0].id,
                    "owner": True,
                }
            ],
            memberships,
        )

    def test_create_or_find_user_already_exists(self) -> None:
        self.service.create_or_find_user("test@example.com")
        user = unwrap(self, self.service.create_or_find_user("test@example.com"))

        self.assertEqual("test@example.com", user.email)

        self.assertEqual(1, len(self.db.query_to_dict("select 1 from accounts")))
        self.assertEqual(1, len(self.db.query_to_dict("select 1 from users")))
        self.assertEqual(1, len(self.db.query_to_dict("select 1 from memberships")))

    def test_add_to_account(self) -> None:
        user = unwrap(self, self.service.create_or_find_user("test@example.com"))
        other_user = unwrap(self, self.service.create_or_find_user("other@example.com"))

        success = self.service.add_to_account("other@example.com", user.account_id)

        self.assertTrue(success)

        self.assertEqual(
            [{"owner": False}],
            self.db.query_to_dict(
                f"""
            select owner from memberships
                where user_id = '{other_user.id}'
                and account_id = '{user.account_id}'
        """
            ),
        )

    def test_add_to_account_not_found(self) -> None:
        user = unwrap(self, self.service.create_or_find_user("test@example.com"))

        success = self.service.add_to_account("other@example.com", user.account_id)

        self.assertFalse(success)

        self.assertEqual(
            1,
            len(
                self.db.query_to_dict(
                    f"""
            select owner from memberships
                where account_id = '{user.account_id}'
        """
                )
            ),
        )
