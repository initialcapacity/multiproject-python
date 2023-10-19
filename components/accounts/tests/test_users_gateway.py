from unittest import TestCase

from accounts.users_gateway import UsersGateway, UserRecord
from test_support.db_template import test_db_template
from test_support.unwrap_optional import unwrap


class TestUsersGateway(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.db = test_db_template()
        self.db.clear()

        self.gateway = UsersGateway(self.db)

    def test_create(self) -> None:
        user_id = unwrap(self, self.gateway.create("test@example.com")).id
        self.assertIsNotNone(user_id)

        result = self.db.query_to_dict("select id, email from users")

        self.assertEqual(
            [
                {
                    "id": user_id,
                    "email": "test@example.com",
                }
            ],
            result,
        )

    def test_find_by_email(self) -> None:
        user_id = unwrap(self, self.gateway.create("test@example.com")).id

        user = self.gateway.find_by_email("test@example.com")
        self.assertEqual(UserRecord(id=user_id, email="test@example.com"), user)

    def test_find_by_email_not_found(self) -> None:
        user = self.gateway.find_by_email("test@example.com")
        self.assertIsNone(user)
