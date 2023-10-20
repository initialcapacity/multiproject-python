from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from accounts.accounts_gateway import AccountsGateway, AccountRecord
from accounts.memberships_gateway import MembershipsGateway
from accounts.users_gateway import UsersGateway, UserRecord
from database_support.database_template import DatabaseTemplate


@dataclass
class UserAccount:
    id: UUID
    email: str
    account_id: Optional[UUID]
    account_name: Optional[str]


class AccountsService:
    def __init__(
        self,
        db: DatabaseTemplate,
        accounts_gateway: AccountsGateway,
        users_gateway: UsersGateway,
        memberships_gateway: MembershipsGateway,
    ):
        self.db = db
        self.accounts_gateway = accounts_gateway
        self.users_gateway = users_gateway
        self.memberships_gateway = memberships_gateway

    def create_or_find_user(self, email: str) -> Optional[UserAccount]:
        record = self.__maybe_create_user(email=email)
        if record is None:
            return None

        accounts = self.accounts_gateway.list_for_user(record.id)
        if len(accounts) == 0:
            return UserAccount(
                id=record.id,
                email=record.email,
                account_id=None,
                account_name=None,
            )

        return UserAccount(
            id=record.id,
            email=record.email,
            account_id=accounts[0].id,
            account_name=accounts[0].name,
        )

    def create_account(
        self, user_id: UUID, account_name: str
    ) -> Optional[AccountRecord]:
        with self.db.begin() as connection:
            account = self.accounts_gateway.create(
                name=account_name, connection=connection
            )
            if account is None:
                connection.rollback()
                return None

            self.memberships_gateway.create(
                account_id=account.id,
                user_id=user_id,
                owner=True,
                connection=connection,
            )

            return account

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

    def __maybe_create_user(self, email: str) -> Optional[UserRecord]:
        with self.db.begin() as connection:
            user_record = self.users_gateway.find_by_email(
                email=email, connection=connection
            )
            if user_record is not None:
                return user_record

            return self.users_gateway.create(email=email, connection=connection)
