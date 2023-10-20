from dataclasses import dataclass
from typing import Optional, cast, List
from uuid import UUID

from sqlalchemy import Connection

from database_support.database_template import DatabaseTemplate
from database_support.result_mapping import map_one_result, map_results


@dataclass
class UserRecord:
    id: UUID
    email: str


class UsersGateway:
    def __init__(self, db: DatabaseTemplate) -> None:
        self.__db = db

    def create(
        self, email: str, connection: Optional[Connection] = None
    ) -> Optional[UserRecord]:
        result = self.__db.query(
            statement="""insert into users (email) values (:email) returning id, email""",
            connection=connection,
            email=email,
        )

        return map_one_result(
            result,
            lambda row: UserRecord(
                id=cast(UUID, row["id"]),
                email=row["email"],
            ),
        )

    def find_by_email(
        self, email: str, connection: Optional[Connection] = None
    ) -> Optional[UserRecord]:
        result = self.__db.query(
            statement="""select id, email from users where email = :email""",
            connection=connection,
            email=email,
        )

        return map_one_result(
            result,
            lambda row: UserRecord(
                id=cast(UUID, row["id"]),
                email=row["email"],
            ),
        )

    def find_for_account(
        self, account_id: UUID, connection: Optional[Connection] = None
    ) -> List[UserRecord]:
        result = self.__db.query(
            statement="""select u.id, u.email from users u
            join public.memberships m on u.id = m.user_id
            where m.account_id = :account_id
            """,
            connection=connection,
            account_id=account_id,
        )

        return map_results(
            result,
            lambda row: UserRecord(
                id=cast(UUID, row["id"]),
                email=row["email"],
            ),
        )
