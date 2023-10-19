from unittest import TestCase

from accounts.accounts_gateway import (
    AccountsGateway,
    AccountRecordWithOwnership,
    AccountRecord,
)
from accounts.memberships_gateway import MembershipsGateway
from accounts.users_gateway import UsersGateway
from test_support.db_template import test_db_template
from test_support.unwrap_optional import unwrap


class TestAccountsGateway(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.db = test_db_template()
        self.db.clear()

        self.users_gateway = UsersGateway(self.db)
        self.memberships_gateway = MembershipsGateway(self.db)

        self.gateway = AccountsGateway(self.db)

    def test_create(self) -> None:
        account_id = unwrap(self, self.gateway.create("Some account")).id

        self.assertIsNotNone(account_id)

        result = self.db.query_to_dict("select id, name from accounts")

        self.assertEqual(
            [
                {
                    "id": account_id,
                    "name": "Some account",
                }
            ],
            result,
        )

    def test_list_for_user(self) -> None:
        user_id = unwrap(self, self.users_gateway.create("test@example.com")).id
        account_id = unwrap(self, self.gateway.create("Some account")).id
        self.memberships_gateway.create(
            account_id=account_id, user_id=user_id, owner=True
        )

        accounts = self.gateway.list_for_user(user_id)

        self.assertEqual(
            [
                AccountRecordWithOwnership(
                    id=account_id, name="Some account", owner=True
                )
            ],
            accounts,
        )

    def test_list_for_user_no_membership(self) -> None:
        user_id = unwrap(self, self.users_gateway.create("test@example.com")).id
        self.gateway.create("Some account")

        accounts = self.gateway.list_for_user(user_id)

        self.assertEqual([], accounts)

    def test_find_for_user(self) -> None:
        user_id = unwrap(self, self.users_gateway.create("test@example.com")).id
        account_id = unwrap(self, self.gateway.create("Some account")).id
        self.memberships_gateway.create(
            account_id=account_id, user_id=user_id, owner=True
        )

        account = self.gateway.find_for_user(user_id=user_id, account_id=account_id)

        self.assertEqual(
            AccountRecordWithOwnership(id=account_id, name="Some account", owner=True),
            account,
        )

    def test_find_for_user_not_member(self) -> None:
        user_id = unwrap(self, self.users_gateway.create("test@example.com")).id
        account_id = unwrap(self, self.gateway.create("Some account")).id

        account = self.gateway.find_for_user(user_id=user_id, account_id=account_id)

        self.assertIsNone(account)

    def test_find_for_owner(self) -> None:
        user_id = unwrap(self, self.users_gateway.create("test@example.com")).id
        account_id = unwrap(self, self.gateway.create("Some account")).id
        self.memberships_gateway.create(
            account_id=account_id, user_id=user_id, owner=True
        )

        account = self.gateway.find_for_owner(user_id=user_id, account_id=account_id)

        self.assertEqual(AccountRecord(id=account_id, name="Some account"), account)

    def test_find_for_owner_not_owner(self) -> None:
        user_id = unwrap(self, self.users_gateway.create("test@example.com")).id
        account_id = unwrap(self, self.gateway.create("Some account")).id
        self.memberships_gateway.create(
            account_id=account_id, user_id=user_id, owner=False
        )

        account = self.gateway.find_for_owner(user_id=user_id, account_id=account_id)

        self.assertIsNone(account)

    def test_find_for_owner_not_member(self) -> None:
        user_id = unwrap(self, self.users_gateway.create("test@example.com")).id
        account_id = unwrap(self, self.gateway.create("Some account")).id

        account = self.gateway.find_for_owner(user_id=user_id, account_id=account_id)

        self.assertIsNone(account)
