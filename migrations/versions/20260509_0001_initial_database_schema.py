"""Initial database schema

Revision ID: 20260509_0001
Revises:
Create Date: 2026-05-09
"""
from alembic import op
import sqlalchemy as sa


revision = '20260509_0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('student_id', sa.String(length=8), nullable=False),
        sa.Column('display_name', sa.String(length=80), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('faculty', sa.String(length=120), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_student_id'), 'users', ['student_id'], unique=True)

    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('planner_reminders', sa.Boolean(), nullable=False),
        sa.Column('unit_catalogue_updates', sa.Boolean(), nullable=False),
        sa.Column('community_replies', sa.Boolean(), nullable=False),
        sa.Column('weekly_digest', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )

    op.create_table(
        'study_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=120), nullable=False),
        sa.Column('primary_degree_slug', sa.String(length=120), nullable=True),
        sa.Column('secondary_degree_slug', sa.String(length=120), nullable=True),
        sa.Column('start_year', sa.Integer(), nullable=False),
        sa.Column('start_semester', sa.Integer(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_study_plans_user_id'), 'study_plans', ['user_id'], unique=False)

    op.create_table(
        'unit_reviews',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('unit_code', sa.String(length=16), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('difficulty', sa.Integer(), nullable=False),
        sa.Column('workload_hours', sa.Integer(), nullable=True),
        sa.Column('semester_taken', sa.String(length=32), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_unit_reviews_unit_code'), 'unit_reviews', ['unit_code'], unique=False)
    op.create_index(op.f('ix_unit_reviews_user_id'), 'unit_reviews', ['user_id'], unique=False)

    op.create_table(
        'study_plan_units',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('study_plan_id', sa.Integer(), nullable=False),
        sa.Column('unit_code', sa.String(length=16), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('semester', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=24), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['study_plan_id'], ['study_plans.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_study_plan_units_study_plan_id'), 'study_plan_units', ['study_plan_id'], unique=False)
    op.create_index(op.f('ix_study_plan_units_unit_code'), 'study_plan_units', ['unit_code'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_study_plan_units_unit_code'), table_name='study_plan_units')
    op.drop_index(op.f('ix_study_plan_units_study_plan_id'), table_name='study_plan_units')
    op.drop_table('study_plan_units')
    op.drop_index(op.f('ix_unit_reviews_user_id'), table_name='unit_reviews')
    op.drop_index(op.f('ix_unit_reviews_unit_code'), table_name='unit_reviews')
    op.drop_table('unit_reviews')
    op.drop_index(op.f('ix_study_plans_user_id'), table_name='study_plans')
    op.drop_table('study_plans')
    op.drop_table('notification_preferences')
    op.drop_index(op.f('ix_users_student_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
