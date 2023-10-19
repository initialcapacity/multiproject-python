from dataclasses import dataclass
from typing import Union
from uuid import UUID

from accounts.accounts_gateway import AccountsGateway
from accounts.memberships_gateway import MembershipsGateway
from accounts.random_name_generator import RandomNameGenerator
from accounts.users_gateway import UsersGateway, UserRecord
from database_support.database_template import DatabaseTemplate


@dataclass
class UserAccount:
    id: UUID
    email: str
    account_id: UUID
    account_name: str


class AccountsService:
    def __init__(
        self,
        db: DatabaseTemplate,
        accounts_gateway: AccountsGateway,
        users_gateway: UsersGateway,
        memberships_gateway: MembershipsGateway,
        name_generator: RandomNameGenerator,
    ):
        self.db = db
        self.accounts_gateway = accounts_gateway
        self.users_gateway = users_gateway
        self.memberships_gateway = memberships_gateway
        self.name_generator = name_generator

    def create_or_find_user(self, email: str) -> Union[None, UserAccount]:
        record = self.__create_or_find_user_and_account(email=email)
        if record is None:
            return None

        accounts = self.accounts_gateway.list_for_user(record.id)
        if len(accounts) == 0:
            return None

        return UserAccount(
            id=record.id,
            email=record.email,
            account_id=accounts[0].id,
            account_name=accounts[0].name,
        )

    def __create_or_find_user_and_account(self, email: str) -> Union[None, UserRecord]:
        with self.db.begin() as connection:
            user_record = self.users_gateway.find_by_email(
                email=email, connection=connection
            )
            if user_record is not None:
                return user_record

            user = self.users_gateway.create(email=email, connection=connection)
            account = self.accounts_gateway.create(
                name=self.name_generator.next(), connection=connection
            )
            if user is None or account is None:
                connection.rollback()
                return None

            self.memberships_gateway.create(
                account_id=account.id,
                user_id=user.id,
                owner=True,
                connection=connection,
            )

            return user

    def add_to_account(self, email: str, account_id: UUID) -> bool:
        with self.db.begin() as connection:
            user = self.users_gateway.find_by_email(email, connection)
            if user is None:
                return False

            membership_id = self.memberships_gateway.create(
                account_id=account_id, user_id=user.id, owner=False
            )

            return membership_id is not None

    def remove_from_account(self, user_id: UUID, account_id: UUID) -> None:
        self.memberships_gateway.delete(account_id=account_id, user_id=user_id)
