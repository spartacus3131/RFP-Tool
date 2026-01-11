"""Add security features: users, audit logs, multi-tenancy

Revision ID: 0001
Revises: None
Create Date: 2026-01-11

This migration adds:
- users table for authentication
- audit_logs table for compliance logging
- organization_id columns for multi-tenancy
- created_by_id for RFP documents
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, index=True, nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('organization', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('is_superuser', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True, index=True),
        sa.Column('user_email', sa.String(255), nullable=True),
        sa.Column('action', sa.String(50), nullable=False, index=True),
        sa.Column('resource_type', sa.String(50), nullable=True),
        sa.Column('resource_id', sa.String(100), nullable=True, index=True),
        sa.Column('details', postgresql.JSONB(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), server_default=sa.func.now(), nullable=False, index=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('success', sa.Boolean(), default=True),
        sa.Column('error_message', sa.Text(), nullable=True),
    )

    # Add organization_id to rfp_documents (multi-tenancy)
    op.add_column('rfp_documents', sa.Column('organization_id', sa.String(255), nullable=True))
    op.add_column('rfp_documents', sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_index('ix_rfp_documents_organization_id', 'rfp_documents', ['organization_id'])

    # Add organization_id to subconsultants (multi-tenancy)
    op.add_column('subconsultants', sa.Column('organization_id', sa.String(255), nullable=True))
    op.create_index('ix_subconsultants_organization_id', 'subconsultants', ['organization_id'])

    # Add organization_id to capital_budgets (multi-tenancy)
    op.add_column('capital_budgets', sa.Column('organization_id', sa.String(255), nullable=True))
    op.create_index('ix_capital_budgets_organization_id', 'capital_budgets', ['organization_id'])


def downgrade() -> None:
    # Remove organization_id from capital_budgets
    op.drop_index('ix_capital_budgets_organization_id', 'capital_budgets')
    op.drop_column('capital_budgets', 'organization_id')

    # Remove organization_id from subconsultants
    op.drop_index('ix_subconsultants_organization_id', 'subconsultants')
    op.drop_column('subconsultants', 'organization_id')

    # Remove organization_id and created_by_id from rfp_documents
    op.drop_index('ix_rfp_documents_organization_id', 'rfp_documents')
    op.drop_column('rfp_documents', 'created_by_id')
    op.drop_column('rfp_documents', 'organization_id')

    # Drop audit_logs table
    op.drop_table('audit_logs')

    # Drop users table
    op.drop_table('users')
