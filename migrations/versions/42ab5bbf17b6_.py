"""empty message

Revision ID: 42ab5bbf17b6
Revises: 
Create Date: 2020-03-31 15:20:00.694662

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '42ab5bbf17b6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('problems', 'first_option',
               existing_type=mysql.TEXT(),
               nullable=True)
    op.alter_column('problems', 'fourth_option',
               existing_type=mysql.TEXT(),
               nullable=True)
    op.alter_column('problems', 'second_option',
               existing_type=mysql.TEXT(),
               nullable=True)
    op.alter_column('problems', 'third_option',
               existing_type=mysql.TEXT(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('problems', 'third_option',
               existing_type=mysql.TEXT(),
               nullable=False)
    op.alter_column('problems', 'second_option',
               existing_type=mysql.TEXT(),
               nullable=False)
    op.alter_column('problems', 'fourth_option',
               existing_type=mysql.TEXT(),
               nullable=False)
    op.alter_column('problems', 'first_option',
               existing_type=mysql.TEXT(),
               nullable=False)
    # ### end Alembic commands ###