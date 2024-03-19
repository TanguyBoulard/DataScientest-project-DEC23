"""create user Table

Revision ID: 99d94075a708
Revises: 
Create Date: 2024-03-20 11:15:46.158839

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '99d94075a708'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Définissez les modifications de la base de données dans la fonction upgrade()
def upgrade():
    op.create_table(
        'user',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('password', sa.String(100), nullable=False)
    )


# Ajoutez le code pour annuler les modifications dans la fonction downgrade()
def downgrade():
    op.drop_table('user')