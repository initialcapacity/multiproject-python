from dataclasses import dataclass
from typing import Optional, cast, Union
from uuid import UUID

from sqlalchemy import Connection

from database_support.database_template import DatabaseTemplate
from database_support.result_mapping import map_one_result


@dataclass
class MembershipRecord:
    id: UUID
    account_id: UUID
    user_id: UUID
    owner: bool


class MembershipsGateway:
    def __init__(self, db: DatabaseTemplate) -> None:
        self.__db = db

    def create(
        self,
        account_id: UUID,
        user_id: UUID,
        owner: bool,
        connection: Optional[Connection] = None,
    ) -> Union[None, UUID]:
        result = self.__db.query(
            statement="""
                    insert into memberships (account_id, user_id, owner)
                        values (:account_id, :user_id, :owner)
                        returning id
                    """,
            connection=connection,
            id=id,
            account_id=account_id,
            user_id=user_id,
            owner=owner,
        )

        return map_one_result(result, lambda row: cast(UUID, row["id"]))

    def delete(
        self, account_id: UUID, user_id: UUID, connection: Optional[Connection] = None
    ) -> None:
        self.__db.query(
            statement="""delete from memberships where account_id = :account_id and user_id = :user_id""",
            connection=connection,
            account_id=account_id,
            user_id=user_id,
        )
