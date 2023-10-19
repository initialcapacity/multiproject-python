from typing import Any, List, cast, Tuple
from uuid import UUID

import sqlalchemy
from sqlalchemy import Engine, RowMapping

from database_support.database_template import DatabaseTemplate
from database_support.result_mapping import map_one_result


class TestDatabaseTemplate(DatabaseTemplate):
    def __init__(self, engine: Engine) -> None:
        super().__init__(engine)

    def clear(self) -> None:
        self.query("delete from memberships")
        self.query("delete from users")
        self.query("delete from accounts")

    def account(self, name: str) -> UUID:
        return cast(
            UUID,
            map_one_result(
                self.query(
                    statement="""insert into accounts (name) values (:name) returning id, name""",
                    name=name,
                ),
                lambda row: row["id"],
            ),
        )

    def account_with_user(
        self, email: str, account_name: str, owner: bool = True
    ) -> Tuple[UUID, UUID]:
        user_id = cast(
            UUID,
            map_one_result(
                self.query(
                    statement="""insert into users (email) values (:email) returning id""",
                    email=email,
                ),
                lambda row: row["id"],
            ),
        )

        account_id = cast(
            UUID,
            map_one_result(
                self.query(
                    statement="""insert into accounts (name) values (:name) returning id""",
                    name=account_name,
                ),
                lambda row: row["id"],
            ),
        )

        self.query(
            statement="""insert into memberships (account_id, user_id, owner)
            values (:account_id, :user_id, :owner)""",
            account_id=account_id,
            user_id=user_id,
            owner=owner,
        )

        return user_id, account_id

    def add_user(self, email: str, account_id: UUID) -> UUID:
        user_id = cast(
            UUID,
            map_one_result(
                self.query(
                    statement="""insert into users (email) values (:email) returning id""",
                    email=email,
                ),
                lambda row: row["id"],
            ),
        )

        return self.membership(user_id=user_id, account_id=account_id)

    def membership(self, user_id: UUID, account_id: UUID) -> UUID:
        self.query(
            statement="""insert into memberships (account_id, user_id, owner)
            values (:account_id, :user_id, false)""",
            account_id=account_id,
            user_id=user_id,
        )

        return user_id

    def query_to_dict(self, statement: str, **kwargs: Any) -> List[RowMapping]:
        return [row._mapping for row in (self.query(statement, **kwargs))]


def test_db_template() -> TestDatabaseTemplate:
    db = sqlalchemy.create_engine(
        url="postgresql://localhost:5432/starter_test?user=starter&password=starter",
        pool_size=2,
    )

    return TestDatabaseTemplate(db)
