"""add radar fields to unit_reviews

Revision ID: 20260513_0001
Revises: e0d76843cf0d
Create Date: 2026-05-13 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260513_0001'
down_revision = 'e0d76843cf0d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('unit_reviews', schema=None) as batch_op:
        batch_op.add_column(sa.Column('exam_difficulty',  sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('group_work',       sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('time_commitment',  sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('rote_learning',    sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('would_recommend',  sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table('unit_reviews', schema=None) as batch_op:
        batch_op.drop_column('would_recommend')
        batch_op.drop_column('rote_learning')
        batch_op.drop_column('time_commitment')
        batch_op.drop_column('group_work')
        batch_op.drop_column('exam_difficulty')
