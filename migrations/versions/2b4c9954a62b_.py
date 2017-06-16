"""empty message

Revision ID: 2b4c9954a62b
Revises: e2f5759562dd
Create Date: 2017-06-16 23:29:20.284870

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2b4c9954a62b'
down_revision = 'e2f5759562dd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comments', sa.Column('creation_date', sa.DateTime(), nullable=True))
    op.add_column('comments', sa.Column('message', sa.Text(), nullable=True))
    op.drop_column('comments', 'added_at')
    op.add_column('projects', sa.Column('bts_link', sa.String(), nullable=True))
    op.add_column('projects', sa.Column('cis_link', sa.String(), nullable=True))
    op.drop_column('projects', 'ci_link')
    op.drop_column('projects', 'bt_link')
    op.add_column('tasks', sa.Column('bts_ticket', sa.Integer(), nullable=True))
    op.drop_column('tasks', 'bt_ticket')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('bt_ticket', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('tasks', 'bts_ticket')
    op.add_column('projects', sa.Column('bt_link', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('projects', sa.Column('ci_link', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('projects', 'cis_link')
    op.drop_column('projects', 'bts_link')
    op.add_column('comments', sa.Column('added_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.drop_column('comments', 'message')
    op.drop_column('comments', 'creation_date')
    # ### end Alembic commands ###