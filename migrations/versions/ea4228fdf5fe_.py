"""empty message

Revision ID: ea4228fdf5fe
Revises: 79a6147b47a8
Create Date: 2018-11-06 20:00:08.612536

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea4228fdf5fe'
down_revision = '79a6147b47a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('menu', sa.Column('name', sa.String(length=140), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('menu', 'name')
    # ### end Alembic commands ###
