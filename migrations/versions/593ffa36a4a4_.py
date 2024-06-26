"""empty message

Revision ID: 593ffa36a4a4
Revises: 197ed66473ef
Create Date: 2017-06-16 03:19:56.677901

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '593ffa36a4a4'
down_revision = '197ed66473ef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sprints', 'order')
    op.add_column('tasks', sa.Column('creation_date', sa.DateTime(), nullable=False))
    op.alter_column('tasks', 'kind',
               existing_type=postgresql.ENUM('FEATURE', 'BUG', name='taskkind'),
               nullable=False)
    op.alter_column('tasks', 'priority',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('tasks', 'status',
               existing_type=postgresql.ENUM('BACKLOG', 'IN_PROCESS', 'DONE', name='taskstatus'),
               nullable=True)
    op.drop_column('tasks', 'order')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tasks', sa.Column('order', sa.INTEGER(), autoincrement=False, nullable=False))
    op.alter_column('tasks', 'status',
               existing_type=postgresql.ENUM('BACKLOG', 'IN_PROCESS', 'DONE', name='taskstatus'),
               nullable=False)
    op.alter_column('tasks', 'priority',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('tasks', 'kind',
               existing_type=postgresql.ENUM('FEATURE', 'BUG', name='taskkind'),
               nullable=True)
    op.drop_column('tasks', 'creation_date')
    op.add_column('sprints', sa.Column('order', sa.INTEGER(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
