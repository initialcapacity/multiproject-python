from dataclasses import dataclass
from typing import Optional, cast, Union, List
from uuid import UUID

from sqlalchemy import Connection

from database_support.database_template import DatabaseTemplate
from database_support.result_mapping import map_one_result, map_results


@dataclass
class AccountRecord:
    id: UUID
    name: str


@dataclass
class AccountRecordWithOwnership:
    id: UUID
    name: str
    owner: bool


class AccountsGateway:
    def __init__(self, db: DatabaseTemplate) -> None:
        self.__db = db

    def create(
        self, name: str, connection: Optional[Connection] = None
    ) -> Union[None, AccountRecord]:
        result = self.__db.query(
            statement="""insert into accounts (name) values (:name) returning id, name""",
            connection=connection,
            name=name,
        )

        return map_one_result(
            result,
            lambda row: AccountRecord(
                id=cast(UUID, row["id"]),
                name=row["name"],
            ),
        )

    def list_for_user(
        self, user_id: UUID, connection: Optional[Connection] = None
    ) -> List[AccountRecordWithOwnership]:
        result = self.__db.query(
            statement="""
            select accounts.id, accounts.name, memberships.owner from accounts
            join memberships on accounts.id = memberships.account_id
            where memberships.user_id = :user_id
            order by memberships.owner desc
            """,
            connection=connection,
            user_id=user_id,
        )

        return map_results(
            result,
            lambda row: AccountRecordWithOwnership(
                id=cast(UUID, row["id"]),
                name=row["name"],
                owner=row["owner"],
            ),
        )

    def find_for_user(
        self, account_id: UUID, user_id: UUID, connection: Optional[Connection] = None
    ) -> Union[None, AccountRecordWithOwnership]:
        result = self.__db.query(
            statement="""
            select accounts.id, accounts.name, memberships.owner from accounts
            join memberships on accounts.id = memberships.account_id
            where memberships.user_id = :user_id
            and accounts.id = :account_id
            """,
            connection=connection,
            user_id=user_id,
            account_id=account_id,
        )

        return map_one_result(
            result,
            lambda row: AccountRecordWithOwnership(
                id=cast(UUID, row["id"]),
                name=row["name"],
                owner=row["owner"],
            ),
        )

    def find_for_owner(
        self, account_id: UUID, user_id: UUID, connection: Optional[Connection] = None
    ) -> Union[None, AccountRecord]:
        result = self.__db.query(
            statement="""
            select accounts.id, accounts.name from accounts
            join memberships on accounts.id = memberships.account_id
            where memberships.user_id = :user_id
            and accounts.id = :account_id
            and memberships.owner is true
            """,
            connection=connection,
            user_id=user_id,
            account_id=account_id,
        )

        return map_one_result(
            result,
            lambda row: AccountRecord(
                id=cast(UUID, row["id"]),
                name=row["name"],
            ),
        )
