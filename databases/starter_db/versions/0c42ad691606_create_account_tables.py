"""create account tables

Revision ID: 0c42ad691606
Revises:
Create Date: 2023-10-18 07:01:33.536063

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "0c42ad691606"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
    create table accounts (
        id uuid not null primary key default gen_random_uuid(),
        name varchar not null check ( name != '' ),
        created_at timestamp default now()
    );

    create table users (
        id uuid not null primary key default gen_random_uuid(),
        email varchar not null check ( email != '' ),
        created_at timestamp default now()
    );

    create table memberships (
        id uuid not null primary key default gen_random_uuid(),
        account_id uuid not null references accounts (id),
        user_id uuid not null references users (id),
        owner boolean not null,
        created_at timestamp default now()
    );

    create unique index memberships_unique_user_and_account on memberships (user_id, account_id);
    """
    )
