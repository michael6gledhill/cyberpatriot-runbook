"""Initial database migration.

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create teams table
    op.create_table(
        'teams',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('team_id', sa.String(10), nullable=False),
        sa.Column('division', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('team_id'),
    )
    op.create_index(op.f('ix_teams_team_id'), 'teams', ['team_id'], unique=True)

    # Add foreign key for users.team_id
    op.create_foreign_key(
        op.f('fk_users_team_id_teams'),
        'users', 'teams',
        ['team_id'], ['id']
    )

    # Create checklists table
    op.create_table(
        'checklists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )

    # Create checklist_items table
    op.create_table(
        'checklist_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('checklist_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['checklist_id'], ['checklists.id'], name=op.f('fk_checklist_items_checklist_id_checklists')),
    )

    # Create checklist_status table
    op.create_table(
        'checklist_status',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('checklist_item_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_checklist_status_user_id_users')),
        sa.ForeignKeyConstraint(['checklist_item_id'], ['checklist_items.id'], name=op.f('fk_checklist_status_checklist_item_id_checklist_items')),
    )

    # Create readmes table
    op.create_table(
        'readmes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('os_type', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name=op.f('fk_readmes_team_id_teams')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_readmes_user_id_users')),
    )

    # Create notes table
    op.create_table(
        'notes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('note_type', sa.String(50), nullable=False),
        sa.Column('is_encrypted', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('encryption_key_salt', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], name=op.f('fk_notes_team_id_teams')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_notes_user_id_users')),
    )

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(255), nullable=False),
        sa.Column('resource_type', sa.String(50), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_audit_logs_user_id_users')),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('notes')
    op.drop_table('readmes')
    op.drop_table('checklist_status')
    op.drop_table('checklist_items')
    op.drop_table('checklists')
    op.drop_constraint(op.f('fk_users_team_id_teams'), 'users', type_='foreignkey')
    op.drop_index(op.f('ix_teams_team_id'), table_name='teams')
    op.drop_table('teams')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
