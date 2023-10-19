from unittest import TestCase

from accounts.accounts_gateway import AccountsGateway
from accounts.memberships_gateway import MembershipsGateway
from accounts.users_gateway import UsersGateway
from test_support.db_template import test_db_template
from test_support.unwrap_optional import unwrap


class TestMembershipsGateway(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.db = test_db_template()
        self.db.clear()

        self.users_gateway = UsersGateway(self.db)
        self.accounts_gateway = AccountsGateway(self.db)

        self.gateway = MembershipsGateway(self.db)

    def test_create(self) -> None:
        user_id = unwrap(self, self.users_gateway.create("test@example.com")).id
        account_id = unwrap(self, self.accounts_gateway.create("Some account")).id

        membership_id = self.gateway.create(
            account_id=account_id, user_id=user_id, owner=False
        )

        self.assertIsNotNone(membership_id)

        result = self.db.query_to_dict(
            "select id, account_id, user_id, owner from memberships"
        )

        self.assertEqual(
            [
                {
                    "id": membership_id,
                    "account_id": account_id,
                    "user_id": user_id,
                    "owner": False,
                }
            ],
            result,
        )

    def test_delete(self) -> None:
        user_id = unwrap(self, self.users_gateway.create("test@example.com")).id
        account_id = unwrap(self, self.accounts_gateway.create("Some account")).id
        self.gateway.create(account_id=account_id, user_id=user_id, owner=False)

        self.gateway.delete(account_id=account_id, user_id=user_id)

        result = self.db.query_to_dict(
            "select id, account_id, user_id, owner from memberships"
        )

        self.assertEqual([], result)
