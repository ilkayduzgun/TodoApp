"""create phone number for user col

Revision ID: 32831e35d269
Revises: 
Create Date: 2023-09-12 09:41:23.691799

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32831e35d269'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users',sa.Column('phone_number',sa.Integer(),nullable=True))


def downgrade() -> None:
    op.drop_column('users','phone_number')
